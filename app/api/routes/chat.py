from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse, StreamingResponse

from app.schemas.chat import ChatStreamRequest
from app.services.chat_service import chat_service


router = APIRouter(
    prefix="/chat",
    tags=["智能聊天"],
)

CHAT_PAGE_PATH = (
    Path(__file__).resolve().parents[2]
    / "static"
    / "chat.html"
)


@router.get(
    "",
    include_in_schema=False,
)
def chat_page() -> FileResponse:
    """返回流式聊天演示页面。"""
    return FileResponse(
        CHAT_PAGE_PATH,
        media_type="text/html",
    )


@router.post(
    "/stream",
    response_class=StreamingResponse,
    responses={
        200: {
            "description": "SSE 流式聊天响应。",
            "content": {
                "text/event-stream": {
                    "schema": {
                        "type": "string",
                    }
                }
            },
        }
    },
)
def stream_chat(
    payload: ChatStreamRequest,
) -> StreamingResponse:
    """使用 SSE 分段返回智能客服回复。"""
    return StreamingResponse(
        chat_service.stream(payload),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )