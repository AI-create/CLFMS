"""Research Management Models"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class ResearchType(str, enum.Enum):
    """Type of research project"""
    CLIENT_SPONSORED = "client_sponsored"
    INTERNAL_RND = "internal_rnd"
    COLLABORATIVE = "collaborative"


class ExperimentStatus(str, enum.Enum):
    """Status of an experiment"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    FAILED = "failed"
    ARCHIVED = "archived"


class ResearchProject(Base):
    """Research project entity"""
    __tablename__ = "research_projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    research_type = Column(Enum(ResearchType), default=ResearchType.INTERNAL_RND, index=True)
    
    # Link to client if sponsored research
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True, index=True)
    
    # Link to project if part of a deliverable
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)
    
    # Objectives and scope
    objectives = Column(Text, nullable=True)
    scope = Column(Text, nullable=True)
    methodology = Column(Text, nullable=True)
    
    # Status and timeline
    status = Column(String(50), default="active", index=True)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    
    # Budget and resources
    budget_allocated = Column(Integer, nullable=True)  # In cents/paise
    budget_spent = Column(Integer, default=0)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(255), nullable=True)
    
    # Relationships
    experiments = relationship("Experiment", back_populates="research_project", cascade="all, delete-orphan")
    logs = relationship("ResearchLog", back_populates="research_project", cascade="all, delete-orphan")
    assets = relationship("ResearchAsset", back_populates="research_project", cascade="all, delete-orphan")


class Experiment(Base):
    """Individual experiment within a research project"""
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True, index=True)
    research_project_id = Column(Integer, ForeignKey("research_projects.id"), nullable=False, index=True)
    
    # Basic info
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Experiment details
    objective = Column(Text, nullable=True)
    hypothesis = Column(Text, nullable=True)
    methodology = Column(Text, nullable=True)
    
    # Materials and methods
    materials_used = Column(Text, nullable=True)  # JSON or text
    equipment = Column(Text, nullable=True)
    
    # Results
    observations = Column(Text, nullable=True)
    results = Column(Text, nullable=True)
    conclusions = Column(Text, nullable=True)
    
    # Status and tracking
    status = Column(Enum(ExperimentStatus), default=ExperimentStatus.PLANNED, index=True)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    
    # Reproducibility and IP
    is_reproducible = Column(Boolean, default=False)
    has_ip_potential = Column(Boolean, default=False)
    ip_notes = Column(Text, nullable=True)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    conducted_by = Column(String(255), nullable=True)
    
    # Relationships
    research_project = relationship("ResearchProject", back_populates="experiments")
    logs = relationship("ResearchLog", back_populates="experiment", cascade="all, delete-orphan")


class ResearchLog(Base):
    """Daily lab notes and timestamped entries"""
    __tablename__ = "research_logs"

    id = Column(Integer, primary_key=True, index=True)
    research_project_id = Column(Integer, ForeignKey("research_projects.id"), nullable=False, index=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id"), nullable=False, index=True)
    
    # Log content
    title = Column(String(255), nullable=True)
    notes = Column(Text, nullable=False)
    
    # Observations
    observations = Column(Text, nullable=True)
    
    # Metadata
    recorded_by = Column(String(255), nullable=True)
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Version tracking
    version = Column(Integer, default=1)
    is_latest = Column(Boolean, default=True, index=True)
    
    # Relationships
    research_project = relationship("ResearchProject", back_populates="logs")
    experiment = relationship("Experiment", back_populates="logs")
    attachments = relationship("ResearchAsset", back_populates="log", cascade="all, delete-orphan")


class ResearchAsset(Base):
    """Data files, images, results attached to research"""
    __tablename__ = "research_assets"

    id = Column(Integer, primary_key=True, index=True)
    research_project_id = Column(Integer, ForeignKey("research_projects.id"), nullable=False, index=True)
    log_id = Column(Integer, ForeignKey("research_logs.id"), nullable=True, index=True)
    
    # File info
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=True)  # image, dataset, report, etc.
    file_size = Column(Integer, nullable=True)
    
    # Metadata
    description = Column(Text, nullable=True)
    uploaded_by = Column(String(255), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    research_project = relationship("ResearchProject", back_populates="assets")
    log = relationship("ResearchLog", back_populates="attachments")
