from sqlalchemy import Column, DateTime, Integer, String, func

from app.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String, nullable=False)  # invoice/project/client
    entity_id = Column(Integer, nullable=False, index=True)
    doc_type = Column(String, nullable=False)  # invoice/receipt/sow/etc
    file_path = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

