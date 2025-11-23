from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class Document:
    """ドキュメントエンティティ"""
    
    id: UUID
    tenant_id: UUID
    title: str
    file_path: str
    status: str  # 'pending', 'processing', 'completed', 'failed'
    created_at: datetime
    updated_at: Optional[datetime] = None
    error_message: Optional[str] = None
    total_chunks: Optional[int] = None
    
    def mark_as_processing(self) -> None:
        """処理中にマーク"""
        self.status = "processing"
    
    def mark_as_completed(self, total_chunks: int) -> None:
        """完了にマーク"""
        self.status = "completed"
        self.total_chunks = total_chunks
    
    def mark_as_failed(self, error_message: str) -> None:
        """失敗にマーク"""
        self.status = "failed"
        self.error_message = error_message
    
    def is_completed(self) -> bool:
        """完了しているか"""
        return self.status == "completed"