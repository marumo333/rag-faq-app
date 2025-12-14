# RAG FAQ Backend

## セットアップ

### 仮想環境の作成と有効化
python -m venv venv
source venv/bin/activate  # macOS/Linux### 依存関係のインストール
pip install -e .### 起動
# 開発サーバー起動
uvicorn interface.api.main:app --reload

# または
python -m interface.api.main## API ドキュメント
起動後、以下にアクセス:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc