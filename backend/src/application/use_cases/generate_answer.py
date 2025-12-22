import logging
import time
from typing import Any, Dict, List, Optional
from uuid import UUID

from application.use_cases.search_chunks import SearchChunksUseCase
from domain.repositories.embedding_repository import EmbeddingRepository
from infrastructure.llm.embedding_client import GeminiEmbeddingClient
from infrastructure.llm.generation_client import GeminiGenerationClient

logger = logging.getLogger(__name__)


class GenerateAnswerUseCase:
    """RAG回答生成ユースケース"""
    
    def __init__(
        self,
        embedding_repository: EmbeddingRepository,
        embedding_client: Optional[GeminiEmbeddingClient] = None,
        generation_client: Optional[GeminiGenerationClient] = None
    ) -> None:
        self.search_use_case = SearchChunksUseCase(
            embedding_repository=embedding_repository,
            embedding_client=embedding_client
        )
        self.generation_client = generation_client or GeminiGenerationClient()
        self.logger = logger
    
    async def execute(
        self,
        question: str,
        tenant_id: UUID,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        質問に対してRAG回答を生成
        
        処理フロー:
        1. 質問の埋め込み生成
        2. ベクトル検索でTop-Kチャンク取得
        3. コンテキストとして整形
        4. LLMで回答生成
        
        Args:
            question: ユーザーの質問
            tenant_id: テナントID
            top_k: 取得するチャンク数
            
        Returns:
            dict: 回答テキスト、引用情報、処理時間など
        """
        start_time = time.time()
        
        try:
            if not question or not question.strip():
                raise ValueError("Question cannot be empty")
            
            self.logger.info(f"Generating answer for: '{question}'")
            
            # 1. ベクトル検索でTop-Kチャンク取得
            self.logger.debug(f"Searching for top-{top_k} similar chunks...")
            search_result = await self.search_use_case.execute(
                query=question,
                tenant_id=tenant_id,
                limit=top_k
            )
            
            search_time = search_result['elapsed_time']
            chunks = search_result['results']
            
            if not chunks:
                return {
                    "question": question,
                    "answer": "申し訳ございません。関連する情報が見つかりませんでした。",
                    "chunks_used": [],
                    "sources": [],
                    "elapsed_time": time.time() - start_time,
                    "search_time": search_time,
                    "generation_time": 0
                }
            
            self.logger.info(f"Found {len(chunks)} relevant chunks")
            
            # 2. LLMで回答生成
            generation_start = time.time()
            generation_result = self.generation_client.generate_answer(
                question=question,
                context_chunks=chunks
            )
            generation_time = time.time() - generation_start
            
            # 3. 引用情報の抽出
            chunk_ids = [chunk['chunk_id'] for chunk in chunks]
            sources = self._extract_sources(chunks)
            
            total_time = time.time() - start_time
            
            self.logger.info(
                f"Answer generated in {total_time:.2f}s "
                f"(search: {search_time:.2f}s, generation: {generation_time:.2f}s)"
            )
            
            return {
                "question": question,
                "answer": generation_result['answer'],
                "chunks_used": chunk_ids,
                "sources": sources,
                "model": generation_result['model'],
                "elapsed_time": total_time,
                "search_time": search_time,
                "generation_time": generation_time
            }
            
        except Exception as e:
            self.logger.error(f"Answer generation failed: {e}", exc_info=True)
            raise
    
    def _extract_sources(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """チャンクから参照元情報を抽出"""
        sources = []
        seen_documents = set()
        
        for chunk in chunks:
            doc_id = chunk.get('document_id')
            if doc_id and doc_id not in seen_documents:
                seen_documents.add(doc_id)
                
                metadata = chunk.get('metadata', {})
                sources.append({
                    "document_id": doc_id,
                    "section": metadata.get('section'),
                    "score": chunk.get('score'),
                    "content": chunk.get('content'),
                    "document_title": chunk.get('document_title'),
                    "position": chunk.get('position'),
                })
        
        return sources