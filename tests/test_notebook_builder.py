import os
import json
import pytest
import pandas as pd
from first_pass.schemas import (
    DataProfile,
    ColumnProfile,
    CleaningPlan,
    CleaningStep,
    AnalysisPlan,
    AnalysisSection,
    AnalysisItem,
)
from first_pass.notebook_builder import NotebookBuilder
from first_pass.export import export_to_py


def test_builder_and_export(tmp_path):
    # Create mock data
    df_path = os.path.join(tmp_path, "mock_data.csv")
    pd.DataFrame({"A": [1, 2, None, 4], "B": ["x", "y", "x", "z"]}).to_csv(df_path, index=False)

    # Mock profiles and plans
    raw_prof = DataProfile(
        row_count=4,
        column_count=2,
        columns=[
            ColumnProfile(name="A", inferred_type="numeric", null_percent=25.0, unique_count=3),
            ColumnProfile(name="B", inferred_type="categorical", null_percent=0.0, unique_count=3),
        ],
    )

    cleaning_plan = CleaningPlan(
        steps=[
            CleaningStep(
                template_id="fill_nulls",
                columns=["A"],
                params=json.dumps({"fill_value": 0}),
                rationale="Fill missing numeric values with 0.",
                playbook_ids=["clean_numeric_nulls"],
            )
        ]
    )

    analysis_plan = AnalysisPlan(
        target_variables=["A"],
        sections=[
            AnalysisSection(
                title="Distribution Overview",
                description="Overview of column distributions.",
                analyses=[
                    AnalysisItem(
                        title="Distribution of A",
                        template_id="histogram_kde",
                        columns=["A"],
                        params="{}",
                        rationale="See the distribution of A.",
                        playbook_ids=["numeric-dist"],
                    )
                ],
            )
        ],
    )

    builder = NotebookBuilder(filename=str(df_path))
    nb_path = os.path.join(tmp_path, "test_output.ipynb")

    builder.build_notebook(
        raw_profile=raw_prof,
        cleaning_plan=cleaning_plan,
        engineering_plan=None,
        cleaned_profile=raw_prof,
        analysis_plan=analysis_plan,
        llm_usage=[
            {
                "stage": "pass1",
                "model": "gemini-3.8-flash",
                "input_tokens": 100,
                "output_tokens": 50,
                "total_tokens": 150,
                "latency_ms": 1000,
                "cost": 0.000125,
            }
        ],
        raw_cleaning_json=cleaning_plan.model_dump_json(indent=2),
        raw_analysis_json=analysis_plan.model_dump_json(indent=2),
        output_path=str(nb_path),
    )

    assert os.path.exists(nb_path)

    with open(nb_path, "r", encoding="utf-8") as f:
        nb_json = json.load(f)
    assert len(nb_json.get("cells", [])) > 0
    assert any(c.get("cell_type") == "code" for c in nb_json["cells"])

    py_path = export_to_py(str(nb_path), str(tmp_path))
    assert os.path.exists(py_path)
