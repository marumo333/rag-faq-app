// FAQ関連の型定義
export interface FaqQuery {
    id: string;
    question: string;
    createdAt: string;
  }
  
  export interface FaqAnswer {
    id: string;
    answer: string;
    chunks: ChunkReference[];
    confidence: number;
  }
  
  export interface ChunkReference {
    id: string;
    documentId: string;
    content: string;
    score: number;
  }