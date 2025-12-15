export interface AnswerRequest {
  question: string
  tenant_id: string
  top_k?: number
}

export interface AnswerResponse {
  question: string
  answer: string
  chunks_used: string[]
  sources: Array<{
    document_id: string
    section: string | null
    score: number
  }>
  elapsed_time: number
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const faqService = {
  /**
   * 質問に対する回答を取得
   */
  async getAnswer(request: AnswerRequest): Promise<AnswerResponse> {
    const response = await fetch(`${API_BASE_URL}/answer`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      throw new Error('Failed to get answer')
    }

    return response.json()
  },
}

