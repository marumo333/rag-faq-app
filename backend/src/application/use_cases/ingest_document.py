from datetime import datetime
from uuid import UUID, uuid4
from domain.entities.document import Document
from domain.entities.chunk import Chunk
from domain.repositories.document_repository import DocumentRepository


class IngestDocumentUseCase:
    """ドキュメント取り込みユースケース（ダミー実装）"""
    
    def __init__(self, document_repository: DocumentRepository):
        self.document_repository = document_repository
    
    async def execute(
        self,
        tenant_id: UUID,
        title: str,
        file_path: str
    ) -> Document:
        """
        ドキュメントを取り込む（ダミー実装）
        
        本番実装では:
        1. PDFからテキスト抽出
        2. チャンクに分割
        3. 埋め込みベクトル生成
        4. データベースに保存
        
        現在はダミーデータを返すのみ
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
        
        # 保存
        created_document = await self.document_repository.create(document)
        
        # ダミーチャンクを作成（実際のPDF処理の代わり）
        dummy_chunks = [
            Chunk(
                id=uuid4(),
                document_id=created_document.id,
                content=f"これはダミーチャンク{i}です。実際の実装ではPDFから抽出されます。",
                section=f"セクション{i}",
                chunk_index=i
            )
            for i in range(3)
        ]
        
        # チャンク保存
        await self.document_repository.save_chunks(dummy_chunks)
        
        # ステータス更新
        created_document.mark_as_completed(total_chunks=len(dummy_chunks))
        await self.document_repository.update(created_document)
        
        return created_document