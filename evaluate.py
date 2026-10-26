#!/usr/bin/env python3
"""
CLI Entrypoint for the First Pass Evaluation & Observability Harness.

Usage:
    python evaluate.py
    python evaluate.py --live
    python evaluate.py --output eval_results.json
"""

import argparse
import json
import sys
import dotenv

dotenv.load_dotenv()

from first_pass.eval_harness import run_full_evaluation


def print_report(results: dict) -> None:
    s = results["summary"]
    prof = results["ingestion_and_profiling"]
    rag = results["rag_retrieval"]
    plan = results["planner_compliance"]
    exec_ev = results["execution_and_observer"]
    telem = results["production_telemetry"]

    print("=" * 84)
    print("  FIRST PASS - AUTONOMOUS AGENTIC RAG EVALUATION & OBSERVABILITY REPORT")
    print("=" * 84)
    print(f"  Evaluated At     : {results['evaluated_at']}")
    print(f"  Harness Duration : {results['harness_duration_sec']:.2f}s")
    print(
        f"  Benchmark Corpus : {s['total_benchmark_datasets']} datasets | "
        f"{s['total_rows_evaluated']:,} rows | {s['total_columns_evaluated']} columns"
    )
    print("-" * 84)

    print("\n[1] INGESTION & STATISTICAL PROFILING LATENCY")
    print(
        f"    * Type Inference Accuracy : {prof['type_inference_accuracy_pct']:.1f}%"
    )
    print(
        f"    * Latency (p50 / Mean / Max): {prof['latency_p50_ms']:.1f} ms / "
        f"{prof['latency_mean_ms']:.1f} ms / {prof['latency_max_ms']:.1f} ms"
    )
    print("    * Per-Dataset Breakdown:")
    for d in prof["datasets"]:
        print(
            f"      - {d['file']:44s} | {d['rows']:6,d} rows x {d['cols']:2d} cols | "
            f"{d['total_ms']:7.1f} ms | Types: {d['type_accuracy']:5.1f}%"
        )

    print("\n[2] HYBRID BM25 + FAISS PLAYBOOK RAG RETRIEVAL")
    print(f"    * Indexed Playbooks : {rag['total_playbooks_indexed']} markdown playbooks")
    print(f"    * Hit Rate @ 1      : {rag['hit_rate_at_1_pct']:.1f}% ({rag['queries_evaluated']} golden queries)")
    print(f"    * Recall @ 3        : {rag['recall_at_3_pct']:.1f}%")
    print(f"    * Mean Recip. Rank  : {rag['mrr']:.4f} MRR")

    print("\n[3] PLANNER SCHEMA & TARGET VARIABLE COMPLIANCE")
    print(f"    * Cleaning Plan Schema Validity : {plan['cleaning_schema_validity_pct']:.1f}%")
    print(f"    * Analysis Plan Schema Validity : {plan['analysis_schema_validity_pct']:.1f}%")
    print(f"    * Template Registry Resolution  : {plan['template_resolution_rate_pct']:.1f}% ({plan['total_planned_analyses']} steps)")
    print(f"    * Target Variable Recall        : {plan['target_identification_accuracy_pct']:.1f}%")

    print("\n[4] NOTEBOOK EXECUTION & MULTIMODAL OBSERVER SELF-CORRECTION")
    print(f"    * Total Executed Code Cells     : {exec_ev['total_code_cells']} cells across {exec_ev['notebooks_evaluated']} notebooks")
    print(f"    * Pre-Observer Execution Rate   : {exec_ev['pre_observer_pass_rate_pct']:.2f}%")
    print(f"    * Post-Observer Execution Rate  : {exec_ev['post_observer_pass_rate_pct']:.2f}% (Failure Rate: {exec_ev['post_observer_failure_rate_pct']:.2f}%)")
    print(
        f"    * Observer Autonomous Patches   : {exec_ev['total_observer_patches']} total "
        f"({exec_ev['runtime_exception_fixes']} runtime exception fix, {exec_ev['visual_layout_fixes']} visual chart layout fixes)"
    )
    print(
        f"    * Post-Execution Synthesis      : {exec_ev['total_charts_rendered']} charts rendered | "
        f"{exec_ev['total_consultant_insights']} cell insights | "
        f"{exec_ev['key_takeaways_coverage_pct']:.0f}% Executive Takeaways"
    )
    print("    * Per-Notebook Execution Breakdown:")
    for nb in exec_ev["notebooks"]:
        print(
            f"      - {nb['file']:44s} | Cells: {nb['code_cells']:2d} | "
            f"Pre-Err: {nb['pre_observer_exceptions']} -> Post-Err: {nb['post_observer_errors']} | "
            f"Patches: {nb['observer_patches_applied']} | Charts: {nb['charts_rendered']:2d} | Insights: {nb['consultant_insights']:2d}"
        )

    print("\n[5] PRODUCTION TELEMETRY, COST & LATENCY MONITORING (telemetry.jsonl)")
    print(
        f"    * Production Run Success Rate   : {telem['run_success_rate_pct']:.1f}% "
        f"({telem['runs_succeeded']}/{telem['runs_started']} runs succeeded, {telem['failure_rate_pct']:.1f}% failure rate)"
    )
    print(
        f"    * End-to-End Cost per Run       : ${telem['mean_cost_usd']:.4f} mean "
        f"(range: ${telem['min_cost_usd']:.4f} - ${telem['max_cost_usd']:.4f} | ~{telem['mean_tokens_per_run']:,} tokens/run)"
    )
    print(
        f"    * End-to-End Pipeline Latency   : {telem['mean_duration_sec']:.1f}s mean "
        f"(range: {telem['min_duration_sec']:.1f}s - {telem['max_duration_sec']:.1f}s across 5 passes + kernel + vision)"
    )
    print(
        f"    * Report Download Conversion    : {telem['download_conversion_rate_pct']:.1f}% "
        f"({telem['total_downloads']} report exports)"
    )
    print("=" * 84)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run First Pass Evaluation Harness")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Use live Gemini API embeddings for RAG retrieval benchmark",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="eval_results.json",
        help="Path to write JSON evaluation results (default: eval_results.json)",
    )
    args = parser.parse_args()

    results = run_full_evaluation(use_live_api=args.live, verify_pre_exceptions=True)
    print_report(results)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"\nSaved structured benchmark results to {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
