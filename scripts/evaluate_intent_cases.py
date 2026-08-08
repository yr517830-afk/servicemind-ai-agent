import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.intent import IntentType, RiskLevel


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES_PATH = PROJECT_ROOT / "evals" / "intent_cases.jsonl"
DEFAULT_PREDICTIONS_PATH = (
    PROJECT_ROOT / "evals" / "intent_predictions_baseline.jsonl"
)


class IntentCase(BaseModel):
    """一条经过人工标注的意图评测样本。"""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    input: str = Field(min_length=1)
    expected_intent: IntentType
    expected_risk: RiskLevel
    annotation_reason: str = Field(min_length=1)


class IntentPrediction(BaseModel):
    """与评测样本对应的一条候选预测。"""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    predicted_intent: IntentType
    predicted_risk: RiskLevel
    prediction_reason: str = Field(min_length=1)


class EvaluationError(BaseModel):
    """一条没有同时匹配意图与风险的结果。"""

    id: str
    input: str
    expected_intent: IntentType
    predicted_intent: IntentType
    expected_risk: RiskLevel
    predicted_risk: RiskLevel
    reason: str


class EvaluationReport(BaseModel):
    """意图与风险标签的汇总评测报告。"""

    total: int
    correct: int
    accuracy: float
    intent_correct: int
    intent_accuracy: float
    risk_correct: int
    risk_accuracy: float
    confusion_matrix: dict[str, dict[str, int]]
    errors: list[EvaluationError]


def _load_jsonl(path: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []

    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        line = raw_line.strip()
        if not line:
            continue

        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"{path}:{line_number}: JSON 格式无效。"
            ) from error

        if not isinstance(record, dict):
            raise ValueError(
                f"{path}:{line_number}: 每行必须是 JSON 对象。"
            )
        records.append(record)

    if not records:
        raise ValueError(f"{path}: 评测文件不能为空。")

    return records


def _ensure_unique_ids(
    records: list[IntentCase] | list[IntentPrediction],
    path: Path,
) -> None:
    counts = Counter(record.id for record in records)
    duplicate_ids = sorted(
        record_id for record_id, count in counts.items() if count > 1
    )

    if duplicate_ids:
        raise ValueError(
            f"{path}: 存在重复 id：{', '.join(duplicate_ids)}。"
        )


def load_cases(path: Path = DEFAULT_CASES_PATH) -> list[IntentCase]:
    """读取并校验人工标注的 JSONL 评测集。"""
    cases = [IntentCase.model_validate(item) for item in _load_jsonl(path)]
    _ensure_unique_ids(cases, path)
    return cases


def load_predictions(
    path: Path = DEFAULT_PREDICTIONS_PATH,
) -> list[IntentPrediction]:
    """读取并校验候选预测 JSONL 文件。"""
    predictions = [
        IntentPrediction.model_validate(item) for item in _load_jsonl(path)
    ]
    _ensure_unique_ids(predictions, path)
    return predictions


def evaluate_cases(
    cases: list[IntentCase],
    predictions: list[IntentPrediction],
) -> EvaluationReport:
    """按 id 对齐金标准与预测并计算准确率和混淆矩阵。"""
    prediction_by_id = {prediction.id: prediction for prediction in predictions}
    case_ids = {case.id for case in cases}
    prediction_ids = set(prediction_by_id)

    missing_ids = sorted(case_ids - prediction_ids)
    extra_ids = sorted(prediction_ids - case_ids)
    if missing_ids or extra_ids:
        details = []
        if missing_ids:
            details.append(f"缺少预测：{', '.join(missing_ids)}")
        if extra_ids:
            details.append(f"多余预测：{', '.join(extra_ids)}")
        raise ValueError("；".join(details))

    correct = 0
    intent_correct = 0
    risk_correct = 0
    errors: list[EvaluationError] = []
    confusion: defaultdict[str, Counter[str]] = defaultdict(Counter)

    for case in cases:
        prediction = prediction_by_id[case.id]
        intent_matches = case.expected_intent == prediction.predicted_intent
        risk_matches = case.expected_risk == prediction.predicted_risk

        confusion[case.expected_intent.value][
            prediction.predicted_intent.value
        ] += 1
        intent_correct += int(intent_matches)
        risk_correct += int(risk_matches)
        correct += int(intent_matches and risk_matches)

        if intent_matches and risk_matches:
            continue

        mismatch_reasons = []
        if not intent_matches:
            mismatch_reasons.append("意图标签不一致")
        if not risk_matches:
            mismatch_reasons.append("风险标签不一致")
        mismatch_reasons.append(f"预测依据：{prediction.prediction_reason}")
        errors.append(
            EvaluationError(
                id=case.id,
                input=case.input,
                expected_intent=case.expected_intent,
                predicted_intent=prediction.predicted_intent,
                expected_risk=case.expected_risk,
                predicted_risk=prediction.predicted_risk,
                reason="；".join(mismatch_reasons),
            )
        )

    total = len(cases)
    matrix = {
        expected: dict(sorted(predicted.items()))
        for expected, predicted in sorted(confusion.items())
    }
    return EvaluationReport(
        total=total,
        correct=correct,
        accuracy=correct / total,
        intent_correct=intent_correct,
        intent_accuracy=intent_correct / total,
        risk_correct=risk_correct,
        risk_accuracy=risk_correct / total,
        confusion_matrix=matrix,
        errors=errors,
    )


def render_report(report: EvaluationReport) -> str:
    """把评测结果格式化为适合终端阅读的文本。"""
    lines = [
        f"总样本：{report.total}",
        (
            f"完全正确：{report.correct}/{report.total} "
            f"({report.accuracy:.1%})"
        ),
        (
            f"意图正确：{report.intent_correct}/{report.total} "
            f"({report.intent_accuracy:.1%})"
        ),
        (
            f"风险正确：{report.risk_correct}/{report.total} "
            f"({report.risk_accuracy:.1%})"
        ),
        "",
        "意图混淆矩阵（expected -> predicted: count）：",
    ]

    for expected, predictions in report.confusion_matrix.items():
        values = ", ".join(
            f"{predicted}={count}"
            for predicted, count in predictions.items()
        )
        lines.append(f"- {expected} -> {values}")

    lines.extend(["", f"错误样本：{len(report.errors)}"])
    for error in report.errors:
        lines.extend(
            [
                f"- {error.id}: {error.input}",
                (
                    "  expected="
                    f"{error.expected_intent.value}/{error.expected_risk.value}, "
                    "predicted="
                    f"{error.predicted_intent.value}/{error.predicted_risk.value}"
                ),
                f"  原因：{error.reason}",
            ]
        )

    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    """解析评测脚本参数。"""
    parser = argparse.ArgumentParser(
        description="统计意图与风险标签的离线评测结果。"
    )
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES_PATH)
    parser.add_argument(
        "--predictions",
        type=Path,
        default=DEFAULT_PREDICTIONS_PATH,
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        help="可选：把完整报告保存为 JSON。",
    )
    return parser.parse_args()


def main() -> None:
    """运行离线意图评测。"""
    args = parse_args()
    report = evaluate_cases(
        load_cases(args.cases),
        load_predictions(args.predictions),
    )
    print(render_report(report))

    if args.json_output is not None:
        args.json_output.write_text(
            report.model_dump_json(indent=2),
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
