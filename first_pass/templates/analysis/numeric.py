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
        return f"import seaborn as sns; import matplotlib.pyplot as plt\nplt.figure(figsize=(10, 6))\nsns.histplot(data=df, x='{col}', kde=True, color='teal', line_kws={{'color': 'orange', 'linewidth': 2}})\nplt.tight_layout(); plt.show()"

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
        return f"import seaborn as sns; import matplotlib.pyplot as plt\nplt.figure(figsize=(10, 6))\nsns.histplot(data=df, x='{col}', log_scale=True, color='teal')\nplt.tight_layout(); plt.show()"

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
        return f"import seaborn as sns; import matplotlib.pyplot as plt\nplt.figure(figsize=(10, 6))\nsns.boxplot(data=df[{cols}], color='skyblue')\nplt.xticks(rotation=45, ha=\'right\'); plt.tight_layout(); plt.show()"

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
        return f"import seaborn as sns; import matplotlib.pyplot as plt\nplt.figure(figsize=(8, 6))\nsns.violinplot(data=df, y='{col}', color='teal')\nplt.tight_layout(); plt.show()"

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
        return f"import seaborn as sns; import matplotlib.pyplot as plt\nplt.figure(figsize=(10, 6))\nsns.ecdfplot(data=df, x='{col}', color='teal', linewidth=2)\nplt.tight_layout(); plt.show()"

class MultiHist(AnalysisTemplate):
    id = "multi_hist"
    @classmethod
    def get_params_schema(cls) -> Any: return {"columns": list}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]: return None
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        cols = params.get('columns', columns)
        return (
            f"import seaborn as sns; import matplotlib.pyplot as plt; import math\n"
            f"cols = {cols}[:12] # Limit to 12\n"
            f"rows = math.ceil(len(cols) / 3)\n"
            f"fig, axes = plt.subplots(rows, min(3, len(cols)), figsize=(15, 4 * rows))\n"
            f"axes = axes.flatten() if len(cols) > 1 else [axes]\n"
            f"for ax, col in zip(axes, cols):\n"
            f"    sns.histplot(data=df, x=col, kde=True, color='teal', ax=ax)\n"
            f"    ax.set_title(col)\n"
            f"for ax in axes[len(cols):]: ax.set_visible(False)\n"
            f"plt.tight_layout(); plt.show()"
        )

class RoundingAnomalies(AnalysisTemplate):
    id = "rounding_anomalies"
    @classmethod
    def get_params_schema(cls) -> Any: return {"column": str, "modulo": int}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]: return None
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        col = params.get('column', columns[0] if columns else None)
        mod = params.get('modulo', 1000)
        return (
            f"import pandas as pd\n"
            f"s = df['{col}'].dropna()\n"
            f"exact_pct = (s % {mod} == 0).mean() * 100\n"
            f"print(f\"Share of {{'{col}'}} falling exactly on a multiple of {{{mod}}}: {{exact_pct:.1f}}%\")\n"
            f"print(f\"Skewness of {{'{col}'}}: {{s.skew():.2f}}\")"
        )

class QqPlot(AnalysisTemplate):
    id = "qq_plot"
    @classmethod
    def get_params_schema(cls) -> Any: return {"column": str}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]: return None
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        col = params.get('column', columns[0] if columns else None)
        return (
            f"import matplotlib.pyplot as plt\n"
            f"import scipy.stats as stats\n"
            f"plt.figure(figsize=(8, 6))\n"
            f"stats.probplot(df['{col}'].dropna(), dist='norm', plot=plt)\n"
            f"plt.title(f'Q-Q Plot: {col}')\n"
            f"plt.tight_layout(); plt.show()"
        )
