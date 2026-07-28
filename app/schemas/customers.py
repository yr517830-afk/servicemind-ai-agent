from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CustomerResponse(BaseModel):
    """客户详情响应。"""

    model_config = ConfigDict(from_attributes=True)

    customer_id: int = Field(
        validation_alias="id",
        ge=1,
        description="客户唯一编号。",
        examples=[1],
    )
    name: str = Field(
        description="客户姓名。",
        examples=["小王"],
    )
    email: str = Field(
        description="客户电子邮箱。",
        examples=["xiaowang@example.com"],
    )
    level: str = Field(
        description="客户等级。",
        examples=["VIP"],
    )
    is_vip: bool = Field(
        description="客户是否为 VIP。",
        examples=[True],
    )
    created_at: datetime = Field(
        description="客户创建时间。",
    )