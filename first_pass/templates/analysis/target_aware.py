from typing import List, Any, Optional
from first_pass.schemas import DataProfile
from first_pass.templates.base import AnalysisTemplate

class TargetDistribution(AnalysisTemplate):
    id = "target_distribution"
    @classmethod
    def get_params_schema(cls) -> Any: return {"target": str}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]: return None
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        target = params.get('target', columns[0] if columns else None)
        return (
            f"import seaborn as sns\n"
            f"import matplotlib.pyplot as plt\n"
            f"plt.figure(figsize=(8, 5))\n"
            f"sns.histplot(data=df, x={repr(target)}, kde=True) if df[{repr(target)}].dtype.kind in 'bifc' else sns.countplot(data=df, x={repr(target)})\n"
            f"plt.title(f'Target Distribution: {target}')\n"
            f"plt.tight_layout(); plt.show()"
        )

class TargetCorrRanked(AnalysisTemplate):
    id = "target_corr_ranked"
    @classmethod
    def get_params_schema(cls) -> Any: return {"target": str, "top_k": int}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]: return None
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        target = params.get('target', columns[0] if columns else None)
        top_k = params.get('top_k', 10)
        return (
            f"import pandas as pd\n"
            f"import seaborn as sns\n"
            f"import matplotlib.pyplot as plt\n"
            f"num_df = df.select_dtypes(include=['number'])\n"
            f"if {repr(target)} in num_df.columns:\n"
            f"    corrs = num_df.corr()[{repr(target)}].drop({repr(target)}).sort_values(key=abs, ascending=False).head({top_k})\n"
            f"    plt.figure(figsize=(10, 6))\n"
            f"    sns.barplot(x=corrs.values, y=corrs.index, hue=corrs.index, palette='coolwarm', legend=False)\n"
            f"    plt.title(f'Top {{min({top_k}, len(corrs))}} Correlations with {target}')\n"
            f"    plt.tight_layout(); plt.show()\n"
        )

class MutualInfoRanked(AnalysisTemplate):
    id = "mutual_info_ranked"
    @classmethod
    def get_params_schema(cls) -> Any: return {"target": str, "top_k": int}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]: return None
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        target = params.get('target', columns[0] if columns else None)
        top_k = params.get('top_k', 10)
        return (
            f"from sklearn.feature_selection import mutual_info_regression, mutual_info_classif\n"
            f"import pandas as pd\n"
            f"import seaborn as sns\n"
            f"import matplotlib.pyplot as plt\n"
            f"df_clean = df.dropna()\n"
            f"num_cols = df_clean.select_dtypes(include=['number']).columns.drop({repr(target)}, errors='ignore')\n"
            f"if len(num_cols) > 0 and {repr(target)} in df_clean.columns:\n"
            f"    is_cat = df_clean[{repr(target)}].dtype == 'object' or df_clean[{repr(target)}].nunique() < 10\n"
            f"    mi = mutual_info_classif(df_clean[num_cols], df_clean[{repr(target)}]) if is_cat else mutual_info_regression(df_clean[num_cols], df_clean[{repr(target)}])\n"
            f"    mi_series = pd.Series(mi, index=num_cols).sort_values(ascending=False).head({top_k})\n"
            f"    plt.figure(figsize=(10, 6))\n"
            f"    sns.barplot(x=mi_series.values, y=mi_series.index, hue=mi_series.index, palette='viridis', legend=False)\n"
            f"    plt.title(f'Top Mutual Information with {target}')\n"
            f"    plt.tight_layout(); plt.show()\n"
        )

class TargetRateByCat(AnalysisTemplate):
    id = "target_rate_by_cat"
    @classmethod
    def get_params_schema(cls) -> Any: return {"target": str, "category": str}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]: return None
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        target = params.get('target', columns[0] if columns else None)
        cat = params.get('category', columns[1] if len(columns) > 1 else None)
        return (
            f"import seaborn as sns\n"
            f"import matplotlib.pyplot as plt\n"
            f"rate = df.groupby({repr(cat)})[{repr(target)}].mean().sort_values(ascending=False)\n"
            f"plt.figure(figsize=(10, 6))\n"
            f"sns.barplot(x=rate.values, y=rate.index, hue=rate.index, palette='mako', legend=False)\n"
            f"plt.title(f'Mean {target} by {cat}')\n"
            f"plt.tight_layout(); plt.show()\n"
        )
