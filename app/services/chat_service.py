import json
from collections.abc import Iterator

from app.clients.llm_client import LLMClient, LLMError, llm_client
from app.schemas.chat import ChatStreamRequest


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
            yield encode_sse_event(
                "error",
                {
                    "code": error.code,
                    "message": str(error),
                },
            )
            return

        yield encode_sse_event(
            "done",
            {"status": "completed"},
        )


chat_service = ChatService()