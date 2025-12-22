from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Any, Dict
from uuid import UUID
import tempfile
import os

from application.use_cases.ingest_document import IngestDocumentUseCase
from infrastructure.database.document_repository_impl import SupabaseDocumentRepository
from infrastructure.database.embedding_repository_impl import SupabaseEmbeddingRepository
from infrastructure.database.supabase_client import get_supabase_client

router = APIRouter()

# Supabaseクライアントとリポジトリの初期化
supabase_client = get_supabase_client()
document_repository = SupabaseDocumentRepository(supabase_client)
embedding_repository = SupabaseEmbeddingRepository(supabase_client)
ingest_use_case = IngestDocumentUseCase(
    document_repository=document_repository,
    embedding_repository=embedding_repository
)

# デフォルトのテナントID（暫定）。必要に応じてフォーム側から tenant_id を渡してください。
DEFAULT_TENANT_ID = "188d1388-ae85-4753-b640-eea55e9d83fe"


@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    tenant_id: str | None = Form(None),
    title: str | None = Form(None),
) -> Dict[str, Any]:
    """
    PDFをアップロードして取り込み（ingest）を実行するエンドポイント。
    - file: PDFファイル
    - tenant_id: 省略時は暫定のデフォルトを利用
    - title: 省略時はファイル名をタイトルとして利用
    """
    try:
        tenant_uuid = UUID(tenant_id or DEFAULT_TENANT_ID)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid tenant_id")

    # アップロードファイルを一時保存
    try:
        suffix = os.path.splitext(file.filename or "")[1] or ".pdf"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    try:
        document = await ingest_use_case.execute(
            tenant_id=tenant_uuid,
            title=title or (file.filename or "uploaded.pdf"),
            file_path=tmp_path,
        )
        return {
            "documentId": str(document.id),
            "message": "Upload & ingest completed",
            "title": document.title,
            "status": document.status,
            "total_chunks": document.total_chunks,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to ingest document: {str(e)}")
    finally:
        # 一時ファイルを削除
        try:
            os.remove(tmp_path)
        except Exception:
            pass
