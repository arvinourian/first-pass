import os

with open('first_pass/first_pass/llm/observer.py', 'r', encoding='utf-8') as f:
    text = f.read()

patch = """        for out in outputs:
            if out.get('output_type') == 'error':
                has_error = True
                error_text += f"{out.get('ename')}: {out.get('evalue')}\\n"
            elif out.get('output_type') == 'stream' and 'Error executing' in out.get('text', ''):
                has_error = True
                error_text += out.get('text', '')
            elif out.get('output_type') == 'display_data' and 'image/png' in out.get('data', {}):"""

text = text.replace("""        for out in outputs:
            if out.get('output_type') == 'error':
                has_error = True
                error_text += f"{out.get('ename')}: {out.get('evalue')}\\n"
            elif out.get('output_type') == 'display_data' and 'image/png' in out.get('data', {}):""", patch)

with open('first_pass/first_pass/llm/observer.py', 'w', encoding='utf-8') as f:
    f.write(text)
