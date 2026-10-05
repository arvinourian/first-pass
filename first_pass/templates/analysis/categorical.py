from typing import List, Any, Optional
from first_pass.schemas import DataProfile
from first_pass.templates.base import AnalysisTemplate

class FreqBar(AnalysisTemplate):
    id = "freq_bar"
    @classmethod
    def get_params_schema(cls) -> Any: return {"column": str, "top_n": int}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]:
        return None
        
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        col = params.get('column', columns[0] if columns else None)
        return f"import seaborn as sns; import matplotlib.pyplot as plt\nplt.figure(figsize=(10, 6))\ndf['{col}'].value_counts().nlargest({params.get('top_n', 12)}).plot.bar(color='teal'); plt.xticks(rotation=45, ha=\'right\'); plt.tight_layout(); plt.show()"

class ValueCountsTable(AnalysisTemplate):
    id = "value_counts_table"
    @classmethod
    def get_params_schema(cls) -> Any: return {"column": str, "top_n": int}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]:
        return None
        
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        col = params.get('column', columns[0] if columns else None)
        return f"display(df['{col}'].value_counts(normalize=True).nlargest({params.get('top_n', 10)}) * 100)"

class ParetoChart(AnalysisTemplate):
    id = "pareto_chart"
    @classmethod
    def get_params_schema(cls) -> Any: return {"column": str, "top_n": int}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]:
        return None
        
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        col = params.get('column', columns[0] if columns else None)
        return f"import matplotlib.pyplot as plt\ncounts = df['{col}'].value_counts().nlargest({params.get('top_n', 10)})\nfig, ax = plt.subplots(figsize=(10,6))\nax.bar(counts.index, counts.values, color='teal', alpha=0.7)\nax2 = ax.twinx()\nax2.plot(counts.index, counts.cumsum()/counts.sum()*100, color='orange', marker='D', ms=7, linewidth=2)\nplt.xticks(rotation=45, ha=\'right\'); plt.tight_layout(); plt.show()"

class MultiBar(AnalysisTemplate):
    id = "multi_bar"
    @classmethod
    def get_params_schema(cls) -> Any: return {"columns": list, "top_n": int}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]: return None
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        cols = params.get('columns', columns)
        top_n = params.get('top_n', 10)
        return (
            f"import seaborn as sns; import matplotlib.pyplot as plt; import math\n"
            f"cols = {cols}[:12] # Limit to 12\n"
            f"rows = math.ceil(len(cols) / 3)\n"
            f"fig, axes = plt.subplots(rows, min(3, len(cols)), figsize=(15, 5 * rows))\n"
            f"axes = axes.flatten() if len(cols) > 1 else [axes]\n"
            f"for ax, col in zip(axes, cols):\n"
            f"    counts = df[col].value_counts().nlargest({top_n})\n"
            f"    sns.barplot(x=counts.index, y=counts.values, ax=ax, color='teal')\n"
            f"    ax.set_title(col)\n"
            f"    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')\n"
            f"for ax in axes[len(cols):]: ax.set_visible(False)\n"
            f"plt.tight_layout(); plt.show()"
        )
