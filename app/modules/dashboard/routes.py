from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import api_success
from app.core.security import require_roles
from app.modules.dashboard.schemas import KpiOut
from app.modules.dashboard.services import get_kpis


router = APIRouter(tags=["Dashboard"])


@router.get("/dashboard/kpis")
def kpis(
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance", "sales", "operations", "pm", "project_manager"])),
):
    return api_success(KpiOut(**get_kpis(db)))

