import pytest

from app.schemas.failures import (
    FailureCode,
    FallbackAction,
)
from app.services.fallback_service import fallback_service


@pytest.mark.parametrize(
    (
        "code",
        "expected_action",
        "expected_retryable",
    ),
    [
        (
            FailureCode.INVALID_RESPONSE,
            FallbackAction.USE_RULES,
            False,
        ),
        (
            FailureCode.MODEL_REFUSAL,
            FallbackAction.HUMAN_HANDOFF,
            False,
        ),
        (
            FailureCode.RATE_LIMITED,
            FallbackAction.RETRY_LATER,
            True,
        ),
        (
            FailureCode.INPUT_TOO_LONG,
            FallbackAction.SHORTEN_INPUT,
            True,
        ),
    ],
)
def test_fallback_service_returns_expected_reply(
    code: FailureCode,
    expected_action: FallbackAction,
    expected_retryable: bool,
) -> None:
    reply = fallback_service.reply_for(code)

    assert reply.code is code
    assert reply.action is expected_action
    assert reply.retryable is expected_retryable
    assert reply.message