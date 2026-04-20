"""Operations Management Routes"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date, datetime

from app.core.database import get_db
from app.core.response import api_error, api_success
from app.core.security import require_roles
from app.modules.operations import services
from app.modules.operations.schemas import (
    CreateEmployee,
    UpdateEmployee,
    CreateActivity,
    UpdateActivity,
    ClockInRequest,
    ClockOutRequest,
    CreateAttendance,
    UpdateAttendance,
    CreateTaskAssignment,
    UpdateTaskAssignment,
    EmployeeOut,
    ActivityOut,
    AttendanceOut,
    TaskAssignmentOut,
    PaginatedEmployees,
    PaginatedActivities,
    PaginatedAttendances,
    PaginatedTaskAssignments,
)
from app.services.activity_logging_service import log_activity


router = APIRouter(tags=["Operations"])


# ===== EMPLOYEE ENDPOINTS =====

@router.post("/employees")
def create_employee(
    payload: CreateEmployee,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "operations", "hr"])),
):
    """Create a new employee"""
    employee = services.OperationsService.create_employee(db, payload)
    
    log_activity(
        db=db,
        user_email=_user.get("email"),
        action="create",
        entity_type="employee",
        entity_id=employee.id,
        entity_name=payload.name,
        new_values=payload.model_dump(),
        description=f"Created employee: {payload.name}"
    )
    
    return api_success(EmployeeOut.model_validate(employee))


@router.get("/employees")
def list_employees(
    department: str | None = Query(None),
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "operations", "hr", "project_manager"])),
):
    """List employees with filters"""
    employees, total = services.OperationsService.list_employees(
        db,
        department=department,
        status=status,
        page=page,
        limit=limit,
    )
    
    return api_success(
        PaginatedEmployees(
            data=[EmployeeOut.model_validate(e) for e in employees],
            meta={"total": total, "page": page, "limit": limit},
        ).model_dump()
    )


@router.get("/employees/{employee_id}")
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "operations", "hr", "project_manager"])),
):
    """Get employee by ID"""
    employee = services.OperationsService.get_employee(db, employee_id)
    if not employee:
        return api_error("NOT_FOUND", "Employee not found", http_status=404)
    return api_success(EmployeeOut.model_validate(employee))


@router.put("/employees/{employee_id}")
def update_employee(
    employee_id: int,
    payload: UpdateEmployee,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "operations", "hr"])),
):
    """Update employee"""
    employee = services.OperationsService.update_employee(
        db, employee_id, payload.model_dump(exclude_unset=True)
    )
    if not employee:
        return api_error("NOT_FOUND", "Employee not found", http_status=404)
    
    log_activity(
        db=db,
        user_email=_user.get("email"),
        action="update",
        entity_type="employee",
        entity_id=employee.id,
        entity_name=employee.name,
        new_values=payload.model_dump(exclude_unset=True),
        description=f"Updated employee: {employee.name}"
    )
    
    return api_success(EmployeeOut.model_validate(employee))


@router.delete("/employees/{employee_id}")
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "hr"])),
):
    """Delete employee"""
    employee = services.OperationsService.get_employee(db, employee_id)
    if not employee:
        return api_error("NOT_FOUND", "Employee not found", http_status=404)
    
    name = employee.name
    deleted = services.OperationsService.delete_employee(db, employee_id)
    
    log_activity(
        db=db,
        user_email=_user.get("email"),
        action="delete",
        entity_type="employee",
        entity_id=employee_id,
        entity_name=name,
        description=f"Deleted employee: {name}"
    )
    
    return api_success({"message": f"Employee '{name}' deleted successfully"})


# ===== ACTIVITY ENDPOINTS =====

@router.post("/employees/{employee_id}/activities")
def create_activity(
    employee_id: int,
    payload: CreateActivity,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "operations", "employee"])),
):
    """Create activity log for employee"""
    # Verify employee exists
    employee = services.OperationsService.get_employee(db, employee_id)
    if not employee:
        return api_error("NOT_FOUND", "Employee not found", http_status=404)
    
    activity = services.OperationsService.create_activity(db, employee_id, payload)
    
    log_activity(
        db=db,
        user_email=_user.get("email"),
        action="create",
        entity_type="activity",
        entity_id=activity.id,
        entity_name=payload.title,
        new_values=payload.model_dump(),
        description=f"Created activity: {payload.title}"
    )
    
    return api_success(ActivityOut.model_validate(activity))


@router.get("/employees/{employee_id}/activities")
def list_activities(
    employee_id: int,
    activity_date: date | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    status: str | None = Query(None),
    billable: bool | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "operations", "project_manager", "employee"])),
):
    """List activities for employee"""
    # Verify employee exists
    employee = services.OperationsService.get_employee(db, employee_id)
    if not employee:
        return api_error("NOT_FOUND", "Employee not found", http_status=404)
    
    activities, total = services.OperationsService.list_activities(
        db,
        employee_id=employee_id,
        activity_date=activity_date,
        date_from=date_from,
        date_to=date_to,
        status=status,
        billable=billable,
        page=page,
        limit=limit,
    )
    
    return api_success(
        PaginatedActivities(
            data=[ActivityOut.model_validate(a) for a in activities],
            meta={"total": total, "page": page, "limit": limit},
        ).model_dump()
    )


@router.get("/activities/{activity_id}")
def get_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "operations", "project_manager", "employee"])),
):
    """Get activity by ID"""
    activity = services.OperationsService.get_activity(db, activity_id)
    if not activity:
        return api_error("NOT_FOUND", "Activity not found", http_status=404)
    return api_success(ActivityOut.model_validate(activity))


@router.put("/activities/{activity_id}")
def update_activity(
    activity_id: int,
    payload: UpdateActivity,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "operations", "employee"])),
):
    """Update activity"""
    activity = services.OperationsService.update_activity(
        db, activity_id, payload.model_dump(exclude_unset=True)
    )
    if not activity:
        return api_error("NOT_FOUND", "Activity not found", http_status=404)
    
    log_activity(
        db=db,
        user_email=_user.get("email"),
        action="update",
        entity_type="activity",
        entity_id=activity.id,
        entity_name=activity.title,
        new_values=payload.model_dump(exclude_unset=True),
        description=f"Updated activity: {activity.title}"
    )
    
    return api_success(ActivityOut.model_validate(activity))


@router.get("/employees/{employee_id}/daily-hours")
def get_daily_hours(
    employee_id: int,
    activity_date: date = Query(None),
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "operations", "project_manager"])),
):
    """Get billable hours for employee on specific date"""
    if activity_date is None:
        activity_date = date.today()
    
    employee = services.OperationsService.get_employee(db, employee_id)
    if not employee:
        return api_error("NOT_FOUND", "Employee not found", http_status=404)
    
    hours = services.OperationsService.get_employee_daily_hours(db, employee_id, activity_date)
    return api_success({
        "employee_id": employee_id,
        "activity_date": activity_date,
        "billable_hours": hours,
    })


# ===== ATTENDANCE ENDPOINTS =====

@router.post("/employees/{employee_id}/clock-in")
def clock_in(
    employee_id: int,
    payload: ClockInRequest,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "operations", "employee"])),
):
    """Clock-in for employee"""
    employee = services.OperationsService.get_employee(db, employee_id)
    if not employee:
        return api_error("NOT_FOUND", "Employee not found", http_status=404)
    
    attendance = services.OperationsService.clock_in(db, employee_id, payload.attendance_date)
    
    log_activity(
        db=db,
        user_email=_user.get("email"),
        action="create",
        entity_type="attendance",
        entity_id=attendance.id,
        entity_name=f"Clock-in {employee.name}",
        new_values={"clock_in_time": attendance.clock_in_time.isoformat()},
        description=f"Employee {employee.name} clocked in"
    )
    
    return api_success(AttendanceOut.model_validate(attendance))


@router.post("/employees/{employee_id}/clock-out")
def clock_out(
    employee_id: int,
    payload: ClockOutRequest,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "operations", "employee"])),
):
    """Clock-out for employee"""
    employee = services.OperationsService.get_employee(db, employee_id)
    if not employee:
        return api_error("NOT_FOUND", "Employee not found", http_status=404)
    
    attendance = services.OperationsService.clock_out(db, employee_id, payload.break_minutes)
    if not attendance:
        return api_error("NOT_FOUND", "No active clock-in found", http_status=404)
    
    log_activity(
        db=db,
        user_email=_user.get("email"),
        action="update",
        entity_type="attendance",
        entity_id=attendance.id,
        entity_name=f"Clock-out {employee.name}",
        new_values={
            "clock_out_time": attendance.clock_out_time.isoformat(),
            "worked_hours": attendance.worked_hours
        },
        description=f"Employee {employee.name} clocked out (worked {attendance.worked_hours} hours)"
    )
    
    return api_success(AttendanceOut.model_validate(attendance))


@router.get("/employees/{employee_id}/attendances")
def list_attendances(
    employee_id: int,
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "operations", "project_manager", "employee"])),
):
    """List attendances for employee"""
    employee = services.OperationsService.get_employee(db, employee_id)
    if not employee:
        return api_error("NOT_FOUND", "Employee not found", http_status=404)
    
    attendances, total = services.OperationsService.list_attendances(
        db,
        employee_id=employee_id,
        date_from=date_from,
        date_to=date_to,
        page=page,
        limit=limit,
    )
    
    return api_success(
        PaginatedAttendances(
            data=[AttendanceOut.model_validate(a) for a in attendances],
            meta={"total": total, "page": page, "limit": limit},
        ).model_dump()
    )


# ===== TASK ASSIGNMENT ENDPOINTS =====

@router.post("/task-assignments")
def create_task_assignment(
    payload: CreateTaskAssignment,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "operations", "project_manager"])),
):
    """Create task assignment"""
    # Verify assigned employee exists
    employee = services.OperationsService.get_employee(db, payload.assigned_to_id)
    if not employee:
        return api_error("NOT_FOUND", "Assigned employee not found", http_status=404)
    
    task = services.OperationsService.create_task_assignment(
        db, _user.get("user_id") or 1, payload
    )
    
    log_activity(
        db=db,
        user_email=_user.get("email"),
        action="create",
        entity_type="task_assignment",
        entity_id=task.id,
        entity_name=payload.title,
        new_values=payload.model_dump(),
        description=f"Assigned task: {payload.title} to {employee.name}"
    )
    
    return api_success(TaskAssignmentOut.model_validate(task))


@router.get("/task-assignments")
def list_task_assignments(
    assigned_to_id: int | None = Query(None),
    status: str | None = Query(None),
    priority: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "operations", "project_manager", "employee"])),
):
    """List task assignments"""
    tasks, total = services.OperationsService.list_task_assignments(
        db,
        assigned_to_id=assigned_to_id,
        status=status,
        priority=priority,
        page=page,
        limit=limit,
    )
    
    return api_success(
        PaginatedTaskAssignments(
            data=[TaskAssignmentOut.model_validate(t) for t in tasks],
            meta={"total": total, "page": page, "limit": limit},
        ).model_dump()
    )


@router.get("/task-assignments/{task_id}")
def get_task_assignment(
    task_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "operations", "project_manager", "employee"])),
):
    """Get task assignment by ID"""
    task = services.OperationsService.get_task_assignment(db, task_id)
    if not task:
        return api_error("NOT_FOUND", "Task assignment not found", http_status=404)
    return api_success(TaskAssignmentOut.model_validate(task))


@router.put("/task-assignments/{task_id}")
def update_task_assignment(
    task_id: int,
    payload: UpdateTaskAssignment,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "operations", "project_manager", "employee"])),
):
    """Update task assignment"""
    task = services.OperationsService.update_task_assignment(
        db, task_id, payload.model_dump(exclude_unset=True)
    )
    if not task:
        return api_error("NOT_FOUND", "Task assignment not found", http_status=404)
    
    log_activity(
        db=db,
        user_email=_user.get("email"),
        action="update",
        entity_type="task_assignment",
        entity_id=task.id,
        entity_name=task.title,
        new_values=payload.model_dump(exclude_unset=True),
        description=f"Updated task: {task.title}"
    )
    
    return api_success(TaskAssignmentOut.model_validate(task))


# ===== ANALYTICS ENDPOINTS =====

@router.get("/employees/{employee_id}/summary")
def get_employee_summary(
    employee_id: int,
    year: int | None = Query(None),
    month: int | None = Query(None),
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "operations", "project_manager", "hr"])),
):
    """Get employee monthly summary"""
    if year is None or month is None:
        today = date.today()
        year = today.year
        month = today.month
    
    summary = services.OperationsService.get_employee_summary(db, employee_id, year, month)
    if not summary:
        return api_error("NOT_FOUND", "Employee not found", http_status=404)
    
    return api_success(summary)
