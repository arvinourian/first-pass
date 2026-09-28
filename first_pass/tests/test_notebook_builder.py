import os
import pytest
import pandas as pd
from first_pass.schemas import DataProfile, ColumnProfile, CleaningPlan, CleaningStep, AnalysisPlan, AnalysisItem
from first_pass.notebook_builder import NotebookBuilder
from first_pass.export import export_notebook

def test_builder_and_export(tmp_path):
    # Create mock data
    df_path = os.path.join(tmp_path, "mock_data.csv")
    pd.DataFrame({"A": [1, 2, None, 4], "B": ["x", "y", "x", "z"]}).to_csv(df_path, index=False)
    
    # Mock profiles and plans
    raw_prof = DataProfile(
        row_count=4, column_count=2,
        columns=[
            ColumnProfile(name="A", inferred_type="numeric", null_percent=25.0, unique_count=3),
            ColumnProfile(name="B", inferred_type="categorical", null_percent=0.0, unique_count=3)
        ]
    )
    
    cleaning_plan = CleaningPlan(steps=[
        CleaningStep(
            template_id="fill_nulls",
            columns=["A"],
            params={"fill_value": 0},
            rationale="Fill missing numeric values with 0.",
            playbook_ids=["clean_numeric_nulls"]
        )
    ])
    
    analysis_plan = AnalysisPlan(analyses=[
        AnalysisItem(
            template_id="univariate_distribution",
            columns=["A"],
            rationale="See the distribution of A.",
            playbook_ids=["analyze_numeric"]
        )
    ])
    
    builder = NotebookBuilder(filename=df_path)
    nb_path = os.path.join(tmp_path, "test_output.ipynb")
    
    builder.build_notebook(
        raw_profile=raw_prof,
        cleaning_plan=cleaning_plan,
        cleaned_profile=raw_prof, # using same for mock
        analysis_plan=analysis_plan,
        llm_usage=[{"stage": "pass1", "model": "test", "input_tokens": 100, "output_tokens": 50, "latency_ms": 1000, "cost": 0.001}],
        raw_cleaning_json="{}",
        raw_analysis_json="{}",
        output_path=nb_path
    )
    
    assert os.path.exists(nb_path)
    
    # Test execution
    executed_path = os.path.join(tmp_path, "test_output_exec.ipynb")
    builder.execute_notebook(nb_path, executed_path)
    assert os.path.exists(executed_path)
    
    # Test export (may fail if playwright isn't installed, but we should test if it runs)
    export_notebook(executed_path, tmp_path)
    # Check that .py exists
    assert os.path.exists(os.path.join(tmp_path, "test_output_exec.py"))
