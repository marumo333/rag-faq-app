
---

## 3. Backlog.md（GitHubでプロジェクト管理する用）

既存 PoC Backlog の形式に合わせた新バージョンです。:contentReference[oaicite:1]{index=1}  

```md
# GitHub Backlog — RAG FAQ App v1.0

対象：**認証はSupabase / 埋め込み生成はPython / Next.jsフロント**  
期間イメージ：**M1〜M3で3〜4週間**

---

## ラベル方針

- 領域: `area:auth` `area:backend` `area:frontend` `area:ingest` `area:retrieval` `area:generation` `area:ops` `area:generation` 
- 種別: `type:backend` `type:frontend` `type:infra` `type:ai` `type:doc` `type:improvement`
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


### [M3][BE/AI] コスト最適化: generation_client.py のリファクタリング

**概要**:

現在、FAQ 2回のリクエストで約 $0.51 のコストが発生しており、実運用に向けてコストが高すぎます。
主な原因は、RAG検索でヒットした大量のコンテキストを無制限にプロンプトに含めていることと、システムプロンプトの結合方法にあると考えられます。
`generation_client.py` を改修し、トークン消費量の制御とモデル設定の最適化を行います。

**現状の課題**:

* コンテキスト（検索結果チャンク）の文字数上限がないため、入力トークンが肥大化しやすい。
* `system_prompt` をユーザー入力と単純結合しているため、モデルの指示追従精度が最適化されていない可能性がある。
* デフォルトモデルがコード上で明示されておらず、呼び出し元次第では高価な Pro モデルが使われるリスクがある。

**変更内容**:

`src/infrastructure/llm/generation_client.py` に対して以下の変更を行う。

1. **システムプロンプトの分離**
* `genai.GenerativeModel` 初期化時に `system_instruction` 引数として渡す形に変更する。


2. **コンテキストサイズの制限 (Hard Limit)**
* `_format_context` メソッドに `max_chars` 引数（デフォルト 15,000文字程度）を追加し、超過分は切り捨てる処理を入れる。


3. **デフォルトモデルの変更**
* デフォルトを `gemini-2.5-flash-lite`に変更し、コストを抑制する。


4. **監査用ログの追加**
* `count_tokens` APIを使用し、リクエスト前の「推定入力トークン数」をINFOログに出力する。



**タスク**:

* [ ] `GeminiGenerationClient` の `__init__` で `system_instruction` を設定するように修正
* [ ] `_format_context` に文字数カウントと break 処理を追加
* [ ] `generate_answer` 内で `count_tokens` を呼び出し、ログ出力する
* [ ] 戻り値の dict に `input_tokens` を含める（将来の監査ログ保存用）

**完了条件(DoD)**:

* [ ] 指定した文字数（例: 15,000文字）を超えるコンテキストを渡した際、エラーにならず適切に切り捨てられること。
* [ ] 実行ログに `Estimated Input Tokens: xxxx` が出力されていること。
* [ ] 修正後もFAQ回答が正常に生成されること。

**関連情報**:

* 対象ファイル: `backend-python/src/infrastructure/llm/generation_client.py`
* ラベル: `area:generation`, `area:ops`, `type:improvement`, `prio:P0`, `size:S`

---


### [Bug] FAQ回答の出典カードに引用テキストが表示されない (No Citation Text)

## 概要

FAQ回答生成時、UI上の出典（引用）カードにおいて、検索スコア（類似度）は表示されるが、肝心の引用テキストが「引用テキスト情報がありません」と表示される。

## 現象

ユーザーが質問を行い、RAG回答が生成された際、出典元リストが以下のように表示される。

**実際の表示:**

> 出典 1
> スコア 0.70
> 引用テキスト情報がありません

**期待される動作:**

> 出典 1
> スコア 0.70
> [ここにチャンクの具体的なテキスト内容が表示されること]

## 原因の仮説 (要調査)

`ARCHITECTURE.md` のデータフローに基づくと、以下のいずれかでデータが脱落している可能性がある。

1. **Backend (`infrastructure/repositories/`)**: pgvector 検索時の SQL クエリで、`content` (チャンクのテキスト本文) カラムを `SELECT` していない、または取得漏れがある。
2. **Backend (`interface/http/api.py`)**: API のレスポンスモデル（Pydantic）において、テキストフィールド名が定義と一致していない（例: DB側が `chunk_text` で API定義が `text` など）。
3. **Frontend (`features/faq/types.ts`)**: バックエンドから送られてくる JSON のフィールド名と、フロントエンドの型定義プロパティ名が不一致を起こしている。

## 再現手順

1. 任意のPDFをアップロードし、Ingestを完了させる。
2. FAQ画面で、そのドキュメントに関連する質問を入力する。
3. 回答生成後の出典エリアを確認する。

## 影響範囲

ユーザーは回答の根拠を確認できず、ハルシネーション（嘘の回答）かどうかの判断がつかないため、サービスの信頼性に関わる重大なバグ。

**ラベル:** `type:bug` `area:frontend` `area:backend` `prio:P0`

## 参考

- 既存PoC用 Backlog (実現可能性推定アプリ) の構成・ラベル付けを流用。:contentReference[oaicite:2]{index=2}  

---

### [M3][P0][OPS/BE] Stripe従量課金 & 利用制限 (High Cost Model)

**目的**: 1アクション原価 $0.25 を回収し、持続的な収益を上げるための課金基盤を導入する。原価が高いため、無料枠と定額枠を厳格に制限する。

**価格設定 (Ver1.0)**:
- **Free**: 月間 **3回** まで (お試し)
- **Standard**: 月額 **1,000円** で **15回** まで (単価 約66円)
- **Overage**: 上限到達時は停止。追加チケット **10回分を 700円** で購入 (単価 70円)

**完了条件**:
- [ ] 質問/DL実行時に `usage_logs` をチェックし、上限到達時に 402 エラーを返すガード処理が稼働
- [ ] フロントエンドから Stripe Checkout へ遷移し、Standardプラン加入またはチケット購入ができる
- [ ] Stripe Webhook を受信し、DBの `subscriptions` や `quota` が即座に更新される
- [ ] 月次バッチ（またはStripeの期間更新イベント）で利用回数がリセットされる

**タスク**:
- [ ] **DB設計**:
  - `user_quotas`: `user_id`, `plan_type`, `remaining_count`, `reset_date`
  - `transactions`: 購入履歴・Stripe Session ID
- [ ] **Backend**:
  - Middleware または Decorator で `check_quota(user_id)` を実装
  - Stripe Webhook ハンドラー (`checkout.session.completed`, `invoice.payment_succeeded`)
- [ ] **Frontend**:
  - 「残り回数」の常時表示コンポーネント
  - 課金モーダル (Free/Standard/Ticket 選択)

**ラベル**: `area:ops` `area:backend` `type:infra` `prio:P0` `size:L`

---

## M4: コスト最適化 & 品質向上 (Post-MVP)

### [M4][P1][AI/BE] RAG原価低減 & キャッシュ戦略

**目的**: 現在の 1回 $0.25 という高額な原価を圧縮し、利益率を改善する。

**完了条件**:
- 同一の質問に対しては LLM を呼び出さず、キャッシュから回答する (原価 $0)
- 難易度の低い質問は安価なモデル (GPT-4o mini / Gemini Flash) にルーティングされる
- 原価が平均 $0.10 以下に抑制されている

**タスク**:
- [ ] **Semantic Cache**: Redis/pgvector を使い、過去の質問と類似度が高い場合はキャッシュ回答を返却
- [ ] **LLM Router**: 質問を分類し、モデルを動的に切り替えるロジック実装
- [ ] **Prompt Optimization**: 入力トークン数を削減 (チャンク数の絞り込み top-k: 5 -> 3 など)

**ラベル**: `area:ai` `area:backend` `type:backend` `prio:P1` `size:M`

