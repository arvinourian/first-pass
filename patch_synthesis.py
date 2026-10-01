import os

with open('first_pass/first_pass/llm/synthesis.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_stream = "text_content += out.get('text', '') + \"\\n\""
new_stream = """t = out.get('text', '')
                    if isinstance(t, list): t = ''.join(t)
                    text_content += t + \"\\n\""""

text = text.replace(old_stream, new_stream)

with open('first_pass/first_pass/llm/synthesis.py', 'w', encoding='utf-8') as f:
    f.write(text)
