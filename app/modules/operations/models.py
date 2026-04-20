"""Operations Management Models"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Boolean, Text, Enum as SQLEnum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class EmployeeStatus(str, enum.Enum):
    """Employee employment status"""
    active = "active"
    inactive = "inactive"
    on_leave = "on_leave"
    terminated = "terminated"


class AttendanceStatus(str, enum.Enum):
    """Attendance status for clock-in/out"""
    clocked_in = "clocked_in"
    clocked_out = "clocked_out"
    break_started = "break_started"
    break_ended = "break_ended"


class ActivityStatus(str, enum.Enum):
    """Activity/task status"""
    assigned = "assigned"
    in_progress = "in_progress"
    on_hold = "on_hold"
    completed = "completed"
    cancelled = "cancelled"


class Employee(Base):
    """Employee master data"""
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    employee_id = Column(String, unique=True, nullable=False)  # Company emp ID
    department = Column(String, nullable=True)
    designation = Column(String, nullable=True)
    status = Column(SQLEnum(EmployeeStatus), default=EmployeeStatus.active)
    hourly_rate = Column(Float, nullable=True)  # For hourly billing
    salary = Column(Float, nullable=True)  # Monthly salary
    phone = Column(String, nullable=True)
    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    date_of_joining = Column(Date, nullable=True)
    date_of_exit = Column(Date, nullable=True)
    is_billable = Column(Boolean, default=True)  # Can be billed to projects
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    activities = relationship("Activity", back_populates="employee", cascade="all, delete-orphan")
    attendances = relationship("Attendance", back_populates="employee", cascade="all, delete-orphan")
    task_assignments = relationship("TaskAssignment", back_populates="assigned_to", cascade="all, delete-orphan", foreign_keys="TaskAssignment.assigned_to_id")
    manager = relationship("Employee", remote_side=[id], backref="subordinates")


class Activity(Base):
    """Daily activity logs for employees"""
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, index=True)
    activity_date = Column(Date, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    hours_spent = Column(Float, nullable=False)  # Hours spent on activity
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)  # Can link to project
    task_assignment_id = Column(Integer, ForeignKey("task_assignments.id"), nullable=True)
    status = Column(SQLEnum(ActivityStatus), default=ActivityStatus.in_progress)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    billable = Column(Boolean, default=True)  # Is this billable to client?
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    employee = relationship("Employee", back_populates="activities")


class Attendance(Base):
    """Clock-in/out records and attendance tracking"""
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, index=True)
    attendance_date = Column(Date, nullable=False, index=True)
    clock_in_time = Column(DateTime, nullable=False)
    clock_out_time = Column(DateTime, nullable=True)
    break_start_time = Column(DateTime, nullable=True)
    break_end_time = Column(DateTime, nullable=True)
    total_break_minutes = Column(Integer, default=0)
    worked_hours = Column(Float, nullable=True)  # Calculated: total time - break time
    status = Column(SQLEnum(AttendanceStatus), default=AttendanceStatus.clocked_in)
    is_manual_entry = Column(Boolean, default=False)  # Whether manually entered vs clocked
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Unique constraint: one entry per employee per date
    __table_args__ = (UniqueConstraint('employee_id', 'attendance_date', name='uq_employee_attendance_date'),)

    # Relationships
    employee = relationship("Employee", back_populates="attendances")


class TaskAssignment(Base):
    """Task assignments for employees"""
    __tablename__ = "task_assignments"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    assigned_to_id = Column(Integer, ForeignKey("employees.id"), nullable=False, index=True)
    assigned_by_id = Column(Integer, ForeignKey("employees.id"), nullable=True)  # Who assigned (nullable: non-employee admins can assign)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    status = Column(SQLEnum(ActivityStatus), default=ActivityStatus.assigned)
    priority = Column(String, default="medium")  # low, medium, high, critical
    estimated_hours = Column(Float, nullable=True)
    actual_hours = Column(Float, nullable=True)
    due_date = Column(Date, nullable=True)
    start_date = Column(Date, nullable=True)
    completion_date = Column(Date, nullable=True)
    completed_percentage = Column(Float, default=0)  # 0-100%
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assigned_to = relationship("Employee", back_populates="task_assignments", foreign_keys=[assigned_to_id])
