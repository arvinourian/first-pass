with open('first_pass/batch_run.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("from first_pass.llm.synthesis import synthesize_report\n", "")

old_block = """    print("  Synthesizing report...")
    report_md = synthesize_report(executed_nb_path, user_instructions)
    with open(executed_nb_path.replace('.ipynb', '_Summary.md'), 'w', encoding='utf-8') as sf:
        sf.write(report_md)
    
    print(f"  Finished {executed_nb_path}\\n")"""

new_block = """    print(f"  Finished {executed_nb_path}\\n")"""

text = text.replace(old_block, new_block)

with open('first_pass/batch_run.py', 'w', encoding='utf-8') as f:
    f.write(text)
