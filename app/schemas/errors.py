from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """统一错误详情。"""

    code: str = Field(
        description="稳定的机器可读错误码。",
        examples=["CUSTOMER_NOT_FOUND"],
    )
    message: str = Field(
        description="供用户或开发者阅读的错误说明。",
        examples=["客户 999 不存在。"],
    )
    resource: str = Field(
        description="发生错误的资源类型。",
        examples=["customer"],
    )
    resource_id: int = Field(
        ge=1,
        description="未找到的资源编号。",
        examples=[999],
    )


class ErrorResponse(BaseModel):
    """统一 API 错误响应。"""

    error: ErrorDetail