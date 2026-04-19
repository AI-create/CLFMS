from datetime import date

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String, func

from app.core.database import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="RESTRICT"), nullable=False, index=True)

    invoice_number = Column(String, nullable=False, unique=True, index=True)

    subtotal = Column(Float, nullable=False, default=0.0)
    cgst = Column(Float, nullable=False, default=0.0)
    sgst = Column(Float, nullable=False, default=0.0)
    igst = Column(Float, nullable=False, default=0.0)
    total = Column(Float, nullable=False, default=0.0)

    status = Column(String, nullable=False, default="draft")  # draft/sent/paid/overdue

    issued_date = Column(Date, nullable=True)
    due_date = Column(Date, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True)

    description = Column(String, nullable=False)
    quantity = Column(Float, nullable=False, default=1.0)
    rate = Column(Float, nullable=False, default=0.0)
    amount = Column(Float, nullable=False, default=0.0)
