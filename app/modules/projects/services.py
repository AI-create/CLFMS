from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.projects.models import Project
from app.modules.projects.schemas import CreateProject


def create_project(db: Session, payload: CreateProject) -> Project:
    project = Project(**payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def get_project(db: Session, project_id: int) -> Project | None:
    stmt = select(Project).where(Project.id == project_id)
    return db.execute(stmt).scalar_one_or_none()


def list_projects(
    db: Session,
    *,
    client_id: int | None,
    page: int,
    limit: int,
) -> tuple[list[Project], int]:
    filters = []
    if client_id is not None:
        filters.append(Project.client_id == client_id)

    total_stmt = select(func.count()).select_from(Project)
    if filters:
        total_stmt = total_stmt.where(*filters)
    total = db.execute(total_stmt).scalar_one()

    stmt = select(Project).order_by(Project.id.desc())
    if filters:
        stmt = stmt.where(*filters)
    stmt = stmt.offset((page - 1) * limit).limit(limit)

    rows = db.execute(stmt).scalars().all()
    return rows, int(total)
