from typing import List, Any, Optional
from first_pass.schemas import DataProfile
from first_pass.templates.base import AnalysisTemplate

def _get_ts(columns, params):
    d = params.get('date', columns[0] if len(columns)>0 else 'None')
    v = params.get('value', columns[1] if len(columns)>1 else 'None')
    return d, v

class LineTime(AnalysisTemplate):
    id = "line_time"
    @classmethod
    def get_params_schema(cls) -> Any: return {"date": str, "value": str, "agg": str}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]: return None
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        d, v = _get_ts(columns, params)
        return f"import matplotlib.pyplot as plt\nplt.figure(figsize=(12, 6))\ndf.groupby(pd.to_datetime(df['{d}']))['{v}'].{params.get('agg', 'sum')}().plot(kind='line', color='teal', linewidth=2)\nplt.title('{v} over time'); plt.tight_layout(); plt.show()"

class ResampleAgg(AnalysisTemplate):
    id = "resample_agg"
    @classmethod
    def get_params_schema(cls) -> Any: return {"date": str, "value": str, "freq": str, "agg": str}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]: return None
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        d, v = _get_ts(columns, params)
        return f"import matplotlib.pyplot as plt\nplt.figure(figsize=(12, 6))\ndf.set_index(pd.to_datetime(df['{d}']))['{v}'].resample('ME' if '{params.get('freq', 'D')}' == 'M' else '{params.get('freq', 'D')}').{params.get('agg', 'sum')}().plot(color='teal', linewidth=2)\nplt.title('Resampled {v}'); plt.tight_layout(); plt.show()"

class RollingMean(AnalysisTemplate):
    id = "rolling_mean"
    @classmethod
    def get_params_schema(cls) -> Any: return {"date": str, "value": str, "window": int}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]: return None
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        d, v = _get_ts(columns, params)
        return f"import matplotlib.pyplot as plt\nplt.figure(figsize=(12, 6))\nts = df.set_index(pd.to_datetime(df['{d}']))['{v}'].sort_index()\nts.plot(alpha=0.4, color='gray', label='Raw')\nts.rolling(window={params.get('window', 7)}).mean().plot(color='orange', linewidth=2, label='Rolling')\nplt.legend(); plt.tight_layout(); plt.show()"

class SmallMultiplesTime(AnalysisTemplate):
    id = "small_multiples_time"
    @classmethod
    def get_params_schema(cls) -> Any: return {"date": str, "value": str, "category": str}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]: return None
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        d, v = _get_ts(columns, params)
        c = params.get('category', columns[2] if len(columns)>2 else 'None')
        return f"import seaborn as sns; import matplotlib.pyplot as plt\ng = sns.FacetGrid(df, col='{c}', col_wrap=4, height=4, aspect=1.5)\ng.map_dataframe(sns.lineplot, x='{d}', y='{v}', color='teal')\nplt.tight_layout(); plt.show()"

class SeasonalityHeatmap(AnalysisTemplate):
    id = "seasonality_heatmap"
    @classmethod
    def get_params_schema(cls) -> Any: return {"date": str, "value": str}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]: return None
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        d, v = _get_ts(columns, params)
        return f"import seaborn as sns; import matplotlib.pyplot as plt; import pandas as pd\ndf_temp = df.copy()\ndf_temp['month'] = pd.to_datetime(df_temp['{d}']).dt.month\ndf_temp['year'] = pd.to_datetime(df_temp['{d}']).dt.year\npivot = df_temp.pivot_table(index='month', columns='year', values='{v}', aggfunc='mean')\nplt.figure(figsize=(10, 6))\nsns.heatmap(pivot, cmap='YlGnBu', annot=True, fmt='.1f')\nplt.tight_layout(); plt.show()"

class PeriodCompare(AnalysisTemplate):
    id = "period_compare"
    @classmethod
    def get_params_schema(cls) -> Any: return {"date": str, "value": str, "period": str}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]: return None
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        d, v = _get_ts(columns, params)
        return f"import matplotlib.pyplot as plt; import pandas as pd\ndf_temp = df.copy()\ndf_temp['year'] = pd.to_datetime(df_temp['{d}']).dt.year\ndf_temp['dayofyear'] = pd.to_datetime(df_temp['{d}']).dt.dayofyear\npivot = df_temp.pivot_table(index='dayofyear', columns='year', values='{v}', aggfunc='mean')\nplt.figure(figsize=(12, 6))\npivot.plot(ax=plt.gca(), colormap='viridis')\nplt.title('Year over Year Comparison')\nplt.tight_layout(); plt.show()"

class PctChange(AnalysisTemplate):
    id = "pct_change"
    @classmethod
    def get_params_schema(cls) -> Any: return {"date": str, "value": str, "freq": str}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]: return None
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        d, v = _get_ts(columns, params)
        return f"import matplotlib.pyplot as plt\nplt.figure(figsize=(12, 6))\ndf.set_index(pd.to_datetime(df['{d}']))['{v}'].resample('ME' if params.get('freq', 'ME') == 'M' else params.get('freq', 'ME')).sum().pct_change().plot(kind='bar', color='teal')\nplt.title('Period-over-Period % Change'); plt.tight_layout(); plt.show()"

class CumulativeSum(AnalysisTemplate):
    id = "cumulative_sum"
    @classmethod
    def get_params_schema(cls) -> Any: return {"date": str, "value": str}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]: return None
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        d, v = _get_ts(columns, params)
        return f"import matplotlib.pyplot as plt\nplt.figure(figsize=(12, 6))\ndf.sort_values('{d}').set_index('{d}')['{v}'].cumsum().plot(color='teal', linewidth=2)\nplt.title('Cumulative Sum of {v}'); plt.tight_layout(); plt.show()"

class TimestampGaps(AnalysisTemplate):
    id = "timestamp_gaps"
    @classmethod
    def get_params_schema(cls) -> Any: return {"date": str}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]: return None
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        d = params.get('date', columns[0] if len(columns)>0 else 'None')
        return f"import matplotlib.pyplot as plt; import pandas as pd\ndiff = pd.to_datetime(df['{d}']).sort_values().diff()\ndisplay(diff.value_counts().head())"

class StackedAreaTime(AnalysisTemplate):
    id = "stacked_area_time"
    @classmethod
    def get_params_schema(cls) -> Any: return {"date": str, "value": str, "category": str}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]: return None
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        d, v = _get_ts(columns, params)
        c = params.get('category', columns[2] if len(columns)>2 else 'None')
        return f"import matplotlib.pyplot as plt; import pandas as pd\npivot = pd.pivot_table(df, values='{v}', index='{d}', columns='{c}', aggfunc='sum')\nplt.figure(figsize=(12, 6))\npivot.plot.area(ax=plt.gca(), colormap='Set2')\nplt.tight_layout(); plt.show()"

class StlDecompose(AnalysisTemplate):
    id = "stl_decompose"
    @classmethod
    def get_params_schema(cls) -> Any: return {"date": str, "value": str, "period": int}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]: return None
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        date = params.get('date', columns[0] if columns else None)
        val = params.get('value', columns[1] if len(columns) > 1 else None)
        period = params.get('period', 7)
        return (
            f"import matplotlib.pyplot as plt\n"
            f"import pandas as pd\n"
            f"from statsmodels.tsa.seasonal import seasonal_decompose\n"
            f"ts = df.set_index(pd.to_datetime(df[{repr(date)}]))[{repr(val)}].dropna().sort_index()\n"
            f"if len(ts) >= {period} * 2:\n"
            f"    result = seasonal_decompose(ts, model='additive', period={period})\n"
            f"    result.plot()\n"
            f"    plt.tight_layout(); plt.show()\n"
            f"else:\n"
            f"    print('Not enough data for seasonal decomposition')\n"
        )

class AcfPlot(AnalysisTemplate):
    id = "acf_plot"
    @classmethod
    def get_params_schema(cls) -> Any: return {"date": str, "value": str, "lags": int}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]: return None
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        date = params.get('date', columns[0] if columns else None)
        val = params.get('value', columns[1] if len(columns) > 1 else None)
        lags = params.get('lags', 30)
        return (
            f"import matplotlib.pyplot as plt\n"
            f"from statsmodels.graphics.tsaplots import plot_acf\n"
            f"ts = df.set_index(pd.to_datetime(df[{repr(date)}]))[{repr(val)}].dropna().sort_index()\n"
            f"if len(ts) > 0:\n"
            f"    fig, ax = plt.subplots(figsize=(10, 4))\n"
            f"    plot_acf(ts, lags=min({lags}, len(ts)-1), ax=ax)\n"
            f"    plt.title(f'Autocorrelation: {val}')\n"
            f"    plt.tight_layout(); plt.show()\n"
            f"else:\n"
            f"    print('No data available for ACF plot')\n"
        )
