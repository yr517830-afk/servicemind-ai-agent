from unittest.mock import Mock

import httpx
import pytest
from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    RateLimitError,
)

from app.clients.llm_client import (
    LLMAuthenticationError,
    LLMClient,
    LLMNotConfiguredError,
    LLMRateLimitError,
    LLMTimeoutError,
    LLMUnavailableError,
)

from app.schemas.intent import IntentExtraction, IntentType, RiskLevel

def configured_client() -> LLMClient:
    """创建不会实际联网的已配置客户端。"""
    return LLMClient(
        api_key="test-key",
        model="test-model",
        base_url="https://example.com/v1",
        timeout=1.0,
        max_retries=0,
    )


def attach_mock_sdk(client: LLMClient) -> Mock:
    """使用 Mock 替换真实 OpenAI SDK 客户端。"""
    sdk = Mock()
    client._client = sdk
    return sdk


def test_llm_client_without_api_key_is_safe() -> None:
    client = LLMClient(api_key="")

    assert client.configured is False
    assert client.health()["status"] == "not_configured"

    with pytest.raises(LLMNotConfiguredError) as error:
        client.generate_text("你好")

    assert error.value.code == "LLM_NOT_CONFIGURED"


def test_llm_client_generates_text() -> None:
    client = configured_client()
    sdk = attach_mock_sdk(client)
    sdk.responses.create.return_value = Mock(output_text="  测试回复  ")

    result = client.generate_text(
        "客户的问题",
        instructions="你是客服助手。",
    )

    assert result == "测试回复"
    sdk.responses.create.assert_called_once_with(
        model="test-model",
        input="客户的问题",
        instructions="你是客服助手。",
    )


def test_llm_client_maps_timeout_error() -> None:
    client = configured_client()
    sdk = attach_mock_sdk(client)
    request = httpx.Request("POST", "https://example.com/v1/responses")
    sdk.responses.create.side_effect = APITimeoutError(request=request)

    with pytest.raises(LLMTimeoutError) as error:
        client.generate_text("测试超时")

    assert error.value.code == "LLM_TIMEOUT"
    assert "test-key" not in str(error.value)


def test_llm_client_maps_rate_limit_error() -> None:
    client = configured_client()
    sdk = attach_mock_sdk(client)
    request = httpx.Request("POST", "https://example.com/v1/responses")
    response = httpx.Response(429, request=request)
    sdk.responses.create.side_effect = RateLimitError(
        "rate limited",
        response=response,
        body=None,
    )

    with pytest.raises(LLMRateLimitError) as error:
        client.generate_text("测试限流")

    assert error.value.code == "LLM_RATE_LIMITED"
    assert "test-key" not in str(error.value)


def test_llm_client_maps_authentication_error() -> None:
    client = configured_client()
    sdk = attach_mock_sdk(client)
    request = httpx.Request("POST", "https://example.com/v1/responses")
    response = httpx.Response(401, request=request)
    sdk.responses.create.side_effect = AuthenticationError(
        "invalid key",
        response=response,
        body=None,
    )

    with pytest.raises(LLMAuthenticationError) as error:
        client.generate_text("测试认证")

    assert error.value.code == "LLM_AUTHENTICATION_FAILED"
    assert "test-key" not in str(error.value)


def test_llm_client_maps_connection_error() -> None:
    client = configured_client()
    sdk = attach_mock_sdk(client)
    request = httpx.Request("POST", "https://example.com/v1/responses")
    sdk.responses.create.side_effect = APIConnectionError(request=request)

    with pytest.raises(LLMUnavailableError) as error:
        client.generate_text("测试连接失败")

    assert error.value.code == "LLM_UNAVAILABLE"
    assert "test-key" not in str(error.value)


def test_llm_client_rejects_empty_response() -> None:
    client = configured_client()
    sdk = attach_mock_sdk(client)
    sdk.responses.create.return_value = Mock(output_text="   ")

    with pytest.raises(LLMUnavailableError) as error:
        client.generate_text("测试空响应")

    assert error.value.code == "LLM_UNAVAILABLE"

def test_llm_client_parses_structured_response() -> None:
    client = configured_client()
    sdk = attach_mock_sdk(client)
    parsed_result = IntentExtraction(
        intent=IntentType.LOGISTICS,
        order_number="SM-20260727-001",
        risk=RiskLevel.LOW,
        confidence_reason="客户正在查询物流进度。",
    )
    sdk.responses.parse.return_value = Mock(
        output_parsed=parsed_result,
    )

    result = client.parse_structured(
        "查询订单 SM-20260727-001 的物流进度",
        response_model=IntentExtraction,
        instructions="提取客户消息中的结构化意图。",
    )

    assert result is parsed_result
    assert result.intent == IntentType.LOGISTICS
    assert result.order_number == "SM-20260727-001"
    sdk.responses.parse.assert_called_once_with(
        model="test-model",
        input="查询订单 SM-20260727-001 的物流进度",
        text_format=IntentExtraction,
        instructions="提取客户消息中的结构化意图。",
    )


def test_llm_client_rejects_missing_structured_response() -> None:
    client = configured_client()
    sdk = attach_mock_sdk(client)
    sdk.responses.parse.return_value = Mock(output_parsed=None)

    with pytest.raises(LLMUnavailableError) as error:
        client.parse_structured(
            "测试无效结构化响应",
            response_model=IntentExtraction,
        )

    assert error.value.code == "LLM_UNAVAILABLE"