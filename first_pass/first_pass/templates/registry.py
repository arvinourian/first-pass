import json
import pkgutil
import importlib
import inspect
from typing import Dict, Type
from first_pass.templates.base import AnalysisTemplate

# Global registry
_ANALYSIS_TEMPLATES: Dict[str, Type[AnalysisTemplate]] = {}

def _load_templates():
    if _ANALYSIS_TEMPLATES: return
    import first_pass.templates.analysis as analysis_pkg
    for _, module_name, _ in pkgutil.iter_modules(analysis_pkg.__path__):
        mod = importlib.import_module(f"first_pass.templates.analysis.{module_name}")
        for name, obj in inspect.getmembers(mod, inspect.isclass):
            if issubclass(obj, AnalysisTemplate) and obj is not AnalysisTemplate:
                if getattr(obj, "id", ""):
                    _ANALYSIS_TEMPLATES[obj.id] = obj

def get_template(template_id: str) -> Type[AnalysisTemplate]:
    _load_templates()
    return _ANALYSIS_TEMPLATES.get(template_id)

def get_template_code(category: str, template_id: str, columns: list, params: dict) -> str:
    """Returns executable python code for a given template."""
    
    if category == 'cleaning':
        # ... keep existing cleaning logic ...
        if template_id == 'fill_nulls':
            fill_value = params.get('fill_value', 0)
            cols_str = json.dumps(columns)
            if isinstance(fill_value, str):
                fill_value = f"'{fill_value}'"
            return f"df[{cols_str}] = df[{cols_str}].fillna({fill_value})"
            
        elif template_id == 'drop_duplicates':
            return "df = df.drop_duplicates()"
            
        elif template_id == 'drop_columns':
            cols_str = json.dumps(columns)
            return f"df = df.drop(columns={cols_str}, errors='ignore')"
            
        elif template_id == 'parse_dates':
            cols_str = json.dumps(columns)
            return (
                f"for col in {cols_str}:\n"
                f"    df[col] = pd.to_datetime(df[col], errors='coerce')"
            )
            
    elif category == 'analysis':
        _load_templates()
        if template_id in _ANALYSIS_TEMPLATES:
            return _ANALYSIS_TEMPLATES[template_id].generate_code(columns, params)
            
    return f"# TODO: Implement template {template_id}"
