import streamlit as st
import os
import pandas as pd
import json
import traceback

from first_pass.ingest import load_spreadsheet
from first_pass.profile import generate_profile, profile_to_json
from first_pass.retrieval.index import PlaybookIndex
from first_pass.llm.planner import plan_cleaning, plan_engineering, plan_analysis, generate_business_questions
from first_pass.llm.client import llm_usage_logs
from first_pass.notebook_builder import NotebookBuilder
from first_pass.export import export_to_html, export_to_py, export_to_docx, export_to_pdf

st.set_page_config(page_title="First Pass", page_icon="🚀", layout="wide")

import dotenv
dotenv.load_dotenv()

# App Header
st.markdown("<h1 style='text-align: center; font-size: 3.5rem; margin-bottom: 0;'>🚀 First Pass</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #555; margin-bottom: 2rem;'>An automated AI data scientist that provides a quick <b>First Pass</b> of your data to guide you in the right direction for further analysis. Upload a dataset to instantly generate an executed Jupyter Notebook, cleaned datasets, and multi-format reports.</p>", unsafe_allow_html=True)

# Main Container
with st.container():
    st.text_input(
        "User Instructions", 
        key="user_text", 
        placeholder="Optional Instructions (e.g., 'this is monthly sales data, I care about regional performance')",
        label_visibility="collapsed"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader("Upload Spreadsheet", type=['csv', 'xlsx', 'xls', 'parquet'])
    with col2:
        context_file = st.file_uploader("Upload Context (Optional .txt, .md, .docx)", type=['txt', 'md', 'docx'])

if uploaded_file is not None:
    os.makedirs("temp", exist_ok=True)
    temp_path = os.path.join("temp", uploaded_file.name)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("⚙️ Advanced AI RAG Passes (Optional)", expanded=False):
        st.write("Enable additional AI reasoning passes to enhance the output quality.")
        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            enable_domain = st.checkbox("Enable Domain Context (Pass 0)", value=True, help="Injects industry KPIs before planning.")
        with col_t2:
            enable_engineering = st.checkbox("Enable Feature Engineering (Pass 2)", value=True, help="Mathematically transforms data before analysis.")
        with col_t3:
            enable_observer = st.checkbox("Enable Multimodal Observer (Pass 4)", value=True, help="Iteratively patches syntax errors and visual chart layouts using a multimodal vision model.")

        
    st.markdown("<br>", unsafe_allow_html=True)
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    with col_btn2:
        run_btn = st.button("✨ Run First Pass", type="primary", use_container_width=True)

    if run_btn:
        if not os.environ.get("GEMINI_API_KEY"):
            st.error("Please add your GEMINI_API_KEY to the .env file in the project directory.")
            st.stop()
            
        context_text = ""
        if context_file is not None:
            try:
                if context_file.name.endswith(('.txt', '.md')):
                    context_text = context_file.read().decode('utf-8', errors='replace')
                elif context_file.name.endswith('.docx'):
                    import docx
                    doc = docx.Document(context_file)
                    context_text = "\n".join([p.text for p in doc.paragraphs])
            except Exception as e:
                st.warning(f"Failed to read context file: {e}")

        combined_instructions = st.session_state.user_text
        if context_text:
            combined_instructions += f"\n\n--- Context Document ({context_file.name}) ---\n{context_text}"
            
        from datetime import datetime
        import time
        run_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        start_time = time.time()
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
                index.build(["playbooks/cleaning", "playbooks/engineering", "playbooks/analysis", "playbooks/domain"])
                return index
            
            try:
                idx = get_index()
            except Exception as e:
                st.error(f"**API Error during Initialization:**\n{e}\n\nPlease check your Gemini API key billing and credits.")
                st.stop()
            
            if enable_domain:
                my_bar.progress(15, text="Stage 2.5: RAG Pass 0 (Domain Context)...")
                domain_query = f"domain industry {raw_profile.row_count} rows " + " ".join([c.name for c in raw_profile.columns]) + combined_instructions
                domain_pbs = idx.hybrid_search(domain_query, "domain", top_k=1, stage="pass0")
                if domain_pbs:
                    combined_instructions += f"\n\n--- Recommended Industry Best Practices ---\n{domain_pbs[0].content}"

            
            my_bar.progress(30, text="Stage 3: RAG Pass 1 (Cleaning Plan)...")
            
            query_c = f"cleaning operations missing values duplicates dates {raw_profile.row_count} rows. " + combined_instructions
            cleaning_pbs = idx.hybrid_search(query_c, "cleaning")
            if not cleaning_pbs and idx.playbooks:
                cleaning_pbs = [pb for pb in idx.playbooks if pb.category == 'cleaning'][:4]
                
            cleaning_plan = plan_cleaning(raw_profile, cleaning_pbs, combined_instructions)
            
            my_bar.progress(50, text="Stage 4: Executing Cleaning (No LLM)...")
            cleaned_profile = raw_profile 
            
            engineering_plan = None
            if enable_engineering:
                my_bar.progress(60, text="Stage 4.5: RAG Pass 2 (Feature Engineering Plan)...")
                query_e = f"engineering scaling datetime binning pca. " + combined_instructions
                engineering_pbs = idx.hybrid_search(query_e, "engineering", stage="pass2")
                if not engineering_pbs and idx.playbooks:
                    engineering_pbs = [pb for pb in idx.playbooks if pb.category == 'engineering'][:4]
                engineering_plan = plan_engineering(cleaned_profile, engineering_pbs, combined_instructions)
            
            my_bar.progress(70, text="Stage 5: RAG Pass 3 (Analysis Plan)...")
            
            query_a = f"analysis distribution categories correlations trends. " + combined_instructions
            analysis_pbs = idx.hybrid_search(query_a, "analysis", top_k=15)
            if not analysis_pbs and idx.playbooks:
                analysis_pbs = [pb for pb in idx.playbooks if pb.category == 'analysis'][:15]
                
            analysis_plan = plan_analysis(cleaned_profile, analysis_pbs, combined_instructions)
            
            # Prepend static overview analyses
            from first_pass.schemas import AnalysisItem, AnalysisSection
            static_analyses = [
                AnalysisItem(title="Column Overview", template_id="column_overview", columns=[], rationale="Overview of column types and missing values.", playbook_ids=[]),
                AnalysisItem(title="Summary Statistics", template_id="summary_stats", columns=[], rationale="High-level summary statistics of all columns.", playbook_ids=[])
            ]
                
            static_section = AnalysisSection(
                title="Data Overview",
                description="High-level summary of data types, summary statistics, and missing values.",
                analyses=static_analyses
            )
            analysis_plan.sections.insert(0, static_section)
            
            my_bar.progress(85, text="Stage 6: Generating Notebook...")
            
            nb_path = os.path.join("temp", f"{os.path.splitext(uploaded_file.name)[0]}_FirstPass.ipynb")
            builder = NotebookBuilder(filename=temp_path, user_text=combined_instructions)
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
            
            my_bar.progress(90, text="Executing Notebook...")
            executed_nb_path = os.path.join("temp", f"{os.path.splitext(uploaded_file.name)[0]}_FirstPass_Executed.ipynb")
            builder.execute_notebook(nb_path, executed_nb_path, enable_observer=enable_observer)
            
            my_bar.progress(95, text="Exporting to HTML format...")
            html_path = export_to_html(executed_nb_path, "temp")
            
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
            st.session_state['synthesis_path'] = None
            st.session_state['run_complete'] = True
            st.session_state['executed_nb_path'] = executed_nb_path
            st.session_state['html_path'] = html_path
            st.session_state['csv_path'] = csv_path
            st.session_state['excel_path'] = excel_path
            st.session_state['xls_path'] = xls_path
            st.session_state['parquet_path'] = parquet_path
            st.session_state['llm_logs'] = llm_usage_logs.copy()
            st.session_state['last_file'] = uploaded_file.name
            st.session_state['run_duration'] = time.time() - start_time
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.text(traceback.format_exc())

    @st.fragment
    def render_downloads():
        st.markdown(f"<h3 style='margin-top: 2rem;'>Downloads: {st.session_state.get('last_file', '')}</h3>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            with st.container(border=True):
                st.markdown("#### 💻 Code")
                if os.path.exists(st.session_state.get('executed_nb_path', '')):
                    with open(st.session_state['executed_nb_path'], "rb") as f:
                        st.download_button("Notebook (.ipynb)", f, file_name=os.path.basename(st.session_state['executed_nb_path']), use_container_width=True, type="primary")
                
                if 'py_path' in st.session_state and os.path.exists(st.session_state['py_path']):
                    with open(st.session_state['py_path'], "rb") as f:
                        st.download_button("Download Script (.py)", f, file_name=os.path.basename(st.session_state['py_path']), use_container_width=True)
                else:
                    if st.button("Generate Script (.py)", use_container_width=True):
                        with st.spinner("Generating..."):
                            st.session_state['py_path'] = export_to_py(st.session_state['executed_nb_path'], "temp")
                    
        with col2:
            with st.container(border=True):
                st.markdown("#### 📊 Reports")
                if os.path.exists(st.session_state.get('html_path', '')):
                    with open(st.session_state['html_path'], "rb") as f:
                        st.download_button("HTML", f, file_name=os.path.basename(st.session_state['html_path']), mime='text/html', use_container_width=True, type="primary")
                
                if 'pdf_path' in st.session_state and os.path.exists(st.session_state['pdf_path']):
                    with open(st.session_state['pdf_path'], "rb") as f:
                        st.download_button("Download PDF", f, file_name=os.path.basename(st.session_state['pdf_path']), use_container_width=True)
                else:
                    if st.button("Generate PDF", use_container_width=True):
                        with st.spinner("Generating..."):
                            st.session_state['pdf_path'] = export_to_pdf(st.session_state['executed_nb_path'], "temp")
                
                if 'docx_path' in st.session_state and os.path.exists(st.session_state['docx_path']):
                    with open(st.session_state['docx_path'], "rb") as f:
                        st.download_button("Download DOCX", f, file_name=os.path.basename(st.session_state['docx_path']), use_container_width=True)
                else:
                    if st.button("Generate DOCX", use_container_width=True):
                        with st.spinner("Generating..."):
                            st.session_state['docx_path'] = export_to_docx(st.session_state['executed_nb_path'], "temp")
                    
        with col3:
            with st.container(border=True):
                st.markdown("#### 💾 Cleaned Datasets")
                if 'csv_path' in st.session_state and os.path.exists(st.session_state['csv_path']):
                    with open(st.session_state['csv_path'], "rb") as f:
                        st.download_button("CSV", f, file_name=os.path.basename(st.session_state['csv_path']), use_container_width=True, type="primary")
                if 'excel_path' in st.session_state and os.path.exists(st.session_state['excel_path']):
                    with open(st.session_state['excel_path'], "rb") as f:
                        st.download_button("Excel (.xlsx)", f, file_name=os.path.basename(st.session_state['excel_path']), use_container_width=True)
                if 'xls_path' in st.session_state and os.path.exists(st.session_state['xls_path']):
                    with open(st.session_state['xls_path'], "rb") as f:
                        st.download_button("Excel (.xls)", f, file_name=os.path.basename(st.session_state['xls_path']), use_container_width=True)
                if 'parquet_path' in st.session_state and os.path.exists(st.session_state['parquet_path']):
                    with open(st.session_state['parquet_path'], "rb") as f:
                        st.download_button("Parquet", f, file_name=os.path.basename(st.session_state['parquet_path']), use_container_width=True)

    if st.session_state.get('run_complete'):
        st.success(f"🚀 First Pass completed successfully for **{st.session_state.get('last_file', 'your file')}**!")
        render_downloads()
                    
        # Show Token Usage
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("⚙️ Diagnostics & Token Usage"):
            if 'llm_logs' in st.session_state and st.session_state['llm_logs']:
                df_usage = pd.DataFrame(st.session_state['llm_logs'])
                if 'timestamp' in df_usage.columns and 'file' in df_usage.columns:
                    cols = ['timestamp', 'file'] + [c for c in df_usage.columns if c not in ['timestamp', 'file']]
                    df_usage = df_usage[cols]
                st.dataframe(df_usage, use_container_width=True)
                st.write(f"**Total Run Cost:** ${df_usage['cost'].sum():.6f}")
                if 'run_duration' in st.session_state:
                    st.write(f"**Total Run Duration:** {st.session_state['run_duration']:.1f} seconds")
            else:
                st.write("No LLM calls logged.")

