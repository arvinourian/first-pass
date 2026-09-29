from typing import List, Any, Optional
from first_pass.schemas import DataProfile
from first_pass.templates.base import AnalysisTemplate

class FinReturns(AnalysisTemplate):
    id = "fin_returns"
    @classmethod
    def get_params_schema(cls) -> Any: return {"date": str, "price": str, "window": int}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]: return None
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        date = params.get('date', columns[0] if columns else None)
        price = params.get('price', columns[1] if len(columns) > 1 else None)
        window = params.get('window', 30)
        return (
            f"import pandas as pd\n"
            f"import matplotlib.pyplot as plt\n"
            f"ts = df.set_index({repr(date)})[{repr(price)}].dropna().sort_index()\n"
            f"returns = ts.pct_change()\n"
            f"vol = returns.rolling({window}).std() * (252**0.5)\n"
            f"fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)\n"
            f"returns.plot(ax=ax1, title='Daily Returns', alpha=0.7)\n"
            f"vol.plot(ax=ax2, title=f'{window}-Period Rolling Volatility (Annualized)', color='orange')\n"
            f"plt.tight_layout(); plt.show()\n"
        )

class CohortRetention(AnalysisTemplate):
    id = "cohort_retention"
    @classmethod
    def get_params_schema(cls) -> Any: return {"user_id": str, "signup_date": str, "activity_date": str, "freq": str}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]: return None
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        user = params.get('user_id')
        signup = params.get('signup_date')
        activity = params.get('activity_date')
        freq = params.get('freq', 'M')
        return (
            f"import pandas as pd\n"
            f"import seaborn as sns\n"
            f"import matplotlib.pyplot as plt\n"
            f"import numpy as np\n"
            f"df_c = df.dropna(subset=[{repr(user)}, {repr(signup)}, {repr(activity)}]).copy()\n"
            f"df_c['cohort'] = pd.to_datetime(df_c[{repr(signup)}]).dt.to_period({repr(freq)})\n"
            f"df_c['activity_period'] = pd.to_datetime(df_c[{repr(activity)}]).dt.to_period({repr(freq)})\n"
            f"df_c['period_diff'] = (df_c['activity_period'] - df_c['cohort']).apply(lambda x: x.n)\n"
            f"cohort_data = df_c.groupby(['cohort', 'period_diff'])[{repr(user)}].nunique().unstack(1)\n"
            f"retention = cohort_data.divide(cohort_data[0], axis=0)\n"
            f"plt.figure(figsize=(12, 8))\n"
            f"sns.heatmap(retention, annot=True, fmt='.0%', cmap='YlGnBu')\n"
            f"plt.title('Cohort Retention Heatmap')\n"
            f"plt.tight_layout(); plt.show()\n"
        )

class Funnel(AnalysisTemplate):
    id = "funnel"
    @classmethod
    def get_params_schema(cls) -> Any: return {"stages": list, "user_id": str}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]: return None
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        stages = params.get('stages', columns)
        user = params.get('user_id')
        return (
            f"import matplotlib.pyplot as plt\n"
            f"import pandas as pd\n"
            f"counts = [df.dropna(subset=[stage])[{repr(user)}].nunique() for stage in {stages}] if {repr(user)} else [df[stage].sum() if pd.api.types.is_numeric_dtype(df[stage]) else df[stage].notna().sum() for stage in {stages}]\n"
            f"pcts = [100.0] + [counts[i]/counts[i-1]*100 if counts[i-1]>0 else 0 for i in range(1, len(counts))]\n"
            f"plt.figure(figsize=(10, 6))\n"
            f"bars = plt.barh({stages}, counts, color='teal')\n"
            f"for bar, pct in zip(bars, pcts):\n"
            f"    plt.text(bar.get_width(), bar.get_y() + bar.get_height()/2, f' {{pct:.1f}}%', va='center')\n"
            f"plt.gca().invert_yaxis()\n"
            f"plt.title('Funnel Analysis')\n"
            f"plt.tight_layout(); plt.show()\n"
        )

class LikertDiverging(AnalysisTemplate):
    id = "likert_diverging"
    @classmethod
    def get_params_schema(cls) -> Any: return {"columns": list, "scale_order": list}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]: return None
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        cols = params.get('columns', columns)
        scale = params.get('scale_order', ['Strongly Disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly Agree'])
        return (
            f"import pandas as pd\n"
            f"import matplotlib.pyplot as plt\n"
            f"data = {{col: df[col].value_counts() for col in {cols}}}\n"
            f"df_likert = pd.DataFrame(data).T\n"
            f"for s in {scale}:\n"
            f"    if s not in df_likert.columns: df_likert[s] = 0\n"
            f"df_likert = df_likert[{scale}].fillna(0)\n"
            f"df_likert.div(df_likert.sum(axis=1), axis=0).plot(kind='barh', stacked=True, figsize=(10, 6), colormap='RdYlGn')\n"
            f"plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')\n"
            f"plt.title('Likert Scale Responses')\n"
            f"plt.tight_layout(); plt.show()\n"
        )

class RfmTable(AnalysisTemplate):
    id = "rfm_table"
    @classmethod
    def get_params_schema(cls) -> Any: return {"customer_id": str, "date": str, "amount": str}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]: return None
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        cust = params.get('customer_id')
        date = params.get('date')
        amt = params.get('amount')
        return (
            f"import pandas as pd\n"
            f"df_r = df.dropna(subset=[{repr(cust)}, {repr(date)}, {repr(amt)}]).copy()\n"
            f"df_r[{repr(date)}] = pd.to_datetime(df_r[{repr(date)}])\n"
            f"max_date = df_r[{repr(date)}].max()\n"
            f"rfm = df_r.groupby({repr(cust)}).agg({{\n"
            f"    {repr(date)}: lambda x: (max_date - x.max()).days,\n"
            f"    {repr(cust)}: 'count',\n"
            f"    {repr(amt)}: 'sum'\n"
            f"}}).rename(columns={{{repr(date)}: 'Recency', {repr(cust)}: 'Frequency', {repr(amt)}: 'Monetary'}})\n"
            f"print(rfm.describe())\n"
            f"print('\nTop 5 by Monetary Value:')\n"
            f"print(rfm.sort_values('Monetary', ascending=False).head())\n"
        )
