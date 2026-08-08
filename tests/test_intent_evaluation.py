import json
from pathlib import Path

import pytest

from scripts.evaluate_intent_cases import (
    DEFAULT_CASES_PATH,
    DEFAULT_PREDICTIONS_PATH,
    evaluate_cases,
    load_cases,
    load_predictions,
    render_report,
)


def test_intent_cases_contain_20_annotated_samples() -> None:
    cases = load_cases()

    assert len(cases) == 20
    assert len({case.id for case in cases}) == 20
    assert all(case.annotation_reason for case in cases)
    assert len({case.expected_intent for case in cases}) == 7


def test_baseline_predictions_match_case_ids() -> None:
    cases = load_cases(DEFAULT_CASES_PATH)
    predictions = load_predictions(DEFAULT_PREDICTIONS_PATH)

    assert len(predictions) == 20
    assert {prediction.id for prediction in predictions} == {
        case.id for case in cases
    }


def test_evaluation_report_contains_scores_and_errors() -> None:
    report = evaluate_cases(load_cases(), load_predictions())

    assert report.total == 20
    assert report.correct == 17
    assert report.accuracy == pytest.approx(0.85)
    assert report.intent_correct == 18
    assert report.intent_accuracy == pytest.approx(0.90)
    assert report.risk_correct == 19
    assert report.risk_accuracy == pytest.approx(0.95)
    assert len(report.errors) == 3
    assert {error.id for error in report.errors} == {
        "damaged-product",
        "duplicate-charge",
        "business-hours",
    }


def test_evaluation_report_builds_confusion_matrix() -> None:
    report = evaluate_cases(load_cases(), load_predictions())

    assert report.confusion_matrix["complaint"] == {
        "complaint": 1,
        "logistics": 1,
    }
    assert report.confusion_matrix["payment"] == {
        "account_security": 1,
        "payment": 2,
    }


def test_evaluation_rejects_missing_predictions() -> None:
    with pytest.raises(ValueError, match="缺少预测"):
        evaluate_cases(load_cases(), load_predictions()[:-1])


def test_loader_rejects_duplicate_ids(tmp_path: Path) -> None:
    first_case = json.loads(
        DEFAULT_CASES_PATH.read_text(encoding="utf-8").splitlines()[0]
    )
    duplicate_path = tmp_path / "duplicate.jsonl"
    duplicate_path.write_text(
        "\n".join(json.dumps(first_case, ensure_ascii=False) for _ in range(2)),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="重复 id"):
        load_cases(duplicate_path)


def test_render_report_includes_required_statistics() -> None:
    output = render_report(evaluate_cases(load_cases(), load_predictions()))

    assert "总样本：20" in output
    assert "完全正确：17/20 (85.0%)" in output
    assert "意图混淆矩阵" in output
    assert "错误样本：3" in output
    assert "damaged-product" in output
    assert "原因：意图标签不一致" in output
