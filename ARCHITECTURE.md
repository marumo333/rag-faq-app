# アーキテクチャ詳細

## システム構成図

```text
[Next.js (TS)]
   │  JWT認証
   ▼
[Supabase Auth + Edge Functions]
   │  HTTP (内部API)
   ▼
[Python RAG Backend (Onion Architecture)]
   │  SQL (pgvector)
   ▼
[Supabase Postgres + pgvector]
```

## バックエンド (Python)

### Onionアーキテクチャ

依存関係: `domain` ← `application` ← `infrastructure` ← `interface`

### ディレクトリ構造

```
backend-python/
  src/
    domain/
      document.py           # ドキュメントエンティティ
      chunk.py              # チャンクエンティティ
    
    application/
      ingest_document.py    # ドキュメント取り込みユースケース
      search_chunks.py      # チャンク検索ユースケース
    
    infrastructure/
      repositories/
        document_repository_pg.py    # ドキュメントリポジトリ (PostgreSQL)
        embedding_repository_pg.py   # 埋め込みリポジトリ (pgvector)
      
      llm/
        embedding_client.py  # 埋め込み生成クライアント
        rag_client.py        # RAG処理クライアント
      
      pdf/
        pdf_extractor.py     # PDFテキスト抽出
      
      db/
        connection.py        # データベース接続管理
    
    interface/
      http/
        api.py               # FastAPIエンドポイント
```

### レイヤーの責務

#### Domain層 (`domain/`)
- ビジネスロジックとエンティティの定義
- フレームワーク・外部依存なし
- **主要クラス:**
  - `Document`: ドキュメントのドメインモデル
  - `Chunk`: チャンクのドメインモデル

#### Application層 (`application/`)
- ユースケースの実装
- ドメインモデルを組み合わせてビジネスフローを構築
- **主要ユースケース:**
  - `IngestDocument`: ドキュメントの取り込み処理
  - `SearchChunks`: ベクトル検索によるチャンク取得

#### Infrastructure層 (`infrastructure/`)
- 外部システムとの連携実装
- **Repositories**: データ永続化
  - PostgreSQL/pgvectorへのCRUD操作
- **LLM**: AI/ML連携
  - 埋め込みベクトルの生成
  - RAG応答の生成
- **PDF**: ドキュメント処理
  - PDFからのテキスト抽出
- **DB**: データベース
  - 接続プール管理

#### Interface層 (`interface/`)
- 外部からのリクエスト受付
- **HTTP**: FastAPIによるREST API
  - エンドポイント定義
  - リクエスト/レスポンスの変換

---

## フロントエンド (Next.js)

### 機能ベースアーキテクチャ

各機能（feature）ごとに独立したモジュールとして構成し、保守性と再利用性を向上。

### ディレクトリ構造

```
frontend/
  src/
    app/
      page.tsx              # トップページ
      layout.tsx            # ルートレイアウト
    
    features/
      auth/                 # 認証機能
        components/         # 認証関連コンポーネント
        hooks/              # 認証カスタムフック
        services/           # 認証API呼び出し
        types.ts            # 認証型定義
      
      documents/            # ドキュメント管理機能
        components/         # ドキュメント関連コンポーネント
        hooks/              # ドキュメントカスタムフック
        services/           # ドキュメントAPI呼び出し
        types.ts            # ドキュメント型定義
      
      faq/                  # FAQ機能
        components/         # FAQ関連コンポーネント
        hooks/              # FAQカスタムフック
        services/           # FAQ API呼び出し
        types.ts            # FAQ型定義
    
    shared/
      components/           # 共通UIコンポーネント
      lib/                  # ユーティリティ関数
      ui/                   # 汎用UIパーツ（Button、Inputなど）
```

### 機能モジュールの構成

各 `features/` 配下のモジュールは以下の構造を持つ：

#### `components/`
- 機能固有のUIコンポーネント
- Presentational/Container パターンを採用可能

#### `hooks/`
- カスタムフック（状態管理、副作用処理）
- 例: `useAuth()`, `useDocumentUpload()`, `useFaqSearch()`

#### `services/`
- APIクライアント
- Supabase/バックエンドとの通信ロジック

#### `types.ts`
- 型定義（TypeScript）
- APIレスポンス、状態の型

### 共通モジュール (`shared/`)

#### `components/`
- 複数機能で再利用される高度なコンポーネント
- 例: `Header`, `Footer`, `Sidebar`

#### `lib/`
- ヘルパー関数、ユーティリティ
- 例: 日付フォーマット、バリデーション

#### `ui/`
- 基本的なUIパーツ（デザインシステム）
- 例: `Button`, `Input`, `Modal`, `Card`

---

## データフロー

### ドキュメント取り込みフロー

```text
[ユーザー] 
  → ドキュメントアップロード (frontend/features/documents)
  → Supabase Storage
  → Edge Function (認証チェック)
  → Python API (interface/http/api.py)
  → IngestDocument UseCase (application/)
  → PDF抽出 (infrastructure/pdf/)
  → チャンク分割 (domain/)
  → 埋め込み生成 (infrastructure/llm/)
  → pgvector保存 (infrastructure/repositories/)
```

### FAQ検索フロー

```text
[ユーザー]
  → 質問入力 (frontend/features/faq)
  → Edge Function (認証チェック)
  → Python API (interface/http/api.py)
  → SearchChunks UseCase (application/)
  → ベクトル検索 (infrastructure/repositories/)
  → RAG生成 (infrastructure/llm/)
  → 回答返却 (引用付き)
```

---

## 技術スタック詳細

### バックエンド
- **言語**: Python 3.11+
- **フレームワーク**: FastAPI
- **ORM/DB**: psycopg2 / SQLAlchemy
- **ベクトルDB**: pgvector (Supabase Postgres拡張)
- **LLM**: Anthropic Claude / Google Gemini
- **PDF処理**: PyPDF2 / pdfplumber

### フロントエンド
- **言語**: TypeScript
- **フレームワーク**: Next.js 14 (App Router)
- **UIライブラリ**: React 18
- **状態管理**: React Hooks / Context API
- **スタイリング**: Tailwind CSS
- **認証**: Supabase Auth

### インフラ
- **認証・DB**: Supabase (Auth + Postgres + Storage)
- **Edge Functions**: Deno (TypeScript)
- **ベクトル拡張**: pgvector

