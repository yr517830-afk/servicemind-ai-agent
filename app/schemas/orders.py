from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class OrderResponse(BaseModel):
    """订单详情响应。"""

    model_config = ConfigDict(from_attributes=True)

    order_id: int = Field(
        validation_alias="id",
        ge=1,
        description="订单数据库编号。",
        examples=[1],
    )
    order_number: str = Field(
        description="面向业务的订单编号。",
        examples=["SM-20260727-001"],
    )
    customer_id: int = Field(
        ge=1,
        description="订单所属客户编号。",
        examples=[1],
    )
    status: str = Field(
        description="订单当前状态。",
        examples=["paid"],
    )
    total_amount: Decimal = Field(
        ge=0,
        description="订单总金额，使用十进制定点数。",
        examples=["299.00"],
    )
    created_at: datetime = Field(
        description="订单创建时间。",
    )