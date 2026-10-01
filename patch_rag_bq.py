import os

for fpath in ['first_pass/app.py', 'first_pass/batch_run.py']:
    if os.path.exists(fpath):
        with open(fpath, 'r', encoding='utf-8') as f:
            text = f.read()
            
        # Update import
        text = text.replace("from first_pass.llm.planner import plan_cleaning, plan_engineering, plan_analysis",
                            "from first_pass.llm.planner import plan_cleaning, plan_engineering, plan_analysis, generate_business_questions")
        
        # Update search query
        old_search = 'analysis_pbs = idx.hybrid_search("analysis " + combined_instructions, "analysis", stage="pass3")'
        if 'analysis_pbs = idx.hybrid_search("analysis " + user_instructions, "analysis", stage="pass3")' in text:
            old_search = 'analysis_pbs = idx.hybrid_search("analysis " + user_instructions, "analysis", stage="pass3")'
            new_search = """questions = generate_business_questions(cleaned_profile, user_instructions)
            analysis_query = " ".join(questions) + " " + user_instructions
            analysis_pbs = idx.hybrid_search(analysis_query, "analysis", stage="pass3")"""
        else:
            old_search = 'analysis_pbs = idx.hybrid_search("analysis " + combined_instructions, "analysis", stage="pass3")'
            new_search = """questions = generate_business_questions(cleaned_profile, combined_instructions)
            analysis_query = " ".join(questions) + " " + combined_instructions
            analysis_pbs = idx.hybrid_search(analysis_query, "analysis", stage="pass3")"""

        text = text.replace(old_search, new_search)

        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(text)
