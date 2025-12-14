以下の内容を `supabase/README.md` に記述してください：

```markdown
# Supabase セットアップ

RAG FAQ アプリのデータベースとバックエンドサービス設定

## 前提条件

- [Supabase CLI](https://supabase.com/docs/guides/cli) がインストール済み
- Docker Desktop が起動している

## ローカル開発環境のセットアップ

### 1. Supabase CLIのインストール

```bash
# macOS
brew install supabase/tap/supabase

# その他のOSは公式ドキュメント参照
# https://supabase.com/docs/guides/cli/getting-started
```

### 2. Dockerの起動確認

```bash
# Dockerが起動しているか確認
docker info

# 起動していない場合は Docker Desktop を起動
open -a Docker
```

### 3. Supabaseローカル環境の起動

```bash
cd supabase
supabase start
```

初回起動時、以下の情報が表示されます（**メモしてください**）:
- API URL: `http://127.0.0.1:54321`
- DB URL: `postgresql://postgres:postgres@127.0.0.1:54322/postgres`
- Studio URL: `http://127.0.0.1:54323`
- anon key: （JWTトークン）
- service_role key: （JWTトークン）

### 4. マイグレーションの確認

起動時に `migrations/` 内のSQLファイルが自動的に実行されます:
1. `20251214000000_enable_pgvector.sql` - pgvector拡張の有効化
2. `20251214000001_create_tables.sql` - テーブル作成
3. `20251214000002_create_rls_policies.sql` - RLSポリシー設定

### 5. Supabase Studioでの確認

ブラウザで以下にアクセス:
```
http://localhost:54323
```

左メニューの「Table Editor」で以下のテーブルを確認:
- ✅ `tenants` - テナント情報
- ✅ `documents` - ドキュメント
- ✅ `faq_chunks` - チャンク
- ✅ `faq_embeddings` - 埋め込みベクトル

## 環境変数の設定

バックエンド（`backend/.env`）に以下を追加:

```env
SUPABASE_URL=http://127.0.0.1:54321
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
```

> **Note**: `supabase start` 実行時に表示されたキーを使用してください

## よく使うコマンド

### Supabaseの停止
```bash
supabase stop
```

### Supabaseの再起動
```bash
supabase stop
supabase start
```

### データベースのリセット
```bash
supabase db reset
```

マイグレーションが再実行され、データがクリアされます。

### マイグレーションの状態確認
```bash
supabase migration list
```

### 新しいマイグレーションの作成
```bash
supabase migration new <migration_name>
```

例: `supabase migration new add_user_profiles`

## 本番環境へのデプロイ

### 1. Supabaseプロジェクトの作成

[Supabase Dashboard](https://app.supabase.com/) でプロジェクトを作成

### 2. ローカル環境とリンク

```bash
supabase link --project-ref <your-project-ref>
```

### 3. マイグレーションのプッシュ

```bash
supabase db push
```

ローカルのマイグレーションが本番環境に適用されます。

## トラブルシューティング

### Supabaseが起動しない

**Dockerが起動していない場合:**
```bash
open -a Docker
# Dockerが起動してから再度実行
supabase start
```

**ポートが使用中の場合:**
```bash
# 既存のSupabaseコンテナを停止
supabase stop
# 起動
supabase start
```

### マイグレーションエラー

```bash
# データベースをリセット
supabase db reset

# それでも解決しない場合
supabase stop
docker system prune -a  # 注意: すべてのDockerリソースを削除
supabase start
```

### ログの確認

```bash
# Supabaseの状態確認
supabase status

# Dockerコンテナログ
docker logs supabase_db_rag-faq-app
```

## データベーススキーマ

### テーブル構成

```
tenants
├── id (UUID, PK)
├── name (TEXT)
├── created_at (TIMESTAMP)
└── updated_at (TIMESTAMP)

documents
├── id (UUID, PK)
├── tenant_id (UUID, FK → tenants)
├── title (TEXT)
├── file_path (TEXT)
├── status (TEXT)
├── created_at (TIMESTAMP)
└── updated_at (TIMESTAMP)

faq_chunks
├── id (UUID, PK)
├── document_id (UUID, FK → documents)
├── content (TEXT)
├── section (TEXT)
├── position (INTEGER)
└── created_at (TIMESTAMP)

faq_embeddings
├── id (UUID, PK)
├── chunk_id (UUID, FK → faq_chunks)
├── embedding (VECTOR(768))
└── created_at (TIMESTAMP)
```

## 参考リンク

- [Supabase CLI Documentation](https://supabase.com/docs/guides/cli)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [Supabase Local Development](https://supabase.com/docs/guides/local-development)
```
