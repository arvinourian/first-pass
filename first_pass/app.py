import streamlit as st
import os
import pandas as pd
import json
import traceback

from first_pass.ingest import load_spreadsheet
from first_pass.profile import generate_profile, profile_to_json
from first_pass.retrieval.index import PlaybookIndex
from first_pass.llm.planner import plan_cleaning, plan_analysis
from first_pass.llm.client import llm_usage_logs
from first_pass.notebook_builder import NotebookBuilder
from first_pass.export import export_notebook

st.set_page_config(page_title="First Pass", layout="wide")

import dotenv
dotenv.load_dotenv()

st.title("First Pass")
st.markdown("An automated AI data scientist that provides a quick \"First Pass\" of your data to guide you in the right direction for further analysis. Upload a dataset to instantly generate an executed Jupyter Notebook, cleaned datasets, and multi-format reports.")
        
st.text_input(
    "User Instructions", 
    key="user_text", 
    placeholder="Optional Instructions (e.g., 'this is monthly sales data, I care about regional performance')",
    label_visibility="collapsed"
)

uploaded_file = st.file_uploader("Upload Spreadsheet", type=['csv', 'xlsx', 'xls', 'parquet'])

if uploaded_file is not None:
    os.makedirs("temp", exist_ok=True)
    temp_path = os.path.join("temp", uploaded_file.name)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    st.write(f"**Uploaded:** {uploaded_file.name}")
    
    if st.button("Run First Pass"):
        if not os.environ.get("GEMINI_API_KEY"):
            st.error("Please add your GEMINI_API_KEY to the .env file in the project directory.")
            st.stop()
            
        from datetime import datetime
        run_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        start_log_idx = len(llm_usage_logs)
            
        progress_placeholder = st.empty()
        my_bar = progress_placeholder.progress(0, text="Stage 1: Ingesting Data...")
        
        try:
            # Stage 1: Ingest
            df = load_spreadsheet(temp_path)
            my_bar.progress(10, text="Stage 2: Profiling Data...")
            
            # Stage 2: Profile
            raw_profile = generate_profile(df)
            
            # Setup Index
            @st.cache_resource
            def get_index():
                index = PlaybookIndex()
                index.build(["playbooks/cleaning", "playbooks/analysis"])
                return index
            
            idx = get_index()
            
            my_bar.progress(30, text="Stage 3: RAG Pass 1 (Cleaning Plan)...")
            
            query_c = f"cleaning operations missing values duplicates dates {raw_profile.row_count} rows. " + st.session_state.user_text
            cleaning_pbs = idx.hybrid_search(query_c, "cleaning")
            if not cleaning_pbs and idx.playbooks:
                cleaning_pbs = [pb for pb in idx.playbooks if pb.category == 'cleaning'][:4]
                
            cleaning_plan = plan_cleaning(raw_profile, cleaning_pbs, st.session_state.user_text)
            
            my_bar.progress(50, text="Stage 4: Executing Cleaning (No LLM)...")
            cleaned_profile = raw_profile 
            
            my_bar.progress(70, text="Stage 5: RAG Pass 2 (Analysis Plan)...")
            
            query_a = f"analysis distribution categories correlations trends. " + st.session_state.user_text
            analysis_pbs = idx.hybrid_search(query_a, "analysis", top_k=6)
            if not analysis_pbs and idx.playbooks:
                analysis_pbs = [pb for pb in idx.playbooks if pb.category == 'analysis'][:6]
                
            analysis_plan = plan_analysis(cleaned_profile, analysis_pbs, st.session_state.user_text)
            
            # Prepend static overview analyses
            from first_pass.schemas import AnalysisItem
            static_analyses = [
                AnalysisItem(template_id="column_overview", columns=[], rationale="Overview of column types and missing values.", playbook_ids=[]),
                AnalysisItem(template_id="summary_stats", columns=[], rationale="High-level summary statistics of all columns.", playbook_ids=[])
            ]
            if any(col.null_percent > 0 for col in cleaned_profile.columns):
                static_analyses.append(AnalysisItem(template_id="missing_bar", columns=[], params='{"min_null_pct": 0}', rationale="Visualize missing values across columns.", playbook_ids=[]))
                
            analysis_plan.analyses = static_analyses + analysis_plan.analyses
            
            my_bar.progress(85, text="Stage 6: Generating Notebook...")
            
            nb_path = os.path.join("temp", f"{os.path.splitext(uploaded_file.name)[0]}_FirstPass.ipynb")
            builder = NotebookBuilder(filename=temp_path, user_text=st.session_state.user_text)
            builder.build_notebook(
                raw_profile=raw_profile,
                cleaning_plan=cleaning_plan,
                cleaned_profile=cleaned_profile,
                analysis_plan=analysis_plan,
                llm_usage=llm_usage_logs,
                raw_cleaning_json=cleaning_plan.model_dump_json(indent=2),
                raw_analysis_json=analysis_plan.model_dump_json(indent=2),
                output_path=nb_path
            )
            
            my_bar.progress(90, text="Executing Notebook...")
            executed_nb_path = os.path.join("temp", f"{os.path.splitext(uploaded_file.name)[0]}_FirstPass_Executed.ipynb")
            builder.execute_notebook(nb_path, executed_nb_path)
            
            my_bar.progress(95, text="Exporting to final formats...")
            py_path, html_path, md_path, docx_path, pdf_path = export_notebook(executed_nb_path, "temp")
            
            # Clear dynamic progress bar because it will be drawn statically
            progress_placeholder.empty()
            
            # Predict dataset paths based on notebook_builder output
            base_name = os.path.splitext(os.path.basename(nb_path))[0]
            csv_path = os.path.join("temp", f"{base_name}_cleaned.csv")
            excel_path = os.path.join("temp", f"{base_name}_cleaned.xlsx")
            xls_path = os.path.join("temp", f"{base_name}_cleaned.xls")
            parquet_path = os.path.join("temp", f"{base_name}_cleaned.parquet")
            
            # Update LLM logs with file and timestamp
            for i in range(start_log_idx, len(llm_usage_logs)):
                llm_usage_logs[i]['file'] = uploaded_file.name
                llm_usage_logs[i]['timestamp'] = run_timestamp
            
            # Save results in session state
            st.session_state['run_complete'] = True
            st.session_state['executed_nb_path'] = executed_nb_path
            st.session_state['py_path'] = py_path
            st.session_state['html_path'] = html_path
            st.session_state['md_path'] = md_path
            st.session_state['docx_path'] = docx_path
            st.session_state['pdf_path'] = pdf_path
            st.session_state['csv_path'] = csv_path
            st.session_state['excel_path'] = excel_path
            st.session_state['xls_path'] = xls_path
            st.session_state['parquet_path'] = parquet_path
            st.session_state['llm_logs'] = llm_usage_logs.copy()
            st.session_state['last_file'] = uploaded_file.name
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.text(traceback.format_exc())

    if st.session_state.get('run_complete'):
        st.progress(100, text="Done!")
        st.success(f"First Pass completed successfully for {st.session_state.get('last_file', 'your file')}!")
        st.markdown(f"### Downloads: {st.session_state.get('last_file', '')}")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            with st.container(border=True):
                st.markdown("#### Code")
                if os.path.exists(st.session_state.get('executed_nb_path', '')):
                    with open(st.session_state['executed_nb_path'], "rb") as f:
                        st.download_button("Notebook (.ipynb)", f, file_name=os.path.basename(st.session_state['executed_nb_path']))
                if os.path.exists(st.session_state.get('py_path', '')):
                    with open(st.session_state['py_path'], "rb") as f:
                        st.download_button("Script (.py)", f, file_name=os.path.basename(st.session_state['py_path']))
                    
        with col2:
            with st.container(border=True):
                st.markdown("#### Reports")
                if 'pdf_path' in st.session_state and os.path.exists(st.session_state['pdf_path']):
                    with open(st.session_state['pdf_path'], "rb") as f:
                        st.download_button("PDF", f, file_name=os.path.basename(st.session_state['pdf_path']))
                if os.path.exists(st.session_state.get('html_path', '')):
                    with open(st.session_state['html_path'], "rb") as f:
                        st.download_button("HTML", f, file_name=os.path.basename(st.session_state['html_path']), mime='text/html')
                if 'md_path' in st.session_state and os.path.exists(st.session_state['md_path']):
                    pass
                if 'docx_path' in st.session_state and os.path.exists(st.session_state['docx_path']):
                    with open(st.session_state['docx_path'], "rb") as f:
                        st.download_button("DOCX", f, file_name=os.path.basename(st.session_state['docx_path']))
                    
        with col3:
            with st.container(border=True):
                st.markdown("#### Cleaned Datasets")
                if 'csv_path' in st.session_state and os.path.exists(st.session_state['csv_path']):
                    with open(st.session_state['csv_path'], "rb") as f:
                        st.download_button("CSV", f, file_name=os.path.basename(st.session_state['csv_path']))
                if 'excel_path' in st.session_state and os.path.exists(st.session_state['excel_path']):
                    with open(st.session_state['excel_path'], "rb") as f:
                        st.download_button("Excel (.xlsx)", f, file_name=os.path.basename(st.session_state['excel_path']))
                if 'xls_path' in st.session_state and os.path.exists(st.session_state['xls_path']):
                    with open(st.session_state['xls_path'], "rb") as f:
                        st.download_button("Excel (.xls)", f, file_name=os.path.basename(st.session_state['xls_path']))
                if 'parquet_path' in st.session_state and os.path.exists(st.session_state['parquet_path']):
                    with open(st.session_state['parquet_path'], "rb") as f:
                        st.download_button("Parquet", f, file_name=os.path.basename(st.session_state['parquet_path']))
                    
        # Show Token Usage
        st.markdown("### LLM Token Usage & Cost (Testing Purposes)")
        if 'llm_logs' in st.session_state and st.session_state['llm_logs']:
            # Reorder columns to put timestamp and file first if they exist
            df_usage = pd.DataFrame(st.session_state['llm_logs'])
            if 'timestamp' in df_usage.columns and 'file' in df_usage.columns:
                cols = ['timestamp', 'file'] + [c for c in df_usage.columns if c not in ['timestamp', 'file']]
                df_usage = df_usage[cols]
            st.dataframe(df_usage)
            st.write(f"**Total Cost:** ${df_usage['cost'].sum():.6f}")
        else:
            st.write("No LLM calls logged.")

