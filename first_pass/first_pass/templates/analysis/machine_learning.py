import json
from typing import List, Any, Optional
from first_pass.schemas import DataProfile
from first_pass.templates.base import AnalysisTemplate

class TrainRandomForest(AnalysisTemplate):
    id = "train_rf"
    
    @classmethod
    def get_params_schema(cls) -> Any:
        return {
            "target": "str (the column to predict)",
            "predictors": "list of str (the columns to use as features)"
        }
        
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]:
        target = params.get("target")
        if not target or target not in columns:
            return "target must be in columns"
        return None
        
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        target = params.get("target")
        predictors = params.get("predictors", [c for c in columns if c != target])
        predictors_str = json.dumps(predictors)
        
        return (
            f"from sklearn.ensemble import RandomForestRegressor\n"
            f"from sklearn.model_selection import train_test_split\n"
            f"from sklearn.metrics import r2_score, mean_absolute_error\n"
            f"import pandas as pd\n"
            f"import numpy as np\n"
            f"import matplotlib.pyplot as plt\n"
            f"import seaborn as sns\n\n"
            f"features = {predictors_str}\n"
            f"target = '{target}'\n"
            f"df_ml = df[features + [target]].dropna()\n"
            f"X = pd.get_dummies(df_ml[features], drop_first=True)\n"
            f"y = df_ml[target]\n\n"
            f"X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)\n"
            f"rf = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)\n"
            f"rf.fit(X_train, y_train)\n"
            f"y_pred = rf.predict(X_test)\n\n"
            f"r2 = r2_score(y_test, y_pred)\n"
            f"mae = mean_absolute_error(y_test, y_pred)\n"
            f"print(f'Random Forest Baseline Model')\n"
            f"print(f'R-squared: {{r2:.4f}}')\n"
            f"print(f'Mean Absolute Error: {{mae:.4f}}')\n\n"
            f"importances = pd.Series(rf.feature_importances_, index=X.columns).sort_values(ascending=False).head(10)\n"
            f"plt.figure(figsize=(10, 6))\n"
            f"sns.barplot(x=importances.values, y=importances.index, hue=importances.index, legend=False, palette='viridis')\n"
            f"plt.title('Top 10 Feature Importances (Random Forest)')\n"
            f"plt.tight_layout(); plt.show()"
        )
