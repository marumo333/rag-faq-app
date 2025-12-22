import logging
import time
from typing import Any, Dict, List, Optional
from uuid import UUID

from domain.entities.embedding import SearchResult
from domain.repositories.embedding_repository import EmbeddingRepository
from infrastructure.llm.embedding_client import GeminiEmbeddingClient

logger = logging.getLogger(__name__)


class SearchChunksUseCase:
    """チャンク検索ユースケース"""
    
    def __init__(
        self,
        embedding_repository: EmbeddingRepository,
        embedding_client: Optional[GeminiEmbeddingClient] = None
    ) -> None:
        self.embedding_repository = embedding_repository
        self.embedding_client = embedding_client or GeminiEmbeddingClient()
        self.logger = logger
    
    async def execute(
        self,
        query: str,
        tenant_id: UUID,
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        質問クエリから類似チャンクを検索
        
        Args:
            query: 検索クエリ（質問文）
            tenant_id: テナントID
            limit: 取得件数
            
        Returns:
            dict: 検索結果と処理時間
        """
        start_time = time.time()
        
        try:
            if not query or not query.strip():
                raise ValueError("Query cannot be empty")
            
            self.logger.info(f"Searching for: '{query}' (limit: {limit})")
            
            # 1. クエリの埋め込み生成
            self.logger.debug("Generating query embedding...")
            query_vector = self.embedding_client.generate_query_embedding(query)
            
            embedding_time = time.time() - start_time
            self.logger.debug(f"Query embedding generated in {embedding_time:.3f}s")
            
            # 2. ベクトル検索
            search_start = time.time()
            results = await self.embedding_repository.search_similar(
                query_vector=query_vector,
                tenant_id=tenant_id,
                limit=limit
            )
            
            search_time = time.time() - search_start
            total_time = time.time() - start_time
            
            self.logger.info(
                f"Found {len(results)} results in {total_time:.3f}s "
                f"(embedding: {embedding_time:.3f}s, search: {search_time:.3f}s)"
            )
            
            return {
                "query": query,
                "results": [result.to_dict() for result in results],
                "total_results": len(results),
                "elapsed_time": total_time,
                "embedding_time": embedding_time,
                "search_time": search_time
            }
            
        except Exception as e:
            self.logger.error(f"Search failed: {e}", exc_info=True)
            raise