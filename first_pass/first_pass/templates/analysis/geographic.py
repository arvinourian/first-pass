from typing import List, Any, Optional
from first_pass.schemas import DataProfile
from first_pass.templates.base import AnalysisTemplate

class LatlonScatter(AnalysisTemplate):
    id = "latlon_scatter"
    @classmethod
    def get_params_schema(cls) -> Any: return {"lat": str, "lon": str, "hue": str}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]: return None
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        lat = params.get('lat', columns[0] if columns else None)
        lon = params.get('lon', columns[1] if len(columns) > 1 else None)
        hue = params.get('hue')
        return (
            f"import seaborn as sns\n"
            f"import matplotlib.pyplot as plt\n"
            f"plt.figure(figsize=(10, 8))\n"
            f"sns.scatterplot(data=df, x={repr(lon)}, y={repr(lat)}, hue={repr(hue)} if {repr(hue)} else None, alpha=0.5)\n"
            f"plt.title('Lat/Lon Scatter Plot')\n"
            f"plt.tight_layout(); plt.show()\n"
        )

class RegionAgg(AnalysisTemplate):
    id = "region_agg"
    @classmethod
    def get_params_schema(cls) -> Any: return {"region": str, "value": str, "agg": str}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]: return None
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        region = params.get('region', columns[0] if columns else None)
        val = params.get('value', columns[1] if len(columns) > 1 else None)
        agg = params.get('agg', 'mean')
        return (
            f"import seaborn as sns\n"
            f"import matplotlib.pyplot as plt\n"
            f"import pandas as pd\n"
            f"agg_df = df.groupby({repr(region)})[{repr(val)}].agg({repr(agg)}).sort_values(ascending=False).head(20)\n"
            f"plt.figure(figsize=(10, 8))\n"
            f"sns.barplot(x=agg_df.values, y=agg_df.index, hue=agg_df.index, palette='viridis', legend=False)\n"
            f"plt.title(f'Top 20 Regions by {agg.capitalize()} of {val}')\n"
            f"plt.tight_layout(); plt.show()\n"
        )

class Choropleth(AnalysisTemplate):
    id = "choropleth"
    @classmethod
    def get_params_schema(cls) -> Any: return {"region": str, "value": str}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]: return None
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        region = params.get('region', columns[0] if columns else None)
        val = params.get('value', columns[1] if len(columns) > 1 else None)
        return (
            f"import pandas as pd\n"
            f"print('Choropleth mapping requires geopandas and shapefiles. Aggregated data:')\n"
            f"print(df.groupby({repr(region)})[{repr(val)}].sum().sort_values(ascending=False).head(10))\n"
        )
