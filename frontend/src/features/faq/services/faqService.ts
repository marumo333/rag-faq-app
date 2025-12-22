import { supabase } from "@/features/auth/services/authService";

export interface AnswerRequest {
  question: string;
  tenant_id: string;
  top_k?: number;
}

export interface AnswerResponse {
  question: string;
  answer: string;
  chunks_used: string[];
  sources: Array<{
    document_id: string;
    section: string | null;
    score: number;
    content: string;
    document_title: string;
    position: number;
  }>;
  elapsed_time: number;
}

// Supabase Edge Function 経由で Python API の /answer を呼び出す
const ANSWER_FUNCTION_URL = process.env.NEXT_PUBLIC_ANSWER_FUNCTION_URL;

export const faqService = {
  /**
   * 質問に対する回答を取得
   */
  async getAnswer(request: AnswerRequest): Promise<AnswerResponse> {
    // Supabase のセッションからアクセストークンを取得
    const {
      data: { session },
      error,
    } = await supabase.auth.getSession();

    if (error || !session) {
      throw new Error("Not authenticated");
    }

    const response = await fetch(ANSWER_FUNCTION_URL!, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${session.access_token}`,
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error("Failed to get answer");
    }

    const json = (await response.json()) as AnswerResponse;
    return json;
  },
};
