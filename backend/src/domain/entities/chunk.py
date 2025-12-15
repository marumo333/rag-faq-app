from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class Chunk:
    """チャンクエンティティ"""
    
    id: UUID
    document_id: UUID
    content: str
    section: Optional[str] = None
    position: Optional[int] = None
    page_number: Optional[int] = None
    chunk_index: int = 0
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def get_metadata(self) -> dict:
        """チャンクのメタデータを取得"""
        return {
            "chunk_id": str(self.id),
            "document_id": str(self.document_id),
            "section": self.section,
            "page_number": self.page_number,
            "chunk_index": self.chunk_index,
        }
    
    def __len__(self) -> int:
        """チャンクの文字数"""
        return len(self.content)