from datetime import date

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String, func

from app.core.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="RESTRICT"), nullable=False, index=True)

    title = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)

    status = Column(String, nullable=False, default="todo")  # todo/in_progress/done
    priority = Column(String, nullable=True)
    assigned_to = Column(Integer, nullable=True)  # user_id (auth.users.id)
    estimated_hours = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class TimeLog(Base):
    __tablename__ = "time_logs"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, nullable=True, index=True)

    hours = Column(Float, nullable=False)
    log_date = Column(Date, nullable=True)
    notes = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
