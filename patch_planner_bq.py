import json
from pydantic import BaseModel
from typing import List

class BusinessQuestions(BaseModel):
    questions: List[str]

with open('first_pass/first_pass/llm/planner.py', 'r', encoding='utf-8') as f:
    text = f.read()

new_func = """
class BusinessQuestions(BaseModel):
    questions: List[str]

def generate_business_questions(profile: DataProfile, user_text: str = "") -> List[str]:
    sys_prompt = "You are a Strategy Consultant. Review this dataset profile and output exactly 5 highly specific narrative business questions that should be answered by exploratory data analysis (e.g. 'Does paying more for tuition yield a higher return on investment?')."
    
    context = f"Data Profile:\\n{profile.model_dump_json(exclude_none=True)}\\n\\n"
    if user_text:
        context += f"User Instructions:\\n{user_text}\\n"
        
    try:
        response_text = generate_plan("pass3_questions", [sys_prompt, context], BusinessQuestions)
        plan = BusinessQuestions.model_validate_json(response_text)
        return plan.questions
    except Exception as e:
        print(f"Error generating questions: {e}")
        return ["What are the key distributions?", "What are the core correlations?"]
"""

text = text.replace("def plan_analysis", new_func + "\ndef plan_analysis")

with open('first_pass/first_pass/llm/planner.py', 'w', encoding='utf-8') as f:
    f.write(text)
