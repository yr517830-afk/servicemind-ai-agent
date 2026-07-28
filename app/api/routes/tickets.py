from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.tickets import (
    TicketCreate,
    TicketListResponse,
    TicketResponse,
    TicketStatus,
    TicketUpdate,
)
from app.services.ticket_service import (
    CustomerNotFoundError,
    OrderNotFoundError,
    TicketNotFoundError,
    create_ticket as create_ticket_service,
    get_ticket as get_ticket_service,
    get_ticket_page,
    update_ticket as update_ticket_service,
)
from ticket_core.exceptions import InvalidTicketError
from ticket_core.models import IssueType, Priority


router = APIRouter(
    prefix="/tickets",
    tags=["工单"],
)

SessionDependency = Annotated[
    Session,
    Depends(get_db),
]


@router.post(
    "",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_ticket(
    payload: TicketCreate,
    session: SessionDependency,
) -> TicketResponse:
    """创建工单并自动执行路由规则。"""
    try:
        ticket = create_ticket_service(
            session,
            payload,
        )
    except (CustomerNotFoundError, OrderNotFoundError) as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except InvalidTicketError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    return TicketResponse.model_validate(ticket)


@router.get(
    "",
    response_model=TicketListResponse,
)
def list_ticket_items(
    session: SessionDependency,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    ticket_status: Annotated[
        TicketStatus | None,
        Query(alias="status"),
    ] = None,
    priority: Priority | None = None,
    issue_type: IssueType | None = None,
) -> TicketListResponse:
    """分页查询工单，并支持状态、优先级和问题类型筛选。"""
    tickets, total = get_ticket_page(
        session,
        page=page,
        page_size=page_size,
        status=ticket_status,
        priority=priority,
        issue_type=issue_type,
    )
    pages = (
        (total + page_size - 1) // page_size
        if total
        else 0
    )

    return TicketListResponse(
        items=[
            TicketResponse.model_validate(ticket)
            for ticket in tickets
        ],
        page=page,
        page_size=page_size,
        total=total,
        pages=pages,
    )


@router.get(
    "/{ticket_id}",
    response_model=TicketResponse,
)
def get_ticket(
    ticket_id: int,
    session: SessionDependency,
) -> TicketResponse:
    """按编号查询一张工单。"""
    try:
        ticket = get_ticket_service(
            session,
            ticket_id,
        )
    except TicketNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return TicketResponse.model_validate(ticket)


@router.patch(
    "/{ticket_id}",
    response_model=TicketResponse,
)
def update_ticket(
    ticket_id: int,
    payload: TicketUpdate,
    session: SessionDependency,
) -> TicketResponse:
    """部分更新工单。"""
    try:
        ticket = update_ticket_service(
            session,
            ticket_id,
            payload,
        )
    except (TicketNotFoundError, CustomerNotFoundError) as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except InvalidTicketError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    return TicketResponse.model_validate(ticket)