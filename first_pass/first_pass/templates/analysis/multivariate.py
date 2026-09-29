from typing import List, Any, Optional
from first_pass.schemas import DataProfile
from first_pass.templates.base import AnalysisTemplate

class PcaOverview(AnalysisTemplate):
    id = "pca_overview"
    @classmethod
    def get_params_schema(cls) -> Any: return {"columns": list, "n_components": int, "hue": str}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]: return None
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        cols = params.get('columns', columns)
        hue = params.get('hue')
        n_comp = params.get('n_components', 2)
        return (
            f"from sklearn.decomposition import PCA\n"
            f"from sklearn.preprocessing import StandardScaler\n"
            f"import seaborn as sns\n"
            f"import matplotlib.pyplot as plt\n"
            f"import pandas as pd\n"
            f"cols = {cols}\n"
            f"df_pca = df[cols].dropna()\n"
            f"if len(df_pca) > 0:\n"
            f"    scaled = StandardScaler().fit_transform(df_pca)\n"
            f"    pca = PCA(n_components={n_comp})\n"
            f"    components = pca.fit_transform(scaled)\n"
            f"    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))\n"
            f"    hue_data = df.loc[df_pca.index, {repr(hue)}] if {repr(hue)} else None\n"
            f"    sns.scatterplot(x=components[:, 0], y=components[:, 1], hue=hue_data, ax=ax1)\n"
            f"    ax1.set_title('PCA: First Two Components')\n"
            f"    ax1.set_xlabel('PC1')\n"
            f"    ax1.set_ylabel('PC2')\n"
            f"    ax2.bar(range(1, {n_comp} + 1), pca.explained_variance_ratio_)\n"
            f"    ax2.set_title('Explained Variance Ratio')\n"
            f"    plt.tight_layout(); plt.show()\n"
        )

class KmeansExplore(AnalysisTemplate):
    id = "kmeans_explore"
    @classmethod
    def get_params_schema(cls) -> Any: return {"columns": list, "k_range": list}
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]: return None
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        cols = params.get('columns', columns)
        k_range = params.get('k_range', [2, 3, 4, 5])
        return (
            f"from sklearn.cluster import KMeans\n"
            f"from sklearn.preprocessing import StandardScaler\n"
            f"import matplotlib.pyplot as plt\n"
            f"cols = {cols}\n"
            f"df_k = df[cols].dropna()\n"
            f"if len(df_k) > 10:\n"
            f"    scaled = StandardScaler().fit_transform(df_k)\n"
            f"    inertias = []\n"
            f"    for k in {k_range}:\n"
            f"        km = KMeans(n_clusters=k, random_state=42, n_init=10)\n"
            f"        km.fit(scaled)\n"
            f"        inertias.append(km.inertia_)\n"
            f"    plt.figure(figsize=(8, 5))\n"
            f"    plt.plot({k_range}, inertias, marker='o')\n"
            f"    plt.title('K-Means Elbow Plot')\n"
            f"    plt.xlabel('Number of Clusters (k)')\n"
            f"    plt.ylabel('Inertia')\n"
            f"    plt.tight_layout(); plt.show()\n"
        )
