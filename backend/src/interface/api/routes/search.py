from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Any, Dict, List
from uuid import UUID

from application.use_cases.search_chunks import SearchChunksUseCase
from infrastructure.database.embedding_repository_impl import SupabaseEmbeddingRepository
from infrastructure.database.supabase_client import get_supabase_client

router = APIRouter()

# リポジトリとユースケースの初期化
supabase_client = get_supabase_client()
embedding_repository = SupabaseEmbeddingRepository(supabase_client)
search_use_case = SearchChunksUseCase(embedding_repository)


class SearchRequest(BaseModel):
    """検索リクエスト"""
    query: str = Field(..., min_length=1, description="検索クエリ（質問文）")
    tenant_id: str = Field(..., description="テナントID")
    limit: int = Field(default=5, ge=1, le=20, description="取得件数（1-20）")


class ChunkResult(BaseModel):
    """チャンク検索結果"""
    chunk_id: str
    document_id: str
    content: str
    score: float = Field(..., description="類似度スコア（0-1、高いほど類似）")
    metadata: Dict[str, Any]


class SearchResponse(BaseModel):
    """検索レスポンス"""
    query: str
    results: List[ChunkResult]
    total_results: int
    elapsed_time: float = Field(..., description="処理時間（秒）")
    embedding_time: float = Field(..., description="埋め込み生成時間（秒）")
    search_time: float = Field(..., description="検索時間（秒）")


@router.post("/search", response_model=SearchResponse)
async def search_chunks(request: SearchRequest) -> SearchResponse:
    """
    ベクトル類似度検索エンドポイント
    
    質問文から類似度の高いチャンクを検索します。
    """
    try:
        tenant_id = UUID(request.tenant_id)
        
        # 検索実行
        result = await search_use_case.execute(
            query=request.query,
            tenant_id=tenant_id,
            limit=request.limit
        )
        
        # レスポンス変換
        chunk_results = [
            ChunkResult(
                chunk_id=r['chunk_id'],
                document_id=r['document_id'],
                content=r['content'],
                score=r['score'],
                metadata=r['metadata']
            )
            for r in result['results']
        ]
        
        return SearchResponse(
            query=result['query'],
            results=chunk_results,
            total_results=result['total_results'],
            elapsed_time=result['elapsed_time'],
            embedding_time=result['embedding_time'],
            search_time=result['search_time']
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/search/health")
async def search_health() -> Dict[str, str]:
    """検索機能のヘルスチェック"""
    return {
        "status": "ok",
        "service": "search",
        "embedding_model": "models/embedding-001"
    }