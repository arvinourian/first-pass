import re

with open('first_pass/batch_run.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update index to include domain and engineering
text = text.replace('idx.build(["playbooks/cleaning", "playbooks/analysis"])',
                    'idx.build(["playbooks/cleaning", "playbooks/engineering", "playbooks/analysis", "playbooks/domain"])')

# 2. Add imports
text = text.replace('from first_pass.llm.planner import plan_cleaning, plan_analysis',
                    'from first_pass.llm.planner import plan_cleaning, plan_engineering, plan_analysis\nfrom first_pass.llm.synthesis import synthesize_report')

# 3. Add domain pass
old_domain = """    print("  Planning cleaning...")"""
new_domain = """    # Domain Pass
    domain_query = f"domain industry {raw_profile.row_count} rows " + " ".join([c.name for c in raw_profile.columns]) + user_instructions
    domain_pbs = idx.hybrid_search(domain_query, "domain", top_k=1)
    if domain_pbs:
        user_instructions += f"\\n\\n--- Recommended Industry Best Practices ---\\n{domain_pbs[0].content}"
        
    print("  Planning cleaning...")"""
text = text.replace(old_domain, new_domain)

# 4. Add engineering pass
old_eng = """    cleaned_profile = raw_profile
    
    print("  Planning analysis...")"""
new_eng = """    cleaned_profile = raw_profile
    
    print("  Planning engineering...")
    query_e = f"engineering scaling datetime binning pca. " + user_instructions
    engineering_pbs = idx.hybrid_search(query_e, "engineering")
    if not engineering_pbs and idx.playbooks:
        engineering_pbs = [pb for pb in idx.playbooks if pb.category == 'engineering'][:4]
    engineering_plan = plan_engineering(cleaned_profile, engineering_pbs, user_instructions)
    
    print("  Planning analysis...")"""
text = text.replace(old_eng, new_eng)

# 5. Add engineering plan to builder
text = text.replace('builder.build_notebook(\n        raw_profile=raw_profile,\n        cleaning_plan=cleaning_plan,\n        cleaned_profile=cleaned_profile,\n        analysis_plan=analysis_plan,',
                    'builder.build_notebook(\n        raw_profile=raw_profile,\n        cleaning_plan=cleaning_plan,\n        engineering_plan=engineering_plan,\n        cleaned_profile=cleaned_profile,\n        analysis_plan=analysis_plan,')

# 6. Add synthesis pass
old_syn = """    if error_count == 0:
        print("  -> Clean execution! No errors.")
    
    print(f"  Finished {executed_nb_path}\\n")"""
new_syn = """    if error_count == 0:
        print("  -> Clean execution! No errors.")
        
    print("  Synthesizing report...")
    report_md = synthesize_report(executed_nb_path, user_instructions)
    with open(executed_nb_path.replace('.ipynb', '_Summary.md'), 'w', encoding='utf-8') as sf:
        sf.write(report_md)
    
    print(f"  Finished {executed_nb_path}\\n")"""
text = text.replace(old_syn, new_syn)

with open('first_pass/batch_run.py', 'w', encoding='utf-8') as f:
    f.write(text)
