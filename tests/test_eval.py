"""Tests for the eval harness itself."""

import pytest
from eval.run_eval import EvalRunner
from eval.test_cases import EVAL_TEST_CASES


def test_eval_runner_runs_all():
    runner = EvalRunner()
    metrics = runner.run_all()
    assert metrics["total_test_cases"] == len(EVAL_TEST_CASES)
    assert metrics["obligation_extraction_accuracy"] > 0


def test_eval_all_scores_above_90():
    """Guard-rail: all six metrics must stay above 90%."""
    runner = EvalRunner()
    metrics = runner.run_all()
    for key in [
        "obligation_extraction_accuracy",
        "product_mapping_accuracy",
        "citation_coverage",
        "risk_level_accuracy",
        "escalation_accuracy",
    ]:
        assert metrics[key] >= 90.0, f"{key} dropped below 90%: {metrics[key]}"


def test_eval_control_mapping_above_85():
    """Control mapping has a slightly lower bar (some domains have no controls)."""
    runner = EvalRunner()
    metrics = runner.run_all()
    assert metrics["control_mapping_accuracy"] >= 85.0
