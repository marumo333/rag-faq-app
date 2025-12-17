-- テナント自動作成トリガー & RLS調整
-- 新規登録時に company_name メタデータがある場合:
--  - tenants にレコードを作成
--  - profiles に tenant_id と role='admin' を付与して作成
-- それ以外は従来通り profiles のみ作成

-- 既存トリガー/関数を置き換え
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
DROP FUNCTION IF EXISTS public.handle_new_user();

CREATE OR REPLACE FUNCTION public.handle_new_tenant_user()
RETURNS TRIGGER AS $$
DECLARE
    new_tenant_id UUID;
    company_name TEXT;
    full_name TEXT;
BEGIN
    company_name := NULLIF(TRIM(COALESCE(NEW.raw_user_meta_data->>'company_name', '')), '');
    full_name := COALESCE(NULLIF(TRIM(NEW.raw_user_meta_data->>'full_name'), ''), NEW.email);

    IF company_name IS NOT NULL THEN
        -- 1. テナント作成
        INSERT INTO public.tenants (name)
        VALUES (company_name)
        RETURNING id INTO new_tenant_id;

        -- 2. プロファイル作成（管理者として紐付け）
        INSERT INTO public.profiles (id, email, full_name, tenant_id, role)
        VALUES (NEW.id, NEW.email, full_name, new_tenant_id, 'admin');
    ELSE
        -- テナント情報が無い場合は従来通りprofilesのみ作成
        INSERT INTO public.profiles (id, email, full_name)
        VALUES (NEW.id, NEW.email, full_name);
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
AFTER INSERT ON auth.users
FOR EACH ROW
EXECUTE FUNCTION public.handle_new_tenant_user();

-- RLS ポリシーの見直し（tenant_id を profiles 経由で判定）
DROP POLICY IF EXISTS "Users can view their own tenant" ON tenants;
CREATE POLICY "Users can view their own tenant"
ON tenants FOR SELECT
USING (
    id IN (
        SELECT tenant_id FROM profiles WHERE id = auth.uid()
    )
);

DROP POLICY IF EXISTS "Users can view documents in their tenant" ON documents;
DROP POLICY IF EXISTS "Users can insert documents in their tenant" ON documents;
CREATE POLICY "Users can view documents in their tenant"
ON documents FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM profiles p
        WHERE p.id = auth.uid() AND p.tenant_id = documents.tenant_id
    )
);

CREATE POLICY "Users can insert documents in their tenant"
ON documents FOR INSERT
WITH CHECK (
    EXISTS (
        SELECT 1 FROM profiles p
        WHERE p.id = auth.uid() AND p.tenant_id = documents.tenant_id
    )
);

DROP POLICY IF EXISTS "Users can view chunks in their tenant" ON faq_chunks;
CREATE POLICY "Users can view chunks in their tenant"
ON faq_chunks FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM documents d
        JOIN profiles p ON p.tenant_id = d.tenant_id AND p.id = auth.uid()
        WHERE d.id = faq_chunks.document_id
    )
);

DROP POLICY IF EXISTS "Users can view embeddings in their tenant" ON faq_embeddings;
CREATE POLICY "Users can view embeddings in their tenant"
ON faq_embeddings FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM faq_chunks c
        JOIN documents d ON d.id = c.document_id
        JOIN profiles p ON p.tenant_id = d.tenant_id AND p.id = auth.uid()
        WHERE c.id = faq_embeddings.chunk_id
    )
);
