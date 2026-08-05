import json
from unittest.mock import Mock

from app.clients.llm_client import LLMNotConfiguredError
from app.schemas.chat import ChatStreamRequest
from app.services.chat_service import ChatService, encode_sse_event


def parse_sse_data(event: str) -> dict[str, object]:
    data_line = next(
        line
        for line in event.splitlines()
        if line.startswith("data: ")
    )
    return json.loads(data_line.removeprefix("data: "))


def test_encode_sse_event() -> None:
    event = encode_sse_event(
        "delta",
        {"text": "你好"},
    )

    assert event == (
        'event: delta\n'
        'data: {"text":"你好"}\n\n'
    )


def test_chat_service_streams_llm_chunks() -> None:
    client = Mock()
    client.stream_text.return_value = iter(
        ["您好，", "请问有什么可以帮助您？"]
    )
    service = ChatService(client=client)

    events = list(
        service.stream(
            ChatStreamRequest(
                message="你好",
            )
        )
    )

    assert events[0].startswith("event: start\n")
    assert events[1].startswith("event: delta\n")
    assert events[2].startswith("event: delta\n")
    assert events[3].startswith("event: done\n")

    assert parse_sse_data(events[1]) == {
        "text": "您好，"
    }
    assert parse_sse_data(events[2]) == {
        "text": "请问有什么可以帮助您？"
    }

    client.stream_text.assert_called_once()


def test_chat_service_returns_structured_error() -> None:
    client = Mock()
    client.stream_text.side_effect = (
        LLMNotConfiguredError("LLM API Key 尚未配置。")
    )
    service = ChatService(client=client)

    events = list(
        service.stream(
            ChatStreamRequest(
                message="你好",
            )
        )
    )

    assert len(events) == 2
    assert events[0].startswith("event: start\n")
    assert events[1].startswith("event: error\n")

    error_data = parse_sse_data(events[1])

    assert error_data["code"] == "LLM_NOT_CONFIGURED"
    assert "API Key" in str(error_data["message"])


def test_chat_service_supports_demo_stream() -> None:
    client = Mock()
    service = ChatService(client=client)

    events = list(
        service.stream(
            ChatStreamRequest(
                message="测试演示模式",
                demo=True,
            )
        )
    )

    assert events[0].startswith("event: start\n")
    assert events[-1].startswith("event: done\n")
    assert sum(
        event.startswith("event: delta\n")
        for event in events
    ) == 4

    client.stream_text.assert_not_called()