import pytest
import pandas as pd
import numpy as np
import json
from first_pass.profile import generate_profile, profile_to_json

def test_generate_profile():
    df = pd.DataFrame({
        "id": range(100),
        "value": np.random.randn(100),
        "category": ["A", "B", "C", "D"] * 25,
        "date": pd.date_range("2023-01-01", periods=100),
        "constant": ["yes"] * 100
    })
    
    # Introduce some nulls
    df.loc[0:9, "value"] = np.nan
    
    profile = generate_profile(df)
    
    assert profile.row_count == 100
    assert profile.column_count == 5
    assert not profile.compressed
    
    # Check ID column
    id_col = next(c for c in profile.columns if c.name == "id")
    assert id_col.inferred_type == "id_like"
    assert "likely_id" in id_col.flags
    
    # Check constant column
    const_col = next(c for c in profile.columns if c.name == "constant")
    assert const_col.inferred_type == "categorical"
    assert "constant" in const_col.flags
    
    # Check value column stats
    val_col = next(c for c in profile.columns if c.name == "value")
    assert val_col.inferred_type == "numeric"
    assert val_col.null_percent == 10.0
    assert val_col.min_val is not None
    assert val_col.mean_val is not None
    
    # Check json output
    json_str = profile_to_json(profile)
    parsed = json.loads(json_str)
    assert parsed["row_count"] == 100
    
def test_compression():
    # Create 60 columns
    data = {f"col_{i}": np.random.randn(100) for i in range(60)}
    df = pd.DataFrame(data)
    
    profile = generate_profile(df, max_columns=50)
    assert profile.compressed
    assert len(profile.columns) == 50
