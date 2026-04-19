"""FI-IO (Financial Inflow-Outflow) Models"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Boolean, Text, Enum as SQLEnum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class IncomeType(str, enum.Enum):
    """Types of income"""
    project_revenue = "project_revenue"
    hourly_billing = "hourly_billing"
    retainer = "retainer"
    service_charge = "service_charge"
    other = "other"


class ExpenseType(str, enum.Enum):
    """Types of expenses"""
    salary = "salary"
    materials = "materials"
    tools = "tools"
    software = "software"
    infrastructure = "infrastructure"
    marketing = "marketing"
    utilities = "utilities"
    other = "other"


class TransactionStatus(str, enum.Enum):
    """Status of a transaction"""
    pending = "pending"
    confirmed = "confirmed"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class HourlyIncome(Base):
    """Hourly income tracking - linked to activities"""
    __tablename__ = "hourly_incomes"

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=True)  # Can link to activity
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    income_date = Column(Date, nullable=False, index=True)
    income_type = Column(SQLEnum(IncomeType), default=IncomeType.hourly_billing)
    hours_billed = Column(Float, nullable=False)  # Hours worked
    hourly_rate = Column(Float, nullable=False)  # Rate applied
    amount = Column(Float, nullable=False)  # hours_billed × hourly_rate
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.pending)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)  # Linked invoice
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    __table_args__ = (UniqueConstraint('activity_id', name='uq_hourly_income_activity'),)


class ProjectIncome(Base):
    """Project-level income tracking"""
    __tablename__ = "project_incomes"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    income_date = Column(Date, nullable=False, index=True)
    income_type = Column(SQLEnum(IncomeType), default=IncomeType.project_revenue)
    amount = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.pending)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class HourlyExpense(Base):
    """Hourly expense tracking - cost per hour worked"""
    __tablename__ = "hourly_expenses"

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, index=True)
    expense_date = Column(Date, nullable=False, index=True)
    expense_type = Column(SQLEnum(ExpenseType), default=ExpenseType.salary)
    hours_worked = Column(Float, nullable=False)  # Hours in this transaction
    hourly_cost = Column(Float, nullable=False)  # Cost per hour
    amount = Column(Float, nullable=False)  # hours_worked × hourly_cost
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.pending)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)  # Can allocate to project
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ProjectExpense(Base):
    """Project-level expense tracking"""
    __tablename__ = "project_expenses"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    expense_date = Column(Date, nullable=False, index=True)
    expense_type = Column(SQLEnum(ExpenseType), default=ExpenseType.materials)
    amount = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    vendor = Column(String, nullable=True)
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.pending)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DailyProfit(Base):
    """Daily profit summary - cached for quick reporting"""
    __tablename__ = "daily_profits"

    id = Column(Integer, primary_key=True, index=True)
    profit_date = Column(Date, nullable=False, unique=True, index=True)
    total_income = Column(Float, default=0.0)  # All income for the day
    total_expense = Column(Float, default=0.0)  # All expenses for the day
    total_profit = Column(Float, default=0.0)  # income - expense
    profit_margin = Column(Float, default=0.0)  # (profit / income) * 100 if income > 0
    active_hours = Column(Float, default=0.0)  # Total billable hours
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ProjectProfit(Base):
    """Project profit summary for profitability analysis"""
    __tablename__ = "project_profits"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, unique=True, index=True)
    total_income = Column(Float, default=0.0)
    total_expense = Column(Float, default=0.0)
    total_profit = Column(Float, default=0.0)
    profit_margin = Column(Float, default=0.0)  # (profit / income) * 100 if income > 0
    hours_billed = Column(Float, default=0.0)
    break_even_point = Column(Float, nullable=True)  # Revenue needed to break even
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
