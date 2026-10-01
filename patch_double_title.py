import os

with open('first_pass/first_pass/llm/synthesis.py', 'r', encoding='utf-8') as f:
    text = f.read()

patch = """    try:
        response_text = generate_plan("pass5_synthesis", prompt, NotebookSynthesis)
        plan = NotebookSynthesis.model_validate_json(response_text)
        
        md = plan.markdown
        # Strip duplicated headers if the LLM already included them
        md = md.replace("## Key Takeaways\\n", "")
        md = md.replace("### Key Takeaways\\n", "")
        md = md.replace("# Key Takeaways\\n", "")
        if md.startswith("## Key Takeaways"): md = md[16:].strip()
        if md.startswith("### Key Takeaways"): md = md[17:].strip()
        
        return "## Key Takeaways\\n\\n" + md.strip()
    except Exception as e:"""

text = text.replace("""    try:
        response_text = generate_plan("pass5_synthesis", prompt, NotebookSynthesis)
        plan = NotebookSynthesis.model_validate_json(response_text)
        return "## Key Takeaways\\n" + plan.markdown
    except Exception as e:""", patch)

with open('first_pass/first_pass/llm/synthesis.py', 'w', encoding='utf-8') as f:
    f.write(text)
