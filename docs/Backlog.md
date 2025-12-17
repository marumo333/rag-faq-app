
---

## 3. Backlog.md（GitHubでプロジェクト管理する用）

既存 PoC Backlog の形式に合わせた新バージョンです。:contentReference[oaicite:1]{index=1}  

```md
# GitHub Backlog — RAG FAQ App v1.0

対象：**認証はSupabase / 埋め込み生成はPython / Next.jsフロント**  
期間イメージ：**M1〜M3で3〜4週間**

---

## ラベル方針

- 領域: `area:auth` `area:backend` `area:frontend` `area:ingest` `area:retrieval` `area:generation` `area:ops`
- 種別: `type:backend` `type:frontend` `type:infra` `type:ai` `type:doc`
- 優先度: `prio:P0` `prio:P1`
- サイズ: `size:S` `size:M` `size:L`

---

## Milestone 概要

| Milestone | 期間目安 | 目的 | DoD |
|---|---|---|---|
| M1 | Week 1 | Supabaseプロジェクト & Python/Next.js 基盤作成 | Auth/RLS/pgvector/各ディレクトリが動く |
| M2 | Week 2 | インジェスト〜RAG回答 API 完成 | PDF→チャンク→埋め込み→Top-K→回答が通る |
| M3 | Week 3 | フロントUI/運用・評価まわり | FAQ画面・ドキュメント管理・基本メトリクス |

---

## M1: 基盤構築

### [M1][P0][INF] リポジトリ初期構成（frontend / backend-python / supabase）

**目的**: 各ディレクトリと最小限の設定を用意し、ローカルで起動できる状態にする。

**完了条件**:
- `frontend/` で Next.js プロジェクトが `npm run dev` で起動
- `backend-python/` で FastAPI (or 他フレームワーク) が devサーバ起動
- `supabase/` にスキーマ定義とセットアップ手順が記載されている

**タスク**:
- [ ] ルート構成の作成（この Backlog に沿ってコマンド化）
- [ ] `frontend` の `package.json` / `tsconfig` / `next.config` 作成
- [ ] `backend-python` の `pyproject.toml` / `src/` 構成作成
- [ ] `supabase` ディレクトリに README と初期SQL置き場を作成

**ラベル**: `area:ops` `type:infra` `prio:P0` `size:S`

---

### [M1][P0][AUTH] Supabase Auth + RLS 初期設定

**目的**: 認証・権限の基盤を Supabase 上に構築する。

**完了条件**:
- Auth (メール+OAuth) の有効化
- `profiles` 的なユーザープロファイルテーブルが作成され、`auth.users` と紐付く
- FAQ/ドキュメント用のベーステーブルが作成され、テナント単位のRLSが設定されている

**タスク**:
- [ ] Supabase プロジェクト作成
- [ ] `users` / `tenants` / `documents` テーブルの仮スキーマ定義
- [ ] RLS ポリシー（テナントID or user_id でフィルタ）
- [ ] Supabaseダッシュボードでの動作確認

**ラベル**: `area:auth` `area:backend` `type:infra` `prio:P0` `size:M`

---

### [M1][P0][INF] pgvector 導入 & ベクトルテーブル設計

**目的**: 埋め込みベクトルを保存するための pgvector 設定とテーブル設計を行う。

**完了条件**:
- `pgvector` 拡張が有効化されている
- `faq_embeddings` テーブル（`id`, `document_id`, `chunk_id`, `embedding vector`, `section`, `created_at` など）が作成済み
- 単純なベクトル検索クエリで動作確認済み

**タスク**:
- [ ] pgvector 拡張の有効化SQL
- [ ] `faq_embeddings` / `faq_chunks` テーブル設計
- [ ] サンプルデータを挿入して cosine距離で検索テスト

**ラベル**: `area:backend` `area:ingest` `type:infra` `prio:P0` `size:S`

---

### [M1][P0][BE/AI] Python Onion アーキテクチャの雛形作成

**目的**: backend-python に Onionアーキテクチャの最小構成を作る。

**完了条件**:
- `domain/`, `application/`, `infrastructure/`, `interface/` ディレクトリ作成
- 代表的なEntity（Document, Chunk）と UseCase（IngestDocument のダミー）が存在
- FastAPI で `/health` が返せる

**タスク**:
- [ ] Domain: `document.py`, `chunk.py`
- [ ] Application: `ingest_document.py`（ダミー実装）
- [ ] Infrastructure: 仮の `document_repository_inmemory.py`
- [ ] Interface: FastAPIエンドポイント `/health` & `/ingest` (仮実装)

**ラベル**: `area:backend` `area:ingest` `type:backend` `type:ai` `prio:P0` `size:M`

---

### [M1][P0][AUTH] Supabase Edge Function で JWT 検証 + Python API ルーティング

**目的**: Supabase Edge Functions を使って認証付きで Python API にリクエストを流す。

**完了条件**:
- Edge Function で JWT を検証し、ユーザー情報を取得
- 認証OKなリクエストのみ Python の `/ingest` に HTTP 連携
- 認証エラー時は 401/403 を返す

**タスク**:
- [ ] Edge Function プロジェクト作成 (`supabase/functions/rag-ingest`)
- [ ] `Authorization` ヘッダ検証ロジック
- [ ] Python バックエンドのURLを環境変数で参照
- [ ] ローカル環境で end-to-end 確認

**ラベル**: `area:auth` `area:backend` `type:infra` `prio:P0` `size:M`

---

## M2: インジェスト〜RAG回答

### [M2][P0][AI/BE] PDF → チャンク分割 UseCase 実装

**目的**: PDFからテキストを抽出し、RAG向けのチャンクに分割するユースケースを実装する。

**完了条件**:
- `.pdf` 1ファイルから
  - テキスト抽出 → 見出し/段落に基づくチャンク分割
- チャンク長がおおよそ 500〜1000文字に収まる
- Supabase `faq_chunks` に保存される

**タスク**:
- [ ] Infrastructure: PDF抽出モジュール（PyPDF2など）
- [ ] Domain: Chunk生成ロジック
- [ ] Application: `IngestDocument` UseCaseで抽出〜分割〜保存を一気通し
- [ ] エラー時のロギング/リトライ方針

**ラベル**: `area:ingest` `type:backend` `type:ai` `prio:P0` `size:M`

---

### [M2][P0][AI/BE] 埋め込み生成 & pgvector 書き込み実装

**目的**: チャンクに対し埋め込みを生成し、pgvectorに保存する。

**完了条件**:
- Claude/Geminiなどの埋め込みAPIからベクトルを取得
- `faq_embeddings` にバルクINSERT
- 1文書あたり数百チャンク規模で動作確認済み

**タスク**:
- [ ] Infrastructure: LLMクライアント（埋め込み用）
- [ ] Application: `GenerateEmbeddingsForDocument` UseCase
- [ ] ベクトル次元に応じたテーブル型調整
- [ ] スループット計測（目標チャンク/分）

**ラベル**: `area:ingest` `area:backend` `area:ai` `type:backend` `prio:P0` `size:M`

---

### [M2][P0][BE] ベクトルTop-K検索 API

**目的**: 質問クエリから埋め込みを生成し、Top-K類似チャンクを取得するAPIを提供。

**完了条件**:
- `/search` に質問を投げると、関連度スコア付きTop-Kチャンクが返ってくる
- 応答時間がDB内で 150ms以下（目安）

**タスク**:
- [ ] クエリ埋め込み生成
- [ ] pgvector によるcosine距離検索SQL
- [ ] FastAPIエンドポイント `/search`
- [ ] 単体テスト追加

**ラベル**: `area:retrieval` `area:backend` `type:backend` `prio:P0` `size:S`

---

### [M2][P0][AI] RAG回答生成（引用付き）

**目的**: Top-Kチャンクをコンテキストに、引用付きのFAQ回答を生成する。

**完了条件**:
- `/answer` に質問を投げると
  - 回答テキスト
  - 使用されたチャンクID一覧
  - 参照文書ID/セクション情報
  が返る

**タスク**:
- [ ] プロンプト設計（役割/禁止事項/出力フォーマット）
- [ ] コンテキスト整形（重複/矛盾抑制）
- [ ] FastAPI `/answer` 実装
- [ ] いくつかのサンプル質問で動作確認

**ラベル**: `area:generation` `area:backend` `area:ai` `prio:P0` `size:M`

---

## M3: フロントエンド & 運用周り

### [M3][P0][FE] Feature-based アーキテクチャの骨組み

**目的**: Next.js に機能別アーキテクチャを導入し、基本ページを作る。

**完了条件**:
- `features/auth`, `features/documents`, `features/faq` の3機能フォルダが存在
- 各機能に `components/`, `hooks/`, `services/` が最低1つずつ
- ログイン→FAQ画面への遷移ができる

**タスク**:
- [ ] `features/auth` … ログインフォーム + Supabase Auth クライアント
- [ ] `features/documents` … PDFアップロード画面の骨組み
- [ ] `features/faq` … 質問入力 + 回答表示の骨組み
- [ ] `shared/components` に共通UIコンポーネント

**ラベル**: `area:frontend` `type:frontend` `prio:P0` `size:M`

---

### [M3][P0][FE] FAQ画面 UI / UX

**目的**: 質問履歴・回答カード・引用表示など、FAQ用のUIを実用レベルまで仕上げる。

**完了条件**:
- 質問履歴がリスト表示される
- 各回答カードにスコア/引用/出典が表示される
- エラー時の表示・ローディングが整備されている

**タスク**:
- [ ] 回答カードコンポーネント
- [ ] 引用箇所のハイライト
- [ ] エラー/ローディング状態のUI

**ラベル**: `area:frontend` `type:frontend` `prio:P0` `size:M`

---

### [M3][P1][OPS] 監査ログ & 簡易メトリクス

**目的**: 質問/回答/参照チャンクのログと、基本的なKPIをとれるようにする。

**完了条件**:
- 質問/回答/参照チャンクID/モデル名を保存
- シンプルな集計クエリで
  - 日別件数
  - RAG回答率
  が取れる

**タスク**:
- [ ] ログテーブル定義
- [ ] Pythonから非同期でログ書き込み
- [ ] 取得用のSQL or 簡易API

**ラベル**: `area:ops` `area:backend` `type:backend` `prio:P1` `size:S`

---

### [M3][P0][BE/DB] テナント新規開設トリガーの実装 (Auth連携)

**概要**:
新規登録（Sign Up）時に、入力された「企業名」を元に自動的に `tenants` レコードを作成し、管理者ユーザーと紐付けるデータベーストリガーを実装する。
フロントエンドは `supabase.auth.signUp()` にメタデータを渡すだけで、DB層で原子的にテナント作成を完結させる。

**目的**:
- 企業と管理者の作成を単一トランザクションで保証し、データ不整合（Orphaned Record）を防ぐ。
- フロントエンドの実装コストを最小化する。

**実装仕様 (Technical Spec)**:

1. **DBトリガー関数 (`public.handle_new_tenant_user`)**
   - `auth.users` の INSERT 後に発火。
   - `new.raw_user_meta_data->>'company_name'` が存在する場合のみ実行。
   - `tenants` に INSERT → 生成された ID を取得。
   - `public.users` (profiles) に `tenant_id` と `role='admin'` をセットして INSERT。
   - **重要**: 関数は `SECURITY DEFINER` で定義すること（新規ユーザーはまだ権限がないため）。

2. **フロントエンド (`features/auth`)**
   - Sign Up 時に `options.data.company_name` を送信するよう実装。

**タスク**:
- [ ] DB: `supabase/migrations/` にトリガー関数とTrigger定義のSQLを作成
- [ ] DB: RLSポリシーが新規作成直後のユーザーにも正しく適用されるか確認
- [ ] FE: `useTenantRegister` フックの実装（`signUp` 呼び出し）
- [ ] Test: 正常系（テナント作成成功）と異常系（テナント名重複などでロールバックされるか）の確認

**完了条件**:
- [ ] フロントエンドからサインアップ後、`tenants` と `public.users` にレコードが作成されている
- [ ] 作成されたユーザーの `tenant_id` が正しい企業を指している

**ラベル**: `area:backend` `area:auth` `type:backend` `prio:P0` `size:S`

---

## 参考

- 既存PoC用 Backlog (実現可能性推定アプリ) の構成・ラベル付けを流用。:contentReference[oaicite:2]{index=2}  

