from fastapi import APIRouter

from app.schemas.tickets import TicketCreate, TicketResponse

from app.services.ticket_service import process_ticket

router = APIRouter(
    prefix="/tickets",
    tags=["工单"],
)

@router.post(
    "",
    response_model=TicketResponse,
    status_code=201,
)
def create_ticket(ticket: TicketCreate) -> TicketResponse:
    """接收一张新工单并交给服务层处理。"""
    return process_ticket(ticket)