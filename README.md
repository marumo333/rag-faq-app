# RAG FAQ App (Supabase + Python + Next.js)

ユーザー向けFAQを、PDF/ドキュメントからRAG（Retrieval-Augmented Generation）で自動回答するアプリケーション。

## 技術スタック

- 認証・DB/RLS: **Supabase (Auth + Postgres + Edge Functions)**
- 埋め込み生成・チャンク分割: **Python (Onionアーキテクチャ)**
- フロントエンド: **Next.js / React / TypeScript（機能別アーキテクチャ）**

## アーキテクチャ概要

```text
[Next.js (TS)]
   │  JWT
   ▼
[Supabase Auth + Edge Functions]
   │  HTTP (内部API)
   ▼
[Python RAG Backend (Onion)]
   │  SQL (pgvector)
   ▼
[Supabase Postgres + pgvector]
```

## プロジェクト構成

### `frontend/`
- App Router + 機能別構成
- `src/features/auth` - 認証機能
- `src/features/faq` - FAQ機能
- `src/features/documents` - ドキュメント管理

### `backend-python/` (Onion Architecture)
- `domain/` - Document, Chunk, Embedding, IngestJob などのドメインモデル
- `application/` - UseCase（IngestDocument, ReindexDocument など）
- `infrastructure/` - pgvectorリポジトリ, LLMクライアント(Claude/Gemini), PDF抽出
- `interface/` - FastAPI などHTTPインターフェース

### `supabase/`
- スキーマ、RLSポリシー
- Edge Functions（認証チェック＋Python APIへのルーティング）

## 主な機能

### ドキュメント処理
PDF/Wordをアップロードすると自動で以下の処理を実行：
1. テキスト抽出
2. チャンク分割
3. 埋め込み生成
4. pgvector保存

### FAQ回答生成
ユーザーの質問に対して以下を実行：
1. Top-Kベクトル検索
2. 根拠付き回答（引用＋出典メタ）を生成

### セキュリティ
- すべてのAPIを Supabase Auth の認証下に配置
- RLSでテナント分離を担保

## 詳細情報

詳細なタスク・Milestoneは `Backlog.md` を参照。
