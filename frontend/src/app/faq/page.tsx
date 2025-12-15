'use client'

import { useEffect } from 'react'
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
  const { answer, loading: faqLoading, error, askQuestion } = useFaq(tenantId)

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login')
    }
  }, [user, authLoading, router])

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
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
    <div className="min-h-screen bg-gray-50">
      {/* ヘッダー */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-xl font-bold">RAG FAQ</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">{user.email}</span>
            <button
              onClick={() => signOut()}
              className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900"
            >
              ログアウト
            </button>
          </div>
        </div>
      </header>

      {/* メインコンテンツ */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="space-y-6">
          {/* 質問フォーム */}
          <QuestionForm onSubmit={handleQuestion} loading={faqLoading} />

          {/* エラー表示 */}
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-600">エラーが発生しました: {error.message}</p>
            </div>
          )}

          {/* 回答表示 */}
          {answer && <AnswerDisplay answer={answer} />}

          {/* 初期メッセージ */}
          {!answer && !faqLoading && (
            <div className="text-center py-12 text-gray-500">
              <p>質問を入力して、FAQを検索してください</p>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

