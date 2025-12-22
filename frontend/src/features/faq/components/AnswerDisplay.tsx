"use client";

import { AnswerResponse } from "../services/faqService";

interface AnswerDisplayProps {
  answer: AnswerResponse;
}

export function AnswerDisplay({ answer }: AnswerDisplayProps) {
  return (
    <article className="w-full p-5 bg-gray-900 text-gray-100 rounded-2xl border border-gray-700 shadow-sm">
      {/* 回答本文 */}
      <div className="mb-3">
        <h3 className="text-sm font-semibold text-emerald-400 mb-1">回答</h3>
        <div className="prose prose-invert max-w-none text-sm leading-relaxed whitespace-pre-wrap">
          {answer.answer}
        </div>
      </div>

      {/* メタ情報 */}
      <div className="mb-3 flex flex-wrap items-center gap-2 text-[11px] text-gray-400">
        <span className="inline-flex items-center gap-1 rounded-full bg-gray-800 px-2 py-1 border border-gray-700">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
          {answer.chunks_used.length} チャンク使用
        </span>
        <span className="inline-flex items-center gap-1 rounded-full bg-gray-800 px-2 py-1 border border-gray-700">
          ⏱ {answer.elapsed_time.toFixed(2)} 秒
        </span>
      </div>

      {/* 引用・出典 */}
      <div className="mt-3 border-t border-gray-800 pt-3">
        <h4 className="text-xs font-semibold text-gray-300 mb-2">
          引用された箇所
        </h4>
        <div className="space-y-2">
          {answer.sources.map((source, index) => (
            <div
              key={index}
              className="rounded-md bg-amber-900/30 border border-amber-700/60 px-3 py-2 text-xs text-amber-50"
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-semibold">出典 {index + 1}</span>
                <span className="text-[10px] text-amber-200">
                  スコア {source.score.toFixed(2)}
                </span>
              </div>
              <p className="whitespace-pre-wrap">
                {source.section || "引用テキスト情報がありません"}
              </p>
            </div>
          ))}
        </div>
      </div>
    </article>
  );
}
