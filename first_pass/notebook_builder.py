import nbformat as nbf
from nbclient import NotebookClient
from datetime import datetime
import json
import os
from .schemas import DataProfile, CleaningPlan, AnalysisPlan

class NotebookBuilder:
    def __init__(self, filename: str, user_text: str = ""):
        self.nb = nbf.v4.new_notebook()
        self.filename = filename
        self.user_text = user_text
        self.version = "1.1.0"
        
    def add_markdown(self, text: str):
        self.nb.cells.append(nbf.v4.new_markdown_cell(text))
        
    def add_code(self, code: str):
        self.nb.cells.append(nbf.v4.new_code_cell(code))
        
    def build_notebook(self, 
                      raw_profile: DataProfile, 
                      cleaning_plan: CleaningPlan,
                       engineering_plan,
                       cleaned_profile: DataProfile,
                      analysis_plan: AnalysisPlan,
                      llm_usage: list,
                      raw_cleaning_json: str,
                      raw_analysis_json: str,
                      output_path: str):
        
        # 1. Title
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.add_markdown(f"# First Pass: {os.path.basename(self.filename)}\n\n"
                          f"**Run Timestamp:** {now}\n"
                          f"**First Pass Version:** {self.version}")
        
        # 2. Input summary
        summary = f"## Input Summary\n"
        summary += f"- **File:** {self.filename}\n"
        summary += f"- **Shape:** {raw_profile.row_count} rows, {raw_profile.column_count} columns\n"
        if self.user_text:
            summary += f"- **User Input:** {self.user_text}\n"
        self.add_markdown(summary)
        
        # 3. Raw data profile + head
        self.add_markdown("## Raw Data Profile")
        safe_filename = self.filename.replace('\\', '/')
        self.add_code(
            f"%matplotlib inline\n"
            f"import pandas as pd\n"
            f"import matplotlib.pyplot as plt\n"
            f"import seaborn as sns\n"
            f"import warnings\n"
            f"warnings.filterwarnings('ignore')\n"
            f"sns.set_theme(style='whitegrid', palette='deep')\n"
            f"from IPython.display import display\n"
            f"from first_pass.ingest import load_spreadsheet\n"
            f"df = load_spreadsheet('{safe_filename}')\n"
            f"display(df.head())\n"
            f"df.info()"
        )
        
        # 4. Cleaning plan
        cleaning_md = "## Cleaning Plan\n"
        if not cleaning_plan.steps:
            cleaning_md += "No cleaning steps planned.\n"
        else:
            cleaning_md += "| Step | Columns | Template | Rationale | Playbooks |\n"
            cleaning_md += "|---|---|---|---|---|\n"
            for i, step in enumerate(cleaning_plan.steps):
                cols = ", ".join(step.columns)
                pbs = ", ".join(step.playbook_ids)
                cleaning_md += f"| {i+1} | {cols} | `{step.template_id}` | {step.rationale} | {pbs} |\n"
        self.add_markdown(cleaning_md)
        
        # 5. Cleaning execution
        self.add_markdown("## Cleaning Execution")
        for step in cleaning_plan.steps:
            self.add_markdown(f"### {step.template_id}\n{step.rationale}")
            # Here we would dynamically look up the template code.
            # For now, we assume templates are in a module and we can format them.
            code = self._render_template('cleaning', step.template_id, step.columns, step.params)
            
            # Wrap with before/after logging
            log_wrapper = (
                f"print(f'Before {step.template_id}: {{df.shape[0]}} rows, {{df.shape[1]}} columns')\n"
                f"{code}\n"
                f"print(f'After {step.template_id}: {{df.shape[0]}} rows, {{df.shape[1]}} columns')\n"
            )
            self.add_code(log_wrapper)
            
        # 6. Cleaned Data Profile
        self.add_markdown("## Cleaned Data Profile")
        self.add_code("display(df.head())\ndf.info()")
        
        # Export Cleaned Data
        self.add_markdown("## Export Cleaned Data")
        base_name = os.path.splitext(os.path.basename(output_path))[0]
        csv_out = os.path.join("temp", f"{base_name}_cleaned.csv")
        excel_out = os.path.join("temp", f"{base_name}_cleaned.xlsx")
        xls_out = os.path.join("temp", f"{base_name}_cleaned.xls")
        parquet_out = os.path.join("temp", f"{base_name}_cleaned.parquet")
        
        self.add_code(
            f"try:\n"
            f"    df.to_csv('{csv_out.replace(chr(92), '/')}', index=False)\n"
            f"    df.to_excel('{excel_out.replace(chr(92), '/')}', index=False)\n"
            f"    df.to_parquet('{parquet_out.replace(chr(92), '/')}', index=False)\n"
            f"    # Manual xls export since pandas dropped it\n"
            f"    import xlwt\n"
            f"    wb = xlwt.Workbook()\n"
            f"    ws = wb.add_sheet('Sheet1')\n"
            f"    import csv\n"
            f"    with open('{csv_out.replace(chr(92), '/')}', 'r', encoding='utf-8') as f:\n"
            f"        for r, row in enumerate(csv.reader(f)):\n"
            f"            for c, val in enumerate(row):\n"
            f"                ws.write(r, c, val)\n"
            f"    wb.save('{xls_out.replace(chr(92), '/')}')\n"
            f"except Exception as e:\n"
            f"    print(f'Error saving dataset: {{e}}')"
        )
        
        # 7. Analysis Plan
        analysis_md = "## Analysis Plan\n"
        if not analysis_plan.sections:
            analysis_md += "No analyses planned.\n"
        else:
            if analysis_plan.target_variables:
                analysis_md += f"**Target Variables:** {', '.join(analysis_plan.target_variables)}\n\n"
            for s_idx, sec in enumerate(analysis_plan.sections):
                analysis_md += f"### Section {s_idx+1}: {sec.title}\n{sec.description}\n\n"
                analysis_md += "| Step | Columns | Template | Rationale | Playbooks |\n"
                analysis_md += "|---|---|---|---|---|\n"
                for i, item in enumerate(sec.analyses):
                    cols = ", ".join(item.columns)
                    pbs = ", ".join(item.playbook_ids)
                    analysis_md += f"| {i+1} | {cols} | `{item.template_id}` | {item.rationale} | {pbs} |\n"
                analysis_md += "\n"
        self.add_markdown(analysis_md)
        
        # 8. Analysis execution
        # Removed the generic "## Analysis Execution" header to let the sections stand on their own
        for s_idx, sec in enumerate(analysis_plan.sections):
            self.add_markdown(f"## {s_idx+1}. {sec.title}\n{sec.description}")
            for item in sec.analyses:
                self.add_markdown(f"### {item.title}\n{item.rationale}")
                code = self._render_template('analysis', item.template_id, item.columns, item.params)
                error_wrapper = (
                    f"try:\n"
                    f"    {code.replace(chr(10), chr(10) + '    ')}\n"
                    f"except Exception as e:\n"
                    f"    print(f'\\nError executing {item.template_id}: {{e}}')\n"
                )
                self.add_code(error_wrapper)
            
        # 8.5 Further Analyses
        if hasattr(analysis_plan, 'further_analyses') and analysis_plan.further_analyses:
            fa_md = "## Further Analyses to Consider\n"
            fa_md += "The following analyses were considered relevant but skipped to keep this first pass concise.\n\n"
            fa_md += "| Tool | Columns | Rationale |\n"
            fa_md += "|---|---|---|\n"
            for item in analysis_plan.further_analyses:
                cols = ", ".join(item.columns) if item.columns else "N/A"
                fa_md += f"| `{item.template_id}` | {cols} | {item.rationale} |\n"
            self.add_markdown(fa_md)
            
        # 9. Appendix
        self.add_markdown("## Appendix")
        self.add_markdown("### Raw Cleaning Plan JSON\n```json\n" + raw_cleaning_json + "\n```")
        self.add_markdown("### Raw Analysis Plan JSON\n```json\n" + raw_analysis_json + "\n```")
        
        # Save generated notebook
        with open(output_path, 'w', encoding='utf-8') as f:
            nbf.write(self.nb, f)
            
        return output_path

    def _render_template(self, category: str, template_id: str, columns: list, params: str) -> str:
        """Looks up a template and injects parameters to return runnable python code."""
        # For phase 2, we will just use a simple registry
        from first_pass.templates.registry import get_template_code
        try:
            params_dict = json.loads(params)
        except Exception:
            params_dict = {}
        return get_template_code(category, template_id, columns, params_dict)

    def execute_notebook(self, notebook_path: str, output_path: str = None, enable_observer: bool = False, max_loops: int = 3):
        if output_path is None:
            output_path = notebook_path
            
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbf.read(f, as_version=4)
            
        client = NotebookClient(nb, timeout=600, kernel_name='python3', allow_errors=True)
        try:
            with client.setup_kernel():
                # Initial Run
                for i, cell in enumerate(nb.cells):
                    client.execute_cell(cell, i)
                    
                if enable_observer:
                    from first_pass.llm.observer import generate_patches
                    
                    for loop in range(max_loops):
                        print(f"  Observer Loop {loop+1}/{max_loops}...")
                        # Convert notebook to dict for observer
                        cells_dict = [c.dict() for c in nb.cells]
                        response = generate_patches(cells_dict, self.user_text)
                        
                        if not response.patches:
                            print("    Observer found no issues. Terminating loop.")
                            break
                            
                        print(f"    Observer found {len(response.patches)} patches.")
                        for patch in response.patches:
                            idx = patch.cell_index
                            if 0 <= idx < len(nb.cells):
                                # Clear old outputs
                                nb.cells[idx].outputs = []
                                nb.cells[idx].execution_count = None
                                # Replace code
                                nb.cells[idx].source = patch.new_code
                                # Re-execute just this cell!
                                try:
                                    client.execute_cell(nb.cells[idx], idx)
                                except Exception as e:
                                    print(f"    Error re-executing cell {idx}: {e}")
                                    
        except Exception as e:
            print(f"Error executing notebook: {e}")
            
        with open(output_path, 'w', encoding='utf-8') as f:
            nbf.write(nb, f)
            
        # Post-execution Synthesis Pass
        if enable_observer:
            from first_pass.llm.synthesis import generate_key_takeaways, generate_interpretations
            
            print("  Generating Interpretations...")
            interpretations = generate_interpretations(output_path, self.user_text)
            
            # Insert interpretations bottom-up to preserve indices
            for interp in sorted(interpretations, key=lambda x: x.cell_index, reverse=True):
                idx = interp.cell_index
                if 0 <= idx < len(nb.cells):
                    interp_cell = nbf.v4.new_markdown_cell(f"**Insight:** {interp.markdown}")
                    nb.cells.insert(idx + 1, interp_cell)
            
            takeaways = generate_key_takeaways(output_path, self.user_text)
            
            # Insert at the top (index 1, right after the title)
            takeaway_cell = nbf.v4.new_markdown_cell(takeaways)
            nb.cells.insert(1, takeaway_cell)
            
            # Save again
            with open(output_path, 'w', encoding='utf-8') as f:
                nbf.write(nb, f)
                
        return output_path
