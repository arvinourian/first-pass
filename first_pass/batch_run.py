import os
import glob
import pandas as pd
import json
import traceback
import dotenv

dotenv.load_dotenv()

from first_pass.ingest import load_spreadsheet
from first_pass.profile import generate_profile
from first_pass.retrieval.index import PlaybookIndex
from first_pass.llm.planner import plan_cleaning, plan_engineering, plan_analysis
from first_pass.llm.client import llm_usage_logs
from first_pass.notebook_builder import NotebookBuilder
from first_pass.schemas import AnalysisItem, AnalysisSection

datasets = [
    {
        'csv': r"C:\Users\arvin\Desktop\Sample Datasets\AI_SocialMedia_Student_Dataset.csv",
        'context': ""
    },
    {
        'csv': r"C:\Users\arvin\Desktop\Sample Datasets\all_ironman_suit.csv",
        'context': ""
    },
    {
        'csv': r"C:\Users\arvin\Desktop\Sample Datasets\college_major_roi.csv",
        'context': r"C:\Users\arvin\Desktop\Sample Datasets\college_major_roi_dict.csv"
    },
    {
        'csv': r"C:\Users\arvin\Desktop\Sample Datasets\opa data - philadelphia_sfh_modeling.csv",
        'context': r"C:\Users\arvin\Desktop\Sample Datasets\opa data - philadelphia_sfh_modeling.md"
    },
    {
        'csv': r"C:\Users\arvin\Desktop\Sample Datasets\Walmart_Sales.csv",
        'context': ""
    }
]

idx = PlaybookIndex()
idx.build(["playbooks/cleaning", "playbooks/engineering", "playbooks/analysis", "playbooks/domain"])

for item in datasets:
    csv_path = item['csv']
    context_path = item['context']
    
    print(f"=== Processing {os.path.basename(csv_path)} ===")
    
    user_instructions = ""
    if context_path and os.path.exists(context_path):
        with open(context_path, 'r', encoding='utf-8') as f:
            user_instructions = f.read()
            
    df = load_spreadsheet(csv_path)
    raw_profile = generate_profile(df)
    
    # Domain Pass
    domain_query = f"domain industry {raw_profile.row_count} rows " + " ".join([c.name for c in raw_profile.columns]) + user_instructions
    domain_pbs = idx.hybrid_search(domain_query, "domain", top_k=1)
    if domain_pbs:
        user_instructions += f"\n\n--- Recommended Industry Best Practices ---\n{domain_pbs[0].content}"
        
    print("  Planning cleaning...")
    query_c = f"cleaning operations missing values duplicates dates {raw_profile.row_count} rows. " + user_instructions
    cleaning_pbs = idx.hybrid_search(query_c, "cleaning")
    if not cleaning_pbs and idx.playbooks:
        cleaning_pbs = [pb for pb in idx.playbooks if pb.category == 'cleaning'][:4]
    cleaning_plan = plan_cleaning(raw_profile, cleaning_pbs, user_instructions)
    
    cleaned_profile = raw_profile
    
    print("  Planning engineering...")
    query_e = f"engineering scaling datetime binning pca. " + user_instructions
    engineering_pbs = idx.hybrid_search(query_e, "engineering")
    if not engineering_pbs and idx.playbooks:
        engineering_pbs = [pb for pb in idx.playbooks if pb.category == 'engineering'][:4]
    engineering_plan = plan_engineering(cleaned_profile, engineering_pbs, user_instructions)
    
    print("  Planning analysis...")
    query_a = f"analysis distribution categories correlations trends. " + user_instructions
    analysis_pbs = idx.hybrid_search(query_a, "analysis", top_k=15)
    if not analysis_pbs and idx.playbooks:
        analysis_pbs = [pb for pb in idx.playbooks if pb.category == 'analysis'][:15]
    analysis_plan = plan_analysis(cleaned_profile, analysis_pbs, user_instructions)
    
    static_analyses = [
        AnalysisItem(template_id="column_overview", columns=[], rationale="Overview of column types and missing values.", playbook_ids=[]),
        AnalysisItem(template_id="summary_stats", columns=[], rationale="High-level summary statistics of all columns.", playbook_ids=[])
    ]
    static_section = AnalysisSection(
        title="Data Overview",
        description="High-level summary of data types, summary statistics, and missing values.",
        analyses=static_analyses
    )
    analysis_plan.sections.insert(0, static_section)
    
    nb_path = os.path.join("temp", f"{os.path.splitext(os.path.basename(csv_path))[0]}_Validation.ipynb")
    os.makedirs("temp", exist_ok=True)
    
    print("  Building and executing notebook...")
    builder = NotebookBuilder(filename=csv_path, user_text=user_instructions)
    builder.build_notebook(
        raw_profile=raw_profile,
        cleaning_plan=cleaning_plan,
        engineering_plan=engineering_plan,
        cleaned_profile=cleaned_profile,
        analysis_plan=analysis_plan,
        llm_usage=llm_usage_logs,
        raw_cleaning_json=cleaning_plan.model_dump_json(indent=2),
        raw_analysis_json=analysis_plan.model_dump_json(indent=2),
        output_path=nb_path
    )
    
    executed_nb_path = nb_path.replace('_Validation.ipynb', '_Validation_Executed.ipynb')
    builder.execute_notebook(nb_path, executed_nb_path, enable_observer=True)
    
    # Parse notebook for errors
    print("  Checking for errors...")
    with open(executed_nb_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
        
    error_count = 0
    for i, cell in enumerate(nb['cells']):
        if cell['cell_type'] == 'code':
            for output in cell.get('outputs', []):
                if output.get('output_type') == 'error':
                    print(f"    ! Cell {i} Error: {output.get('ename')}")
                    error_count += 1
                elif output.get('output_type') == 'stream' and 'text' in output:
                    text = ''.join(output['text'])
                    if 'Error executing' in text or 'Traceback' in text:
                        print(f"    ! Cell {i} Caught Exception: {text.strip().split(chr(10))[0]}")
                        error_count += 1
                        
    if error_count == 0:
        print("  -> Clean execution! No errors.")
        
    print(f"  Finished {executed_nb_path}\n")
