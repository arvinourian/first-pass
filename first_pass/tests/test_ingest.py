import pytest
import pandas as pd
import numpy as np
import os
from first_pass.ingest import load_spreadsheet, infer_type, _find_header_row

def test_infer_type():
    # Numeric
    assert infer_type(pd.Series([1, 2, 3, 4.5, np.nan])) == "numeric"
    # Categorical
    assert infer_type(pd.Series(["A", "B", "A", "C", "B"])) == "categorical"
    # Boolean
    assert infer_type(pd.Series([True, False, True, np.nan])) == "boolean"
    # ID
    assert infer_type(pd.Series([1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010, 1011])) == "id_like"
    # Datetime
    assert infer_type(pd.Series(["2023-01-01", "2023-01-02", "2023-01-03"])) == "datetime"
    
def test_find_header_row():
    # Mock dataframe with a title row, empty row, then header
    data = [
        ["Title of the report", np.nan, np.nan],
        [np.nan, np.nan, np.nan],
        ["Col1", "Col2", "Col3"],
        [1, 2, 3],
        [4, 5, 6]
    ]
    df = pd.DataFrame(data)
    assert _find_header_row(df) == 2
