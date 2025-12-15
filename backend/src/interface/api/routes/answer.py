from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID

from application.use_cases.generate_answer import GenerateAnswerUseCase
from infrastructure.database.embedding_repository_impl import SupabaseEmbeddingRepository
from infrastructure.database.supabase_client import get_supabase_client

router = APIRouter()

# リポジトリとユースケースの初期化
supabase_client = get_supabase_client()
embedding_repository = SupabaseEmbeddingRepository(supabase_client)
answer_use_case = GenerateAnswerUseCase(embedding_repository)


class AnswerRequest(BaseModel):
    """回答生成リクエスト"""
    question: str = Field(..., min_length=1, description="質問文")
    tenant_id: str = Field(..., description="テナントID")
    top_k: int = Field(default=5, ge=1, le=10, description="使用するチャンク数（1-10）")


class SourceInfo(BaseModel):
    """参照元情報"""
    document_id: str
    section: Optional[str]
    score: float


class AnswerResponse(BaseModel):
    """回答レスポンス"""
    question: str
    answer: str = Field(..., description="生成された回答")
    chunks_used: List[str] = Field(..., description="使用したチャンクIDリスト")
    sources: List[SourceInfo] = Field(..., description="参照文書/セクション情報")
    model: str = Field(..., description="使用したLLMモデル")
    elapsed_time: float = Field(..., description="総処理時間（秒）")
    search_time: float = Field(..., description="検索時間（秒）")
    generation_time: float = Field(..., description="回答生成時間（秒）")


@router.post("/answer", response_model=AnswerResponse)
async def generate_answer(request: AnswerRequest):
    """
    RAG回答生成エンドポイント
    
    質問に対して、関連文書を検索し、AIが回答を生成します。
    """
    try:
        tenant_id = UUID(request.tenant_id)
        
        # 回答生成実行
        result = await answer_use_case.execute(
            question=request.question,
            tenant_id=tenant_id,
            top_k=request.top_k
        )
        
        # SourceInfoに変換
        sources = [
            SourceInfo(
                document_id=src['document_id'],
                section=src.get('section'),
                score=src.get('score', 0.0)
            )
            for src in result['sources']
        ]
        
        return AnswerResponse(
            question=result['question'],
            answer=result['answer'],
            chunks_used=result['chunks_used'],
            sources=sources,
            model=result['model'],
            elapsed_time=result['elapsed_time'],
            search_time=result['search_time'],
            generation_time=result['generation_time']
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Answer generation failed: {str(e)}")


@router.get("/answer/health")
async def answer_health():
    """回答生成機能のヘルスチェック"""
    return {
        "status": "ok",
        "service": "answer_generation",
        "model": "gemini-pro"
    }