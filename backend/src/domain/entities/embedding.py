from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID


@dataclass
class Embedding:
    """埋め込みエンティティ"""
    
    id: UUID
    chunk_id: UUID
    vector: List[float]
    model: str
    created_at: Optional[datetime] = None
    
    def __post_init__(self) -> None:
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
    score: float
    metadata: Dict[str, Any]
    document_title: Optional[str] = None
    position: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
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