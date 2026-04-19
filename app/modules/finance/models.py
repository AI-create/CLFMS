from datetime import date

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String, func

from app.core.database import Base


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)

    amount = Column(Float, nullable=False, default=0.0)
    category = Column(String, nullable=False)
    description = Column(String, nullable=True)
    expense_date = Column(Date, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
