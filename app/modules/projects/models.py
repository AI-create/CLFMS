from datetime import date

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Date, func

from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)

    client_id = Column(
        Integer,
        ForeignKey("clients.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)

    status = Column(String, nullable=False, default="active")
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    budget = Column(Float, nullable=True)

    # Billing configuration
    billing_type = Column(String, nullable=True)          # 'upfront' | 'in_arrears'
    billing_cycle = Column(String, nullable=True)         # 'one_time' | 'monthly' | 'quarterly' | 'yearly'
    billing_rate = Column(Float, nullable=True)           # fixed fee (upfront) or hourly rate (in_arrears)
    auto_billing_enabled = Column(Boolean, nullable=False, default=False)
    last_billed_date = Column(Date, nullable=True)
    next_billing_date = Column(Date, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
