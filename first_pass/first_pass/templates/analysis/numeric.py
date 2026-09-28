from typing import List, Any, Optional
from first_pass.schemas import DataProfile
from first_pass.templates.base import AnalysisTemplate

class HistogramKde(AnalysisTemplate):
    id = "histogram_kde"
    @classmethod
    def get_params_schema(cls) -> Any: return {"column": str, "bins": int}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]:
        return None
        
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        col = params.get('column', columns[0] if columns else None)
        return f"import seaborn as sns; import matplotlib.pyplot as plt\nplt.figure(figsize=(10, 6))\nsns.histplot(data=df, x='{col}', kde=True, color='teal', line_kws={{'color': 'orange', 'linewidth': 2}})\nplt.show()"

class HistogramLog(AnalysisTemplate):
    id = "histogram_log"
    @classmethod
    def get_params_schema(cls) -> Any: return {"column": str, "bins": int}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]:
        return None
        
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        col = params.get('column', columns[0] if columns else None)
        return f"import seaborn as sns; import matplotlib.pyplot as plt\nplt.figure(figsize=(10, 6))\nsns.histplot(data=df, x='{col}', log_scale=True, color='teal')\nplt.show()"

class BoxMulti(AnalysisTemplate):
    id = "box_multi"
    @classmethod
    def get_params_schema(cls) -> Any: return {"columns": list}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]:
        return None
        
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        cols = params.get('columns', columns)
        return f"import seaborn as sns; import matplotlib.pyplot as plt\nplt.figure(figsize=(10, 6))\nsns.boxplot(data=df[{cols}], palette='Set2')\nplt.xticks(rotation=45); plt.show()"

class Violin(AnalysisTemplate):
    id = "violin"
    @classmethod
    def get_params_schema(cls) -> Any: return {"column": str}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]:
        return None
        
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        col = params.get('column', columns[0] if columns else None)
        return f"import seaborn as sns; import matplotlib.pyplot as plt\nplt.figure(figsize=(8, 6))\nsns.violinplot(data=df, y='{col}', color='teal')\nplt.show()"

class Ecdf(AnalysisTemplate):
    id = "ecdf"
    @classmethod
    def get_params_schema(cls) -> Any: return {"column": str}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]:
        return None
        
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        col = params.get('column', columns[0] if columns else None)
        return f"import seaborn as sns; import matplotlib.pyplot as plt\nplt.figure(figsize=(10, 6))\nsns.ecdfplot(data=df, x='{col}', color='teal', linewidth=2)\nplt.show()"
