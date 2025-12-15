import logging
import time
from typing import List, Optional
from uuid import UUID, uuid4

from domain.entities.embedding import Embedding
from domain.repositories.document_repository import DocumentRepository
from domain.repositories.embedding_repository import EmbeddingRepository
from infrastructure.llm.embedding_client import GeminiEmbeddingClient

logger = logging.getLogger(__name__)


class GenerateEmbeddingsUseCase:
    """埋め込み生成ユースケース"""
    
    def __init__(
        self,
        document_repository: DocumentRepository,
        embedding_repository: EmbeddingRepository,
        embedding_client: Optional[GeminiEmbeddingClient] = None
    ):
        self.document_repository = document_repository
        self.embedding_repository = embedding_repository
        self.embedding_client = embedding_client or GeminiEmbeddingClient()
        self.logger = logger
    
    async def execute(self, document_id: UUID) -> dict:
        """
        ドキュメントのチャンクに対して埋め込みを生成
        
        Args:
            document_id: ドキュメントID
            
        Returns:
            dict: 処理結果（チャンク数、処理時間など）
        """
        start_time = time.time()
        
        try:
            # ドキュメント取得
            document = await self.document_repository.get_by_id(document_id)
            if not document:
                raise ValueError(f"Document {document_id} not found")
            
            self.logger.info(f"Generating embeddings for document: {document_id}")
            
            # チャンク取得
            chunks = await self.document_repository.get_chunks_by_document(document_id)
            
            if not chunks:
                raise ValueError(f"No chunks found for document {document_id}")
            
            self.logger.info(f"Found {len(chunks)} chunks to process")
            
            # テキストリストを作成
            texts = [chunk.content for chunk in chunks]
            
            # 埋め込み生成
            self.logger.info("Generating embeddings using Gemini API...")
            vectors = self.embedding_client.generate_embeddings_batch(texts)
            
            # Embeddingエンティティのリスト作成
            embeddings = []
            for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
                embedding = Embedding(
                    id=uuid4(),
                    chunk_id=chunk.id,
                    vector=vector,
                    model="models/embedding-001"
                )
                embeddings.append(embedding)
            
            # 一括保存
            self.logger.info(f"Saving {len(embeddings)} embeddings to database...")
            await self.embedding_repository.save_batch(embeddings)
            
            # 処理時間計測
            elapsed_time = time.time() - start_time
            throughput = len(chunks) / elapsed_time if elapsed_time > 0 else 0
            
            self.logger.info(
                f"Embedding generation completed: "
                f"{len(chunks)} chunks in {elapsed_time:.2f}s "
                f"({throughput:.2f} chunks/sec)"
            )
            
            return {
                "document_id": str(document_id),
                "total_chunks": len(chunks),
                "total_embeddings": len(embeddings),
                "elapsed_time": elapsed_time,
                "throughput": throughput
            }
            
        except Exception as e:
            self.logger.error(f"Embedding generation failed: {e}", exc_info=True)
            raise