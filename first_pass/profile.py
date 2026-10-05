import pandas as pd
import numpy as np
from typing import Dict, Any, List
from .schemas import DataProfile, ColumnProfile
from .ingest import infer_type
import warnings

def generate_profile(df: pd.DataFrame, max_columns: int = 50) -> DataProfile:
    """Generates a compact JSON-serializable profile of the dataset."""
    row_count = len(df)
    col_count = len(df.columns)
    
    columns_profile = []
    
    # Process each column
    for col in df.columns:
        series = df[col]
        
        # Calculate base stats
        null_count = series.isna().sum()
        null_percent = round((null_count / row_count) * 100, 2) if row_count > 0 else 0.0
        
        # Drop nulls for further analysis
        s = series.dropna()
        unique_count = s.nunique()
        
        inferred = infer_type(series)
        
        # Flags
        flags = []
        if unique_count == 1:
            flags.append("constant")
        if inferred == "id_like":
            flags.append("likely_id")
        if unique_count > min(100, row_count * 0.9) and inferred == "categorical":
            flags.append("high_cardinality")
            
        # Currency check
        if inferred == "categorical" and s.dtype == 'object':
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                if s.astype(str).str.contains(r'^\$?\s*\d+[,\.]?\d*\s*$').mean() > 0.8:
                    flags.append("likely_currency")
        
        # Mixed types
        if s.apply(type).nunique() > 1:
            flags.append("mixed_types")
            
        col_prof = ColumnProfile(
            name=str(col),
            inferred_type=inferred,
            null_percent=null_percent,
            unique_count=unique_count,
            flags=flags
        )
        
        # Type-specific stats
        if inferred == "numeric" and pd.api.types.is_numeric_dtype(series):
            col_prof.min_val = float(s.min()) if not s.empty else None
            col_prof.max_val = float(s.max()) if not s.empty else None
            col_prof.mean_val = float(s.mean()) if not s.empty else None
            col_prof.median_val = float(s.median()) if not s.empty else None
            col_prof.std_val = float(s.std()) if not s.empty and len(s) > 1 else None
            
        elif inferred in ["categorical", "boolean", "likely_currency"]:
            if not s.empty:
                top_v = s.value_counts().head(5).index.tolist()
                # Make JSON serializable
                col_prof.top_values = [str(v) if pd.notna(v) else None for v in top_v]
                
        elif inferred == "datetime":
            try:
                parsed = pd.to_datetime(s, errors='coerce').dropna()
                if not parsed.empty:
                    col_prof.date_range = {
                        "start": parsed.min().isoformat(),
                        "end": parsed.max().isoformat()
                    }
            except:
                pass
                
        columns_profile.append(col_prof)
        
    compressed = False
    # Compress if too many columns
    if len(columns_profile) > max_columns:
        compressed = True
        # Rank by signal:
        # High signal: low null rate, not constant, not ID
        def score_column(cp: ColumnProfile) -> float:
            score = 100.0
            score -= cp.null_percent
            if "constant" in cp.flags:
                score -= 50
            if "likely_id" in cp.flags:
                score -= 30
            return score
            
        columns_profile.sort(key=score_column, reverse=True)
        # Keep top max_columns
        columns_profile = columns_profile[:max_columns]

    return DataProfile(
        row_count=row_count,
        column_count=col_count,
        columns=columns_profile,
        compressed=compressed
    )

def profile_to_json(profile: DataProfile) -> str:
    """Returns the profile as a compact JSON string."""
    return profile.model_dump_json(exclude_none=True, indent=2)
