import re
with open('first_pass/first_pass/llm/planner.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(r'Planner selection rules:.*9\. Every plan item must include [^\n]+', """Planner selection rules:
1. Prioritize analyses involving columns or goals the user mentioned in their text input. Explicitly extract and list the `target_variables`.
2. NARRATIVE ARCHITECTURE: Do NOT group your analyses by statistical methodology (e.g. "Distributions", "Multivariate"). Instead, you must act as a Senior Strategy Consultant. Group your analyses into `sections` representing narrative business questions (e.g. "Return on Investment: Does paying more for tuition pay off?", "Student-level Levers: Internships & GPA", "Geographic Trends").
3. Be EXHAUSTIVE and COMPREHENSIVE in your exploration, but PRUNE redundant charts. Do not pick 5 simple bar charts; use `multi_bar` instead.
4. Utilize advanced tools like `ols_regression`, `scatter_regression`, and `target_corr_ranked` if there is a clear target variable.
5. ADVANCED DOMAIN MODELING: You are a senior data scientist. If standard templates are not enough to explore a domain-specific hypothesis, use the `custom_code` template to write highly complex, free-form code!
6. If there are interesting avenues for future investigation that are beyond the scope of these templates, list them in the `further_analyses` field.
7. DATA LEAKAGE & REDUNDANCY: Recognize mathematically equivalent or derived features.
8. Never select a template whose "Applies when" preconditions are not met.
9. Every AnalysisItem must include a `title` representing a specific human-readable business question (e.g. "What is the ROI distribution?"), `template_id`, `columns`, `params`, `rationale`, and `playbook_ids`.""", text, flags=re.DOTALL)

with open('first_pass/first_pass/llm/planner.py', 'w', encoding='utf-8') as f:
    f.write(text)
