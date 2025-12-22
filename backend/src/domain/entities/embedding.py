from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import UUID


@dataclass
class Embedding:
    """埋め込みエンティティ"""
    
    id: UUID
    chunk_id: UUID
    vector: List[float]
    model: str
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    @property
    def dimension(self) -> int:
        """ベクトルの次元数"""
        return len(self.vector)
    
    def validate_dimension(self, expected_dimension: int) -> bool:
        """次元数の検証"""
        return self.dimension == expected_dimension


@dataclass
class SearchResult:
    """検索結果エンティティ"""
    
    chunk_id: UUID
    document_id: UUID
    content: str
    document_title: str
    position: int
    score: float
    metadata: dict
    
    def to_dict(self) -> dict:
        """辞書に変換"""
        return {
            "chunk_id": str(self.chunk_id),
            "document_id": str(self.document_id),
            "content": self.content,
            "document_title": self.document_title,
            "position": self.position,
            "score": self.score,
            "metadata": self.metadata,
        }