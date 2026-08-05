from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class FailureCode(StrEnum):
    """Day19 需要覆盖的模型故障类型。"""

    INVALID_RESPONSE = "INVALID_RESPONSE"
    MODEL_REFUSAL = "MODEL_REFUSAL"
    RATE_LIMITED = "RATE_LIMITED"
    INPUT_TOO_LONG = "INPUT_TOO_LONG"


class FallbackAction(StrEnum):
    """模型失败后的安全降级动作。"""

    USE_RULES = "use_rules"
    RETRY_LATER = "retry_later"
    SHORTEN_INPUT = "shorten_input"
    HUMAN_HANDOFF = "human_handoff"


class FailureReply(BaseModel):
    """返回给调用方的统一降级信息。"""

    model_config = ConfigDict(extra="forbid")

    code: FailureCode = Field(
        description="故障类型代码。",
    )
    message: str = Field(
        min_length=1,
        description="用户可以理解的中文提示。",
    )
    action: FallbackAction = Field(
        description="系统采用的降级动作。",
    )
    retryable: bool = Field(
        default=False,
        description="用户稍后重试是否可能成功。",
    )