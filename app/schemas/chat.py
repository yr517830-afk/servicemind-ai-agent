from pydantic import BaseModel, Field, field_validator


class ChatStreamRequest(BaseModel):
    """流式聊天请求。"""

    message: str = Field(
        min_length=1,
        max_length=4000,
        description="用户发送的消息。",
        examples=["请帮我查询订单物流进度。"],
    )
    demo: bool = Field(
        default=False,
        description="是否使用无需 API Key 的本地演示流。",
    )

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        message = value.strip()

        if not message:
            raise ValueError("消息不能为空。")

        return message