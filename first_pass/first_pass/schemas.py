from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ColumnProfile(BaseModel):
    name: str
    inferred_type: str  # numeric, categorical, datetime, boolean, free_text, id_like
    null_percent: float
    unique_count: int
    top_values: Optional[List[Any]] = None
    min_val: Optional[float] = None
    max_val: Optional[float] = None
    mean_val: Optional[float] = None
    median_val: Optional[float] = None
    std_val: Optional[float] = None
    date_range: Optional[Dict[str, str]] = None
    flags: List[str] = Field(default_factory=list) # constant, likely_id, likely_currency, mixed_types, high_cardinality

class DataProfile(BaseModel):
    row_count: int
    column_count: int
    columns: List[ColumnProfile]
    compressed: bool = False

class CleaningStep(BaseModel):
    template_id: str
    columns: List[str]
    params: str = "{}"
    rationale: str
    playbook_ids: List[str]

class CleaningPlan(BaseModel):
    steps: List[CleaningStep]

class AnalysisItem(BaseModel):
    template_id: str
    columns: List[str]
    params: str = "{}"
    rationale: str
    playbook_ids: List[str]

class AnalysisSection(BaseModel):
    title: str
    description: str
    analyses: List[AnalysisItem]

class FurtherAnalysis(BaseModel):
    template_id: str
    columns: List[str]
    rationale: str

class AnalysisPlan(BaseModel):
    target_variables: List[str] = Field(default_factory=list, description="Primary outcome variables (e.g. price, churn)")
    sections: List[AnalysisSection]
    further_analyses: List[FurtherAnalysis] = Field(default_factory=list)
