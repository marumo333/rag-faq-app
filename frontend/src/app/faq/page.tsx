'use client'

import { useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { useFaq } from '@/features/faq/hooks/useFaq'
import { QuestionForm } from '@/features/faq/components/QuestionForm'
import { AnswerDisplay } from '@/features/faq/components/AnswerDisplay'

export default function FaqPage() {
  const { user, loading: authLoading, signOut } = useAuth()
  const router = useRouter()
  
  // 仮のテナントID（実際はuserから取得）
  const tenantId = '188d1388-ae85-4753-b640-eea55e9d83fe'
  const { history, loading: faqLoading, error, askQuestion } = useFaq(tenantId)

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login')
    }
  }, [user, authLoading, router])

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900 text-white">
        <p>読み込み中...</p>
      </div>
    )
  }

  if (!user) {
    return null
  }

  const handleQuestion = async (question: string) => {
    try {
      await askQuestion(question)
    } catch (err) {
      console.error('Failed to get answer:', err)
    }
  }

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 flex flex-col">
      {/* ヘッダー */}
      <header className="border-b border-gray-800 bg-gray-900/80 backdrop-blur sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-2xl font-semibold text-black bg-white rounded-md px-2 py-1">
              RAG FAQ
            </span>
          </div>
          <nav className="flex items-center gap-4 text-sm">
            <span className="text-white font-semibold">
              FAQ
            </span>
            <Link href="/documents" className="text-gray-300 hover:text-white">
              Documents
            </Link>
            <span className="ml-4 text-gray-400 hidden sm:inline">
              {user.email}
            </span>
            <button
              onClick={() => signOut()}
              className="ml-2 px-3 py-1.5 rounded-md border border-gray-700 text-xs sm:text-sm text-gray-200 hover:bg-gray-800"
            >
              ログアウト
            </button>
          </nav>
        </div>
      </header>

      {/* メインコンテンツ（ChatGPT風レイアウト） */}
      <main className="flex-1 flex flex-col items-center">
        <div className="w-full max-w-5xl flex-1 flex flex-col md:flex-row px-4 pt-6 pb-24 gap-4">
          {/* 左カラム: 質問履歴 */}
          <aside className="hidden md:flex md:w-60 flex-col border border-gray-800 rounded-2xl bg-gray-900/60 p-3 text-xs text-gray-300">
            <div className="flex items-center justify-between mb-2">
              <span className="font-semibold text-gray-100">質問履歴</span>
              <span className="text-[10px] text-gray-500">
                {history.length} 件
              </span>
            </div>
            <div className="flex-1 overflow-y-auto space-y-1 pr-1">
              {history.length === 0 && (
                <p className="text-[11px] text-gray-500">
                  まだ質問はありません。
                </p>
              )}
              {history.map((item, idx) => (
                <div
                  key={`${item.question}-${idx}`}
                  className="rounded-lg bg-gray-800/80 hover:bg-gray-700/80 border border-gray-700 px-2 py-1.5 cursor-default"
                >
                  <p className="text-[11px] line-clamp-2">{item.question}</p>
                </div>
              ))}
            </div>
          </aside>

          {/* 右カラム: チャットエリア */}
          <div className="flex-1 flex flex-col">
            <div className="flex-1 space-y-4 overflow-y-auto">
              {/* 初期メッセージ */}
              {history.length === 0 && !faqLoading && !error && (
                <div className="flex justify-center mt-10">
                  <div className="text-center text-gray-400">
                    <h1 className="text-3xl font-semibold mb-3">RAG FAQ へようこそ</h1>
                    <p className="text-sm">
                      画面下部の入力欄から質問すると、FAQ ドキュメントから回答を生成します。
                    </p>
                  </div>
                </div>
              )}

              {/* 質問履歴 + 回答カード */}
              {history.map((item, idx) => (
                <div key={`${item.question}-${idx}`} className="space-y-2">
                  {/* ユーザー質問バブル */}
                  <div className="flex justify-end">
                    <div className="max-w-[80%] rounded-2xl bg-emerald-600 text-white px-4 py-3 shadow">
                      <p className="text-sm whitespace-pre-wrap">{item.question}</p>
                    </div>
                  </div>
                  {/* 回答カード */}
                  <div className="flex justify-start">
                    <AnswerDisplay answer={item} />
                  </div>
                </div>
              ))}

              {/* エラー表示 */}
              {error && (
                <div className="flex justify-center">
                  <div className="max-w-[80%] rounded-2xl bg-red-900/40 border border-red-700 px-4 py-3 text-sm text-red-100">
                    エラーが発生しました: {error.message}
                  </div>
                </div>
              )}

              {/* ローディング状態 */}
              {faqLoading && (
                <div className="flex justify-center mt-4">
                  <div className="inline-flex items-center gap-2 text-xs text-gray-200 px-3 py-2 rounded-full border border-gray-700 bg-gray-900/80">
                    <span className="w-4 h-4 border-2 border-emerald-400 border-t-transparent rounded-full animate-spin" />
                    回答を生成しています...
                  </div>
                </div>
              )}
            </div>

            {/* 入力フォーム（画面下固定） */}
            <div className="mt-4">
              <div className="fixed bottom-0 left-0 right-0 bg-gradient-to-t from-gray-900 via-gray-900/95 to-transparent pb-4 pt-2">
                <div className="max-w-3xl mx-auto px-4">
                  <QuestionForm onSubmit={handleQuestion} loading={faqLoading} />
                  <p className="mt-2 text-[10px] text-gray-500 text-center">
                    モデルの回答は誤っている可能性があります。重要な内容は必ず確認してください。
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

