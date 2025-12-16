# Supabase 設定

このディレクトリには Supabase プロジェクト用の設定・マイグレーション・Edge Functions が含まれます。

## 構成

- `config.toml` : Supabase CLI 用設定
- `migrations/` : Postgres スキーマ・RLS・関数などのマイグレーション SQL
- `functions/`
  - `rag-ingest/` : PDF ingest 用 Edge Function
  - `rag-answer/` : FAQ 回答生成用 Edge Function

## ローカル開発

```bash
cd supabase
supabase start           # ローカル Supabase スタック起動
supabase functions serve rag-ingest --env-file ./supabase/.env.local
supabase functions serve rag-answer --env-file ./supabase/.env.local
```

## データベースマイグレーション

```bash
# ローカルに適用
supabase db reset

# 本番プロジェクトに適用
supabase link --project-ref <PROJECT_REF> --password '<DB_PASSWORD>'
supabase db push
```

## 必要な環境変数（Edge Functions 用）

Supabase ダッシュボードの Functions → Environment Variables で設定します。

- `PYTHON_API_URL` : Backend FastAPI の URL（Render など）
- その他、必要に応じて API キー等

Edge Functions 内では `Deno.env.get('...')` で参照します。
