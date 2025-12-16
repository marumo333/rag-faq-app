# RAG FAQ Frontend

Next.js (App Router) + TypeScript で実装されたフロントエンドです。Supabase 認証でログインし、FAQ 質問画面とドキュメントアップロード画面を提供します。

## 技術スタック

- Next.js 14 / React 18
- TypeScript
- Tailwind CSS
- Supabase Auth

## 画面構成

- `/login` : ログイン画面（メール + パスワード）
- `/faq` : ChatGPT 風の FAQ 質問・回答画面
- `/documents` : PDF ドキュメントアップロード画面

## ローカル開発

```bash
cd frontend
npm install
npm run dev
```

## 必要な環境変数

`frontend/.env.local` に設定します。

```env
NEXT_PUBLIC_SUPABASE_URL=...         # Supabase Project URL
NEXT_PUBLIC_SUPABASE_ANON_KEY=...    # Supabase anon public key
NEXT_PUBLIC_API_URL=...              # Backend API ベース URL (Render 等)
NEXT_PUBLIC_ANSWER_FUNCTION_URL=...  # rag-answer Edge Function URL (ローカル開発時など)
```

## 主な責務

- Supabase Auth を使ったログイン / ログアウト
- FAQ 質問フォームから Edge Function 経由で回答取得
- ドキュメントアップロード画面から Backend `/documents/upload` を呼び出し
