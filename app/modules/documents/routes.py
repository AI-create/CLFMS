from pathlib import Path

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import api_error, api_success
from app.core.security import require_roles
from app.modules.documents.schemas import DocumentOut, GenerateDocumentRequest
from app.modules.documents import services as doc_services
from app.services.activity_logging_service import log_activity


router = APIRouter(tags=["Documents"])


@router.get("/documents")
def list_documents(
    entity_type: str | None = None,
    entity_id: int | None = None,
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance"])),
):
    from app.modules.documents.models import Document as DocumentModel
    from sqlalchemy import desc as sa_desc
    query = db.query(DocumentModel)
    if entity_type:
        query = query.filter(DocumentModel.entity_type == entity_type)
    if entity_id:
        query = query.filter(DocumentModel.entity_id == entity_id)
    total = query.count()
    docs = query.order_by(sa_desc(DocumentModel.created_at)).offset((page - 1) * limit).limit(limit).all()
    return api_success(
        {
            "data": [DocumentOut.model_validate(d) for d in docs],
            "meta": {"total": total, "page": page, "limit": limit},
        }
    )


@router.post("/documents/generate")
def generate_document(
    payload: GenerateDocumentRequest,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance"])),
):
    try:
        if payload.type == "invoice":
            doc = doc_services.generate_invoice_html(db, payload.entity_id)
        else:
            return api_error("INVALID_INPUT", "Unsupported document type", http_status=400)
    except ValueError:
        return api_error("NOT_FOUND", "Entity not found", http_status=404)

    # Log the activity
    log_activity(
        db=db,
        user_email=_user.get("email"),
        action="generate",
        entity_type=payload.type,
        entity_id=payload.entity_id,
        entity_name=f"Generated {payload.type} document",
        new_values={"type": payload.type, "entity_id": payload.entity_id},
        description=f"Generated {payload.type} document for entity {payload.entity_id}"
    )

    return api_success(DocumentOut.model_validate(doc))


@router.get("/documents/{doc_id}/download")
def download_document(
    doc_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance"])),
):
    doc = doc_services.get_document(db, doc_id)
    if not doc:
        return api_error("NOT_FOUND", "Document not found", http_status=404)

    path = Path(doc.file_path)
    if not path.exists():
        return api_error("NOT_FOUND", "File not found", http_status=404)

    # Log the activity
    log_activity(
        db=db,
        user_email=_user.get("email"),
        action="download",
        entity_type="document",
        entity_id=doc_id,
        entity_name=f"Downloaded {path.name}",
        description=f"Downloaded document {path.name}"
    )

    return FileResponse(path=str(path), filename=path.name, media_type="text/html")

