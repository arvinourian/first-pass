import os

for fpath in ['first_pass/app.py', 'first_pass/batch_run.py']:
    if os.path.exists(fpath):
        with open(fpath, 'r', encoding='utf-8') as f:
            text = f.read()
            
        old_item1 = 'AnalysisItem(template_id="column_overview", columns=[], rationale="Overview of column types and missing values.", playbook_ids=[])'
        new_item1 = 'AnalysisItem(title="Column Overview", template_id="column_overview", columns=[], rationale="Overview of column types and missing values.", playbook_ids=[])'
        
        old_item2 = 'AnalysisItem(template_id="summary_stats", columns=[], rationale="Descriptive statistics of the dataset.", playbook_ids=[])'
        new_item2 = 'AnalysisItem(title="Summary Statistics", template_id="summary_stats", columns=[], rationale="Descriptive statistics of the dataset.", playbook_ids=[])'

        text = text.replace(old_item1, new_item1)
        text = text.replace(old_item2, new_item2)

        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(text)
