"""FI-IO Services"""
from datetime import datetime, date, timedelta, timezone
from sqlalchemy import select, and_, func
from sqlalchemy.orm import Session

from app.modules.fiio.models import (
    HourlyIncome, ProjectIncome, HourlyExpense, ProjectExpense,
    DailyProfit, ProjectProfit
)
from app.modules.fiio.schemas import (
    CreateHourlyIncome, CreateProjectIncome, CreateHourlyExpense, CreateProjectExpense
)
from app.modules.invoices.models import Invoice
from app.modules.payments.models import Payment
from app.modules.finance.models import Expense
from app.modules.operations.models import Employee, Activity, Attendance


class FIIOService:
    """Service for Financial Inflow/Outflow management"""

    # ===== HOURLY INCOME =====

    @staticmethod
    def create_hourly_income(db: Session, payload: CreateHourlyIncome) -> HourlyIncome:
        """Create hourly income record"""
        amount = payload.hours_billed * payload.hourly_rate
        income = HourlyIncome(
            activity_id=payload.activity_id,
            employee_id=payload.employee_id,
            project_id=payload.project_id,
            client_id=payload.client_id,
            income_date=payload.income_date,
            income_type=payload.income_type,
            hours_billed=payload.hours_billed,
            hourly_rate=payload.hourly_rate,
            amount=amount,
            description=payload.description,
        )
        db.add(income)
        db.commit()
        db.refresh(income)
        return income

    @staticmethod
    def get_hourly_income(db: Session, income_id: int) -> HourlyIncome | None:
        """Get hourly income by ID"""
        return db.query(HourlyIncome).filter(HourlyIncome.id == income_id).first()

    @staticmethod
    def list_hourly_incomes(
        db: Session,
        employee_id: int | None = None,
        project_id: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[HourlyIncome], int]:
        """List hourly incomes with filters"""
        query = db.query(HourlyIncome)
        
        if employee_id:
            query = query.filter(HourlyIncome.employee_id == employee_id)
        if project_id:
            query = query.filter(HourlyIncome.project_id == project_id)
        if date_from:
            query = query.filter(HourlyIncome.income_date >= date_from)
        if date_to:
            query = query.filter(HourlyIncome.income_date <= date_to)
        
        total = query.count()
        query = query.order_by(HourlyIncome.income_date.desc()).offset((page - 1) * limit).limit(limit)
        return query.all(), total

    @staticmethod
    def update_hourly_income(db: Session, income_id: int, payload: dict) -> HourlyIncome | None:
        """Update hourly income"""
        income = FIIOService.get_hourly_income(db, income_id)
        if not income:
            return None
        
        for key, value in payload.items():
            if value is not None and key not in ['amount']:
                setattr(income, key, value)
        
        # Recalculate amount if hours or rate changed
        if 'hours_billed' in payload or 'hourly_rate' in payload:
            income.amount = income.hours_billed * income.hourly_rate
        
        income.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(income)
        return income

    # ===== PROJECT INCOME =====

    @staticmethod
    def create_project_income(db: Session, payload: CreateProjectIncome) -> ProjectIncome:
        """Create project income record"""
        income = ProjectIncome(
            project_id=payload.project_id,
            client_id=payload.client_id,
            income_date=payload.income_date,
            income_type=payload.income_type,
            amount=payload.amount,
            description=payload.description,
        )
        db.add(income)
        db.commit()
        db.refresh(income)
        return income

    @staticmethod
    def get_project_income(db: Session, income_id: int) -> ProjectIncome | None:
        """Get project income by ID"""
        return db.query(ProjectIncome).filter(ProjectIncome.id == income_id).first()

    @staticmethod
    def list_project_incomes(
        db: Session,
        project_id: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[ProjectIncome], int]:
        """List project incomes"""
        query = db.query(ProjectIncome)
        
        if project_id:
            query = query.filter(ProjectIncome.project_id == project_id)
        if date_from:
            query = query.filter(ProjectIncome.income_date >= date_from)
        if date_to:
            query = query.filter(ProjectIncome.income_date <= date_to)
        
        total = query.count()
        query = query.order_by(ProjectIncome.income_date.desc()).offset((page - 1) * limit).limit(limit)
        return query.all(), total

    # ===== HOURLY EXPENSE =====

    @staticmethod
    def create_hourly_expense(db: Session, payload: CreateHourlyExpense) -> HourlyExpense:
        """Create hourly expense record"""
        amount = payload.hours_worked * payload.hourly_cost
        expense = HourlyExpense(
            activity_id=payload.activity_id,
            employee_id=payload.employee_id,
            expense_date=payload.expense_date,
            expense_type=payload.expense_type,
            hours_worked=payload.hours_worked,
            hourly_cost=payload.hourly_cost,
            amount=amount,
            description=payload.description,
            project_id=payload.project_id,
        )
        db.add(expense)
        db.commit()
        db.refresh(expense)
        return expense

    @staticmethod
    def get_hourly_expense(db: Session, expense_id: int) -> HourlyExpense | None:
        """Get hourly expense by ID"""
        return db.query(HourlyExpense).filter(HourlyExpense.id == expense_id).first()

    @staticmethod
    def list_hourly_expenses(
        db: Session,
        employee_id: int | None = None,
        project_id: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[HourlyExpense], int]:
        """List hourly expenses"""
        query = db.query(HourlyExpense)
        
        if employee_id:
            query = query.filter(HourlyExpense.employee_id == employee_id)
        if project_id:
            query = query.filter(HourlyExpense.project_id == project_id)
        if date_from:
            query = query.filter(HourlyExpense.expense_date >= date_from)
        if date_to:
            query = query.filter(HourlyExpense.expense_date <= date_to)
        
        total = query.count()
        query = query.order_by(HourlyExpense.expense_date.desc()).offset((page - 1) * limit).limit(limit)
        return query.all(), total

    # ===== PROJECT EXPENSE =====

    @staticmethod
    def create_project_expense(db: Session, payload: CreateProjectExpense) -> ProjectExpense:
        """Create project expense record"""
        expense = ProjectExpense(
            project_id=payload.project_id,
            expense_date=payload.expense_date,
            expense_type=payload.expense_type,
            amount=payload.amount,
            description=payload.description,
            vendor=payload.vendor,
        )
        db.add(expense)
        db.commit()
        db.refresh(expense)
        return expense

    @staticmethod
    def get_project_expense(db: Session, expense_id: int) -> ProjectExpense | None:
        """Get project expense by ID"""
        return db.query(ProjectExpense).filter(ProjectExpense.id == expense_id).first()

    @staticmethod
    def list_project_expenses(
        db: Session,
        project_id: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[ProjectExpense], int]:
        """List project expenses"""
        query = db.query(ProjectExpense)
        
        if project_id:
            query = query.filter(ProjectExpense.project_id == project_id)
        if date_from:
            query = query.filter(ProjectExpense.expense_date >= date_from)
        if date_to:
            query = query.filter(ProjectExpense.expense_date <= date_to)
        
        total = query.count()
        query = query.order_by(ProjectExpense.expense_date.desc()).offset((page - 1) * limit).limit(limit)
        return query.all(), total

    # ===== DAILY PROFIT =====

    @staticmethod
    def get_daily_profit(db: Session, profit_date: date) -> DailyProfit | None:
        """Get or create daily profit summary"""
        profit = db.query(DailyProfit).filter(DailyProfit.profit_date == profit_date).first()
        
        if not profit:
            # Calculate on the fly
            hourly_income = db.query(func.sum(HourlyIncome.amount)).filter(
                HourlyIncome.income_date == profit_date
            ).scalar() or 0.0
            project_income = db.query(func.sum(ProjectIncome.amount)).filter(
                ProjectIncome.income_date == profit_date
            ).scalar() or 0.0
            hourly_expense = db.query(func.sum(HourlyExpense.amount)).filter(
                HourlyExpense.expense_date == profit_date
            ).scalar() or 0.0
            project_expense = db.query(func.sum(ProjectExpense.amount)).filter(
                ProjectExpense.expense_date == profit_date
            ).scalar() or 0.0
            
            total_income = hourly_income + project_income
            total_expense = hourly_expense + project_expense
            total_profit = total_income - total_expense
            profit_margin = (total_profit / total_income * 100) if total_income > 0 else 0.0
            
            active_hours = db.query(func.sum(HourlyIncome.hours_billed)).filter(
                HourlyIncome.income_date == profit_date
            ).scalar() or 0.0
            
            profit = DailyProfit(
                profit_date=profit_date,
                total_income=total_income,
                total_expense=total_expense,
                total_profit=total_profit,
                profit_margin=profit_margin,
                active_hours=active_hours,
            )
            db.add(profit)
            db.commit()
            db.refresh(profit)
        
        return profit

    @staticmethod
    def get_daily_profits(
        db: Session,
        date_from: date,
        date_to: date,
    ) -> list[DailyProfit]:
        """Get daily profits for date range"""
        # Get existing DailyProfit records
        existing = db.query(DailyProfit).filter(
            and_(
                DailyProfit.profit_date >= date_from,
                DailyProfit.profit_date <= date_to,
            )
        ).all()
        
        existing_dates = {p.profit_date for p in existing}
        results = list(existing)
        
        # For missing dates, calculate on the fly
        current = date_from
        while current <= date_to:
            if current not in existing_dates:
                # Calculate and add to existing list
                hourly_income = db.query(func.sum(HourlyIncome.amount)).filter(
                    HourlyIncome.income_date == current
                ).scalar() or 0.0
                project_income = db.query(func.sum(ProjectIncome.amount)).filter(
                    ProjectIncome.income_date == current
                ).scalar() or 0.0
                hourly_expense = db.query(func.sum(HourlyExpense.amount)).filter(
                    HourlyExpense.expense_date == current
                ).scalar() or 0.0
                project_expense = db.query(func.sum(ProjectExpense.amount)).filter(
                    ProjectExpense.expense_date == current
                ).scalar() or 0.0
                
                total_income = hourly_income + project_income
                total_expense = hourly_expense + project_expense
                total_profit = total_income - total_expense
                profit_margin = (total_profit / total_income * 100) if total_income > 0 else 0.0
                
                active_hours = db.query(func.sum(HourlyIncome.hours_billed)).filter(
                    HourlyIncome.income_date == current
                ).scalar() or 0.0
                
                if total_income > 0 or total_expense > 0:  # Only create if there's activity
                    profit = DailyProfit(
                        profit_date=current,
                        total_income=total_income,
                        total_expense=total_expense,
                        total_profit=total_profit,
                        profit_margin=profit_margin,
                        active_hours=active_hours,
                    )
                    db.add(profit)
                    db.flush()  # Flush to get id/timestamps
                    results.append(profit)
            
            current += timedelta(days=1)
        
        return sorted(results, key=lambda x: x.profit_date, reverse=True)

    # ===== PROJECT PROFIT =====

    @staticmethod
    def get_project_profit(db: Session, project_id: int) -> ProjectProfit | None:
        """Get or create project profit summary"""
        profit = db.query(ProjectProfit).filter(ProjectProfit.project_id == project_id).first()
        
        if not profit:
            # Calculate on the fly
            hourly_income = db.query(func.sum(HourlyIncome.amount)).filter(
                HourlyIncome.project_id == project_id
            ).scalar() or 0.0
            project_income = db.query(func.sum(ProjectIncome.amount)).filter(
                ProjectIncome.project_id == project_id
            ).scalar() or 0.0
            hourly_expense = db.query(func.sum(HourlyExpense.amount)).filter(
                HourlyExpense.project_id == project_id
            ).scalar() or 0.0
            project_expense = db.query(func.sum(ProjectExpense.amount)).filter(
                ProjectExpense.project_id == project_id
            ).scalar() or 0.0
            
            total_income = hourly_income + project_income
            total_expense = hourly_expense + project_expense
            total_profit = total_income - total_expense
            profit_margin = (total_profit / total_income * 100) if total_income > 0 else 0.0
            
            hours_billed = db.query(func.sum(HourlyIncome.hours_billed)).filter(
                HourlyIncome.project_id == project_id
            ).scalar() or 0.0
            
            # Break-even: income needed to cover expenses
            break_even_point = None
            if hours_billed > 0:
                avg_rate = total_income / hours_billed if total_income > 0 else 0
                if avg_rate > 0:
                    hours_to_break_even = total_expense / avg_rate
                    break_even_point = hours_to_break_even
            
            profit = ProjectProfit(
                project_id=project_id,
                total_income=total_income,
                total_expense=total_expense,
                total_profit=total_profit,
                profit_margin=profit_margin,
                hours_billed=hours_billed,
                break_even_point=break_even_point,
            )
            db.add(profit)
            db.commit()
            db.refresh(profit)
        
        return profit

    # ===== ANALYTICS =====

    @staticmethod
    def get_live_profit_summary(db: Session, days: int = 30) -> dict:
        """Get live profit summary for last N days"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days - 1)
        
        daily_profits = FIIOService.get_daily_profits(db, start_date, end_date)
        
        total_income = sum(p.total_income for p in daily_profits)
        total_expense = sum(p.total_expense for p in daily_profits)
        total_profit = sum(p.total_profit for p in daily_profits)
        avg_profit_margin = (total_profit / total_income * 100) if total_income > 0 else 0.0
        total_hours = sum(p.active_hours for p in daily_profits)
        
        best_day = max(daily_profits, key=lambda x: x.total_profit) if daily_profits else None
        worst_day = min(daily_profits, key=lambda x: x.total_profit) if daily_profits else None
        
        return {
            "period_days": days,
            "total_income": total_income,
            "total_expense": total_expense,
            "total_profit": total_profit,
            "avg_profit_margin": round(avg_profit_margin, 2),
            "total_hours_billed": total_hours,
            "avg_daily_profit": total_profit / len(daily_profits) if daily_profits else 0,
            "best_profit_day": best_day.profit_date if best_day else None,
            "worst_profit_day": worst_day.profit_date if worst_day else None,
        }

    @staticmethod
    def get_intelligence(db: Session, days: int = 30) -> dict:
        """
        Auto-aggregate financial intelligence across ALL company modules.
        Tracks income (invoices + payments + fiio-incomes), expenses (finance expenses
        + fiio-expenses), hourly earnings from operations, and earning potential.
        """
        today = date.today()
        period_start = today - timedelta(days=days - 1)

        # ── INCOME SOURCES ──────────────────────────────────────────────────
        # 1. Payments received (actual cash in)
        payments_total = db.query(func.sum(Payment.amount)).filter(
            Payment.payment_date >= period_start
        ).scalar() or 0.0

        # 2. Invoice totals (billed, including unpaid)
        invoices_total = db.query(func.sum(Invoice.total)).filter(
            Invoice.issued_date >= period_start
        ).scalar() or 0.0

        paid_invoices = db.query(func.sum(Invoice.total)).filter(
            Invoice.issued_date >= period_start,
            Invoice.status == "paid",
        ).scalar() or 0.0

        unpaid_invoices = invoices_total - paid_invoices

        # 3. FIIO manual income entries
        fiio_hourly_income = db.query(func.sum(HourlyIncome.amount)).filter(
            HourlyIncome.income_date >= period_start
        ).scalar() or 0.0
        fiio_project_income = db.query(func.sum(ProjectIncome.amount)).filter(
            ProjectIncome.income_date >= period_start
        ).scalar() or 0.0

        total_income = payments_total + fiio_hourly_income + fiio_project_income

        # ── EXPENSE SOURCES ──────────────────────────────────────────────────
        # 1. Finance module expenses
        finance_expenses = db.query(func.sum(Expense.amount)).filter(
            Expense.expense_date >= period_start
        ).scalar() or 0.0

        # 2. FIIO manual expenses
        fiio_hourly_expense = db.query(func.sum(HourlyExpense.amount)).filter(
            HourlyExpense.expense_date >= period_start
        ).scalar() or 0.0
        fiio_project_expense = db.query(func.sum(ProjectExpense.amount)).filter(
            ProjectExpense.expense_date >= period_start
        ).scalar() or 0.0

        total_expense = finance_expenses + fiio_hourly_expense + fiio_project_expense

        # ── PROFIT ────────────────────────────────────────────────────────────
        net_profit = total_income - total_expense
        profit_margin = round((net_profit / total_income * 100), 2) if total_income > 0 else 0.0

        # ── HOURLY EARNINGS ──────────────────────────────────────────────────
        # Hours billed via FIIO
        fiio_hours_billed = db.query(func.sum(HourlyIncome.hours_billed)).filter(
            HourlyIncome.income_date >= period_start
        ).scalar() or 0.0

        # Hours worked via Operations activities
        ops_hours_worked = db.query(func.sum(Activity.hours_spent)).filter(
            Activity.activity_date >= period_start
        ).scalar() or 0.0

        # Hours worked via Attendance
        attendance_hours = db.query(func.sum(Attendance.worked_hours)).filter(
            Attendance.attendance_date >= period_start,
            Attendance.worked_hours.isnot(None),
        ).scalar() or 0.0

        # Effective hourly earning rate (income per billed hour)
        effective_hourly_rate = round(total_income / fiio_hours_billed, 2) if fiio_hours_billed > 0 else 0.0

        # ── EARNING POTENTIAL ────────────────────────────────────────────────
        # Active billable employees
        active_employees = db.query(func.count(Employee.id)).filter(
            Employee.status == "active",
            Employee.is_billable == True,  # noqa: E712
        ).scalar() or 0

        # Average hourly rate across billable employees
        avg_employee_rate = db.query(func.avg(Employee.hourly_rate)).filter(
            Employee.status == "active",
            Employee.is_billable == True,  # noqa: E712
            Employee.hourly_rate.isnot(None),
        ).scalar() or 0.0

        # Standard working hours: 8h/day × working days in period
        working_days = sum(
            1 for i in range(days)
            if (period_start + timedelta(days=i)).weekday() < 5
        )
        capacity_hours = active_employees * working_days * 8

        # Potential earnings if all capacity was billed at avg rate
        potential_earnings = round(capacity_hours * avg_employee_rate, 2)

        # Utilization rate: billed hours vs total worked hours
        utilization_rate = round((fiio_hours_billed / ops_hours_worked * 100), 2) if ops_hours_worked > 0 else 0.0

        # Unrealized potential: what's left on the table
        unrealized_potential = max(0.0, potential_earnings - total_income)

        # ── INCOME BREAKDOWN BY SOURCE ──────────────────────────────────────
        income_breakdown = [
            {"source": "Payments Received", "amount": round(payments_total, 2), "type": "cash_in"},
            {"source": "Hourly Billing (FIIO)", "amount": round(fiio_hourly_income, 2), "type": "hourly"},
            {"source": "Project Revenue (FIIO)", "amount": round(fiio_project_income, 2), "type": "project"},
        ]

        # ── EXPENSE BREAKDOWN BY SOURCE ──────────────────────────────────────
        expense_breakdown = [
            {"source": "Finance Expenses", "amount": round(finance_expenses, 2), "type": "operational"},
            {"source": "Hourly Costs (FIIO)", "amount": round(fiio_hourly_expense, 2), "type": "labor"},
            {"source": "Project Costs (FIIO)", "amount": round(fiio_project_expense, 2), "type": "project"},
        ]

        # ── EXPENSE BY CATEGORY (Finance module) ────────────────────────────
        expense_by_category = []
        cats = db.query(
            Expense.category,
            func.sum(Expense.amount).label("total"),
        ).filter(
            Expense.expense_date >= period_start
        ).group_by(Expense.category).all()
        for cat in cats:
            expense_by_category.append({"category": cat.category, "amount": round(cat.total, 2)})

        # ── DEPARTMENT EARNINGS ──────────────────────────────────────────────
        dept_earnings = []
        dept_rows = db.query(
            Employee.department,
            func.sum(HourlyIncome.amount).label("income"),
            func.sum(HourlyIncome.hours_billed).label("hours"),
        ).join(HourlyIncome, HourlyIncome.employee_id == Employee.id).filter(
            HourlyIncome.income_date >= period_start,
            Employee.department.isnot(None),
        ).group_by(Employee.department).all()
        for row in dept_rows:
            dept_earnings.append({
                "department": row.department,
                "income": round(row.income or 0.0, 2),
                "hours": round(row.hours or 0.0, 2),
                "hourly_rate": round((row.income / row.hours), 2) if row.hours else 0.0,
            })

        return {
            "period_days": days,
            "period_start": str(period_start),
            "period_end": str(today),

            # Overall financial summary
            "total_income": round(total_income, 2),
            "total_expense": round(total_expense, 2),
            "net_profit": round(net_profit, 2),
            "profit_margin": profit_margin,

            # Invoice status
            "invoices_billed": round(invoices_total, 2),
            "invoices_paid": round(paid_invoices, 2),
            "invoices_unpaid": round(unpaid_invoices, 2),

            # Hourly intelligence
            "hours_billed": round(fiio_hours_billed, 2),
            "hours_worked_ops": round(ops_hours_worked, 2),
            "hours_attendance": round(attendance_hours, 2),
            "effective_hourly_rate": effective_hourly_rate,

            # Earning potential
            "active_billable_employees": active_employees,
            "avg_employee_hourly_rate": round(avg_employee_rate, 2),
            "capacity_hours": round(capacity_hours, 2),
            "potential_earnings": potential_earnings,
            "utilization_rate": utilization_rate,
            "unrealized_potential": round(unrealized_potential, 2),

            # Breakdowns
            "income_breakdown": income_breakdown,
            "expense_breakdown": expense_breakdown,
            "expense_by_category": expense_by_category,
            "department_earnings": dept_earnings,
        }
