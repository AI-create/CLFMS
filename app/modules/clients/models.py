from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, func

from app.core.database import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False, index=True)

    gstin = Column(String, nullable=True, index=True)
    state = Column(String, nullable=True, index=True)
    address = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
