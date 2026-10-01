import re

with open('first_pass/app.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_text = """            # Save results in session state
            st.session_state['run_complete'] = True"""

new_text = """            
            synthesis_path = None
            if enable_synthesis:
                my_bar.progress(95, text="Stage 7: RAG Pass 3 (Executive Synthesis)...")
                from first_pass.llm.synthesis import synthesize_report
                report_md = synthesize_report(executed_nb_path, combined_instructions)
                synthesis_path = os.path.join("temp", f"{base_name}_Executive_Summary.md")
                with open(synthesis_path, 'w', encoding='utf-8') as sf:
                    sf.write(report_md)
            
            # Save results in session state
            st.session_state['synthesis_path'] = synthesis_path
            st.session_state['run_complete'] = True"""

text = text.replace(old_text, new_text)

# We also need to add a download button for the synthesis report!
old_ui_text = """                        st.download_button(
                            label="📄 Excel",
                            data=f,
                            file_name=os.path.basename(st.session_state['excel_path']),
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )"""

new_ui_text = """                        st.download_button(
                            label="📄 Excel",
                            data=f,
                            file_name=os.path.basename(st.session_state['excel_path']),
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                if st.session_state.get('synthesis_path') and os.path.exists(st.session_state['synthesis_path']):
                    with open(st.session_state['synthesis_path'], "rb") as f:
                        st.download_button(
                            label="📝 Executive Summary",
                            data=f,
                            file_name=os.path.basename(st.session_state['synthesis_path']),
                            mime="text/markdown",
                            use_container_width=True
                        )"""

text = text.replace(old_ui_text, new_ui_text)

with open('first_pass/app.py', 'w', encoding='utf-8') as f:
    f.write(text)
