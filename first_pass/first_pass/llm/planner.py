import json
from typing import List
from pydantic import BaseModel
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


class BusinessQuestions(BaseModel):
    questions: List[str]

def generate_business_questions(profile: DataProfile, user_text: str = "") -> List[str]:
    sys_prompt = "You are a Strategy Consultant. Review this dataset profile and output exactly 5 highly specific narrative business questions that should be answered by exploratory data analysis (e.g. 'Does paying more for tuition yield a higher return on investment?')."
    
    context = f"Data Profile:\n{profile.model_dump_json(exclude_none=True)}\n\n"
    if user_text:
        context += f"User Instructions:\n{user_text}\n"
        
    try:
        response_text = generate_plan("pass3_questions", [sys_prompt, context], BusinessQuestions)
        plan = BusinessQuestions.model_validate_json(response_text)
        return plan.questions
    except Exception as e:
        print(f"Error generating questions: {e}")
        return ["What are the key distributions?", "What are the core correlations?"]

def plan_analysis(profile: DataProfile, playbooks: List[Playbook], user_text: str = "") -> AnalysisPlan:
    sys_prompt = """You are a data analysis planning AI. Output a structured JSON plan for analysis. For the `params` field, output a valid JSON string representing the parameter dictionary.
CRITICAL: Only use templates that are explicitly specified in the provided Playbooks. Do not hallucinate template IDs.

Planner selection rules:
1. Prioritize analyses involving columns or goals the user mentioned in their text input. Explicitly extract and list the `target_variables`.
2. NARRATIVE ARCHITECTURE: Do NOT group your analyses by statistical methodology (e.g. "Distributions", "Multivariate"). Instead, you must act as a Senior Strategy Consultant. Group your analyses into `sections` representing narrative business questions (e.g. "Return on Investment: Does paying more for tuition pay off?", "Student-level Levers: Internships & GPA", "Geographic Trends").
3. Be EXHAUSTIVE and COMPREHENSIVE in your exploration, but PRUNE redundant charts. Do not pick 5 simple bar charts; use `multi_bar` instead.
4. Utilize advanced tools like `ols_regression`, `scatter_regression`, and `target_corr_ranked` if there is a clear target variable.
5. ADVANCED DOMAIN MODELING: You are a senior data scientist. If standard templates are not enough to explore a domain-specific hypothesis, use the `custom_code` template to write highly complex, free-form code!
6. If there are interesting avenues for future investigation that are beyond the scope of these templates, list them in the `further_analyses` field.
7. DATA LEAKAGE & REDUNDANCY: Recognize mathematically equivalent or derived features.
8. Never select a template whose "Applies when" preconditions are not met.
9. Every AnalysisItem must include a `title` representing a specific human-readable business question (e.g. "What is the ROI distribution?"), `template_id`, `columns`, `params`, `rationale`, and `playbook_ids`.
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
        for sec in plan.sections:
            for item in sec.analyses:
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
        response_text = generate_plan("pass3", prompt, AnalysisPlan)
        plan = AnalysisPlan.model_validate_json(response_text)
        return _validate(plan)
    except Exception as e:
        repair_prompt = prompt + f"\n\nYour previous attempt failed with error: {e}. Please fix the JSON and try again."
        response_text = generate_plan("pass3-repair", repair_prompt, AnalysisPlan)
        plan = AnalysisPlan.model_validate_json(response_text)
        return _validate(plan)

from pydantic import BaseModel
from first_pass.schemas import CleaningPlan

def plan_engineering(profile: DataProfile, playbooks: List[Playbook], user_text: str = "") -> CleaningPlan:
    sys_prompt = "You are a data engineering AI. Your job is to output a structured JSON plan to engineer new features mathematically (scaling, binning, datetime extraction). Only use templates specified in the playbooks. For the `params` field, output a valid JSON string representing the parameter dictionary (e.g. \"{\\\"column\\\": \\\"date\\\"}\")."
    
    context = f"Data Profile:\n{profile.model_dump_json(exclude_none=True)}\n\n"
    if user_text:
        context += f"User Instructions:\n{user_text}\n\n"
    context += f"Available Playbooks:\n{format_playbooks(playbooks)}\n"
    
    prompt = sys_prompt + "\n\n" + context
    
    try:
        response_text = generate_plan("pass2", prompt, CleaningPlan)
        plan = CleaningPlan.model_validate_json(response_text)
        return plan
    except Exception as e:
        repair_prompt = prompt + f"\n\nYour previous attempt failed with error: {e}. Please fix the JSON and try again."
        response_text = generate_plan("pass2-repair", repair_prompt, CleaningPlan)
        plan = CleaningPlan.model_validate_json(response_text)
        return plan
