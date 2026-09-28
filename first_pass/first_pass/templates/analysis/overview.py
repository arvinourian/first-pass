from typing import List, Any, Optional
from first_pass.schemas import DataProfile
from first_pass.templates.base import AnalysisTemplate

class SummaryStats(AnalysisTemplate):
    id = "summary_stats"
    @classmethod
    def get_params_schema(cls) -> Any: return {"columns": list}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]:
        return None
        
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        return f"display(df.describe(include='all'))"

class ColumnOverview(AnalysisTemplate):
    id = "column_overview"
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]:
        return None
        
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        return f"display(df.dtypes)"

class MissingBar(AnalysisTemplate):
    id = "missing_bar"
    @classmethod
    def get_params_schema(cls) -> Any: return {"min_null_pct": float}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]:
        return None
        
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        return "import matplotlib.pyplot as plt\nplt.figure(figsize=(10, 6))\nmissing = df.isnull().sum()\nmissing[missing > 0].plot.bar(color='tomato')\nplt.title('Missing Values Count'); plt.xticks(rotation=45); plt.show()"

class MissingMatrix(AnalysisTemplate):
    id = "missing_matrix"
    @classmethod
    def get_params_schema(cls) -> Any: return {"max_rows_sampled": int}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]:
        return None
        
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        return "import seaborn as sns; import matplotlib.pyplot as plt\nplt.figure(figsize=(10, 6))\nsns.heatmap(df.isnull(), cbar=False, cmap='viridis')\nplt.title('Missing Values Matrix'); plt.show()"

class DuplicateSummary(AnalysisTemplate):
    id = "duplicate_summary"
    @classmethod
    def get_params_schema(cls) -> Any: return {"subset_columns": list}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]:
        return None
        
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        return "print(f'Duplicates: {df.duplicated().sum()}')"

class CardinalityBar(AnalysisTemplate):
    id = "cardinality_bar"
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]:
        return None
        
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        return "import matplotlib.pyplot as plt\nplt.figure(figsize=(10, 6))\ndf.select_dtypes(include=['object', 'category']).nunique().plot.bar(color='teal')\nplt.title('Cardinality (Unique Values) per Categorical Column'); plt.xticks(rotation=45); plt.show()"

class OutlierFlags(AnalysisTemplate):
    id = "outlier_flags"
    @classmethod
    def get_params_schema(cls) -> Any: return {"method": str, "threshold": float}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]:
        return None
        
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        return "import numpy as np\nnum_cols = df.select_dtypes(include=[np.number]).columns\nQ1 = df[num_cols].quantile(0.25)\nQ3 = df[num_cols].quantile(0.75)\nIQR = Q3 - Q1\noutliers = ((df[num_cols] < (Q1 - 1.5 * IQR)) | (df[num_cols] > (Q3 + 1.5 * IQR))).sum()\ndisplay(outliers[outliers > 0])"
