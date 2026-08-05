from fastapi.testclient import TestClient


def test_chat_stream_returns_sse_events(
    api_client: TestClient,
) -> None:
    with api_client.stream(
        "POST",
        "/chat/stream",
        json={
            "message": "请演示流式输出",
            "demo": True,
        },
    ) as response:
        body = response.read().decode("utf-8")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "text/event-stream"
    )
    assert response.headers["cache-control"] == "no-cache"
    assert response.headers["x-accel-buffering"] == "no"

    assert "event: start" in body
    assert "event: delta" in body
    assert "event: done" in body
    assert "流式输出演示" in body

    assert body.index("event: start") < body.index(
        "event: delta"
    )
    assert body.index("event: delta") < body.index(
        "event: done"
    )


def test_chat_stream_rejects_empty_message(
    api_client: TestClient,
) -> None:
    response = api_client.post(
        "/chat/stream",
        json={
            "message": "   ",
            "demo": True,
        },
    )

    assert response.status_code == 422


def test_chat_stream_returns_long_input_fallback(
    api_client: TestClient,
) -> None:
    with api_client.stream(
        "POST",
        "/chat/stream",
        json={
            "message": "问题" * 1001,
            "demo": False,
        },
    ) as response:
        body = response.read().decode("utf-8")

    assert response.status_code == 200
    assert "event: error" in body
    assert "INPUT_TOO_LONG" in body
    assert "shorten_input" in body


def test_openapi_describes_chat_stream(
    api_client: TestClient,
) -> None:
    openapi = api_client.get("/openapi.json").json()

    operation = openapi["paths"]["/chat/stream"]["post"]

    assert "智能聊天" in operation["tags"]
    assert "text/event-stream" in operation["responses"]["200"][
        "content"
    ]

def test_chat_page_returns_demo_html(
    api_client: TestClient,
) -> None:
    response = api_client.get("/chat")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "text/html"
    )
    assert "ServiceMind AI Agent" in response.text
    assert "/chat/stream" in response.text
    assert "textContent" in response.text
    assert 'id="fallback-panel"' in response.text
    assert "use_rules" in response.text
    assert "retry_later" in response.text
    assert "shorten_input" in response.text
    assert "human_handoff" in response.text
