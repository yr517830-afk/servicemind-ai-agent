from pydantic import BaseModel,Field

from ticket_core.models import IssueType

class TicketCreate(BaseModel):
    """创建工单时由客户端提交的数据。"""

    customer_name: str = Field(
        min_length=1,
        max_length=100,
        examples=["小王"],
    )
    issue_type: IssueType
    message: str =Field(
        min_length=1,
        max_length=1000,
        examples=["我的订单什么时候送到？"],
    )
    wait_minutes: int = Field(
        default=0,
        ge=0,
        examples=[15],
    )
    is_vip: bool = Field(
        default=False,
        examples=[True],
    )

class TicketResponse(TicketCreate):
    """工单创建成功后返回的数据。"""

    ticket_id: int =Field(ge=1)
    status: str =Field(examples=["received"])