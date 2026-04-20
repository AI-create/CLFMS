from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import api_error, api_success
from app.core.security import require_roles
from app.modules.tasks import services
from app.modules.tasks.schemas import CreateTask, CreateTimeLog, TaskOut, TimeLogOut


router = APIRouter(tags=["Tasks"])


@router.post("/tasks")
def create_task(
    payload: CreateTask,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "operations", "project_manager", "pm", "sales", "finance", "researcher"])),
):
    task = services.create_task(db, payload)
    return api_success(TaskOut.model_validate(task))


@router.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "operations", "project_manager", "pm"])),
):
    task = services.get_task(db, task_id)
    if not task:
        return api_error("NOT_FOUND", "Task not found", http_status=404)

    services.delete_task(db, task_id)
    return api_success({"message": "Task deleted successfully"})


@router.put("/tasks/{task_id}")
def update_task(
    task_id: int,
    payload: CreateTask,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "operations", "project_manager", "pm", "sales", "finance", "researcher"])),
):
    task = services.update_task(db, task_id, payload)
    if not task:
        return api_error("NOT_FOUND", "Task not found", http_status=404)
    return api_success(TaskOut.model_validate(task))


@router.get("/tasks")
def list_tasks(
    project_id: int | None = None,
    status: str | None = None,
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "operations", "project_manager", "pm", "sales", "finance", "researcher"])),
):
    page = max(page, 1)
    limit = min(max(limit, 1), 100)
    rows, total = services.list_tasks(db, project_id=project_id, status=status, page=page, limit=limit)
    return api_success(
        {
            "data": [TaskOut.model_validate(t) for t in rows],
            "meta": {"total": total, "page": page, "limit": limit},
        }
    )


@router.post("/time-logs")
def create_time_log(
    payload: CreateTimeLog,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "operations", "project_manager", "pm", "sales", "finance", "researcher"])),
):
    # Basic validation: ensure task exists.
    if not services.get_task(db, payload.task_id):
        return api_error("NOT_FOUND", "Task not found", http_status=404)
    time_log = services.create_time_log(db, payload)
    return api_success(TimeLogOut.model_validate(time_log))
