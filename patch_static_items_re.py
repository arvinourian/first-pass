import os
import re

for fpath in ['first_pass/app.py', 'first_pass/batch_run.py']:
    if os.path.exists(fpath):
        with open(fpath, 'r', encoding='utf-8') as f:
            text = f.read()
            
        # Replace all AnalysisItem without title
        text = re.sub(r'AnalysisItem\(template_id="column_overview"', 'AnalysisItem(title="Column Overview", template_id="column_overview"', text)
        text = re.sub(r'AnalysisItem\(template_id="summary_stats"', 'AnalysisItem(title="Summary Statistics", template_id="summary_stats"', text)

        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(text)
