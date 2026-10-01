import re

with open('first_pass/first_pass/templates/registry.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_load = """def _load_templates():
    if _ANALYSIS_TEMPLATES: return
    import first_pass.templates.analysis as analysis_pkg
    for _, module_name, _ in pkgutil.iter_modules(analysis_pkg.__path__):
        mod = importlib.import_module(f"first_pass.templates.analysis.{module_name}")
        for name, obj in inspect.getmembers(mod, inspect.isclass):
            if issubclass(obj, AnalysisTemplate) and obj is not AnalysisTemplate:
                if getattr(obj, "id", ""):
                    _ANALYSIS_TEMPLATES[obj.id] = obj"""

new_load = """def _load_templates():
    if _ANALYSIS_TEMPLATES: return
    import first_pass.templates.analysis as analysis_pkg
    try:
        import first_pass.templates.engineering as engineering_pkg
    except ImportError:
        engineering_pkg = None

    for _, module_name, _ in pkgutil.iter_modules(analysis_pkg.__path__):
        mod = importlib.import_module(f"first_pass.templates.analysis.{module_name}")
        for name, obj in inspect.getmembers(mod, inspect.isclass):
            if issubclass(obj, AnalysisTemplate) and obj is not AnalysisTemplate:
                if getattr(obj, "id", ""):
                    _ANALYSIS_TEMPLATES[obj.id] = obj
                    
    if engineering_pkg:
        for _, module_name, _ in pkgutil.iter_modules(engineering_pkg.__path__):
            mod = importlib.import_module(f"first_pass.templates.engineering.{module_name}")
            for name, obj in inspect.getmembers(mod, inspect.isclass):
                if issubclass(obj, AnalysisTemplate) and obj is not AnalysisTemplate:
                    if getattr(obj, "id", ""):
                        _ANALYSIS_TEMPLATES[obj.id] = obj"""

text = text.replace(old_load, new_load)

old_cat = """    elif category == 'analysis':
        _load_templates()
        if template_id in _ANALYSIS_TEMPLATES:
            return _ANALYSIS_TEMPLATES[template_id].generate_code(columns, params)"""

new_cat = """    elif category in ('analysis', 'engineering'):
        _load_templates()
        if template_id in _ANALYSIS_TEMPLATES:
            return _ANALYSIS_TEMPLATES[template_id].generate_code(columns, params)"""

text = text.replace(old_cat, new_cat)

with open('first_pass/first_pass/templates/registry.py', 'w', encoding='utf-8') as f:
    f.write(text)
