with open('first_pass/first_pass/llm/synthesis.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_try = """    try:
        response_text = generate_plan("pass5_synthesis", prompt, NotebookSynthesis)
        plan = NotebookSynthesis.model_validate_json(response_text)
        return "## Key Takeaways\\n" + plan.markdown
    except Exception as e:"""

new_try = """    try:
        response_text = generate_plan("pass5_synthesis", prompt, NotebookSynthesis)
        plan = NotebookSynthesis.model_validate_json(response_text)
        md = plan.markdown
        import re
        # Strip duplicated headers
        md = re.sub(r'^(#+\\s.*?[\\r\\n]+)+', '', md.strip(), flags=re.MULTILINE).strip()
        if md.startswith('## Key Takeaways'):
            md = md[16:].strip()
        if md.startswith('### Key Takeaways'):
            md = md[17:].strip()
        return "## Key Takeaways\\n\\n" + md
    except Exception as e:"""

text = text.replace(old_try, new_try)

old_sys = "sys_prompt = \"You are a Senior Data Consultant. Review this generated Exploratory Data Analysis notebook and write a concise, bulleted 'Key Takeaways' section summarizing the most critical business insights found in the data. Format it elegantly in Markdown.\""
new_sys = "sys_prompt = \"You are a Senior Data Consultant. Review this generated Exploratory Data Analysis notebook and write a concise, bulleted 'Key Takeaways' section summarizing the most critical business insights found in the data. Format it elegantly in Markdown. DO NOT INCLUDE A TITLE OR HEADER (e.g. do not write '## Key Takeaways'), just provide the bullet points directly.\""

text = text.replace(old_sys, new_sys)

with open('first_pass/first_pass/llm/synthesis.py', 'w', encoding='utf-8') as f:
    f.write(text)
