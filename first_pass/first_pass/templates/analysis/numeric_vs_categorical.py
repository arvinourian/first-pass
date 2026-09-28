from typing import List, Any, Optional
from first_pass.schemas import DataProfile
from first_pass.templates.base import AnalysisTemplate

def _get_num_cat(columns: List[str], params: dict) -> tuple[str, str]:
    num = params.get('numeric', columns[0] if len(columns) > 0 else 'None')
    cat = params.get('category', columns[1] if len(columns) > 1 else 'None')
    return num, cat

class GroupedBox(AnalysisTemplate):
    id = "grouped_box"
    @classmethod
    def get_params_schema(cls) -> Any: return {"numeric": str, "category": str, "top_n_groups": int}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]:
        return None
        
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        num, cat = _get_num_cat(columns, params)
        return f"import seaborn as sns; import matplotlib.pyplot as plt\nplt.figure(figsize=(10, 6))\nsns.boxplot(data=df, x='{cat}', y='{num}', hue='{cat}', palette='Set2', legend=False); plt.xticks(rotation=45); plt.show()"

class GroupedViolin(AnalysisTemplate):
    id = "grouped_violin"
    @classmethod
    def get_params_schema(cls) -> Any: return {"numeric": str, "category": str}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]:
        return None
        
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        num, cat = _get_num_cat(columns, params)
        return f"import seaborn as sns; import matplotlib.pyplot as plt\nplt.figure(figsize=(10, 6))\nsns.violinplot(data=df, x='{cat}', y='{num}', hue='{cat}', palette='Set2', legend=False); plt.xticks(rotation=45); plt.show()"

class GroupMeanCi(AnalysisTemplate):
    id = "group_mean_ci"
    @classmethod
    def get_params_schema(cls) -> Any: return {"numeric": str, "category": str}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]:
        return None
        
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        num, cat = _get_num_cat(columns, params)
        return f"import seaborn as sns; import matplotlib.pyplot as plt\nplt.figure(figsize=(10, 6))\nsns.barplot(data=df, x='{cat}', y='{num}', hue='{cat}', palette='Set2', legend=False); plt.xticks(rotation=45); plt.show()"

class StripSwarm(AnalysisTemplate):
    id = "strip_swarm"
    @classmethod
    def get_params_schema(cls) -> Any: return {"numeric": str, "category": str}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]:
        return None
        
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        num, cat = _get_num_cat(columns, params)
        return f"import seaborn as sns; import matplotlib.pyplot as plt\nplt.figure(figsize=(10, 6))\nsns.stripplot(data=df, x='{cat}', y='{num}', hue='{cat}', palette='Set2', legend=False, alpha=0.6, jitter=True); plt.xticks(rotation=45); plt.show()"

class GroupSummaryTable(AnalysisTemplate):
    id = "group_summary_table"
    @classmethod
    def get_params_schema(cls) -> Any: return {"numeric": str, "category": str}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]:
        return None
        
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        num, cat = _get_num_cat(columns, params)
        return f"display(df.groupby('{cat}')['{num}'].agg(['count', 'mean', 'median', 'std']))"
