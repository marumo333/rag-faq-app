-- クオータテーブル
CREATE TABLE IF NOT EXISTS user_quotas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    plan_type TEXT NOT NULL CHECK (plan_type IN ('free', 'standard')),
    remaining_count INTEGER NOT NULL,
    reset_date TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
); 

-- インデックス作成（user_idで検索が多いため）
CREATE INDEX IF NOT EXISTS idx_user_quotas_user_id ON user_quotas(user_id);

-- RLS有効化
ALTER TABLE user_quotas ENABLE ROW LEVEL SECURITY;

-- RLSポリシー: 自分のクオータのみ閲覧可能
CREATE POLICY "Users can view own quota"
ON user_quotas FOR SELECT
USING (user_id = auth.uid());

-- RLSポリシー: 自分のクオータのみ更新可能
CREATE POLICY "Users can update own quota"
ON user_quotas FOR UPDATE
USING (user_id = auth.uid());

-- サービスロールは全てアクセス可能（バックエンドから操作するため）
CREATE POLICY "Service role has full access to user_quotas"
ON user_quotas FOR ALL
USING (auth.role() = 'service_role');

--トリガー: クオータ更新時にupdated_atを更新
CREATE TRIGGER update_user_quotas_updated_at
BEFORE UPDATE ON user_quotas
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- トランザクションテーブル
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    stripe_session_id TEXT NOT NULL UNIQUE,
    stripe_customer_id TEXT,
    transaction_type TEXT NOT NULL CHECK (transaction_type IN ('subscription', 'ticket')),
    status TEXT NOT NULL CHECK (status IN ('pending', 'completed', 'failed')),
    amount INTEGER NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_stripe_session_id ON transactions(stripe_session_id);

-- RLS有効化
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;

-- RLSポリシー: 自分のトランザクションのみ閲覧可能
CREATE POLICY "Users can view own transactions"
ON transactions FOR SELECT
USING (user_id = auth.uid());

-- RLSポリシー: 自分のトランザクションのみ更新可能
CREATE POLICY "Users can update own transactions"
ON transactions FOR UPDATE
USING (user_id = auth.uid());

-- RLSポリシー: サービスロールは全てアクセス可能（Webhookから作成するため）
CREATE POLICY "Service role has full access to transactions"
ON transactions FOR ALL
USING (auth.role() = 'service_role');

-- トリガー: トランザクション更新時にupdated_atを更新
CREATE TRIGGER update_transactions_updated_at
BEFORE UPDATE ON transactions
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- 利用ログテーブル
CREATE TABLE IF NOT EXISTS usage_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    action_type TEXT NOT NULL,
    resource_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- インデックス作成（user_id単独）
CREATE INDEX IF NOT EXISTS idx_usage_logs_user_id ON usage_logs(user_id);

-- 複合インデックス作成（月次集計用: user_id + created_at）
CREATE INDEX IF NOT EXISTS idx_usage_logs_user_created ON usage_logs(user_id, created_at);

-- RLS有効化
ALTER TABLE usage_logs ENABLE ROW LEVEL SECURITY;

-- RLSポリシー: 自分の利用ログのみ閲覧可能
CREATE POLICY "Users can view own usage logs"
ON usage_logs FOR SELECT
USING (user_id = auth.uid());

-- RLSポリシー: サービスロールは全てアクセス可能（バックエンドから記録するため）
CREATE POLICY "Service role has full access to usage_logs"
ON usage_logs FOR ALL
USING (auth.role() = 'service_role');