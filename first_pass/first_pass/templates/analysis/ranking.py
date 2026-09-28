from typing import List, Any, Optional
from first_pass.schemas import DataProfile
from first_pass.templates.base import AnalysisTemplate

def _get_ranking_cols(columns: List[str], params: dict) -> tuple[str, str]:
    entity = params.get('entity', columns[0] if len(columns)>0 else 'None')
    value = params.get('value', columns[1] if len(columns)>1 else 'None')
    return entity, value

class TopBottomN(AnalysisTemplate):
    id = "top_bottom_n"
    @classmethod
    def get_params_schema(cls) -> Any: return {"entity": str, "value": str, "n": int, "agg": str}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]:
        return None
        
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        entity, value = _get_ranking_cols(columns, params)
        return f"import matplotlib.pyplot as plt\nplt.figure(figsize=(10, 6))\ndf.groupby('{entity}')['{value}'].{params.get('agg', 'sum')}().nlargest({params.get('n', 10)}).plot.bar(color='teal')\nplt.xticks(rotation=45); plt.show()"

class CumulativeShare(AnalysisTemplate):
    id = "cumulative_share"
    @classmethod
    def get_params_schema(cls) -> Any: return {"entity": str, "value": str}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]:
        return None
        
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        entity, value = _get_ranking_cols(columns, params)
        return f"import matplotlib.pyplot as plt\nplt.figure(figsize=(10, 6))\nsums = df.groupby('{entity}')['{value}'].sum().sort_values(ascending=False)\n(sums.cumsum() / sums.sum()).plot(color='teal', linewidth=2)\nplt.title('Cumulative Share of {value} by {entity}'); plt.show()"

class LorenzGini(AnalysisTemplate):
    id = "lorenz_gini"
    @classmethod
    def get_params_schema(cls) -> Any: return {"entity": str, "value": str}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]:
        return None
        
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        entity, value = _get_ranking_cols(columns, params)
        return f"import numpy as np; import matplotlib.pyplot as plt\nplt.figure(figsize=(8, 8))\nvals = df.groupby('{entity}')['{value}'].sum().sort_values().values\ncum = np.cumsum(vals) / np.sum(vals)\nplt.plot(np.linspace(0,1,len(cum)), cum, color='teal', linewidth=2, label='Lorenz Curve')\nplt.plot([0,1],[0,1],'--', color='orange', label='Perfect Equality')\nplt.legend(); plt.show()"
