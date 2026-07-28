from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from ticket_core.models import IssueType, Priority


TicketStatus = Literal[
    "received",
    "processing",
    "resolved",
    "closed",
]


class TicketCreate(BaseModel):
    """创建工单时由客户端提交的数据。"""

    customer_id: int = Field(
        ge=1,
        examples=[1],
    )
    order_id: int | None = Field(
        default=None,
        ge=1,
        examples=[1],
    )
    issue_type: IssueType
    message: str = Field(
        min_length=1,
        max_length=1000,
        examples=["我的订单什么时候送到？"],
    )
    wait_minutes: int = Field(
        default=0,
        ge=0,
        examples=[15],
    )


class TicketUpdate(BaseModel):
    """更新工单时允许修改的数据。"""

    message: str | None = Field(
        default=None,
        min_length=1,
        max_length=1000,
    )
    wait_minutes: int | None = Field(
        default=None,
        ge=0,
    )
    status: TicketStatus | None = None


class TicketResponse(BaseModel):
    """API 返回的工单数据。"""

    model_config = ConfigDict(from_attributes=True)

    ticket_id: int = Field(
        validation_alias="id",
        ge=1,
    )
    customer_id: int
    order_id: int | None
    issue_type: IssueType
    message: str
    wait_minutes: int
    priority: Priority
    assigned_team: str
    sla_minutes: int
    reason: str
    status: TicketStatus
    created_at: datetime


class TicketListResponse(BaseModel):
    """分页工单列表。"""

    items: list[TicketResponse]
    page: int
    page_size: int
    total: int
    pages: int