from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import api_success
from app.core.security import require_roles
from app.modules.dashboard.schemas import (
    KpiOut,
    FinancialSummaryOut,
    DailyProfitTrendOut,
    ProjectStatsOut,
)
from app.modules.dashboard.services import (
    get_kpis,
    get_financial_summary,
    get_30day_trend,
    get_top_projects,
)


router = APIRouter(tags=["Dashboard"])


@router.get("/dashboard/kpis")
def kpis(
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance", "sales", "operations", "pm", "project_manager", "researcher"])),
):
    """Get key performance indicators"""
    return api_success(KpiOut(**get_kpis(db)))


@router.get("/dashboard/financial-summary")
def financial_summary(
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance", "project_manager", "researcher"])),
):
    """Get comprehensive financial summary including income/expense breakdown"""
    summary = get_financial_summary(db)
    return api_success(FinancialSummaryOut(**summary))


@router.get("/dashboard/profit-trend")
def profit_trend(
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance", "project_manager", "researcher"])),
):
    """Get 30-day profit trend for charting"""
    trend = get_30day_trend(db)
    return api_success({
        "data": [DailyProfitTrendOut(**item).model_dump() for item in trend],
        "meta": {"days": 30, "period": "last_30_days"},
    })


@router.get("/dashboard/top-projects")
def top_projects(
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance", "project_manager", "researcher"])),
):
    """Get top performing projects by profit"""
    projects = get_top_projects(db, limit)
    return api_success({
        "data": [ProjectStatsOut(**item).model_dump() for item in projects],
        "meta": {"limit": limit, "count": len(projects)},
    })


