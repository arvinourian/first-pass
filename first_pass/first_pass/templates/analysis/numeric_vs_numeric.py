from typing import List, Any, Optional
from first_pass.schemas import DataProfile
from first_pass.templates.base import AnalysisTemplate

class CorrHeatmap(AnalysisTemplate):
    id = "corr_heatmap"
    @classmethod
    def get_params_schema(cls) -> Any: return {"columns": list, "methods": list}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]:
        return None
        
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        cols_str = str(columns) if columns else "df.select_dtypes('number').columns"
        return f"import seaborn as sns; import matplotlib.pyplot as plt\ncorr = df[{cols_str}].corr(numeric_only=True)\nplt.figure(figsize=(8, 6))\nsns.heatmap(corr, annot=True, cmap='coolwarm', vmin=-1, vmax=1, center=0, square=True)\nplt.show()"

class CorrRankedBar(AnalysisTemplate):
    id = "corr_ranked_bar"
    @classmethod
    def get_params_schema(cls) -> Any: return {"top_k_pairs": int}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]:
        return None
        
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        cols_str = str(columns) if columns else "df.select_dtypes('number').columns"
        return f"import matplotlib.pyplot as plt\ncorr = df[{cols_str}].corr(numeric_only=True).unstack().sort_values(ascending=False).drop_duplicates()\ncorr[corr < 1].head(10).plot.bar(color='teal'); plt.ylabel('Correlation'); plt.show()"

class Scatter(AnalysisTemplate):
    id = "scatter"
    @classmethod
    def get_params_schema(cls) -> Any: return {"x": str, "y": str, "hue": str}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]:
        return None
        
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        x = params.get('x', columns[0] if len(columns) > 0 else 'None')
        y = params.get('y', columns[1] if len(columns) > 1 else 'None')
        hue_arg = f", hue='{params['hue']}'" if params.get('hue') else ""
        return f"import seaborn as sns; import matplotlib.pyplot as plt\nplt.figure(figsize=(8, 6))\nsns.scatterplot(data=df, x='{x}', y='{y}'{hue_arg}, alpha=0.6)\nplt.show()"

class ScatterRegression(AnalysisTemplate):
    id = "scatter_regression"
    @classmethod
    def get_params_schema(cls) -> Any: return {"x": str, "y": str}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]:
        return None
        
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        x = params.get('x', columns[0] if len(columns) > 0 else 'None')
        y = params.get('y', columns[1] if len(columns) > 1 else 'None')
        return f"import seaborn as sns; import matplotlib.pyplot as plt\nplt.figure(figsize=(8, 6))\nsns.regplot(data=df, x='{x}', y='{y}', scatter_kws={{'alpha':0.5}}, line_kws={{'color':'red'}})\nplt.show()"

class Hexbin(AnalysisTemplate):
    id = "hexbin"
    @classmethod
    def get_params_schema(cls) -> Any: return {"x": str, "y": str, "gridsize": int}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]:
        return None
        
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        x = params.get('x', columns[0] if len(columns) > 0 else 'None')
        y = params.get('y', columns[1] if len(columns) > 1 else 'None')
        return f"import matplotlib.pyplot as plt\nplt.figure(figsize=(8, 6))\ndf.plot.hexbin(x='{x}', y='{y}', gridsize={params.get('gridsize', 30)}, cmap='viridis', sharex=False)\nplt.show()"
