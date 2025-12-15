'use client'

import { useQuestionForm } from '@/features/faq/hooks/useQuestionForm'

interface QuestionFormProps {
  onSubmit: (question: string) => void
  loading?: boolean
}

export function QuestionForm({ onSubmit, loading = false }: QuestionFormProps) {
  const { question, setQuestion, handleSubmit } = useQuestionForm({ onSubmit })

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="flex gap-2">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="質問を入力してください..."
          className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !question.trim()}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? '処理中...' : '質問'}
        </button>
      </div>
    </form>
  )
}