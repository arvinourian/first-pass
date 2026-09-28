import pandas as pd
import numpy as np
import os
import warnings

def load_spreadsheet(filepath: str) -> pd.DataFrame:
    """Loads a spreadsheet and attempts to find the correct header row."""
    ext = os.path.splitext(filepath)[1].lower()
    
    if ext == '.csv':
        df_raw = pd.read_csv(filepath, header=None, nrows=50, on_bad_lines='skip')
        header_idx = _find_header_row(df_raw)
        df = pd.read_csv(filepath, header=header_idx, on_bad_lines='skip')
    elif ext in ['.xls', '.xlsx']:
        df_raw = pd.read_excel(filepath, header=None, nrows=50)
        header_idx = _find_header_row(df_raw)
        df = pd.read_excel(filepath, header=header_idx)
    elif ext == '.parquet':
        df = pd.read_parquet(filepath)
    else:
        raise ValueError(f"Unsupported file format: {ext}")
        
    # Clean up column names
    df.columns = [str(c).strip() for c in df.columns]
    
    return df

def _find_header_row(df_raw: pd.DataFrame) -> int:
    """Heuristic to find the header row by looking for a row with strings and few nulls."""
    best_idx = 0
    max_score = -1
    for idx, row in df_raw.iterrows():
        # count non-null string values
        str_count = sum(isinstance(v, str) for v in row if pd.notna(v))
        notna_count = row.notna().sum()
        score = str_count + (notna_count * 0.1)
        if score > max_score:
            max_score = score
            best_idx = idx
            
        # If we find a row where almost all columns are strings, it's likely the header
        if str_count == len(row) and notna_count > 0:
            return idx
            
    return best_idx

def infer_type(series: pd.Series) -> str:
    """
    Infers the logical type of a pandas Series.
    Returns one of: numeric, categorical, datetime, boolean, free_text, id_like
    """
    if series.empty:
        return "categorical"
        
    # Drop nulls for inference
    s = series.dropna()
    if s.empty:
        return "categorical"
        
    num_unique = s.nunique()
    total = len(s)
    
    # Boolean
    if set(s.unique()).issubset({True, False, 1, 0, 'True', 'False', 'true', 'false', 'Y', 'N', 'Yes', 'No'}):
        if num_unique <= 2:
            return "boolean"
            
    # Datetime
    if pd.api.types.is_datetime64_any_dtype(s):
        return "datetime"
    
    # Try converting strings to datetime
    if s.dtype == 'object':
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                sample = s.iloc[:min(100, len(s))]
                # Basic check if it looks like date, prevent random numbers parsing as dates
                if sample.astype(str).str.match(r'^[\d/\-:\. T]+[a-zA-Z]*$').mean() > 0.8:
                    parsed = pd.to_datetime(sample, errors='coerce')
                    if parsed.notna().sum() > 0.8 * len(sample):
                        return "datetime"
        except:
            pass
            
    # Numeric
    if pd.api.types.is_numeric_dtype(s):
        if pd.api.types.is_integer_dtype(s) and num_unique == total and total > 10:
            return "id_like"
        return "numeric"
        
    # Text-based inference
    if s.dtype == 'object':
        if num_unique == total and total > 10:
            avg_len = s.astype(str).str.len().mean()
            if avg_len < 50:
                return "id_like"
                
        if num_unique < 20 or num_unique / total < 0.2:
            return "categorical"
            
        avg_len = s.astype(str).str.len().mean()
        if avg_len > 50:
            return "free_text"
            
        return "categorical"
        
    return "categorical"
