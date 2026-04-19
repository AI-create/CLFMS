from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.clients.models import Client
from app.modules.clients.schemas import CreateClient


def create_client(db: Session, payload: CreateClient) -> Client:
    client = Client(**payload.model_dump())
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


def get_client(db: Session, client_id: int) -> Client | None:
    stmt = select(Client).where(Client.id == client_id)
    return db.execute(stmt).scalar_one_or_none()


def update_client(db: Session, client_id: int, payload: CreateClient) -> Client:
    client = get_client(db, client_id)
    if client:
        for key, value in payload.model_dump().items():
            setattr(client, key, value)
        db.commit()
        db.refresh(client)
    return client


def list_clients(db: Session, *, page: int, limit: int) -> tuple[list[Client], int]:
    total_stmt = select(func.count()).select_from(Client)
    total = db.execute(total_stmt).scalar_one()

    stmt = select(Client).order_by(Client.id.desc()).offset((page - 1) * limit).limit(limit)
    rows = db.execute(stmt).scalars().all()
    return rows, int(total)
