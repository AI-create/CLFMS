"""Operations Management Services"""
from datetime import datetime, date, timedelta, timezone
from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from app.modules.operations.models import Employee, Activity, Attendance, TaskAssignment, EmployeeStatus, ActivityStatus, AttendanceStatus
from app.modules.operations.schemas import CreateEmployee, CreateActivity, CreateAttendance, CreateTaskAssignment


class OperationsService:
    """Service for operations management"""

    # ===== EMPLOYEE OPERATIONS =====

    @staticmethod
    def create_employee(db: Session, payload: CreateEmployee) -> Employee:
        """Create a new employee"""
        employee = Employee(
            email=payload.email,
            name=payload.name,
            employee_id=payload.employee_id,
            department=payload.department,
            designation=payload.designation,
            hourly_rate=payload.hourly_rate,
            salary=payload.salary,
            phone=payload.phone,
            manager_id=payload.manager_id,
            date_of_joining=payload.date_of_joining,
            is_billable=payload.is_billable,
        )
        db.add(employee)
        db.commit()
        db.refresh(employee)
        return employee

    @staticmethod
    def get_employee(db: Session, employee_id: int) -> Employee | None:
        """Get employee by ID"""
        return db.query(Employee).filter(Employee.id == employee_id).first()

    @staticmethod
    def list_employees(
        db: Session,
        department: str | None = None,
        status: str | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Employee], int]:
        """List employees with filters"""
        query = db.query(Employee)
        
        if department:
            query = query.filter(Employee.department == department)
        if status:
            query = query.filter(Employee.status == status)
        
        total = query.count()
        query = query.offset((page - 1) * limit).limit(limit)
        return query.all(), total

    @staticmethod
    def update_employee(db: Session, employee_id: int, payload: dict) -> Employee | None:
        """Update employee"""
        employee = OperationsService.get_employee(db, employee_id)
        if not employee:
            return None
        
        for key, value in payload.items():
            if value is not None:
                setattr(employee, key, value)
        
        employee.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(employee)
        return employee

    @staticmethod
    def delete_employee(db: Session, employee_id: int) -> bool:
        """Delete employee by ID"""
        employee = OperationsService.get_employee(db, employee_id)
        if not employee:
            return False
        db.delete(employee)
        db.commit()
        return True

    # ===== ACTIVITY OPERATIONS =====

    @staticmethod
    def create_activity(db: Session, employee_id: int, payload: CreateActivity) -> Activity:
        """Create activity log"""
        activity = Activity(
            employee_id=employee_id,
            activity_date=payload.activity_date,
            title=payload.title,
            description=payload.description,
            hours_spent=payload.hours_spent,
            project_id=payload.project_id,
            task_assignment_id=payload.task_assignment_id,
            status=payload.status,
            billable=payload.billable,
            notes=payload.notes,
        )
        db.add(activity)
        db.commit()
        db.refresh(activity)
        return activity

    @staticmethod
    def get_activity(db: Session, activity_id: int) -> Activity | None:
        """Get activity by ID"""
        return db.query(Activity).filter(Activity.id == activity_id).first()

    @staticmethod
    def list_activities(
        db: Session,
        employee_id: int | None = None,
        activity_date: date | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        status: str | None = None,
        billable: bool | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Activity], int]:
        """List activities with filters"""
        query = db.query(Activity)
        
        if employee_id:
            query = query.filter(Activity.employee_id == employee_id)
        if activity_date:
            query = query.filter(Activity.activity_date == activity_date)
        if date_from:
            query = query.filter(Activity.activity_date >= date_from)
        if date_to:
            query = query.filter(Activity.activity_date <= date_to)
        if status:
            query = query.filter(Activity.status == status)
        if billable is not None:
            query = query.filter(Activity.billable == billable)
        
        total = query.count()
        query = query.order_by(Activity.activity_date.desc()).offset((page - 1) * limit).limit(limit)
        return query.all(), total

    @staticmethod
    def update_activity(db: Session, activity_id: int, payload: dict) -> Activity | None:
        """Update activity"""
        activity = OperationsService.get_activity(db, activity_id)
        if not activity:
            return None
        
        for key, value in payload.items():
            if value is not None:
                setattr(activity, key, value)
        
        activity.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(activity)
        return activity

    @staticmethod
    def get_employee_daily_hours(db: Session, employee_id: int, activity_date: date) -> float:
        """Get total billable hours for employee on a specific date"""
        activities = db.query(Activity).filter(
            and_(
                Activity.employee_id == employee_id,
                Activity.activity_date == activity_date,
                Activity.billable == True
            )
        ).all()
        return sum(a.hours_spent for a in activities)

    @staticmethod
    def get_employee_monthly_hours(db: Session, employee_id: int, year: int, month: int) -> float:
        """Get total billable hours for employee in a month"""
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        activities = db.query(Activity).filter(
            and_(
                Activity.employee_id == employee_id,
                Activity.activity_date >= start_date,
                Activity.activity_date <= end_date,
                Activity.billable == True
            )
        ).all()
        return sum(a.hours_spent for a in activities)

    # ===== ATTENDANCE OPERATIONS =====

    @staticmethod
    def clock_in(db: Session, employee_id: int, attendance_date: date | None = None) -> Attendance:
        """Clock-in for employee"""
        if attendance_date is None:
            attendance_date = date.today()
        
        # Check if already clocked in
        existing = db.query(Attendance).filter(
            and_(
                Attendance.employee_id == employee_id,
                Attendance.attendance_date == attendance_date
            )
        ).first()
        
        if existing and existing.clock_out_time is None:
            return existing  # Already clocked in
        
        attendance = Attendance(
            employee_id=employee_id,
            attendance_date=attendance_date,
            clock_in_time=datetime.now(timezone.utc),
            status=AttendanceStatus.clocked_in,
        )
        db.add(attendance)
        db.commit()
        db.refresh(attendance)
        return attendance

    @staticmethod
    def clock_out(db: Session, employee_id: int, break_minutes: int = 0) -> Attendance | None:
        """Clock-out for employee"""
        attendance = db.query(Attendance).filter(
            and_(
                Attendance.employee_id == employee_id,
                Attendance.attendance_date == date.today(),
                Attendance.clock_out_time == None
            )
        ).first()
        
        if not attendance:
            return None
        
        clock_out_time = datetime.now(timezone.utc)
        attendance.clock_out_time = clock_out_time
        attendance.total_break_minutes = break_minutes
        attendance.status = AttendanceStatus.clocked_out
        
        # Calculate worked hours
        # Make sure both times are timezone-aware for subtraction
        clock_in = attendance.clock_in_time
        if clock_in.tzinfo is None:
            clock_in = clock_in.replace(tzinfo=timezone.utc)
        
        duration = clock_out_time - clock_in
        total_minutes = duration.total_seconds() / 60
        worked_minutes = max(0, total_minutes - break_minutes)  # Don't allow negative
        attendance.worked_hours = round(worked_minutes / 60, 2)
        
        db.commit()
        db.refresh(attendance)
        return attendance

    @staticmethod
    def get_attendance(db: Session, attendance_id: int) -> Attendance | None:
        """Get attendance by ID"""
        return db.query(Attendance).filter(Attendance.id == attendance_id).first()

    @staticmethod
    def list_attendances(
        db: Session,
        employee_id: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Attendance], int]:
        """List attendances with filters"""
        query = db.query(Attendance)
        
        if employee_id:
            query = query.filter(Attendance.employee_id == employee_id)
        if date_from:
            query = query.filter(Attendance.attendance_date >= date_from)
        if date_to:
            query = query.filter(Attendance.attendance_date <= date_to)
        
        total = query.count()
        query = query.order_by(Attendance.attendance_date.desc()).offset((page - 1) * limit).limit(limit)
        return query.all(), total

    # ===== TASK ASSIGNMENT OPERATIONS =====

    @staticmethod
    def create_task_assignment(
        db: Session,
        assigned_by_id: int,
        payload: CreateTaskAssignment,
    ) -> TaskAssignment:
        """Create task assignment"""
        task = TaskAssignment(
            title=payload.title,
            description=payload.description,
            assigned_to_id=payload.assigned_to_id,
            assigned_by_id=assigned_by_id,
            project_id=payload.project_id,
            priority=payload.priority,
            estimated_hours=payload.estimated_hours,
            due_date=payload.due_date,
            start_date=payload.start_date,
            notes=payload.notes,
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def get_task_assignment(db: Session, task_id: int) -> TaskAssignment | None:
        """Get task assignment by ID"""
        return db.query(TaskAssignment).filter(TaskAssignment.id == task_id).first()

    @staticmethod
    def list_task_assignments(
        db: Session,
        assigned_to_id: int | None = None,
        status: str | None = None,
        priority: str | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[TaskAssignment], int]:
        """List task assignments with filters"""
        query = db.query(TaskAssignment)
        
        if assigned_to_id:
            query = query.filter(TaskAssignment.assigned_to_id == assigned_to_id)
        if status:
            query = query.filter(TaskAssignment.status == status)
        if priority:
            query = query.filter(TaskAssignment.priority == priority)
        
        total = query.count()
        query = query.order_by(TaskAssignment.due_date).offset((page - 1) * limit).limit(limit)
        return query.all(), total

    @staticmethod
    def update_task_assignment(db: Session, task_id: int, payload: dict) -> TaskAssignment | None:
        """Update task assignment"""
        task = OperationsService.get_task_assignment(db, task_id)
        if not task:
            return None
        
        for key, value in payload.items():
            if value is not None:
                setattr(task, key, value)
        
        task.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(task)
        return task

    # ===== ANALYTICS =====

    @staticmethod
    def get_employee_summary(db: Session, employee_id: int, year: int, month: int) -> dict:
        """Get employee monthly summary"""
        employee = OperationsService.get_employee(db, employee_id)
        if not employee:
            return None
        
        billable_hours = OperationsService.get_employee_monthly_hours(db, employee_id, year, month)
        
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        # Get completed tasks
        completed_tasks = db.query(TaskAssignment).filter(
            and_(
                TaskAssignment.assigned_to_id == employee_id,
                TaskAssignment.status == "completed",
                TaskAssignment.completion_date >= start_date,
                TaskAssignment.completion_date <= end_date,
            )
        ).count()
        
        # Get pending tasks
        pending_tasks = db.query(TaskAssignment).filter(
            and_(
                TaskAssignment.assigned_to_id == employee_id,
                TaskAssignment.status.in_(["assigned", "in_progress"]),
            )
        ).count()
        
        return {
            "employee_id": employee_id,
            "employee_name": employee.name,
            "year": year,
            "month": month,
            "billable_hours": billable_hours,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "hourly_rate": employee.hourly_rate or 0,
            "estimated_revenue": (billable_hours * (employee.hourly_rate or 0)),
        }
