from typing import List, Optional
from uuid import UUID
from supabase import Client

from domain.entities.document import Document
from domain.entities.chunk import Chunk
from domain.repositories.document_repository import DocumentRepository


class SupabaseDocumentRepository(DocumentRepository):
    """Supabaseを使用したドキュメントリポジトリの実装"""
    
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
    
    async def create(self, document: Document) -> Document:
        """ドキュメントを作成"""
        response = self.client.table('documents').insert({
            'id': str(document.id),
            'tenant_id': str(document.tenant_id),
            'title': document.title,
            'file_path': document.file_path,
            'status': document.status,
            'created_at': document.created_at.isoformat() if document.created_at else None,
            'updated_at': document.updated_at.isoformat() if document.updated_at else None,
        }).execute()
        
        return document
    
    async def get_by_id(self, document_id: UUID) -> Optional[Document]:
        """IDでドキュメントを取得"""
        response = self.client.table('documents').select('*').eq('id', str(document_id)).execute()
        
        if not response.data:
            return None
        
        data = response.data[0]
        return self._map_to_document(data)
    
    async def update(self, document: Document) -> Document:
        """ドキュメントを更新"""
        self.client.table('documents').update({
            'title': document.title,
            'file_path': document.file_path,
            'status': document.status,
            'total_chunks': document.total_chunks,
            'error_message': document.error_message,
        }).eq('id', str(document.id)).execute()
        
        return document
    
    async def delete(self, document_id: UUID) -> bool:
        """ドキュメントを削除"""
        response = self.client.table('documents').delete().eq('id', str(document_id)).execute()
        return len(response.data) > 0
    
    async def list_by_tenant(self, tenant_id: UUID) -> List[Document]:
        """テナントのドキュメント一覧を取得"""
        response = self.client.table('documents').select('*').eq('tenant_id', str(tenant_id)).execute()
        
        return [self._map_to_document(data) for data in response.data]
    
    async def save_chunks(self, chunks: List[Chunk]) -> List[Chunk]:
        """チャンクを保存"""
        chunk_data = []
        for chunk in chunks:
            chunk_data.append({
                'id': str(chunk.id),
                'document_id': str(chunk.document_id),
                'content': chunk.content,
                'section': chunk.section,
                'position': chunk.position,
                'created_at': chunk.created_at.isoformat() if chunk.created_at else None,
            })
        
        self.client.table('faq_chunks').insert(chunk_data).execute()
        return chunks
    
    async def get_chunks_by_document(self, document_id: UUID) -> List[Chunk]:
        """ドキュメントのチャンク一覧を取得"""
        response = self.client.table('faq_chunks').select('*').eq(
            'document_id', str(document_id)
        ).order('position').execute()
        
        return [self._map_to_chunk(data) for data in response.data]
    
    def _map_to_document(self, data: dict) -> Document:
        """データベースレコードをDocumentエンティティに変換"""
        from datetime import datetime
        from uuid import UUID
        
        return Document(
            id=UUID(data['id']),
            tenant_id=UUID(data['tenant_id']),
            title=data['title'],
            file_path=data.get('file_path', ''),
            status=data['status'],
            created_at=datetime.fromisoformat(data['created_at'].replace('Z', '+00:00')),
            updated_at=datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00')) if data.get('updated_at') else None,
        )
    
    def _map_to_chunk(self, data: dict) -> Chunk:
        """データベースレコードをChunkエンティティに変換"""
        from datetime import datetime
        from uuid import UUID
        
        return Chunk(
            id=UUID(data['id']),
            document_id=UUID(data['document_id']),
            content=data['content'],
            section=data.get('section'),
            position=data.get('position'),
        )