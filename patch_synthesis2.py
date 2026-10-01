import os

with open('first_pass/first_pass/llm/synthesis.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_plain = "text_content += out['data']['text/plain'] + \"\\n\""
new_plain = """p = out['data']['text/plain']
                    if isinstance(p, list): p = ''.join(p)
                    text_content += p + \"\\n\""""

text = text.replace(old_plain, new_plain)

with open('first_pass/first_pass/llm/synthesis.py', 'w', encoding='utf-8') as f:
    f.write(text)
