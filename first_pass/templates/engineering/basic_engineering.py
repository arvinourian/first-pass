from typing import List, Any, Optional
from first_pass.schemas import DataProfile
from first_pass.templates.base import AnalysisTemplate

class ExtractDatetime(AnalysisTemplate):
    id = "extract_datetime"
    @classmethod
    def get_params_schema(cls) -> Any: return {"column": str}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]: return None
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        col = params.get('column', columns[0])
        return (
            f"import pandas as pd\n"
            f"df[{repr(col + '_year')}] = pd.to_datetime(df[{repr(col)}]).dt.year\n"
            f"df[{repr(col + '_month')}] = pd.to_datetime(df[{repr(col)}]).dt.month\n"
            f"print(f'Extracted year and month from {col}')"
        )

class StandardScale(AnalysisTemplate):
    id = "standard_scale"
    @classmethod
    def get_params_schema(cls) -> Any: return {"columns": list}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]: return None
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        cols = params.get('columns', columns)
        return (
            f"from sklearn.preprocessing import StandardScaler\n"
            f"scaler = StandardScaler()\n"
            f"df[{repr(cols)}] = scaler.fit_transform(df[{repr(cols)}])\n"
            f"print(f'Standard scaled columns: {cols}')"
        )

class BinNumeric(AnalysisTemplate):
    id = "bin_numeric"
    @classmethod
    def get_params_schema(cls) -> Any: return {"column": str, "bins": int}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]: return None
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        col = params.get('column', columns[0])
        bins = params.get('bins', 4)
        return (
            f"import pandas as pd\n"
            f"df[{repr(col + '_binned')}] = pd.qcut(df[{repr(col)}], q={bins}, duplicates='drop')\n"
            f"print(f'Binned {col} into {bins} quantiles')"
        )
