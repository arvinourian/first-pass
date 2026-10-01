with open('first_pass/app.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Remove UI checkbox
text = text.replace("""        with col_t3:
            enable_synthesis = st.checkbox("Enable Executive Synthesis (Pass 4)", value=True, help="Writes a human-readable business report of the findings.")""", "")

# Remove synthesis execution
old_synth = """            synthesis_path = None
            if enable_synthesis:
                my_bar.progress(95, text="Stage 7: RAG Pass 4 (Executive Synthesis)...")
                from first_pass.llm.synthesis import synthesize_report
                report_md = synthesize_report(executed_nb_path, combined_instructions)
                synthesis_path = os.path.join("temp", f"{base_name}_Executive_Summary.md")
                with open(synthesis_path, 'w', encoding='utf-8') as sf:
                    sf.write(report_md)
            
            # Save results in session state
            st.session_state['synthesis_path'] = synthesis_path"""

new_synth = """            # Save results in session state
            st.session_state['synthesis_path'] = None"""

text = text.replace(old_synth, new_synth)

with open('first_pass/app.py', 'w', encoding='utf-8') as f:
    f.write(text)
