from typing import List, Any, Optional
from first_pass.schemas import DataProfile
from first_pass.templates.base import AnalysisTemplate
import pandas as pd

def _get_cats(columns: List[str], params: dict) -> tuple[str, str]:
    c1 = params.get('row', params.get('x', columns[0] if len(columns) > 0 else 'None'))
    c2 = params.get('col', params.get('stack', columns[1] if len(columns) > 1 else 'None'))
    return c1, c2

class CrosstabTable(AnalysisTemplate):
    id = "crosstab_table"
    @classmethod
    def get_params_schema(cls) -> Any: return {"row": str, "col": str, "normalize": str}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]:
        return None
        
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        row, col = _get_cats(columns, params)
        norm = params.get('normalize', False)
        if isinstance(norm, str):
            if norm.lower() == 'false': norm = False
            elif norm.lower() == 'true': norm = True
        return f"display(pd.crosstab(df['{row}'], df['{col}'], normalize={repr(norm)}))"

class CrosstabHeatmap(AnalysisTemplate):
    id = "crosstab_heatmap"
    @classmethod
    def get_params_schema(cls) -> Any: return {"row": str, "col": str, "normalize": str}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]:
        return None
        
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        row, col = _get_cats(columns, params)
        return (
            f"import seaborn as sns\n"
            f"import matplotlib.pyplot as plt\n"
            f"import pandas as pd\n"
            f"ct = pd.crosstab(df[{repr(row)}], df[{repr(col)}])\n"
            f"width = max(8, ct.shape[1] * 0.7)\n"
            f"height = max(6, ct.shape[0] * 0.5)\n"
            f"plt.figure(figsize=(width, height))\n"
            f"sns.heatmap(ct, annot=True, fmt='g', cmap='Blues')\n"
            f"plt.xticks(rotation=45, ha='right')\n"
            f"plt.yticks(rotation=0)\n"
            f"plt.title(f'{{ct.index.name}} vs {{ct.columns.name}}')\n"
            f"plt.tight_layout(); plt.show()\n"
        )

class StackedBar(AnalysisTemplate):
    id = "stacked_bar"
    @classmethod
    def get_params_schema(cls) -> Any: return {"x": str, "stack": str, "percent": bool}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]:
        return None
        
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        x, stack = _get_cats(columns, params)
        return (
            f"import matplotlib.pyplot as plt\n"
            f"import pandas as pd\n"
            f"ct = pd.crosstab(df[{repr(x)}], df[{repr(stack)}])\n"
            f"width = max(10, ct.shape[0] * 0.5 + 2)\n"
            f"ax = ct.plot(kind='bar', stacked=True, figsize=(width, 6), colormap='viridis')\n"
            f"plt.xticks(rotation=45, ha='right')\n"
            f"plt.legend(title={repr(stack)}, bbox_to_anchor=(1.05, 1), loc='upper left')\n"
            f"plt.tight_layout(); plt.show()\n"
        )


class ChiSquare(AnalysisTemplate):
    id = "chi_square"
    @classmethod
    def get_params_schema(cls) -> Any: return {"row": str, "col": str}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]: return None
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        row = params.get('row', columns[0] if columns else None)
        col = params.get('col', columns[1] if len(columns) > 1 else None)
        return (
            f"import scipy.stats as stats\n"
            f"import pandas as pd\n"
            f"import numpy as np\n"
            f"contingency = pd.crosstab(df[{repr(row)}], df[{repr(col)}])\n"
            f"chi2, p_val, dof, expected = stats.chi2_contingency(contingency)\n"
            f"n = contingency.sum().sum()\n"
            f"min_dim = min(contingency.shape) - 1\n"
            f"cramer_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 and n > 0 else 0\n"
            f"print(f'Chi-square statistic: {{chi2:.4f}}')\n"
            f"print(f'p-value: {{p_val:.4g}}')\n"
            f"print(f\"Cramer's V: {{cramer_v:.4f}}\")\n"
        )
