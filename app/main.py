from fastapi import FastAPI

from app.schemas import TicketCreate,TicketResponse

app = FastAPI(
    title="ServiceMind API",
    description="智能工单系统 HTTP API",
    version="0.1.0",
)

@app.get("/health", tags=["系统"])
def health_check() -> dict[str,str]:
    """检查ServiceMind API是否正常运行。"""
    return {
        "status":"ok",
        "service":"ServiceMind"
    }

@app.post(
    "/tickets",
    response_model=TicketResponse,
    status_code=201,
    tags=["工单"],
)
def create_ticket(ticket: TicketCreate) -> TicketResponse:
    """接收并返回一张经过校验的新工单。"""
    return TicketResponse(
        ticket_id=1,
        status="received",
        **ticket.model_dump(),
    )