import json
from typing import List, Any, Optional
from first_pass.schemas import DataProfile
from first_pass.templates.base import AnalysisTemplate

class SalesRatioStudy(AnalysisTemplate):
    id = "sales_ratio_study"
    
    @classmethod
    def get_params_schema(cls) -> Any:
        return {
            "assessment_col": "str",
            "sale_col": "str"
        }
        
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]:
        return None
        
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        assessment = params.get("assessment_col", columns[0])
        sale = params.get("sale_col", columns[1])
        
        return (
            f"import numpy as np\n"
            f"import pandas as pd\n"
            f"import matplotlib.pyplot as plt\n"
            f"import seaborn as sns\n\n"
            f"df_ratio = df[[{repr(assessment)}, {repr(sale)}]].dropna().copy()\n"
            f"df_ratio = df_ratio[(df_ratio[{repr(sale)}] > 0) & (df_ratio[{repr(assessment)}] > 0)]\n"
            f"df_ratio['ratio'] = df_ratio[{repr(assessment)}] / df_ratio[{repr(sale)}]\n\n"
            f"median_ratio = df_ratio['ratio'].median()\n"
            f"mean_ratio = df_ratio['ratio'].mean()\n"
            f"avg_abs_dev = (df_ratio['ratio'] - median_ratio).abs().mean()\n"
            f"cod = (avg_abs_dev / median_ratio) * 100\n"
            f"prd = mean_ratio / (df_ratio[{repr(assessment)}].sum() / df_ratio[{repr(sale)}].sum())\n\n"
            f"print('=== IAAO Sales Ratio Study ===')\n"
            f"print(f'Median Assessment Ratio: {{median_ratio:.3f}}')\n"
            f"print(f'Coefficient of Dispersion (COD): {{cod:.2f}} (IAAO standard is 5-15)')\n"
            f"print(f'Price-Related Differential (PRD): {{prd:.3f}} (IAAO standard is 0.98-1.03)')\n\n"
            f"plt.figure(figsize=(10, 6))\n"
            f"sns.histplot(df_ratio['ratio'], bins=50, kde=True, color='teal')\n"
            f"plt.axvline(median_ratio, color='red', linestyle='--', label=f'Median Ratio: {{median_ratio:.3f}}')\n"
            f"plt.axvline(1.0, color='black', linestyle=':', label='1.0 Ratio')\n"
            f"plt.title('Distribution of Assessment-to-Sales Ratios')\n"
            f"plt.xlabel('Assessed Value / Sale Price')\n"
            f"plt.xlim(0, 3)\n"
            f"plt.legend()\n"
            f"plt.tight_layout(); plt.show()"
        )
