import os

old_block = """    print("  Synthesizing report...")
    report_md = synthesize_report(executed_nb_path, user_instructions)
    with open(executed_nb_path.replace('.ipynb', '_Summary.md'), 'w', encoding='utf-8') as sf:
        sf.write(report_md)
        
    print(f"  Finished {executed_nb_path}\\n")"""

new_block = """    print(f"  Finished {executed_nb_path}\\n")"""

for fpath in ['first_pass/test_opa.py', 'first_pass/test_opa_forced.py']:
    if os.path.exists(fpath):
        with open(fpath, 'r', encoding='utf-8') as f:
            text = f.read()
        text = text.replace("from first_pass.llm.synthesis import synthesize_report\n", "")
        text = text.replace(old_block, new_block)
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(text)
