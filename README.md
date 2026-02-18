# RAG FAQ App (Supabase + Python + Next.js)

ユーザー向けFAQを、PDF/ドキュメントからRAG（Retrieval-Augmented Generation）で自動回答するアプリケーション。  
toB向けに自社プロダクトを提供する企業のサポートチームが、社内向けFAQとして利用する想定です。

公開先リンク
- https://rag-faq-app.vercel.app/
## 技術スタック

- 認証・DB/RLS: **Supabase (Auth + Postgres + Edge Functions)**
- 埋め込み生成・チャンク分割: **Python (Onionアーキテクチャ)**
- フロントエンド: **Next.js / React / TypeScript（機能別アーキテクチャ）**

## アーキテクチャ概要

```text
[Next.js 16 (TS/React 19)]
   │ JWT付き fetch
   ▼
[Supabase Auth]
   │ access_token
   ▼
[Supabase Edge Functions]
   ├─ rag-answer (FAQ回答転送)
   └─ rag-ingest  (必要に応じてインジェスト転送)
        │
        ▼
[FastAPI RAG Backend]
   ├─ /answer /search /ingest /documents/upload
   ▼
[Supabase Postgres + pgvector]
```

- 質問/回答は Edge Function で JWT 検証後に FastAPI へ転送。
- ドキュメントアップロードは Next.js → FastAPI `/documents/upload` へ直接 POST（PDF受信→一時保存→Ingest）。
- サインアップで `company_name` メタデータを送信し、DBトリガーで `tenants` と `profiles` を原子的に作成。

## プロジェクト構成

### `frontend/`
- App Router + 機能別構成
- `src/features/auth` - 認証機能
- `src/features/faq` - FAQ機能
- `src/features/documents` - ドキュメント管理

### `backend/` (Onion + Clean/Hexagonal 要素)
- 依存方向: `domain` ← `application` ← `infrastructure` ← `interface`
- `domain/` … entities/repositories/services（純粋なモデルと契約）
- `application/use_cases/` … ingest/search/generate_embeddings/generate_answer などユースケース層
- `infrastructure/` … Supabase/pgvectorリポジトリ実装、LLMクライアント、PDF抽出
- `interface/api/` … FastAPIエンドポイント（/health, /ingest, /search, /answer, /documents/upload）

### `supabase/`
- スキーマ、RLSポリシー
- Edge Functions（認証チェック＋Python APIへのルーティング）

## 主な機能

### ドキュメント処理
- Next.js `/documents` から PDF をアップロード → FastAPI `/documents/upload` で受信
- PDF抽出 → チャンク分割 → 埋め込み生成 → pgvectorへ保存

### FAQ回答生成
- Edge Function rag-answer で JWT を検証し、FastAPI `/answer` へ転送
- Top-K ベクトル検索 → 回答生成（引用・スコア付き）を返却

### セキュリティ
- すべてのAPIを Supabase Auth の認証下に配置
- RLSでテナント分離を担保

## 詳細情報

詳細なタスク・Milestoneは `Backlog.md` を参照。

## License

MIT License (see `LICENSE`).
