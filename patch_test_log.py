with open('first_pass/test_opa_forced.py', 'r', encoding='utf-8') as f:
    text = f.read()

text += """
print('--- LLM USAGE LOGS ---')
from first_pass.llm.client import llm_usage_logs
for log in llm_usage_logs:
    print(log['stage'])
"""
with open('first_pass/test_opa_forced.py', 'w', encoding='utf-8') as f:
    f.write(text)
