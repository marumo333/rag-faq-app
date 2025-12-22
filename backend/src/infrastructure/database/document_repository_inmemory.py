from typing import Dict, List, Optional
from uuid import UUID
from domain.entities.document import Document
from domain.entities.chunk import Chunk
from domain.repositories.document_repository import DocumentRepository


class InMemoryDocumentRepository(DocumentRepository):
    """インメモリドキュメントリポジトリ（テスト用）"""
    
    def __init__(self) -> None:
        self._documents: Dict[UUID, Document] = {}
        self._chunks: Dict[UUID, Chunk] = {}
    
    async def create(self, document: Document) -> Document:
        """ドキュメントを作成"""
        self._documents[document.id] = document
        return document
    
    async def get_by_id(self, document_id: UUID) -> Optional[Document]:
        """IDでドキュメントを取得"""
        return self._documents.get(document_id)
    
    async def update(self, document: Document) -> Document:
        """ドキュメントを更新"""
        if document.id not in self._documents:
            raise ValueError(f"Document {document.id} not found")
        self._documents[document.id] = document
        return document
    
    async def delete(self, document_id: UUID) -> bool:
        """ドキュメントを削除"""
        if document_id in self._documents:
            del self._documents[document_id]
            # 関連するチャンクも削除
            chunks_to_delete = [
                chunk_id for chunk_id, chunk in self._chunks.items()
                if chunk.document_id == document_id
            ]
            for chunk_id in chunks_to_delete:
                del self._chunks[chunk_id]
            return True
        return False
    
    async def list_by_tenant(self, tenant_id: UUID) -> List[Document]:
        """テナントのドキュメント一覧を取得"""
        return [
            doc for doc in self._documents.values()
            if doc.tenant_id == tenant_id
        ]
    
    async def save_chunks(self, chunks: List[Chunk]) -> List[Chunk]:
        """チャンクを保存"""
        for chunk in chunks:
            self._chunks[chunk.id] = chunk
        return chunks
    
    async def get_chunks_by_document(self, document_id: UUID) -> List[Chunk]:
        """ドキュメントのチャンク一覧を取得"""
        return [
            chunk for chunk in self._chunks.values()
            if chunk.document_id == document_id
        ]