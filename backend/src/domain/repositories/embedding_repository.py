from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from domain.entities.embedding import Embedding, SearchResult


class EmbeddingRepository(ABC):
    """埋め込みリポジトリのインターフェース"""
    
    @abstractmethod
    async def save(self, embedding: Embedding) -> Embedding:
        """埋め込みを保存"""
        pass
    
    @abstractmethod
    async def save_batch(self, embeddings: List[Embedding]) -> List[Embedding]:
        """埋め込みを一括保存"""
        pass
    
    @abstractmethod
    async def get_by_chunk_id(self, chunk_id: UUID) -> Optional[Embedding]:
        """チャンクIDで埋め込みを取得"""
        pass
    
    @abstractmethod
    async def search_similar(
        self,
        query_vector: List[float],
        tenant_id: UUID,
        limit: int = 5
    ) -> List[SearchResult]:
        """類似チャンクを検索"""
        pass
    
    @abstractmethod
    async def delete_by_document(self, document_id: UUID) -> bool:
        """ドキュメントに紐づく埋め込みを削除"""
        pass