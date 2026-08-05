import json
from collections.abc import Iterator

from app.clients.llm_client import (
    LLMClient,
    LLMError,
    LLMInvalidResponseError,
    LLMRateLimitError,
    LLMRefusalError,
    llm_client,
)
from app.schemas.chat import ChatStreamRequest
from app.schemas.failures import FailureCode, FailureReply
from app.services.fallback_service import fallback_service


MAX_CHAT_MESSAGE_LENGTH = 2000

CHAT_INSTRUCTIONS = """
你是 ServiceMind 智能客服助手。

请使用简洁、礼貌、清晰的中文回答客户问题。
不要虚构订单状态、退款结果或账户信息。
如果缺少必要信息，应明确告诉客户需要补充哪些内容。
""".strip()

DEMO_CHUNKS = (
    "您好，",
    "这是 ServiceMind 的流式输出演示。",
    "当前内容正在分段返回，",
    "真实模式需要配置 OpenAI API Key。",
)


def encode_sse_event(
    event: str,
    data: dict[str, object],
) -> str:
    """将事件编码为标准 SSE 文本格式。"""
    payload = json.dumps(
        data,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return f"event: {event}\ndata: {payload}\n\n"


class ChatService:
    """生成聊天 SSE 事件流。"""

    def __init__(self, client: LLMClient = llm_client) -> None:
        self.client = client

    @staticmethod
    def failure_reply_for(
        error: LLMError,
    ) -> FailureReply | None:
        """将需要降级的 LLM 异常转换为统一回复。"""

        if isinstance(error, LLMInvalidResponseError):
            return fallback_service.reply_for(
                FailureCode.INVALID_RESPONSE
            )

        if isinstance(error, LLMRefusalError):
            return fallback_service.reply_for(
                FailureCode.MODEL_REFUSAL
            )

        if isinstance(error, LLMRateLimitError):
            return fallback_service.reply_for(
                FailureCode.RATE_LIMITED
            )

        return None

    def stream(
        self,
        request: ChatStreamRequest,
    ) -> Iterator[str]:
        mode = "demo" if request.demo else "llm"

        yield encode_sse_event(
            "start",
            {
                "status": "started",
                "mode": mode,
            },
        )

        if len(request.message) > MAX_CHAT_MESSAGE_LENGTH:
            reply = fallback_service.reply_for(
                FailureCode.INPUT_TOO_LONG
            )

            yield encode_sse_event(
                "error",
                reply.model_dump(mode="json"),
            )
            return

        if request.demo:
            for chunk in DEMO_CHUNKS:
                yield encode_sse_event(
                    "delta",
                    {"text": chunk},
                )

            yield encode_sse_event(
                "done",
                {"status": "completed"},
            )
            return

        try:
            chunks = self.client.stream_text(
                request.message,
                instructions=CHAT_INSTRUCTIONS,
            )

            for chunk in chunks:
                yield encode_sse_event(
                    "delta",
                    {"text": chunk},
                )

        except LLMError as error:
            reply = self.failure_reply_for(error)

            if reply is not None:
                error_data = reply.model_dump(mode="json")
            else:
                error_data = {
                    "code": error.code,
                    "message": str(error),
                }

            yield encode_sse_event(
                "error",
                error_data,
            )
            return

        yield encode_sse_event(
            "done",
            {"status": "completed"},
        )


chat_service = ChatService()
