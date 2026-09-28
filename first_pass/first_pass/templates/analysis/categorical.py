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
        return f"import seaborn as sns; import matplotlib.pyplot as plt\nplt.figure(figsize=(10, 6))\ndf['{col}'].value_counts().nlargest({params.get('top_n', 12)}).plot.bar(color='teal'); plt.xticks(rotation=45); plt.show()"

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
        return f"import matplotlib.pyplot as plt\ncounts = df['{col}'].value_counts().nlargest({params.get('top_n', 10)})\nfig, ax = plt.subplots(figsize=(10,6))\nax.bar(counts.index, counts.values, color='teal', alpha=0.7)\nax2 = ax.twinx()\nax2.plot(counts.index, counts.cumsum()/counts.sum()*100, color='orange', marker='D', ms=7, linewidth=2)\nplt.xticks(rotation=45); plt.show()"
