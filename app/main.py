from fastapi import FastAPI

from app.api.routes.health import router as health_router

from app.api.routes.tickets import router as tickets_router

from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    description="智能工单系统 HTTP API",
    version=settings.app_version,
    debug=settings.debug,
)

app.include_router(health_router)

app.include_router(tickets_router)
