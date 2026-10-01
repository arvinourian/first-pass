with open('first_pass/first_pass/llm/planner.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("from first_pass.schemas import", "from pydantic import BaseModel\nfrom first_pass.schemas import")

with open('first_pass/first_pass/llm/planner.py', 'w', encoding='utf-8') as f:
    f.write(text)
