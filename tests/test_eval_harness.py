import pytest
from first_pass.eval_harness import (
    evaluate_ingestion_and_profiling,
    evaluate_rag_retrieval,
    evaluate_planner_compliance,
    evaluate_execution_and_observer,
)
from first_pass.telemetry import get_telemetry_summary


def test_eval_ingestion_and_profiling():
    res = evaluate_ingestion_and_profiling()
    assert res["datasets_evaluated"] == 5
    assert res["total_rows_processed"] == 121850
    assert res["total_columns_profiled"] == 87
    assert res["type_inference_accuracy_pct"] == 100.0
    assert res["latency_p50_ms"] < 250.0


def test_eval_rag_retrieval():
    res = evaluate_rag_retrieval(use_live_api=False)
    assert res["total_playbooks_indexed"] == 25
    assert res["queries_evaluated"] == 10
    assert res["hit_rate_at_1_pct"] >= 90.0
    assert res["recall_at_3_pct"] == 100.0
    assert res["mrr"] >= 0.90


def test_eval_planner_compliance():
    res = evaluate_planner_compliance()
    assert res["benchmarks_evaluated"] == 5
    assert res["cleaning_schema_validity_pct"] == 100.0
    assert res["analysis_schema_validity_pct"] == 100.0
    assert res["template_resolution_rate_pct"] == 100.0
    assert res["target_identification_accuracy_pct"] == 100.0


def test_eval_execution_and_observer():
    res = evaluate_execution_and_observer(verify_pre_exceptions=False)
    assert res["notebooks_evaluated"] == 5
    assert res["total_code_cells"] == 55
    assert res["post_observer_pass_rate_pct"] == 100.0
    assert res["post_observer_failure_rate_pct"] == 0.0
    assert res["total_observer_patches"] == 5
    assert res["total_charts_rendered"] == 30
    assert res["total_consultant_insights"] == 33
    assert res["key_takeaways_coverage_pct"] == 100.0


def test_telemetry_monitoring_summary():
    telem = get_telemetry_summary()
    assert telem["runs_started"] >= 2
    assert telem["run_success_rate_pct"] == 100.0
    assert telem["failure_rate_pct"] == 0.0
    assert 0.01 <= telem["mean_cost_usd"] <= 0.05
    assert telem["download_conversion_rate_pct"] == 100.0
