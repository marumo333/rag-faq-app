from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from domain.entities.document import Document
from domain.entities.chunk import Chunk


class DocumentRepository(ABC):
    """ドキュメントリポジトリのインターフェース"""
    
    @abstractmethod
    async def create(self, document: Document) -> Document:
        """ドキュメントを作成"""
        pass
    
    @abstractmethod
    async def get_by_id(self, document_id: UUID) -> Optional[Document]:
        """IDでドキュメントを取得"""
        pass
    
    @abstractmethod
    async def update(self, document: Document) -> Document:
        """ドキュメントを更新"""
        pass
    
    @abstractmethod
    async def delete(self, document_id: UUID) -> bool:
        """ドキュメントを削除"""
        pass
    
    @abstractmethod
    async def list_by_tenant(self, tenant_id: UUID) -> List[Document]:
        """テナントのドキュメント一覧を取得"""
        pass
    
    @abstractmethod
    async def save_chunks(self, chunks: List[Chunk]) -> List[Chunk]:
        """チャンクを保存"""
        pass
    
    @abstractmethod
    async def get_chunks_by_document(self, document_id: UUID) -> List[Chunk]:
        """ドキュメントのチャンク一覧を取得"""
        pass