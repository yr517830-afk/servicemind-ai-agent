import pytest

from app.prompts.loader import (
    available_intent_prompt_versions,
    load_intent_prompt,
)
from app.schemas.intent import IntentExtraction


@pytest.mark.parametrize(
    ("version", "expected_example_count"),
    [
        ("v1", 3),
        ("v2", 5),
    ],
)
def test_load_intent_prompt_versions(
    version: str,
    expected_example_count: int,
) -> None:
    bundle = load_intent_prompt(version)

    assert bundle.metadata.name == "intent_extraction"
    assert bundle.metadata.version == version
    assert bundle.metadata.output_schema == "IntentExtraction"
    assert bundle.system_prompt
    assert len(bundle.examples) == expected_example_count
    assert all(
        isinstance(example.output, IntentExtraction)
        for example in bundle.examples
    )


def test_available_intent_prompt_versions() -> None:
    versions = available_intent_prompt_versions()

    assert versions == ["v1", "v2"]


def test_load_intent_prompt_uses_cache() -> None:
    load_intent_prompt.cache_clear()

    first = load_intent_prompt("v2")
    second = load_intent_prompt("v2")

    assert first is second


@pytest.mark.parametrize(
    "invalid_version",
    [
        "../v1",
        "v0",
        "v01",
        "latest",
        "V1",
    ],
)
def test_load_intent_prompt_rejects_invalid_version(
    invalid_version: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="无效的 Prompt 版本",
    ):
        load_intent_prompt(invalid_version)