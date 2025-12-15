'use client'

import { useState } from 'react'
import { faqService, AnswerResponse } from '../services/faqService'

export function useFaq(tenantId: string) {
  const [answer, setAnswer] = useState<AnswerResponse | null>(null)
  const [history, setHistory] = useState<AnswerResponse[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  async function askQuestion(question: string, topK: number = 5) {
    setLoading(true)
    setError(null)
    
    try {
      const result = await faqService.getAnswer({
        question,
        tenant_id: tenantId,
        top_k: topK,
      })
      
      setAnswer(result)
      setHistory((prev) => [...prev, result])
      return result
    } catch (err) {
      setError(err as Error)
      throw err
    } finally {
      setLoading(false)
    }
  }

  function clearAnswer() {
    setAnswer(null)
    setError(null)
    setHistory([])
  }

  return {
    answer,
    history,
    loading,
    error,
    askQuestion,
    clearAnswer,
  }
}

