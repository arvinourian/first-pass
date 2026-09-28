from typing import List, Any, Optional
from first_pass.schemas import DataProfile
from first_pass.templates.base import AnalysisTemplate

class TextLengthDist(AnalysisTemplate):
    id = "text_length_dist"
    @classmethod
    def get_params_schema(cls) -> Any: return {"column": str}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]: return None
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        col = params.get('column', columns[0] if columns else None)
        return (
            f"import seaborn as sns\n"
            f"import matplotlib.pyplot as plt\n"
            f"lengths = df[{repr(col)}].dropna().astype(str).str.len()\n"
            f"plt.figure(figsize=(10, 6))\n"
            f"sns.histplot(lengths, kde=True, bins=30)\n"
            f"plt.title(f'Text Length Distribution: {{{col}}}')\n"
            f"plt.xlabel('Character Count')\n"
            f"plt.show()\n"
        )

class TopNgrams(AnalysisTemplate):
    id = "top_ngrams"
    @classmethod
    def get_params_schema(cls) -> Any: return {"column": str, "n": int, "top_k": int, "stopwords": list}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]: return None
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        col = params.get('column', columns[0] if columns else None)
        n = params.get('n', 2)
        top_k = params.get('top_k', 10)
        return (
            f"from collections import Counter\n"
            f"import pandas as pd\n"
            f"import seaborn as sns\n"
            f"import matplotlib.pyplot as plt\n"
            f"import re\n"
            f"texts = df[{repr(col)}].dropna().astype(str).str.lower()\n"
            f"words = [re.findall(r'\\b\\w+\\b', t) for t in texts]\n"
            f"ngrams = []\n"
            f"for w_list in words:\n"
            f"    if len(w_list) >= {n}:\n"
            f"        ngrams.extend([' '.join(w_list[i:i+{n}]) for i in range(len(w_list)-{n}+1)])\n"
            f"counts = pd.Series(Counter(ngrams)).sort_values(ascending=False).head({top_k})\n"
            f"plt.figure(figsize=(10, 6))\n"
            f"sns.barplot(x=counts.values, y=counts.index, palette='Blues_r')\n"
            f"plt.title(f'Top {{min({top_k}, len(counts))}} {n}-grams in {{{col}}}')\n"
            f"plt.show()\n"
        )
