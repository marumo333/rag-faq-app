from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import UUID

from application.use_cases.ingest_document import IngestDocumentUseCase
from infrastructure.database.document_repository_inmemory import InMemoryDocumentRepository

router = APIRouter()

# 依存性注入（簡易版）
# 本番ではdependencies.pyで管理
document_repository = InMemoryDocumentRepository()
ingest_use_case = IngestDocumentUseCase(document_repository)


class IngestRequest(BaseModel):
    """ドキュメント取り込みリクエスト"""
    tenant_id: str
    title: str
    file_path: str


class IngestResponse(BaseModel):
    """ドキュメント取り込みレスポンス"""
    document_id: str
    title: str
    status: str
    total_chunks: int | None


@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(request: IngestRequest):
    """
    ドキュメント取り込みエンドポイント（仮実装）
    
    本番実装では:
    - ファイルアップロード処理
    - バックグラウンドタスク実行
    - 進捗状況の追跡
    """
    try:
        tenant_id = UUID(request.tenant_id)
        
        # ユースケース実行
        document = await ingest_use_case.execute(
            tenant_id=tenant_id,
            title=request.title,
            file_path=request.file_path
        )
        
        return IngestResponse(
            document_id=str(document.id),
            title=document.title,
            status=document.status,
            total_chunks=document.total_chunks
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/ingest/{document_id}")
async def get_document_status(document_id: str):
    """ドキュメント処理状況の取得（仮実装）"""
    try:
        doc_uuid = UUID(document_id)
        document = await document_repository.get_by_id(doc_uuid)
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {
            "document_id": str(document.id),
            "title": document.title,
            "status": document.status,
            "total_chunks": document.total_chunks,
            "error_message": document.error_message
        }
    
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID")