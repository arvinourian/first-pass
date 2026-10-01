import re

with open('first_pass/app.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update index to include playbooks/engineering
text = text.replace('index.build(["playbooks/cleaning", "playbooks/analysis", "playbooks/domain"])',
                    'index.build(["playbooks/cleaning", "playbooks/engineering", "playbooks/analysis", "playbooks/domain"])')

# 2. Add plan_engineering import
text = text.replace('from first_pass.llm.planner import plan_cleaning, plan_analysis',
                    'from first_pass.llm.planner import plan_cleaning, plan_engineering, plan_analysis')

# 3. Add engineering pass
old_text = """            my_bar.progress(50, text="Stage 4: Executing Cleaning (No LLM)...")
            cleaned_profile = raw_profile 
            
            my_bar.progress(70, text="Stage 5: RAG Pass 2 (Analysis Plan)...")"""

new_text = """            my_bar.progress(50, text="Stage 4: Executing Cleaning (No LLM)...")
            cleaned_profile = raw_profile 
            
            engineering_plan = None
            if enable_engineering:
                my_bar.progress(60, text="Stage 4.5: RAG Pass 1.5 (Feature Engineering Plan)...")
                query_e = f"engineering scaling datetime binning pca. " + combined_instructions
                engineering_pbs = idx.hybrid_search(query_e, "engineering")
                if not engineering_pbs and idx.playbooks:
                    engineering_pbs = [pb for pb in idx.playbooks if pb.category == 'engineering'][:4]
                engineering_plan = plan_engineering(cleaned_profile, engineering_pbs, combined_instructions)
            
            my_bar.progress(70, text="Stage 5: RAG Pass 2 (Analysis Plan)...")"""

text = text.replace(old_text, new_text)

# 4. Pass engineering_plan to builder
text = text.replace('builder.build_notebook(\n                raw_profile=raw_profile,\n                cleaning_plan=cleaning_plan,\n                cleaned_profile=cleaned_profile,\n                analysis_plan=analysis_plan,',
                    'builder.build_notebook(\n                raw_profile=raw_profile,\n                cleaning_plan=cleaning_plan,\n                engineering_plan=engineering_plan,\n                cleaned_profile=cleaned_profile,\n                analysis_plan=analysis_plan,')

with open('first_pass/app.py', 'w', encoding='utf-8') as f:
    f.write(text)
