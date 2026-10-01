with open('first_pass/first_pass/notebook_builder.py', 'r', encoding='utf-8') as f:
    text = f.read()

old = '# 5. Analysis'
new = """# 4.5 Engineering
        if engineering_plan and hasattr(engineering_plan, 'steps') and engineering_plan.steps:
            self.add_markdown("## Feature Engineering")
            for step in engineering_plan.steps:
                self.add_markdown(f"### {step.rationale}")
                code = get_template_code('engineering', step.template_id, step.columns, step.params)
                self.add_code(code)
                
        # 5. Analysis"""

if '# 4.5 Engineering' not in text:
    text = text.replace(old, new)
    with open('first_pass/first_pass/notebook_builder.py', 'w', encoding='utf-8') as f:
        f.write(text)
