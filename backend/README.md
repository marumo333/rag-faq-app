# RAG FAQ Backend

FastAPI ベースの RAG FAQ バックエンドです。Supabase をデータストアとして利用し、PDF ドキュメントの取り込み・埋め込み生成・FAQ 検索 API を提供します。

## 技術スタック

- Python 3.11
- FastAPI + Uvicorn
- Supabase (Postgres + pgvector)
- Google Gemini Embedding API (`GOOGLE_API_KEY`)

## 主要エンドポイント

- `GET /health` : ヘルスチェック
- `POST /answer` : 質問に対する回答生成
- `POST /search` : ベクトル検索（必要に応じて）
- `POST /documents/upload` : PDF アップロード + ingest 実行

## ローカル開発

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install .
uvicorn interface.api.main:app --host 0.0.0.0 --port 8000 --reload
```

## 必要な環境変数

`.env` もしくは Render / Fly.io の環境変数に設定します。

- `SUPABASE_URL` : Supabase プロジェクトの URL
- `SUPABASE_SERVICE_ROLE_KEY` : Supabase Service Role Key
- `GOOGLE_API_KEY` : Gemini API Key

## デプロイ（Render の例）

- Root Directory: `backend`
- Build Command: `pip install .`
- Start Command: `uvicorn interface.api.main:app --host 0.0.0.0 --port 8000`
- Environment Variables に上記キーを登録
