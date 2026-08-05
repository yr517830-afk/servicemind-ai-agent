from fastapi import FastAPI

from app.api.routes.chat import router as chat_router
from app.api.routes.customers import router as customers_router
from app.api.routes.health import router as health_router
from app.api.routes.orders import router as orders_router
from app.api.routes.tickets import router as tickets_router
from app.core.config import settings
from app.core.exception_handlers import register_exception_handlers


app = FastAPI(
    title=settings.app_name,
    description="智能工单系统 HTTP API",
    version=settings.app_version,
    debug=settings.debug,
)

register_exception_handlers(app)

app.include_router(health_router)
app.include_router(customers_router)
app.include_router(orders_router)
app.include_router(tickets_router)
app.include_router(chat_router)