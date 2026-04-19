from contextlib import asynccontextmanager
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.middleware.auth import AuthMiddleware
from app.middleware.logging import RequestLoggingMiddleware

# Import models so SQLAlchemy metadata is fully populated.
from app.modules.auth import models as auth_models  # noqa: F401
from app.modules.clients import models as clients_models  # noqa: F401
from app.modules.finance import models as finance_models  # noqa: F401
from app.modules.invoices import models as invoices_models  # noqa: F401
from app.modules.payments import models as payments_models  # noqa: F401
from app.modules.projects import models as projects_models  # noqa: F401
from app.modules.tasks import models as tasks_models  # noqa: F401
from app.modules.documents import models as documents_models  # noqa: F401
from app.modules.leads import models as leads_models  # noqa: F401
from app.modules.onboarding import models as onboarding_models  # noqa: F401
from app.modules.closure import models as closure_models  # noqa: F401
from app.modules.files import models as files_models  # noqa: F401
from app.modules.activity_logs import models as activity_logs_models  # noqa: F401
from app.modules.research import models as research_models  # noqa: F401
from app.modules.operations import models as operations_models  # noqa: F401
from app.modules.fiio import models as fiio_models  # noqa: F401

from app.modules.auth.services import ensure_default_admin
from app.modules.auth.routes import router as auth_router
from app.modules.clients.routes import router as clients_router
from app.modules.projects.routes import router as projects_router
from app.modules.tasks.routes import router as tasks_router
from app.modules.invoices.routes import router as invoices_router
from app.modules.payments.routes import router as payments_router
from app.modules.finance.routes import router as finance_router
from app.modules.dashboard.routes import router as dashboard_router
from app.modules.documents.routes import router as documents_router
from app.modules.leads.routes import router as leads_router
from app.modules.onboarding.routes import router as onboarding_router
from app.modules.closure.routes import router as closure_router
from app.modules.files.routes import router as files_router
from app.modules.activity_logs.routes import router as activity_logs_router
from app.modules.research.routes import router as research_router
from app.modules.operations.routes import router as operations_router
from app.modules.fiio.routes import router as fiio_router


API_PREFIX = "/api/v1"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)

    # Seed a default admin user for local development.
    db = SessionLocal()
    try:
        ensure_default_admin(db)
    finally:
        db.close()

    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(AuthMiddleware)
app.add_middleware(RequestLoggingMiddleware)

if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/")
def health():
    return {"success": True, "message": "CLFMS API is running"}


app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(leads_router, prefix=API_PREFIX)
app.include_router(clients_router, prefix=API_PREFIX)
app.include_router(projects_router, prefix=API_PREFIX)
app.include_router(tasks_router, prefix=API_PREFIX)
app.include_router(invoices_router, prefix=API_PREFIX)
app.include_router(payments_router, prefix=API_PREFIX)
app.include_router(finance_router, prefix=API_PREFIX)
app.include_router(dashboard_router, prefix=API_PREFIX)
app.include_router(documents_router, prefix=API_PREFIX)
app.include_router(onboarding_router, prefix=API_PREFIX)
app.include_router(closure_router, prefix=API_PREFIX)
app.include_router(files_router, prefix=API_PREFIX)
app.include_router(activity_logs_router, prefix=API_PREFIX)
app.include_router(research_router, prefix=API_PREFIX)
app.include_router(operations_router, prefix=API_PREFIX)
app.include_router(fiio_router, prefix=API_PREFIX)

# Serve frontend static files
frontend_static_path = Path(__file__).parent / "static" / "frontend"
if frontend_static_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_static_path), html=True), name="frontend")
