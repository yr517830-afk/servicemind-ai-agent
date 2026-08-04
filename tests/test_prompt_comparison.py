from unittest.mock import Mock

import pytest

from app.clients.llm_client import LLMClient
from app.schemas.intent import IntentExtraction
from app.services.intent_service import IntentService
from scripts.compare_intent_prompts import (
    DEFAULT_SAMPLES_PATH,
    load_samples,
    matches_expected,
    run_dry_comparison,
)


def test_evaluation_dataset_contains_15_samples() -> None:
    samples = load_samples(DEFAULT_SAMPLES_PATH)

    assert len(samples) == 15
    assert len({sample.id for sample in samples}) == 15


@pytest.mark.parametrize(
    ("version", "expected_example_count"),
    [
        ("v1", 3),
        ("v2", 5),
    ],
)
def test_intent_service_switches_prompt_versions(
    version: str,
    expected_example_count: int,
) -> None:
    client = Mock(spec=LLMClient)
    service = IntentService(
        client,
        prompt_version=version,
    )

    assert service.prompt_version == version
    assert (
        len(service.prompt_bundle.examples)
        == expected_example_count
    )


def test_model_input_contains_examples_and_message() -> None:
    client = Mock(spec=LLMClient)
    service = IntentService(
        client,
        prompt_version="v2",
    )
    customer_message = "查询订单 SM-20260727-999"

    model_input = service.build_model_input(
        customer_message,
        service.prompt_bundle,
    )

    assert customer_message in model_input
    assert "以下是已标注的参考示例" in model_input
    assert "现在分析以下客户消息" in model_input

    for example in service.prompt_bundle.examples:
        assert example.input in model_input


def test_matches_expected_result() -> None:
    sample = load_samples(DEFAULT_SAMPLES_PATH)[0]
    result = IntentExtraction(
        intent=sample.expected_intent,
        order_number=sample.expected_order_number,
        risk=sample.expected_risk,
        confidence_reason="测试结果。",
    )

    assert matches_expected(result, sample) is True


def test_dry_comparison_uses_both_versions(
    capsys: pytest.CaptureFixture[str],
) -> None:
    samples = load_samples(DEFAULT_SAMPLES_PATH)

    run_dry_comparison(
        samples,
        ["v1", "v2"],
    )

    output = capsys.readouterr().out

    assert "mode: dry-run" in output
    assert "samples: 15" in output
    assert "v1: examples=3" in output
    assert "v2: examples=5" in output