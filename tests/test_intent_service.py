from unittest.mock import Mock

import pytest

from app.clients.llm_client import (
    LLMClient,
    LLMInvalidResponseError,
    LLMRateLimitError,
    LLMRefusalError,
    LLMUnavailableError,
)
from app.schemas.intent import IntentExtraction, IntentType, RiskLevel
from app.services.intent_service import IntentService


@pytest.mark.parametrize(
    (
        "message",
        "expected_intent",
        "expected_order_number",
        "expected_risk",
    ),
    [
        (
            "查询订单 SM-20260727-001 的物流进度",
            IntentType.LOGISTICS,
            "SM-20260727-001",
            RiskLevel.LOW,
        ),
        (
            "订单 SM-20260727-002 现在是什么状态",
            IntentType.ORDER_STATUS,
            "SM-20260727-002",
            RiskLevel.LOW,
        ),
        (
            "我要申请订单 SM-20260727-003 的退款",
            IntentType.REFUND,
            "SM-20260727-003",
            RiskLevel.MEDIUM,
        ),
        (
            "订单 SM-20260727-004 支付失败",
            IntentType.PAYMENT,
            "SM-20260727-004",
            RiskLevel.MEDIUM,
        ),
        (
            "发现一笔不是我本人支付的订单",
            IntentType.ACCOUNT_SECURITY,
            None,
            RiskLevel.HIGH,
        ),
        (
            "账号可能被盗了",
            IntentType.ACCOUNT_SECURITY,
            None,
            RiskLevel.HIGH,
        ),
        (
            "物流已经十天没有更新",
            IntentType.LOGISTICS,
            None,
            RiskLevel.MEDIUM,
        ),
        (
            "收到的商品已经损坏，我要投诉",
            IntentType.COMPLAINT,
            None,
            RiskLevel.MEDIUM,
        ),
        (
            "退款什么时候到账",
            IntentType.REFUND,
            None,
            RiskLevel.LOW,
        ),
        (
            "银行卡被重复扣款",
            IntentType.PAYMENT,
            None,
            RiskLevel.HIGH,
        ),
        (
            "订单 SM-20260727-011 显示已签收但没有收到",
            IntentType.LOGISTICS,
            "SM-20260727-011",
            RiskLevel.MEDIUM,
        ),
        (
            "帮我查看订单 SM-20260727-012",
            IntentType.ORDER_STATUS,
            "SM-20260727-012",
            RiskLevel.LOW,
        ),
        (
            "客服一直没有处理我的问题",
            IntentType.COMPLAINT,
            None,
            RiskLevel.LOW,
        ),
        (
            "你好，请问你们几点下班",
            IntentType.OTHER,
            None,
            RiskLevel.LOW,
        ),
        (
            "我不知道怎么描述这个问题",
            IntentType.OTHER,
            None,
            RiskLevel.UNKNOWN,
        ),
    ],
    ids=[
        "logistics-with-order",
        "order-status",
        "refund-with-order",
        "payment-failed",
        "unauthorized-payment",
        "account-stolen",
        "logistics-delayed",
        "damaged-product",
        "refund-progress",
        "duplicate-charge",
        "missing-delivery",
        "query-order",
        "complaint",
        "business-hours",
        "unknown-problem",
    ],
)
def test_intent_service_parses_customer_messages(
    message: str,
    expected_intent: IntentType,
    expected_order_number: str | None,
    expected_risk: RiskLevel,
) -> None:
    client = Mock(spec=LLMClient)
    client.parse_structured.return_value = IntentExtraction(
        intent=expected_intent,
        order_number=expected_order_number,
        risk=expected_risk,
        confidence_reason="测试模型返回的结构化判断。",
    )
    service = IntentService(client)

    result = service.extract(message)

    assert isinstance(result, IntentExtraction)
    assert result.intent == expected_intent
    assert result.order_number == expected_order_number
    assert result.risk == expected_risk
    assert result.confidence_reason
    client.parse_structured.assert_called_once()


def test_intent_service_uses_fallback_when_llm_fails() -> None:
    client = Mock(spec=LLMClient)
    client.parse_structured.side_effect = LLMUnavailableError(
        "测试模拟的服务异常。"
    )
    service = IntentService(client)

    result = service.extract("查询订单 SM-20260727-099")

    assert result.intent == IntentType.OTHER
    assert result.order_number is None
    assert result.risk == RiskLevel.UNKNOWN
    assert "use_rules" in result.confidence_reason


def test_intent_service_handles_empty_message_without_llm() -> None:
    client = Mock(spec=LLMClient)
    service = IntentService(client)

    result = service.extract("   ")

    assert result.intent == IntentType.OTHER
    assert result.order_number is None
    assert result.risk == RiskLevel.UNKNOWN
    assert result.confidence_reason == "客户消息为空，无法判断意图。"
    client.parse_structured.assert_not_called()

@pytest.mark.parametrize(
    ("error", "expected_text"),
    [
        (
            LLMInvalidResponseError("非法结构化结果"),
            "use_rules",
        ),
        (
            LLMRefusalError("模型拒答"),
            "human_handoff",
        ),
        (
            LLMRateLimitError("触发限流"),
            "retry_later",
        ),
    ],
)
def test_intent_service_uses_specific_fallback(
    error: Exception,
    expected_text: str,
) -> None:
    client = Mock(spec=LLMClient)
    client.parse_structured.side_effect = error
    service = IntentService(client)

    result = service.extract("查询订单状态")

    assert result.intent == IntentType.OTHER
    assert result.risk == RiskLevel.UNKNOWN
    assert expected_text in result.confidence_reason


def test_intent_service_rejects_long_input_without_llm() -> None:
    client = Mock(spec=LLMClient)
    service = IntentService(client)

    result = service.extract("问题" * 1001)

    assert result.intent == IntentType.OTHER
    assert result.risk == RiskLevel.UNKNOWN
    assert "shorten_input" in result.confidence_reason
    client.parse_structured.assert_not_called()