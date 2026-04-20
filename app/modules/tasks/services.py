from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.tasks.models import Task, TimeLog
from app.modules.tasks.schemas import CreateTask, CreateTimeLog


def create_task(db: Session, payload: CreateTask) -> Task:
    task = Task(**payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_task(db: Session, task_id: int) -> Task | None:
    stmt = select(Task).where(Task.id == task_id)
    return db.execute(stmt).scalar_one_or_none()


def list_tasks(
    db: Session,
    *,
    project_id: int | None,
    status: str | None,
    page: int,
    limit: int,
) -> tuple[list[Task], int]:
    filters = []
    if project_id is not None:
        filters.append(Task.project_id == project_id)
    if status is not None:
        filters.append(Task.status == status)

    total_stmt = select(func.count()).select_from(Task)
    if filters:
        total_stmt = total_stmt.where(*filters)
    total = db.execute(total_stmt).scalar_one()

    stmt = select(Task).order_by(Task.id.desc())
    if filters:
        stmt = stmt.where(*filters)
    stmt = stmt.offset((page - 1) * limit).limit(limit)

    rows = db.execute(stmt).scalars().all()
    return rows, int(total)


def delete_task(db: Session, task_id: int) -> bool:
    task = get_task(db, task_id)
    if not task:
        return False
    db.delete(task)
    db.commit()
    return True


def update_task(db: Session, task_id: int, payload: CreateTask) -> Task | None:
    task = get_task(db, task_id)
    if not task:
        return None
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task


def create_time_log(db: Session, payload: CreateTimeLog) -> TimeLog:
    time_log = TimeLog(**payload.model_dump())
    db.add(time_log)
    db.commit()
    db.refresh(time_log)
    return time_log


def total_hours_for_project(db: Session, *, project_id: int) -> float:
    # Sum hours of all time logs attached to tasks for the project.
    stmt = (
        select(func.coalesce(func.sum(TimeLog.hours), 0.0))
        .join(Task, Task.id == TimeLog.task_id)
        .where(Task.project_id == project_id)
    )
    total = db.execute(stmt).scalar_one()
    return float(total or 0.0)
