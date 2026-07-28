from sqlalchemy.orm import Session

from app.core.exceptions import (
    CustomerNotFoundError,
    OrderNotFoundError,
    TicketNotFoundError,
)
from app.models import Customer, Ticket
from app.repositories.customer_repository import get_customer_by_id
from app.repositories.order_repository import get_order_for_customer
from app.repositories.ticket_repository import (
    add_ticket,
    get_ticket_by_id,
    list_tickets,
)
from app.schemas.tickets import TicketCreate, TicketUpdate
from ticket_core.exceptions import InvalidTicketError
from ticket_core.models import (
    CustomerProfile,
    IssueType,
    Priority,
    TicketDecision,
    TicketInput,
)
from ticket_core.rules import decide_ticket
from ticket_core.validators import validate_ticket_input


def _make_decision(
    *,
    customer: Customer,
    issue_type: IssueType,
    message: str,
    wait_minutes: int,
) -> TicketDecision:
    """调用第 1 周校验器和规则引擎生成工单决策。"""
    ticket_input = TicketInput(
        customer_name=customer.name,
        issue_type=issue_type,
        message=message,
        wait_minutes=wait_minutes,
    )
    validate_ticket_input(ticket_input)

    customer_profile = CustomerProfile(
        customer_id=customer.id,
        name=customer.name,
        level=customer.level,
        is_vip=customer.is_vip,
    )

    return decide_ticket(
        ticket_input,
        customer_profile,
    )


def create_ticket(
    session: Session,
    payload: TicketCreate,
) -> Ticket:
    """校验客户和订单，执行规则，再保存新工单。"""
    customer = get_customer_by_id(
        session,
        payload.customer_id,
    )
    if customer is None:
        raise CustomerNotFoundError(payload.customer_id)

    if payload.order_id is not None:
        order = get_order_for_customer(
            session,
            payload.order_id,
            payload.customer_id,
        )
        if order is None:
            raise OrderNotFoundError(
                payload.order_id,
                payload.customer_id,
            )

    decision = _make_decision(
        customer=customer,
        issue_type=payload.issue_type,
        message=payload.message,
        wait_minutes=payload.wait_minutes,
    )

    database_ticket = Ticket(
        customer_id=payload.customer_id,
        order_id=payload.order_id,
        issue_type=payload.issue_type.value,
        message=payload.message,
        wait_minutes=payload.wait_minutes,
        priority=decision.priority.value,
        assigned_team=decision.assigned_team,
        sla_minutes=decision.sla_minutes,
        reason=decision.reason,
        status="received",
    )

    try:
        saved_ticket = add_ticket(
            session,
            database_ticket,
        )
        session.commit()
        session.refresh(saved_ticket)
    except Exception:
        session.rollback()
        raise

    return saved_ticket


def get_ticket(
    session: Session,
    ticket_id: int,
) -> Ticket:
    """查询一张工单，不存在时抛出异常。"""
    ticket = get_ticket_by_id(
        session,
        ticket_id,
    )
    if ticket is None:
        raise TicketNotFoundError(ticket_id)

    return ticket


def get_ticket_page(
    session: Session,
    *,
    page: int,
    page_size: int,
    status: str | None = None,
    priority: Priority | None = None,
    issue_type: IssueType | None = None,
) -> tuple[list[Ticket], int]:
    """查询一页工单及总记录数。"""
    return list_tickets(
        session,
        page=page,
        page_size=page_size,
        status=status,
        priority=priority,
        issue_type=issue_type,
    )


def update_ticket(
    session: Session,
    ticket_id: int,
    payload: TicketUpdate,
) -> Ticket:
    """部分更新工单，必要时重新执行规则。"""
    ticket = get_ticket(
        session,
        ticket_id,
    )
    changes = payload.model_dump(exclude_unset=True)

    if not changes:
        raise InvalidTicketError(
            "至少需要提供一个要更新的字段。",
        )

    null_fields = [
        field_name
        for field_name, value in changes.items()
        if value is None
    ]
    if null_fields:
        raise InvalidTicketError(
            f"字段不能为 null：{', '.join(null_fields)}。",
        )

    should_recalculate = bool(
        {"message", "wait_minutes"} & changes.keys(),
    )

    for field_name, value in changes.items():
        setattr(ticket, field_name, value)

    if should_recalculate:
        customer = get_customer_by_id(
            session,
            ticket.customer_id,
        )
        if customer is None:
            raise CustomerNotFoundError(ticket.customer_id)

        decision = _make_decision(
            customer=customer,
            issue_type=IssueType(ticket.issue_type),
            message=ticket.message,
            wait_minutes=ticket.wait_minutes,
        )
        ticket.priority = decision.priority.value
        ticket.assigned_team = decision.assigned_team
        ticket.sla_minutes = decision.sla_minutes
        ticket.reason = decision.reason

    try:
        session.commit()
        session.refresh(ticket)
    except Exception:
        session.rollback()
        raise

    return ticket
