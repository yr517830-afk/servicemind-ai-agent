from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Ticket
from ticket_core.models import IssueType, Priority


def add_ticket(
    session: Session,
    ticket: Ticket,
) -> Ticket:
    """添加工单并取得数据库生成的数据。"""
    session.add(ticket)
    session.flush()
    session.refresh(ticket)
    return ticket


def get_ticket_by_id(
    session: Session,
    ticket_id: int,
) -> Ticket | None:
    """按编号查询工单。"""
    return session.get(Ticket, ticket_id)


def list_tickets(
    session: Session,
    *,
    page: int,
    page_size: int,
    status: str | None = None,
    priority: Priority | None = None,
    issue_type: IssueType | None = None,
) -> tuple[list[Ticket], int]:
    """分页查询工单，并返回当前页数据和总数。"""
    filters = []

    if status is not None:
        filters.append(Ticket.status == status)

    if priority is not None:
        filters.append(Ticket.priority == priority.value)

    if issue_type is not None:
        filters.append(Ticket.issue_type == issue_type.value)

    count_statement = select(func.count(Ticket.id)).where(*filters)
    total = session.scalar(count_statement) or 0

    query_statement = (
        select(Ticket)
        .where(*filters)
        .order_by(
            Ticket.created_at.desc(),
            Ticket.id.desc(),
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    tickets = list(session.scalars(query_statement))

    return tickets, total
