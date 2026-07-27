from app.schemas.tickets import TicketCreate, TicketResponse


def process_ticket(ticket: TicketCreate) -> TicketResponse:
    """处理新工单并生成响应结果。"""
    return TicketResponse(
        ticket_id=1,
        status="received",
        **ticket.model_dump(),
    )