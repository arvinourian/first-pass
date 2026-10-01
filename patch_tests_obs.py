import os
for fpath in ['first_pass/batch_run.py', 'first_pass/test_opa.py', 'first_pass/test_opa_forced.py']:
    if os.path.exists(fpath):
        with open(fpath, 'r', encoding='utf-8') as f:
            text = f.read()
        text = text.replace("builder.execute_notebook(nb_path, executed_nb_path)", "builder.execute_notebook(nb_path, executed_nb_path, enable_observer=True)")
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(text)
