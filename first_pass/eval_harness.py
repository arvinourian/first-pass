"""
First Pass — Automated Evaluation & Observability Harness
=========================================================
Evaluates the 5 core dimensions of the First Pass Agentic RAG pipeline:
1. Deterministic Ingestion & Statistical Profiling (Latency & Type Inference Accuracy)
2. Hybrid BM25 + FAISS Playbook RAG Retrieval (Hit@1, Recall@3, MRR)
3. Planner Schema Validity, Precondition Compliance & Target Variable Identification
4. Execution Reliability & Multimodal Observer Self-Correction (Pre vs. Post Observer Pass Rate)
5. Production Telemetry, Token Cost & End-to-End Latency Monitoring
"""

import glob
import json
import os
import statistics
import textwrap
import time
from typing import Any, Dict, List, Optional

import faiss
import numpy as np
import pandas as pd
from rank_bm25 import BM25Okapi

from first_pass.ingest import load_spreadsheet
from first_pass.profile import generate_profile
from first_pass.retrieval.index import Playbook, PlaybookIndex
from first_pass.schemas import AnalysisPlan, CleaningPlan, DataProfile
from first_pass.telemetry import get_telemetry_summary
from first_pass.templates.registry import get_template

# ---------------------------------------------------------------------------
# Benchmark Dataset Specifications
# ---------------------------------------------------------------------------
BENCHMARK_DATASETS: List[Dict[str, Any]] = [
    {
        "id": "ai_social_media",
        "csv": "Sample Inputs/AI_SocialMedia_Student_Dataset.csv",
        "domain": "Education & Behavioral Health",
        "expected_rows": 16000,
        "expected_cols": 10,
        "expected_types": {
            "Student_ID": "id_like",
            "Age": "numeric",
            "Mental_Health_Score": "numeric",
            "Physical_Health_Score": "numeric",
        },
        "expected_targets": ["Mental_Health_Score", "Physical_Health_Score"],
        "validation_nb": "temp/AI_SocialMedia_Student_Dataset_Validation.ipynb",
        "executed_nb": "temp/AI_SocialMedia_Student_Dataset_Validation_Executed.ipynb",
    },
    {
        "id": "walmart_sales",
        "csv": "Sample Inputs/Walmart_Sales.csv",
        "domain": "Retail Time-Series Forecasting",
        "expected_rows": 6435,
        "expected_cols": 8,
        "expected_types": {
            "Date": "datetime",
            "Weekly_Sales": "numeric",
            "Holiday_Flag": "boolean",
            "Temperature": "numeric",
        },
        "expected_targets": ["Weekly_Sales"],
        "validation_nb": "temp/Walmart_Sales_Validation.ipynb",
        "executed_nb": "temp/Walmart_Sales_Validation_Executed.ipynb",
    },
    {
        "id": "ironman_suits",
        "csv": "Sample Inputs/all_ironman_suit.csv",
        "domain": "Entity & Valuation Catalog",
        "expected_rows": 49,
        "expected_cols": 7,
        "expected_types": {
            "Model": "id_like",
            "Era": "categorical",
            "Primary Ability": "free_text",
        },
        "expected_targets": ["Estimated Value"],
        "validation_nb": "temp/all_ironman_suit_Validation.ipynb",
        "executed_nb": "temp/all_ironman_suit_Validation_Executed.ipynb",
    },
    {
        "id": "college_major_roi",
        "csv": "Sample Inputs/college_major_roi.csv",
        "domain": "Higher Education Financial ROI",
        "expected_rows": 30000,
        "expected_cols": 18,
        "expected_types": {
            "major_category": "categorical",
            "gpa": "numeric",
            "completed_on_time": "boolean",
            "roi_pct": "numeric",
            "earnings_10yr_usd": "numeric",
        },
        "expected_targets": ["net_roi_usd", "roi_pct", "earnings_10yr_usd"],
        "validation_nb": "temp/college_major_roi_Validation.ipynb",
        "executed_nb": "temp/college_major_roi_Validation_Executed.ipynb",
    },
    {
        "id": "philadelphia_opa_sfh",
        "csv": "Sample Inputs/opa data - philadelphia_sfh_modeling.csv",
        "domain": "Municipal Real Estate Assessments",
        "expected_rows": 69366,
        "expected_cols": 44,
        "expected_types": {
            "document_date": "datetime",
            "observed_price": "numeric",
            "log_price": "numeric",
            "split": "categorical",
        },
        "expected_targets": ["log_price", "observed_price"],
        "validation_nb": "temp/opa data - philadelphia_sfh_modeling_Validation.ipynb",
        "executed_nb": "temp/opa data - philadelphia_sfh_modeling_Validation_Executed.ipynb",
    },
]

# ---------------------------------------------------------------------------
# Golden Queries for Hybrid RAG Retrieval Benchmark
# ---------------------------------------------------------------------------
GOLDEN_RAG_QUERIES: List[Dict[str, Any]] = [
    {
        "query": "domain industry 6435 rows Store Date Weekly_Sales Holiday_Flag Temperature Fuel_Price CPI Unemployment retail store sales",
        "category": "domain",
        "expected_id": "retail",
    },
    {
        "query": "domain industry 30000 rows student_id major_name major_category institution_type tuition_usd gpa earnings_10yr_usd net_roi_usd",
        "category": "domain",
        "expected_id": "education",
    },
    {
        "query": "domain industry 69366 rows parcel_number document_date observed_price published_opa_2025 total_livable_area zoning property assessment",
        "category": "domain",
        "expected_id": "real_estate",
    },
    {
        "query": "cleaning operations parse date strings convert datetime columns Date document_date timestamp ISO",
        "category": "cleaning",
        "expected_id": "clean_parse_dates",
    },
    {
        "query": "cleaning operations drop duplicate rows identical records deduplication",
        "category": "cleaning",
        "expected_id": "clean_drop_duplicates",
    },
    {
        "query": "cleaning operations numeric missing values impute fillna median zero nulls",
        "category": "cleaning",
        "expected_id": "clean_numeric_nulls",
    },
    {
        "query": "engineering scaling datetime binning extract year month day of week standard scale",
        "category": "engineering",
        "expected_id": "basic-engineering",
    },
    {
        "query": "analysis seasonality heatmap period comparison year over year percentage change cumulative sum time series",
        "category": "analysis",
        "expected_id": "timeseries-advanced",
    },
    {
        "query": "analysis latitude longitude spatial coordinates choropleth region aggregation geographic map",
        "category": "analysis",
        "expected_id": "geographic",
    },
    {
        "query": "analysis target variable correlation ranked mutual information target distribution outcome driver",
        "category": "analysis",
        "expected_id": "target-aware",
    },
]


# ---------------------------------------------------------------------------
# 1. Ingestion & Statistical Profiling Evaluation
# ---------------------------------------------------------------------------
def evaluate_ingestion_and_profiling() -> Dict[str, Any]:
    dataset_results = []
    total_type_checks = 0
    correct_type_checks = 0
    total_rows = 0
    total_cols = 0

    for spec in BENCHMARK_DATASETS:
        csv_path = spec["csv"]
        if not os.path.exists(csv_path):
            continue

        t0 = time.perf_counter()
        df = load_spreadsheet(csv_path)
        ingest_ms = (time.perf_counter() - t0) * 1000.0

        t1 = time.perf_counter()
        profile: DataProfile = generate_profile(df)
        profile_ms = (time.perf_counter() - t1) * 1000.0
        total_ms = ingest_ms + profile_ms

        col_map = {c.name: c.inferred_type for c in profile.columns}
        matched_types = 0
        expected_types = spec["expected_types"]
        for col_name, exp_type in expected_types.items():
            total_type_checks += 1
            if col_map.get(col_name) == exp_type:
                matched_types += 1
                correct_type_checks += 1

        total_rows += profile.row_count
        total_cols += profile.column_count

        dataset_results.append(
            {
                "id": spec["id"],
                "file": os.path.basename(csv_path),
                "domain": spec["domain"],
                "rows": profile.row_count,
                "cols": profile.column_count,
                "rows_match": profile.row_count == spec["expected_rows"],
                "cols_match": profile.column_count == spec["expected_cols"],
                "type_accuracy": round(matched_types / len(expected_types) * 100.0, 1)
                if expected_types
                else 100.0,
                "ingest_ms": round(ingest_ms, 2),
                "profile_ms": round(profile_ms, 2),
                "total_ms": round(total_ms, 2),
            }
        )

    latencies = [r["total_ms"] for r in dataset_results]
    p50_ms = statistics.median(latencies) if latencies else 0.0
    p95_ms = max(latencies) if latencies else 0.0
    mean_ms = statistics.mean(latencies) if latencies else 0.0

    return {
        "datasets_evaluated": len(dataset_results),
        "total_rows_processed": total_rows,
        "total_columns_profiled": total_cols,
        "type_inference_accuracy_pct": round(
            (correct_type_checks / total_type_checks * 100.0) if total_type_checks else 100.0, 2
        ),
        "latency_p50_ms": round(p50_ms, 2),
        "latency_mean_ms": round(mean_ms, 2),
        "latency_max_ms": round(p95_ms, 2),
        "datasets": dataset_results,
    }


# ---------------------------------------------------------------------------
# 2. Hybrid RAG Retrieval Evaluation
# ---------------------------------------------------------------------------
def _build_offline_hybrid_index(playbook_dirs: List[str]) -> PlaybookIndex:
    """
    Builds a PlaybookIndex using BM25 + deterministic character/token n-gram dense vectors
    with FAISS inner-product search so CI/offline evaluation tests the exact hybrid ranking
    pipeline without requiring external API calls.
    """
    idx = PlaybookIndex()
    for pdir in playbook_dirs:
        category = os.path.basename(pdir)
        if not os.path.exists(pdir):
            continue
        for fname in sorted(os.listdir(pdir)):
            if fname.endswith(".md"):
                idx.playbooks.append(Playbook(category, os.path.join(pdir, fname)))

    corpus = [pb.get_search_text().lower().split() for pb in idx.playbooks]
    idx.bm25 = BM25Okapi(corpus)

    # Build deterministic vocabulary embedding space for FAISS
    vocab = sorted({tok for doc in corpus for tok in doc if len(tok) > 2})
    tok_to_i = {t: i for i, t in enumerate(vocab)}
    dim = max(len(vocab), 16)

    def _embed_text(text: str) -> np.ndarray:
        vec = np.zeros(dim, dtype="float32")
        for tok in text.lower().split():
            if tok in tok_to_i:
                vec[tok_to_i[tok]] += 1.0
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        return vec

    emb_matrix = np.vstack([_embed_text(pb.get_search_text()) for pb in idx.playbooks]).astype(
        "float32"
    )
    faiss.normalize_L2(emb_matrix)
    idx.faiss_index = faiss.IndexFlatIP(dim)
    idx.faiss_index.add(emb_matrix)
    idx._offline_embed = _embed_text
    return idx


def _hybrid_search_eval(
    idx: PlaybookIndex, query: str, category: str, top_k: int = 3, use_live_api: bool = False
) -> List[Playbook]:
    if use_live_api:
        return idx.hybrid_search(query, category, top_k=top_k)

    cat_indices = [i for i, pb in enumerate(idx.playbooks) if pb.category == category]
    if not cat_indices:
        return []

    tokenized_query = query.lower().split()
    bm25_scores = idx.bm25.get_scores(tokenized_query)

    q_emb = idx._offline_embed(query)
    q_emb_matrix = np.array([q_emb], dtype="float32")
    faiss.normalize_L2(q_emb_matrix)

    D, I = idx.faiss_index.search(q_emb_matrix, len(idx.playbooks))
    faiss_scores = np.zeros(len(idx.playbooks))
    for i, p_idx in enumerate(I[0]):
        faiss_scores[p_idx] = float(D[0][i])

    if np.max(bm25_scores) > np.min(bm25_scores):
        bm25_norm = (bm25_scores - np.min(bm25_scores)) / (
            np.max(bm25_scores) - np.min(bm25_scores)
        )
    else:
        bm25_norm = np.zeros_like(bm25_scores)

    if np.max(faiss_scores) > np.min(faiss_scores):
        faiss_norm = (faiss_scores - np.min(faiss_scores)) / (
            np.max(faiss_scores) - np.min(faiss_scores)
        )
    else:
        faiss_norm = np.zeros_like(faiss_scores)

    hybrid_scores = 0.5 * bm25_norm + 0.5 * faiss_norm
    cat_scores = [(i, hybrid_scores[i]) for i in cat_indices]
    cat_scores.sort(key=lambda x: x[1], reverse=True)
    return [idx.playbooks[x[0]] for x in cat_scores[:top_k]]


def evaluate_rag_retrieval(use_live_api: bool = False) -> Dict[str, Any]:
    playbook_dirs = [
        "playbooks/cleaning",
        "playbooks/engineering",
        "playbooks/analysis",
        "playbooks/domain",
    ]
    if use_live_api:
        idx = PlaybookIndex()
        idx.build(playbook_dirs)
    else:
        idx = _build_offline_hybrid_index(playbook_dirs)

    hits_at_1 = 0
    hits_at_3 = 0
    reciprocal_ranks = []
    query_details = []

    for item in GOLDEN_RAG_QUERIES:
        results = _hybrid_search_eval(
            idx, item["query"], item["category"], top_k=3, use_live_api=use_live_api
        )
        retrieved_ids = [pb.metadata.get("id") for pb in results]
        expected_id = item["expected_id"]

        rank = None
        if expected_id in retrieved_ids:
            rank = retrieved_ids.index(expected_id) + 1
            hits_at_3 += 1
            if rank == 1:
                hits_at_1 += 1
            reciprocal_ranks.append(1.0 / rank)
        else:
            reciprocal_ranks.append(0.0)

        query_details.append(
            {
                "category": item["category"],
                "expected_id": expected_id,
                "retrieved_top3": retrieved_ids,
                "rank": rank,
                "hit_at_1": rank == 1,
            }
        )

    total_q = len(GOLDEN_RAG_QUERIES)
    return {
        "total_playbooks_indexed": len(idx.playbooks),
        "queries_evaluated": total_q,
        "hit_rate_at_1_pct": round(hits_at_1 / total_q * 100.0, 2) if total_q else 0.0,
        "recall_at_3_pct": round(hits_at_3 / total_q * 100.0, 2) if total_q else 0.0,
        "mrr": round(statistics.mean(reciprocal_ranks), 4) if reciprocal_ranks else 0.0,
        "queries": query_details,
    }


# ---------------------------------------------------------------------------
# 3. Planner Schema, Precondition & Target Variable Compliance
# ---------------------------------------------------------------------------
def evaluate_planner_compliance() -> Dict[str, Any]:
    notebooks_checked = 0
    valid_cleaning_schemas = 0
    valid_analysis_schemas = 0
    total_planned_analyses = 0
    valid_template_ids = 0
    target_matches = 0
    dataset_plans = []

    for spec in BENCHMARK_DATASETS:
        nb_path = spec["validation_nb"]
        if not os.path.exists(nb_path):
            continue
        notebooks_checked += 1

        with open(nb_path, "r", encoding="utf-8") as f:
            nb = json.load(f)

        md_cells = ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "markdown"]
        cleaning_plan: Optional[CleaningPlan] = None
        analysis_plan: Optional[AnalysisPlan] = None

        for m in md_cells:
            if "### Raw Cleaning Plan JSON" in m:
                raw = m.split("```json")[1].split("```")[0].strip()
                cleaning_plan = CleaningPlan.model_validate_json(raw)
                valid_cleaning_schemas += 1
            elif "### Raw Analysis Plan JSON" in m:
                raw = m.split("```json")[1].split("```")[0].strip()
                analysis_plan = AnalysisPlan.model_validate_json(raw)
                valid_analysis_schemas += 1

        if analysis_plan:
            planned_items = [
                item for sec in analysis_plan.sections for item in sec.analyses
            ]
            total_planned_analyses += len(planned_items)
            for item in planned_items:
                if get_template(item.template_id) is not None:
                    valid_template_ids += 1

            expected_targets = set(spec["expected_targets"])
            actual_targets = set(analysis_plan.target_variables)
            has_target_overlap = bool(expected_targets & actual_targets)
            if has_target_overlap:
                target_matches += 1

            dataset_plans.append(
                {
                    "id": spec["id"],
                    "cleaning_steps": len(cleaning_plan.steps) if cleaning_plan else 0,
                    "analysis_sections": len(analysis_plan.sections),
                    "analysis_items": len(planned_items),
                    "target_variables": analysis_plan.target_variables,
                    "target_match": has_target_overlap,
                }
            )

    return {
        "benchmarks_evaluated": notebooks_checked,
        "cleaning_schema_validity_pct": round(
            valid_cleaning_schemas / notebooks_checked * 100.0, 2
        )
        if notebooks_checked
        else 0.0,
        "analysis_schema_validity_pct": round(
            valid_analysis_schemas / notebooks_checked * 100.0, 2
        )
        if notebooks_checked
        else 0.0,
        "template_resolution_rate_pct": round(
            valid_template_ids / total_planned_analyses * 100.0, 2
        )
        if total_planned_analyses
        else 0.0,
        "target_identification_accuracy_pct": round(
            target_matches / notebooks_checked * 100.0, 2
        )
        if notebooks_checked
        else 0.0,
        "total_planned_analyses": total_planned_analyses,
        "plans": dataset_plans,
    }


# ---------------------------------------------------------------------------
# 4. Execution Reliability & Multimodal Observer Evaluation
# ---------------------------------------------------------------------------
def _detect_pre_observer_runtime_exceptions(nb_pre: dict) -> List[Dict[str, Any]]:
    """
    Executes the inner body of pre-Observer code cells in a fast headless matplotlib ('Agg')
    sandbox to detect runtime exceptions that occurred before the Observer patched them.
    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    code_cells = ["".join(c["source"]) for c in nb_pre["cells"] if c["cell_type"] == "code"]
    env: Dict[str, Any] = {"display": lambda *a, **k: None}
    exceptions = []

    for idx, src in enumerate(code_cells):
        if "df.to_parquet" in src:
            continue
        clean_src = (
            src.replace("%matplotlib inline", "")
            .replace("from IPython.display import display", "")
            .replace("plt.show()", "plt.close('all')")
            .replace("df.info()", "pass")
        )
        if clean_src.strip().startswith("try:\n") and "except Exception as e:" in clean_src:
            body = textwrap.dedent(
                clean_src.split("try:\n", 1)[1].rsplit("except Exception as e:", 1)[0]
            )
        else:
            body = clean_src

        try:
            exec(body, env)
        except Exception as e:
            exceptions.append(
                {
                    "cell_index": idx,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                }
            )
        finally:
            plt.close("all")

    return exceptions


def evaluate_execution_and_observer(verify_pre_exceptions: bool = True) -> Dict[str, Any]:
    total_code_cells = 0
    pre_observer_failed_cells = 0
    post_observer_failed_cells = 0
    total_observer_patches = 0
    runtime_exception_patches = 0
    visual_layout_patches = 0
    total_charts_rendered = 0
    total_insights_generated = 0
    notebooks_with_takeaways = 0

    notebook_reports = []

    for spec in BENCHMARK_DATASETS:
        pre_path = spec["validation_nb"]
        post_path = spec["executed_nb"]
        if not (os.path.exists(pre_path) and os.path.exists(post_path)):
            continue

        with open(pre_path, "r", encoding="utf-8") as f:
            nb_pre = json.load(f)
        with open(post_path, "r", encoding="utf-8") as f:
            nb_post = json.load(f)

        pre_code_cells = [c for c in nb_pre["cells"] if c["cell_type"] == "code"]
        post_code_cells = [c for c in nb_post["cells"] if c["cell_type"] == "code"]

        n_cells = len(post_code_cells)
        total_code_cells += n_cells

        # Count cells patched by Observer
        patched_cell_indices = []
        for idx, (c1, c2) in enumerate(zip(pre_code_cells, post_code_cells)):
            if "".join(c1.get("source", [])) != "".join(c2.get("source", [])):
                patched_cell_indices.append(idx)

        # Detect pre-observer runtime exceptions
        pre_exceptions = (
            _detect_pre_observer_runtime_exceptions(nb_pre) if verify_pre_exceptions else []
        )
        n_pre_err = len(pre_exceptions)
        pre_observer_failed_cells += n_pre_err

        n_patches = len(patched_cell_indices)
        total_observer_patches += n_patches
        runtime_exception_patches += n_pre_err
        visual_layout_patches += max(0, n_patches - n_pre_err)

        # Inspect post-observer outputs for errors and rendered charts
        n_post_err = 0
        n_charts = 0
        for c in post_code_cells:
            for out in c.get("outputs", []):
                if out.get("output_type") == "error":
                    n_post_err += 1
                elif out.get("output_type") == "stream":
                    txt = "".join(out.get("text", []))
                    if "Error executing" in txt or "Traceback" in txt:
                        n_post_err += 1
                elif out.get("output_type") == "display_data" and "image/png" in out.get(
                    "data", {}
                ):
                    n_charts += 1

        post_observer_failed_cells += n_post_err
        total_charts_rendered += n_charts

        # Count post-execution synthesis insights and takeaways
        md_sources = [
            "".join(c.get("source", []))
            for c in nb_post["cells"]
            if c.get("cell_type") == "markdown"
        ]
        n_insights = sum(1 for m in md_sources if m.startswith("**Insight:**"))
        has_takeaways = any("## Key Takeaways" in m for m in md_sources)
        total_insights_generated += n_insights
        if has_takeaways:
            notebooks_with_takeaways += 1

        notebook_reports.append(
            {
                "id": spec["id"],
                "file": os.path.basename(spec["csv"]),
                "code_cells": n_cells,
                "pre_observer_exceptions": n_pre_err,
                "observer_patches_applied": n_patches,
                "patched_cell_indices": patched_cell_indices,
                "post_observer_errors": n_post_err,
                "charts_rendered": n_charts,
                "consultant_insights": n_insights,
                "has_key_takeaways": has_takeaways,
            }
        )

    pre_pass_rate = (
        (total_code_cells - pre_observer_failed_cells) / total_code_cells * 100.0
        if total_code_cells
        else 0.0
    )
    post_pass_rate = (
        (total_code_cells - post_observer_failed_cells) / total_code_cells * 100.0
        if total_code_cells
        else 0.0
    )

    return {
        "notebooks_evaluated": len(notebook_reports),
        "total_code_cells": total_code_cells,
        "pre_observer_pass_rate_pct": round(pre_pass_rate, 2),
        "post_observer_pass_rate_pct": round(post_pass_rate, 2),
        "post_observer_failure_rate_pct": round(100.0 - post_pass_rate, 2),
        "total_observer_patches": total_observer_patches,
        "runtime_exception_fixes": runtime_exception_patches,
        "visual_layout_fixes": visual_layout_patches,
        "total_charts_rendered": total_charts_rendered,
        "total_consultant_insights": total_insights_generated,
        "key_takeaways_coverage_pct": round(
            notebooks_with_takeaways / len(notebook_reports) * 100.0, 2
        )
        if notebook_reports
        else 0.0,
        "notebooks": notebook_reports,
    }


# ---------------------------------------------------------------------------
# Full Harness Orchestrator
# ---------------------------------------------------------------------------
def run_full_evaluation(
    use_live_api: bool = False, verify_pre_exceptions: bool = True
) -> Dict[str, Any]:
    t0 = time.perf_counter()
    profiling_eval = evaluate_ingestion_and_profiling()
    rag_eval = evaluate_rag_retrieval(use_live_api=use_live_api)
    planner_eval = evaluate_planner_compliance()
    execution_eval = evaluate_execution_and_observer(
        verify_pre_exceptions=verify_pre_exceptions
    )
    telemetry_eval = get_telemetry_summary()
    harness_duration_sec = round(time.perf_counter() - t0, 2)

    return {
        "harness_version": "1.2.0",
        "evaluated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "harness_duration_sec": harness_duration_sec,
        "summary": {
            "total_benchmark_datasets": profiling_eval["datasets_evaluated"],
            "total_rows_evaluated": profiling_eval["total_rows_processed"],
            "total_columns_evaluated": profiling_eval["total_columns_profiled"],
            "profiling_latency_p50_ms": profiling_eval["latency_p50_ms"],
            "type_inference_accuracy_pct": profiling_eval["type_inference_accuracy_pct"],
            "rag_hit_rate_at_1_pct": rag_eval["hit_rate_at_1_pct"],
            "rag_recall_at_3_pct": rag_eval["recall_at_3_pct"],
            "rag_mrr": rag_eval["mrr"],
            "planner_schema_validity_pct": planner_eval["analysis_schema_validity_pct"],
            "target_identification_accuracy_pct": planner_eval[
                "target_identification_accuracy_pct"
            ],
            "pre_observer_cell_pass_rate_pct": execution_eval["pre_observer_pass_rate_pct"],
            "post_observer_cell_pass_rate_pct": execution_eval["post_observer_pass_rate_pct"],
            "unhandled_cell_failure_rate_pct": execution_eval["post_observer_failure_rate_pct"],
            "observer_patches_applied": execution_eval["total_observer_patches"],
            "mean_run_cost_usd": telemetry_eval["mean_cost_usd"],
            "mean_e2e_duration_sec": telemetry_eval["mean_duration_sec"],
            "min_e2e_duration_sec": telemetry_eval["min_duration_sec"],
            "max_e2e_duration_sec": telemetry_eval["max_duration_sec"],
            "production_run_success_rate_pct": telemetry_eval["run_success_rate_pct"],
        },
        "ingestion_and_profiling": profiling_eval,
        "rag_retrieval": rag_eval,
        "planner_compliance": planner_eval,
        "execution_and_observer": execution_eval,
        "production_telemetry": telemetry_eval,
    }
