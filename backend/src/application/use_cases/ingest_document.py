import logging
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

from domain.entities.document import Document
from domain.entities.chunk import Chunk
from domain.repositories.document_repository import DocumentRepository
from domain.services.chunk_splitter import ChunkSplitter
from infrastructure.pdf.pdf_extractor import PDFExtractor

logger = logging.getLogger(__name__)


class IngestDocumentUseCase:
    """ドキュメント取り込みユースケース（本番実装）"""
    
    def __init__(
        self,
        document_repository: DocumentRepository,
        pdf_extractor: Optional[PDFExtractor] = None,
        chunk_splitter: Optional[ChunkSplitter] = None
    ):
        self.document_repository = document_repository
        self.pdf_extractor = pdf_extractor or PDFExtractor()
        self.chunk_splitter = chunk_splitter or ChunkSplitter(
            chunk_size=800,
            chunk_overlap=200,
            min_chunk_size=100
        )
        self.logger = logger
    
    async def execute(
        self,
        tenant_id: UUID,
        title: str,
        file_path: str
    ) -> Document:
        """
        ドキュメントを取り込む
        
        処理フロー:
        1. ドキュメントレコード作成（status: pending）
        2. PDFからテキスト抽出
        3. チャンクに分割
        4. チャンク保存
        5. ドキュメントステータス更新（status: completed）
        """
        # ドキュメント作成
        document = Document(
            id=uuid4(),
            tenant_id=tenant_id,
            title=title,
            file_path=file_path,
            status="pending",
            created_at=datetime.utcnow()
        )
        
        try:
            # データベースに保存
            created_document = await self.document_repository.create(document)
            self.logger.info(f"Document created: {created_document.id}")
            
            # ステータスを処理中に更新
            created_document.mark_as_processing()
            await self.document_repository.update(created_document)
            
            # PDFからテキスト抽出
            self.logger.info(f"Extracting text from: {file_path}")
            text = self.pdf_extractor.extract_text(file_path)
            
            if not text or len(text) < 10:
                raise ValueError("Extracted text is too short or empty")
            
            # チャンクに分割
            self.logger.info(f"Splitting text into chunks (text length: {len(text)})")
            chunks = self.chunk_splitter.split(created_document.id, text)
            
            if not chunks:
                raise ValueError("No chunks generated from PDF")
            
            self.logger.info(f"Generated {len(chunks)} chunks")
            
            # チャンク保存
            await self.document_repository.save_chunks(chunks)
            self.logger.info(f"Saved {len(chunks)} chunks to database")
            
            # ステータスを完了に更新
            created_document.mark_as_completed(total_chunks=len(chunks))
            await self.document_repository.update(created_document)
            
            self.logger.info(f"Document processing completed: {created_document.id}")
            return created_document
            
        except Exception as e:
            # エラー時の処理
            self.logger.error(f"Document processing failed: {e}", exc_info=True)
            
            try:
                # ステータスを失敗に更新
                created_document.mark_as_failed(error_message=str(e))
                await self.document_repository.update(created_document)
            except Exception as update_error:
                self.logger.error(f"Failed to update document status: {update_error}")
            
            # エラーを再送出
            raise