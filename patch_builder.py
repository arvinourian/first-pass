import re

with open('first_pass/first_pass/notebook_builder.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update signature
old_sig = """    def build_notebook(self, 
                       raw_profile: DataProfile, 
                       cleaning_plan: CleaningPlan,
                       cleaned_profile: DataProfile,
                       analysis_plan: AnalysisPlan,"""

new_sig = """    def build_notebook(self, 
                       raw_profile: DataProfile, 
                       cleaning_plan: CleaningPlan,
                       engineering_plan,
                       cleaned_profile: DataProfile,
                       analysis_plan: AnalysisPlan,"""

text = text.replace(old_sig, new_sig)

# 2. Inject Engineering Phase
old_clean = """        # 4. Cleaning
        self.add_markdown("## Data Cleaning")
        for step in cleaning_plan.steps:"""

new_clean = """        # 4. Cleaning
        self.add_markdown("## Data Cleaning")
        for step in cleaning_plan.steps:"""

# Wait, I need to find the end of cleaning.
# We'll just insert engineering before "5. Analysis"
old_analysis = """        # 5. Analysis
        self.add_markdown("## Data Analysis")"""

new_analysis = """        # 4.5 Engineering
        if engineering_plan and engineering_plan.steps:
            self.add_markdown("## Feature Engineering")
            for step in engineering_plan.steps:
                self.add_markdown(f"### {step.rationale}")
                code = get_template_code(step.template_id, step.columns, step.params)
                self.add_code(code)
                
        # 5. Analysis
        self.add_markdown("## Data Analysis")"""

text = text.replace(old_analysis, new_analysis)

with open('first_pass/first_pass/notebook_builder.py', 'w', encoding='utf-8') as f:
    f.write(text)
