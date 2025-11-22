// 認証関連の型定義
export interface User {
    id: string;
    email: string;
    role?: string;
  }
  
  export interface AuthState {
    user: User | null;
    loading: boolean;
    error: Error | null;
  }