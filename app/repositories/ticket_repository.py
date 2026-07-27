from pathlib import Path

from app.core.config import settings
from ticket_core.models import TicketDecision, TicketInput
from ticket_core.repository import list_tickets
from ticket_core.repository import save_ticket as save_ticket_to_database


def save(
    ticket: TicketInput,
    decision: TicketDecision,
) -> int:
    """保存工单并返回数据库生成的工单编号。"""
    database_path = Path(settings.database_path)

    return save_ticket_to_database(
        ticket,
        decision,
        database_path,
    )


def list_recent() -> list[dict[str, object]]:
    """查询数据库中最近保存的工单。"""
    database_path = Path(settings.database_path)
    rows = list_tickets(database_path)

    return [dict(row) for row in rows]