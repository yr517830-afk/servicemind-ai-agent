import argparse
import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from app.clients.llm_client import llm_client
from app.schemas.intent import IntentExtraction, IntentType, RiskLevel
from app.services.intent_service import IntentService


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SAMPLES_PATH = (
    PROJECT_ROOT
    / "evals"
    / "intent_extraction_samples.json"
)
DEFAULT_VERSIONS = ["v1", "v2"]


class EvaluationSample(BaseModel):
    """一条意图提取评估样本。"""

    model_config = ConfigDict(extra="forbid")

    id: str
    input: str
    expected_intent: IntentType
    expected_order_number: str | None
    expected_risk: RiskLevel


def load_samples(path: Path) -> list[EvaluationSample]:
    """读取并校验评估数据集。"""
    raw_samples = json.loads(
        path.read_text(encoding="utf-8")
    )
    samples = [
        EvaluationSample.model_validate(sample)
        for sample in raw_samples
    ]

    if not samples:
        raise ValueError("评估数据集不能为空。")

    return samples


def matches_expected(
    result: IntentExtraction,
    sample: EvaluationSample,
) -> bool:
    """判断结构化结果是否匹配预期关键字段。"""
    return (
        result.intent == sample.expected_intent
        and result.order_number
        == sample.expected_order_number
        and result.risk == sample.expected_risk
    )


def run_dry_comparison(
    samples: list[EvaluationSample],
    versions: list[str],
) -> None:
    """对比 Prompt 结构，不调用真实模型。"""
    print("mode: dry-run")
    print(f"samples: {len(samples)}")

    for version in versions:
        service = IntentService(
            prompt_version=version,
        )
        bundle = service.prompt_bundle
        rendered_lengths = [
            len(
                service.build_model_input(
                    sample.input,
                    bundle,
                )
            )
            for sample in samples
        ]
        average_length = sum(rendered_lengths) / len(
            rendered_lengths
        )

        print(
            f"{version}: "
            f"examples={len(bundle.examples)}, "
            f"system_chars={len(bundle.system_prompt)}, "
            f"average_input_chars={average_length:.1f}, "
            f"purpose={bundle.metadata.purpose}"
        )


def evaluate_version(
    samples: list[EvaluationSample],
    version: str,
) -> tuple[int, int]:
    """使用真实模型评估一个 Prompt 版本。"""
    service = IntentService(
        prompt_version=version,
    )
    passed = 0

    print(f"\nPrompt {version}")

    for sample in samples:
        result = service.extract(sample.input)
        matched = matches_expected(result, sample)

        if matched:
            passed += 1

        status = "PASS" if matched else "FAIL"
        print(
            f"[{status}] {sample.id}: "
            f"intent={result.intent.value}, "
            f"order={result.order_number}, "
            f"risk={result.risk.value}"
        )

    return passed, len(samples)


def run_live_comparison(
    samples: list[EvaluationSample],
    versions: list[str],
) -> None:
    """使用同一批样本执行真实模型对比。"""
    if not llm_client.configured:
        raise RuntimeError(
            "未配置 OPENAI_API_KEY，"
            "无法执行真实模型对比。"
        )

    print("mode: live")
    print(f"samples: {len(samples)}")

    scores = {}

    for version in versions:
        passed, total = evaluate_version(
            samples,
            version,
        )
        scores[version] = (passed, total)

    print("\nSummary")

    for version, (passed, total) in scores.items():
        accuracy = passed / total
        print(
            f"{version}: "
            f"{passed}/{total} "
            f"accuracy={accuracy:.1%}"
        )


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(
        description="对比意图提取 Prompt v1/v2。",
    )
    parser.add_argument(
        "--samples",
        type=Path,
        default=DEFAULT_SAMPLES_PATH,
        help="评估样本 JSON 文件路径。",
    )
    parser.add_argument(
        "--versions",
        nargs="+",
        default=DEFAULT_VERSIONS,
        help="需要对比的 Prompt 版本。",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="调用真实模型；默认只执行安全 dry-run。",
    )
    return parser.parse_args()


def main() -> None:
    """运行 Prompt 对比。"""
    args = parse_args()
    samples = load_samples(args.samples)

    if args.live:
        run_live_comparison(
            samples,
            args.versions,
        )
    else:
        run_dry_comparison(
            samples,
            args.versions,
        )


if __name__ == "__main__":
    main()