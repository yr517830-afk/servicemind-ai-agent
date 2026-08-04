import json
import re
from datetime import date
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from app.schemas.intent import IntentExtraction


PROMPTS_ROOT = Path(__file__).resolve().parents[2] / "prompts"
VERSION_PATTERN = re.compile(r"v[1-9]\d*")


class PromptMetadata(BaseModel):
    """Prompt 版本元数据。"""

    model_config = ConfigDict(extra="forbid")

    name: str
    version: str
    purpose: str
    model_family: str
    output_schema: str
    created_at: date
    based_on: str | None = None
    notes: str


class PromptExample(BaseModel):
    """单条 few-shot 示例。"""

    model_config = ConfigDict(extra="forbid")

    input: str
    output: IntentExtraction


class PromptBundle(BaseModel):
    """完整 Prompt 版本。"""

    model_config = ConfigDict(extra="forbid")

    metadata: PromptMetadata
    system_prompt: str
    examples: list[PromptExample]


def available_intent_prompt_versions() -> list[str]:
    """返回全部有效的意图提取 Prompt 版本。"""
    prompt_directory = PROMPTS_ROOT / "intent_extraction"

    if not prompt_directory.exists():
        return []

    versions = [
        path.name
        for path in prompt_directory.iterdir()
        if path.is_dir() and VERSION_PATTERN.fullmatch(path.name)
    ]

    return sorted(
        versions,
        key=lambda version: int(version.removeprefix("v")),
    )


@lru_cache
def load_intent_prompt(version: str) -> PromptBundle:
    """加载并校验指定版本的意图提取 Prompt。"""
    if not VERSION_PATTERN.fullmatch(version):
        raise ValueError(f"无效的 Prompt 版本：{version}")

    version_directory = (
        PROMPTS_ROOT / "intent_extraction" / version
    )
    metadata_path = version_directory / "metadata.json"
    system_path = version_directory / "system.md"
    examples_path = version_directory / "examples.json"

    required_files = [
        metadata_path,
        system_path,
        examples_path,
    ]
    missing_files = [
        path.name
        for path in required_files
        if not path.is_file()
    ]

    if missing_files:
        missing = ", ".join(missing_files)
        raise FileNotFoundError(
            f"Prompt {version} 缺少文件：{missing}"
        )

    metadata = PromptMetadata.model_validate_json(
        metadata_path.read_text(encoding="utf-8")
    )

    if metadata.name != "intent_extraction":
        raise ValueError(
            f"Prompt 名称不匹配：{metadata.name}"
        )

    if metadata.version != version:
        raise ValueError(
            f"Prompt 版本不匹配：期望 {version}，"
            f"实际 {metadata.version}"
        )

    if metadata.output_schema != "IntentExtraction":
        raise ValueError(
            "Prompt 输出结构必须是 IntentExtraction"
        )

    system_prompt = system_path.read_text(
        encoding="utf-8"
    ).strip()

    if not system_prompt:
        raise ValueError(
            f"Prompt {version} 的 system.md 不能为空"
        )

    raw_examples = json.loads(
        examples_path.read_text(encoding="utf-8")
    )
    examples = [
        PromptExample.model_validate(example)
        for example in raw_examples
    ]

    if not examples:
        raise ValueError(
            f"Prompt {version} 至少需要一条 few-shot 示例"
        )

    return PromptBundle(
        metadata=metadata,
        system_prompt=system_prompt,
        examples=examples,
    )