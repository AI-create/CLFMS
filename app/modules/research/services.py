"""Research Management Services"""
from sqlalchemy import func, desc, select
from sqlalchemy.orm import Session
from app.modules.research.models import (
    ResearchProject,
    Experiment,
    ResearchLog,
    ResearchAsset,
    ExperimentStatus,
)
from app.modules.research.schemas import (
    CreateResearchProject,
    CreateExperiment,
    CreateResearchLog,
    UpdateResearchProject,
)


class ResearchService:
    """Service for research management operations"""

    @staticmethod
    def create_research_project(db: Session, payload: CreateResearchProject) -> ResearchProject:
        """Create a new research project"""
        project = ResearchProject(**payload.model_dump())
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def get_research_project(db: Session, project_id: int) -> ResearchProject | None:
        """Get a research project by ID"""
        stmt = select(ResearchProject).where(ResearchProject.id == project_id)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def list_research_projects(
        db: Session,
        client_id: int | None = None,
        research_type: str | None = None,
        status: str | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[ResearchProject], int]:
        """List research projects with filters"""
        stmt = select(ResearchProject)

        if client_id:
            stmt = stmt.where(ResearchProject.client_id == client_id)
        if research_type:
            stmt = stmt.where(ResearchProject.research_type == research_type)
        if status:
            stmt = stmt.where(ResearchProject.status == status)

        total_stmt = select(func.count()).select_from(ResearchProject)
        if client_id:
            total_stmt = total_stmt.where(ResearchProject.client_id == client_id)
        if research_type:
            total_stmt = total_stmt.where(ResearchProject.research_type == research_type)
        if status:
            total_stmt = total_stmt.where(ResearchProject.status == status)

        total = db.execute(total_stmt).scalar_one()

        stmt = stmt.order_by(desc(ResearchProject.created_at)).offset((page - 1) * limit).limit(limit)
        rows = db.execute(stmt).scalars().all()
        return rows, int(total)

    @staticmethod
    def update_research_project(
        db: Session, project_id: int, payload: UpdateResearchProject
    ) -> ResearchProject | None:
        """Update a research project"""
        project = ResearchService.get_research_project(db, project_id)
        if not project:
            return None

        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(project, key, value)

        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def create_experiment(db: Session, project_id: int, payload: CreateExperiment) -> Experiment:
        """Create an experiment for a research project"""
        experiment = Experiment(research_project_id=project_id, **payload.model_dump())
        db.add(experiment)
        db.commit()
        db.refresh(experiment)
        return experiment

    @staticmethod
    def get_experiment(db: Session, experiment_id: int) -> Experiment | None:
        """Get an experiment by ID"""
        stmt = select(Experiment).where(Experiment.id == experiment_id)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def list_experiments(
        db: Session,
        project_id: int | None = None,
        status: str | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Experiment], int]:
        """List experiments with filters"""
        stmt = select(Experiment)

        if project_id:
            stmt = stmt.where(Experiment.research_project_id == project_id)
        if status:
            stmt = stmt.where(Experiment.status == status)

        total_stmt = select(func.count()).select_from(Experiment)
        if project_id:
            total_stmt = total_stmt.where(Experiment.research_project_id == project_id)
        if status:
            total_stmt = total_stmt.where(Experiment.status == status)

        total = db.execute(total_stmt).scalar_one()

        stmt = stmt.order_by(desc(Experiment.created_at)).offset((page - 1) * limit).limit(limit)
        rows = db.execute(stmt).scalars().all()
        return rows, int(total)

    @staticmethod
    def update_experiment(db: Session, experiment_id: int, payload: dict) -> Experiment | None:
        """Update an experiment"""
        experiment = ResearchService.get_experiment(db, experiment_id)
        if not experiment:
            return None

        for key, value in payload.items():
            if value is not None:
                setattr(experiment, key, value)

        db.commit()
        db.refresh(experiment)
        return experiment

    @staticmethod
    def create_research_log(
        db: Session, project_id: int, experiment_id: int, payload: CreateResearchLog
    ) -> ResearchLog:
        """Create a research log entry"""
        log = ResearchLog(
            research_project_id=project_id,
            experiment_id=experiment_id,
            **payload.model_dump()
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    @staticmethod
    def get_experiment_logs(db: Session, experiment_id: int) -> list[ResearchLog]:
        """Get all logs for an experiment"""
        stmt = select(ResearchLog).where(ResearchLog.experiment_id == experiment_id).order_by(desc(ResearchLog.recorded_at))
        return db.execute(stmt).scalars().all()

    @staticmethod
    def get_latest_log(db: Session, experiment_id: int) -> ResearchLog | None:
        """Get the latest log for an experiment"""
        stmt = (
            select(ResearchLog)
            .where(ResearchLog.experiment_id == experiment_id, ResearchLog.is_latest == True)
            .order_by(desc(ResearchLog.recorded_at))
        )
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def get_ip_potential_experiments(db: Session, project_id: int | None = None) -> list[Experiment]:
        """Get experiments with IP potential"""
        stmt = select(Experiment).where(Experiment.has_ip_potential == True)
        if project_id:
            stmt = stmt.where(Experiment.research_project_id == project_id)
        return db.execute(stmt).scalars().all()

    @staticmethod
    def get_reproducible_experiments(db: Session, project_id: int | None = None) -> list[Experiment]:
        """Get reproducible experiments"""
        stmt = select(Experiment).where(Experiment.is_reproducible == True)
        if project_id:
            stmt = stmt.where(Experiment.research_project_id == project_id)
        return db.execute(stmt).scalars().all()

    @staticmethod
    def get_project_summary(db: Session, project_id: int) -> dict:
        """Get a summary of research project activity"""
        project = ResearchService.get_research_project(db, project_id)
        if not project:
            return {}

        total_experiments = len(project.experiments)
        completed_experiments = len(
            [e for e in project.experiments if e.status == ExperimentStatus.COMPLETED]
        )
        ip_potential = len([e for e in project.experiments if e.has_ip_potential])
        reproducible = len([e for e in project.experiments if e.is_reproducible])
        total_logs = len(project.logs)

        return {
            "project_id": project.id,
            "project_name": project.name,
            "total_experiments": total_experiments,
            "completed_experiments": completed_experiments,
            "completion_rate": (completed_experiments / total_experiments * 100) if total_experiments > 0 else 0,
            "ip_potential_experiments": ip_potential,
            "reproducible_experiments": reproducible,
            "total_logs": total_logs,
            "budget_allocated": project.budget_allocated,
            "budget_spent": project.budget_spent,
            "budget_remaining": (project.budget_allocated - project.budget_spent) if project.budget_allocated else 0,
        }
