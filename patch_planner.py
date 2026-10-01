with open('first_pass/first_pass/llm/planner.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('generate_plan("pass2", prompt', 'generate_plan("pass3", prompt')
text = text.replace('generate_plan("pass2-repair", repair_prompt', 'generate_plan("pass3-repair", repair_prompt')

text = text.replace('generate_plan("pass1.5", prompt', 'generate_plan("pass2", prompt')
text = text.replace('generate_plan("pass1.5-repair", repair_prompt', 'generate_plan("pass2-repair", repair_prompt')

with open('first_pass/first_pass/llm/planner.py', 'w', encoding='utf-8') as f:
    f.write(text)
