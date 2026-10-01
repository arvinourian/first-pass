import os
from dotenv import load_dotenv
load_dotenv()

import pandas as pd
from first_pass.schemas import DataProfile
from first_pass.retrieval.index import PlaybookIndex
from first_pass.llm.planner import plan_cleaning, plan_engineering, plan_analysis
from first_pass.notebook_builder import NotebookBuilder
from first_pass.profile import generate_profile
from first_pass.ingest import load_spreadsheet

# 1. Setup Index
idx = PlaybookIndex()
idx.build(["playbooks/cleaning", "playbooks/engineering", "playbooks/analysis", "playbooks/domain"])

# 2. Run OPA Data
f = "opa data - philadelphia_sfh_modeling.csv"
filepath = os.path.join("C:/Users/arvin/Desktop/Sample Datasets", f)
print(f"=== Processing {f} ===")

user_instructions = ""

try:
    df_raw = load_spreadsheet(filepath)
    raw_profile = generate_profile(df_raw)
    
    # Domain Pass
    domain_query = f"domain industry {raw_profile.row_count} rows " + " ".join([c.name for c in raw_profile.columns]) + user_instructions
    domain_pbs = idx.hybrid_search(domain_query, "domain", top_k=1, stage="pass0")
    if domain_pbs:
        user_instructions += f"\n\n--- Recommended Industry Best Practices ---\n{domain_pbs[0].content}"
        
    print("  Planning cleaning...")
    query = f"clean missing values outliers anomalies. " + user_instructions
    cleaning_pbs = idx.hybrid_search(query, "cleaning", stage="pass1")
    if not cleaning_pbs and idx.playbooks:
        cleaning_pbs = [pb for pb in idx.playbooks if pb.category == 'cleaning'][:3]
    cleaning_plan = plan_cleaning(raw_profile, cleaning_pbs, user_instructions)
    
    print("  Planning engineering...")
    query_e = f"engineering scaling datetime binning pca. " + user_instructions
    engineering_pbs = idx.hybrid_search(query_e, "engineering", stage="pass2")
    if not engineering_pbs and idx.playbooks:
        engineering_pbs = [pb for pb in idx.playbooks if pb.category == 'engineering'][:4]
    engineering_plan = plan_engineering(raw_profile, engineering_pbs, user_instructions)
    
    print("  Planning analysis...")
    analysis_pbs = idx.hybrid_search("analysis " + user_instructions, "analysis", stage="pass3")
    if not analysis_pbs and idx.playbooks:
        analysis_pbs = [pb for pb in idx.playbooks if pb.category == 'analysis']
    analysis_plan = plan_analysis(raw_profile, analysis_pbs, user_instructions)
    
    print("  Building and executing notebook...")
    builder = NotebookBuilder(filename=f, user_text=user_instructions)
    executed_nb_path = builder.build_notebook(
        raw_profile=raw_profile,
        cleaning_plan=cleaning_plan,
        engineering_plan=engineering_plan,
        cleaned_profile=raw_profile,
        analysis_plan=analysis_plan,
        llm_usage=[],
        raw_cleaning_json=cleaning_plan.model_dump_json(indent=2),
        raw_analysis_json=analysis_plan.model_dump_json(indent=2),
        output_path=os.path.join("temp", f.replace('.csv', '_Validation_Executed.ipynb'))
    )
    
    print("  Checking for errors...")
    import json
    with open(executed_nb_path, 'r', encoding='utf-8') as nb_f:
        nb = json.load(nb_f)
    error_count = 0
    for i, cell in enumerate(nb.get('cells', [])):
        if cell['cell_type'] == 'code':
            for output in cell.get('outputs', []):
                if output.get('output_type') == 'error':
                    print(f"    ! Cell {i} Caught Exception: {output.get('ename')}: {output.get('evalue')}")
                    error_count += 1
    if error_count == 0:
        print("  -> Clean execution! No errors.")
        
    print(f"  Finished {executed_nb_path}\n")

except Exception as e:
    import traceback
    traceback.print_exc()
