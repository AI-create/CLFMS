from datetime import date

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String, func

from app.core.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True)

    amount = Column(Float, nullable=False, default=0.0)
    payment_date = Column(Date, nullable=True)
    method = Column(String, nullable=True)
    reference = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
