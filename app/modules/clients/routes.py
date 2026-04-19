from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.core.response import api_error, api_success
from app.core.security import require_roles
from app.modules.clients.schemas import ClientOut, CreateClient, PaginatedClients
from app.modules.clients import services
from app.services.activity_logging_service import log_activity


router = APIRouter(tags=["Clients"])


@router.post("/clients")
def create_client(
    payload: CreateClient,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "sales", "operations", "finance"])),
):
    client = services.create_client(db, payload)
    
    # Log the activity
    log_activity(
        db=db,
        user_email=_user.get("email"),
        action="create",
        entity_type="client",
        entity_id=client.id,
        entity_name=payload.company_name,
        new_values=payload.model_dump(),
        description=f"Created client: {payload.company_name}"
    )
    
    return api_success(ClientOut.model_validate(client))


@router.get("/clients")
def list_clients(
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "sales", "operations", "finance"])),
):
    page = max(page, 1)
    limit = min(max(limit, 1), 100)

    rows, total = services.list_clients(db, page=page, limit=limit)
    return api_success(
        PaginatedClients(
            data=[ClientOut.model_validate(c) for c in rows],
            meta={"total": total, "page": page, "limit": limit},
        )
    )


@router.get("/clients/{client_id}")
def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "sales", "operations", "finance"])),
):
    client = services.get_client(db, client_id)
    if not client:
        return api_error("NOT_FOUND", "Client not found", http_status=404)
    return api_success(ClientOut.model_validate(client))


@router.put("/clients/{client_id}")
def update_client(
    client_id: int,
    payload: CreateClient,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "sales", "operations", "finance"])),
):
    client = services.get_client(db, client_id)
    if not client:
        return api_error("NOT_FOUND", "Client not found", http_status=404)
    
    # Store old values before update
    old_client = ClientOut.model_validate(client)
    old_values = {
        k: v for k, v in old_client.model_dump().items()
        if not isinstance(v, datetime) or v is None
    }
    
    # Update client
    client = services.update_client(db, client_id, payload)
    
    # Log the activity
    log_activity(
        db=db,
        user_email=_user.get("email"),
        action="update",
        entity_type="client",
        entity_id=client.id,
        entity_name=client.company_name,
        new_values={
            k: v for k, v in payload.model_dump().items()
            if not isinstance(v, datetime) or v is None
        },
        old_values=old_values,
        description=f"Updated client: {client.company_name}"
    )
    
    return api_success(ClientOut.model_validate(client))
