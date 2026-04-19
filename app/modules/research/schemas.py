"""Research Management Schemas"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class ResearchAssetOut(BaseModel):
    """Research asset response schema"""
    id: int
    file_name: str
    file_path: str
    file_type: Optional[str]
    description: Optional[str]
    uploaded_by: Optional[str]
    uploaded_at: datetime

    class Config:
        from_attributes = True


class ExperimentOut(BaseModel):
    """Experiment response schema"""
    id: int
    title: str
    description: Optional[str]
    objective: Optional[str]
    hypothesis: Optional[str]
    status: str
    start_date: datetime
    end_date: Optional[datetime]
    is_reproducible: bool
    has_ip_potential: bool
    ip_notes: Optional[str]
    conducted_by: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class CreateExperiment(BaseModel):
    """Create experiment schema"""
    title: str
    description: Optional[str] = None
    objective: Optional[str] = None
    hypothesis: Optional[str] = None
    methodology: Optional[str] = None
    materials_used: Optional[str] = None
    equipment: Optional[str] = None
    status: str = "planned"
    conducted_by: Optional[str] = None


class ResearchLogOut(BaseModel):
    """Research log response schema"""
    id: int
    title: Optional[str]
    notes: str
    observations: Optional[str]
    recorded_by: Optional[str]
    recorded_at: datetime
    version: int
    is_latest: bool

    class Config:
        from_attributes = True


class CreateResearchLog(BaseModel):
    """Create research log schema"""
    title: Optional[str] = None
    notes: str
    observations: Optional[str] = None
    recorded_by: Optional[str] = None


class ResearchProjectOut(BaseModel):
    """Research project response schema"""
    id: int
    name: str
    description: Optional[str]
    research_type: str
    client_id: Optional[int]
    project_id: Optional[int]
    objectives: Optional[str]
    status: str
    start_date: datetime
    end_date: Optional[datetime]
    budget_allocated: Optional[int]
    budget_spent: int
    created_at: datetime
    created_by: Optional[str]
    experiments: List[ExperimentOut] = []
    logs: List[ResearchLogOut] = []
    assets: List[ResearchAssetOut] = []

    class Config:
        from_attributes = True


class CreateResearchProject(BaseModel):
    """Create research project schema"""
    name: str
    description: Optional[str] = None
    research_type: str = "internal_rnd"
    client_id: Optional[int] = None
    project_id: Optional[int] = None
    objectives: Optional[str] = None
    scope: Optional[str] = None
    methodology: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget_allocated: Optional[int] = None
    created_by: Optional[str] = None


class UpdateResearchProject(BaseModel):
    """Update research project schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    objectives: Optional[str] = None
    status: Optional[str] = None
    end_date: Optional[datetime] = None
    budget_spent: Optional[int] = None


class PaginatedExperiments(BaseModel):
    """Paginated experiments response"""
    data: List[ExperimentOut]
    meta: dict


class PaginatedResearchProjects(BaseModel):
    """Paginated research projects response"""
    data: List[ResearchProjectOut]
    meta: dict
