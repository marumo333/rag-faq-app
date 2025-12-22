import logging
from typing import List, Optional
from uuid import UUID
from supabase import Client

from domain.entities.embedding import Embedding, SearchResult
from domain.repositories.embedding_repository import EmbeddingRepository

logger = logging.getLogger(__name__)


class SupabaseEmbeddingRepository(EmbeddingRepository):
    """Supabaseを使用した埋め込みリポジトリの実装"""
    
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
        self.logger = logger
    
    async def save(self, embedding: Embedding) -> Embedding:
        """埋め込みを保存"""
        self.client.table('faq_embeddings').insert({
            'id': str(embedding.id),
            'chunk_id': str(embedding.chunk_id),
            'embedding': embedding.vector,
        }).execute()
        
        return embedding
    
    async def save_batch(self, embeddings: List[Embedding]) -> List[Embedding]:
        """埋め込みを一括保存"""
        if not embeddings:
            return []
        
        self.logger.info(f"Saving {len(embeddings)} embeddings to database")
        
        # バルクINSERT用のデータ準備
        embedding_data = []
        for emb in embeddings:
            embedding_data.append({
                'id': str(emb.id),
                'chunk_id': str(emb.chunk_id),
                'embedding': emb.vector,
            })
        
        # バッチサイズを制限（Supabaseの制限対応）
        batch_size = 100
        for i in range(0, len(embedding_data), batch_size):
            batch = embedding_data[i:i + batch_size]
            self.client.table('faq_embeddings').insert(batch).execute()
            self.logger.info(f"Saved batch {i//batch_size + 1} ({len(batch)} embeddings)")
        
        self.logger.info(f"Successfully saved {len(embeddings)} embeddings")
        return embeddings
    
    async def get_by_chunk_id(self, chunk_id: UUID) -> Optional[Embedding]:
        """チャンクIDで埋め込みを取得"""
        response = self.client.table('faq_embeddings').select('*').eq(
            'chunk_id', str(chunk_id)
        ).execute()
        
        if not response.data:
            return None
        
        data = response.data[0]
        return self._map_to_embedding(data)
    
    async def search_similar(
        self,
        query_vector: List[float],
        tenant_id: UUID,
        limit: int = 5
    ) -> List[SearchResult]:
        """
        類似チャンクを検索
        
        Args:
            query_vector: クエリの埋め込みベクトル
            tenant_id: テナントID
            limit: 取得件数
            
        Returns:
            List[SearchResult]: 類似チャンクのリスト
        """
        # RPCを使用してベクトル検索（Supabaseの制限により直接SQLを実行できないため）
        # または、PostgreSQL接続を使用
        
        # 簡易版: postgrestの機能を使用
        response = self.client.rpc(
            'search_embeddings',
            {
                'query_embedding': query_vector,
                'match_count': limit,
                'filter_tenant_id': str(tenant_id)
            }
        ).execute()
        
        results = []
        for data in response.data:
            results.append(SearchResult(
                chunk_id=UUID(data['chunk_id']),
                document_id=UUID(data['document_id']),
                content=data['content'],
                document_title=data.get['document_title'],
                position=data.get['position'],
                score=float(data['similarity']),
                metadata=data.get('metadata', {})
            ))
        
        return results
    
    async def delete_by_document(self, document_id: UUID) -> bool:
        """ドキュメントに紐づく埋め込みを削除"""
        # チャンクIDを取得
        chunks_response = self.client.table('faq_chunks').select('id').eq(
            'document_id', str(document_id)
        ).execute()
        
        if not chunks_response.data:
            return False
        
        chunk_ids = [chunk['id'] for chunk in chunks_response.data]
        
        # 埋め込みを削除
        for chunk_id in chunk_ids:
            self.client.table('faq_embeddings').delete().eq(
                'chunk_id', chunk_id
            ).execute()
        
        self.logger.info(f"Deleted embeddings for {len(chunk_ids)} chunks")
        return True
    
    def _map_to_embedding(self, data: dict) -> Embedding:
        """データベースレコードをEmbeddingエンティティに変換"""
        from datetime import datetime
        
        return Embedding(
            id=UUID(data['id']),
            chunk_id=UUID(data['chunk_id']),
            vector=data['embedding'],
            model='gemini-embedding-001',
            created_at=datetime.fromisoformat(data['created_at'].replace('Z', '+00:00')) if data.get('created_at') else None
        )