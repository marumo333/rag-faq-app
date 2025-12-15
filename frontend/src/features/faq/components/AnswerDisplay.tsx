'use client'

import { AnswerResponse } from '../services/faqService'

interface AnswerDisplayProps {
  answer: AnswerResponse
}

export function AnswerDisplay({ answer }: AnswerDisplayProps) {
  return (
    <div className="w-full p-6 bg-white border border-gray-200 rounded-lg shadow-sm">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">質問</h3>
        <p className="text-gray-700">{answer.question}</p>
      </div>

      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">回答</h3>
        <div className="prose max-w-none text-gray-700 whitespace-pre-wrap">
          {answer.answer}
        </div>
      </div>

      <div className="border-t pt-4 mt-4">
        <h4 className="text-sm font-semibold text-gray-600 mb-2">参照情報</h4>
        <div className="space-y-2">
          {answer.sources.map((source, index) => (
            <div key={index} className="text-sm text-gray-500">
              <span className="font-medium">
                参考 {index + 1}:
              </span>{' '}
              {source.section || '情報なし'}{' '}
              <span className="text-xs">(スコア: {source.score.toFixed(2)})</span>
            </div>
          ))}
        </div>
        
        <div className="mt-2 text-xs text-gray-400">
          処理時間: {answer.elapsed_time.toFixed(2)}秒
          ({answer.chunks_used.length}個のチャンクを使用)
        </div>
      </div>
    </div>
  )
}

