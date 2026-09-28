import json
from typing import List
from first_pass.schemas import DataProfile, CleaningPlan, AnalysisPlan
from first_pass.llm.client import generate_plan
from first_pass.retrieval.index import Playbook

def format_playbooks(playbooks: List[Playbook]) -> str:
    res = ""
    for pb in playbooks:
        res += f"### Playbook ID: {pb.metadata.get('id')}\n"
        res += f"Title: {pb.metadata.get('title')}\n"
        res += f"Applies When: {pb.metadata.get('applies_when')}\n"
        res += f"Templates to use: {', '.join(pb.metadata.get('templates', []))}\n"
        res += f"Instructions: {pb.content}\n\n"
    return res

def plan_cleaning(profile: DataProfile, playbooks: List[Playbook], user_text: str = "") -> CleaningPlan:
    sys_prompt = "You are a data cleaning planning AI. Your job is to output a structured JSON plan to clean the data. Only use templates specified in the playbooks. For the `params` field, output a valid JSON string representing the parameter dictionary (e.g. \"{\\\"fill_value\\\": 0}\")."
    
    context = f"Data Profile:\n{profile.model_dump_json(exclude_none=True)}\n\n"
    if user_text:
        context += f"User Instructions:\n{user_text}\n\n"
    context += f"Available Playbooks:\n{format_playbooks(playbooks)}\n"
    
    prompt = sys_prompt + "\n\n" + context
    
    try:
        response_text = generate_plan("pass1", prompt, CleaningPlan)
        plan = CleaningPlan.model_validate_json(response_text)
        return plan
    except Exception as e:
        repair_prompt = prompt + f"\n\nYour previous attempt failed with error: {e}. Please fix the JSON and try again."
        response_text = generate_plan("pass1-repair", repair_prompt, CleaningPlan)
        plan = CleaningPlan.model_validate_json(response_text)
        return plan

def plan_analysis(profile: DataProfile, playbooks: List[Playbook], user_text: str = "") -> AnalysisPlan:
    sys_prompt = """You are a data analysis planning AI. Output a structured JSON plan for analysis. For the `params` field, output a valid JSON string representing the parameter dictionary.
CRITICAL: Only use templates that are explicitly specified in the provided Playbooks. Do not hallucinate template IDs.

Planner selection rules:
1. Prioritize analyses involving columns or goals the user mentioned in their
   text input.
2. Prefer breadth over depth: one analysis per distinct question, not multiple
   views of the same relationship.
3. Respect the analysis cap (default 8, configurable). Rank candidates by expected usefulness for a
   first look.
4. List candidates that were considered but cut by the cap in a
   `further_analyses` field of the plan. The notebook renders these as a
   "Further analyses to consider" section — this is how First Pass points the
   user in the right direction.
5. Never select a template whose "Applies when" preconditions are not met.
6. Never use pie charts, 3D charts, dual-axis charts, or word clouds.
7. Every plan item must include `template_id`, `columns`, `params`,
   `rationale` (one sentence), and `playbook_ids`.
"""
    
    context = f"Cleaned Data Profile:\n{profile.model_dump_json(exclude_none=True)}\n\n"
    if user_text:
        context += f"User Instructions:\n{user_text}\n\n"
    context += f"Available Playbooks:\n{format_playbooks(playbooks)}\n"
    
    # Extract schemas for the templates
    from first_pass.templates.registry import get_template
    tmpl_schemas = []
    for pb in playbooks:
        for tmpl_id in pb.metadata.get('templates', []):
            tmpl = get_template(tmpl_id)
            if tmpl:
                schema = tmpl.get_params_schema()
                tmpl_schemas.append(f"- {tmpl_id}: {schema}")
    if tmpl_schemas:
        context += "Template Parameter Schemas (must use these keys in the params dict):\n" + "\n".join(set(tmpl_schemas)) + "\n"
    
    prompt = sys_prompt + "\n\n" + context

    def _validate(plan: AnalysisPlan) -> AnalysisPlan:
        errors = []
        for item in plan.analyses:
            tmpl = get_template(item.template_id)
            if not tmpl:
                # If template doesn't exist, skip validation (it might be an overview template not implemented yet)
                continue
            
            try:
                params_dict = json.loads(item.params)
            except Exception:
                params_dict = {}
                
            err = tmpl.check_preconditions(item.columns, params_dict, profile)
            if err:
                errors.append(f"Template {item.template_id} precondition failed for columns {item.columns}: {err}")
        if errors:
            raise ValueError("\n".join(errors))
        return plan
    
    try:
        response_text = generate_plan("pass2", prompt, AnalysisPlan)
        plan = AnalysisPlan.model_validate_json(response_text)
        return _validate(plan)
    except Exception as e:
        repair_prompt = prompt + f"\n\nYour previous attempt failed with error: {e}. Please fix the JSON and try again."
        response_text = generate_plan("pass2-repair", repair_prompt, AnalysisPlan)
        plan = AnalysisPlan.model_validate_json(response_text)
        return _validate(plan)
