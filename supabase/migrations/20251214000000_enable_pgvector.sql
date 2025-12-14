-- pgvector拡張を有効化
-- ベクトル型と類似度検索機能を提供
CREATE EXTENSION IF NOT EXISTS vector;

-- UUID生成機能を有効化
-- テーブルのプライマリキーで使用
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
