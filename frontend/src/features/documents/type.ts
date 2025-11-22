// ドキュメント関連の型定義
export interface Document {
    id: string;
    title: string;
    filename: string;
    uploadedAt: string;
    status: 'processing' | 'completed' | 'failed';
  }
  
  export interface UploadResponse {
    documentId: string;
    message: string;
  }