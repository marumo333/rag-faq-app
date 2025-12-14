-- Row Level Security (RLS) の有効化
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE faq_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE faq_embeddings ENABLE ROW LEVEL SECURITY;

-- テナント: 認証ユーザーは自分のテナントのみアクセス可能
CREATE POLICY "Users can view their own tenant"
ON tenants FOR SELECT
USING (auth.uid()::text = id::text);


-- ドキュメント: テナントIDでフィルタ
CREATE POLICY "Users can view documents in their tenant"
ON documents FOR SELECT
USING (tenant_id IN (
    SELECT id FROM tenants WHERE auth.uid()::text = id::text
));

CREATE POLICY "Users can insert documents in their tenant"
ON documents FOR INSERT
WITH CHECK (tenant_id IN (
    SELECT id FROM tenants WHERE auth.uid()::text = id::text
));

-- チャンク: ドキュメント経由でテナントIDチェック
CREATE POLICY "Users can view chunks in their tenant"
ON faq_chunks FOR SELECT
USING (document_id IN (
    SELECT id FROM documents WHERE tenant_id IN (
        SELECT id FROM tenants WHERE auth.uid()::text = id::text
    )
));

-- 埋め込み: チャンク経由でアクセス制御
CREATE POLICY "Users can view embeddings in their tenant"
ON faq_embeddings FOR SELECT
USING (chunk_id IN (
    SELECT id FROM faq_chunks WHERE document_id IN (
        SELECT id FROM documents WHERE tenant_id IN (
            SELECT id FROM tenants WHERE auth.uid()::text = id::text
        )
    )
));

-- サービスロールは全てアクセス可能
CREATE POLICY "Service role has full access to tenants"
ON tenants FOR ALL
USING (auth.role() = 'service_role');

CREATE POLICY "Service role has full access to documents"
ON documents FOR ALL
USING (auth.role() = 'service_role');

CREATE POLICY "Service role has full access to chunks"
ON faq_chunks FOR ALL
USING (auth.role() = 'service_role');

CREATE POLICY "Service role has full access to embeddings"
ON faq_embeddings FOR ALL
USING (auth.role() = 'service_role');