-- documentsテーブルにカラムを追加
ALTER TABLE documents 
ADD COLUMN IF NOT EXISTS error_message TEXT,
ADD COLUMN IF NOT EXISTS total_chunks INTEGER;

-- ステータスでの検索を高速化
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);

-- コメント追加
COMMENT ON COLUMN documents.error_message IS 'エラー発生時のエラーメッセージ';
COMMENT ON COLUMN documents.total_chunks IS '生成されたチャンクの総数';