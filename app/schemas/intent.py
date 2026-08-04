from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class IntentType(StrEnum):
    """客服消息意图类型。"""

    ORDER_STATUS = "order_status"
    REFUND = "refund"
    LOGISTICS = "logistics"
    PAYMENT = "payment"
    ACCOUNT_SECURITY = "account_security"
    COMPLAINT = "complaint"
    OTHER = "other"


class RiskLevel(StrEnum):
    """客服消息风险等级。"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"


class IntentExtraction(BaseModel):
    """从客户消息中提取的结构化信息。"""

    model_config = ConfigDict(extra="forbid")

    intent: IntentType = Field(
        description="客户消息的主要意图。",
    )
    order_number: str | None = Field(
        description="消息中的订单号；没有订单号时返回 null。",
    )
    risk: RiskLevel = Field(
        description="消息的风险等级。",
    )
    confidence_reason: str = Field(
        description="说明为什么做出该意图和风险判断。",
    )