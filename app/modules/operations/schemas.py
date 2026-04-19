"""Operations Management Schemas"""
from datetime import datetime, date, time
from typing import Optional, List
from pydantic import BaseModel


# ===== EMPLOYEE SCHEMAS =====

class CreateEmployee(BaseModel):
    email: str
    name: str
    employee_id: str
    department: Optional[str] = None
    designation: Optional[str] = None
    hourly_rate: Optional[float] = None
    salary: Optional[float] = None
    phone: Optional[str] = None
    manager_id: Optional[int] = None
    date_of_joining: Optional[date] = None
    is_billable: bool = True


class UpdateEmployee(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    status: Optional[str] = None
    hourly_rate: Optional[float] = None
    salary: Optional[float] = None
    phone: Optional[str] = None
    manager_id: Optional[int] = None
    is_billable: Optional[bool] = None


class EmployeeOut(BaseModel):
    id: int
    email: str
    name: str
    employee_id: str
    department: Optional[str]
    designation: Optional[str]
    status: str
    hourly_rate: Optional[float]
    salary: Optional[float]
    phone: Optional[str]
    manager_id: Optional[int]
    date_of_joining: Optional[date]
    date_of_exit: Optional[date]
    is_billable: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ===== ACTIVITY SCHEMAS =====

class CreateActivity(BaseModel):
    activity_date: date
    title: str
    description: Optional[str] = None
    hours_spent: float
    project_id: Optional[int] = None
    task_assignment_id: Optional[int] = None
    status: Optional[str] = "in_progress"
    billable: bool = True
    notes: Optional[str] = None


class UpdateActivity(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    hours_spent: Optional[float] = None
    status: Optional[str] = None
    billable: Optional[bool] = None
    notes: Optional[str] = None


class ActivityOut(BaseModel):
    id: int
    employee_id: int
    activity_date: date
    title: str
    description: Optional[str]
    hours_spent: float
    project_id: Optional[int]
    task_assignment_id: Optional[int]
    status: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    billable: bool
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ===== ATTENDANCE SCHEMAS =====

class ClockInRequest(BaseModel):
    """Clock-in request"""
    attendance_date: date = None  # Defaults to today if not provided


class ClockOutRequest(BaseModel):
    """Clock-out request"""
    break_minutes: int = 0


class BreakStartRequest(BaseModel):
    """Start break"""
    pass


class BreakEndRequest(BaseModel):
    """End break"""
    pass


class CreateAttendance(BaseModel):
    attendance_date: date
    clock_in_time: datetime
    clock_out_time: Optional[datetime] = None
    total_break_minutes: int = 0
    is_manual_entry: bool = True
    remarks: Optional[str] = None


class UpdateAttendance(BaseModel):
    clock_out_time: Optional[datetime] = None
    total_break_minutes: Optional[int] = None
    remarks: Optional[str] = None


class AttendanceOut(BaseModel):
    id: int
    employee_id: int
    attendance_date: date
    clock_in_time: datetime
    clock_out_time: Optional[datetime]
    break_start_time: Optional[datetime]
    break_end_time: Optional[datetime]
    total_break_minutes: int
    worked_hours: Optional[float]
    status: str
    is_manual_entry: bool
    remarks: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ===== TASK ASSIGNMENT SCHEMAS =====

class CreateTaskAssignment(BaseModel):
    title: str
    description: Optional[str] = None
    assigned_to_id: int
    project_id: Optional[int] = None
    priority: str = "medium"
    estimated_hours: Optional[float] = None
    due_date: Optional[date] = None
    start_date: Optional[date] = None
    notes: Optional[str] = None


class UpdateTaskAssignment(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    due_date: Optional[date] = None
    start_date: Optional[date] = None
    completion_date: Optional[date] = None
    completed_percentage: Optional[float] = None
    notes: Optional[str] = None


class TaskAssignmentOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    assigned_to_id: int
    assigned_by_id: int
    project_id: Optional[int]
    status: str
    priority: str
    estimated_hours: Optional[float]
    actual_hours: Optional[float]
    due_date: Optional[date]
    start_date: Optional[date]
    completion_date: Optional[date]
    completed_percentage: float
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ===== PAGINATION SCHEMAS =====

class PaginatedEmployees(BaseModel):
    data: List[EmployeeOut]
    meta: dict


class PaginatedActivities(BaseModel):
    data: List[ActivityOut]
    meta: dict


class PaginatedAttendances(BaseModel):
    data: List[AttendanceOut]
    meta: dict


class PaginatedTaskAssignments(BaseModel):
    data: List[TaskAssignmentOut]
    meta: dict
