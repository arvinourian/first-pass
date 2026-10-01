with open('first_pass/batch_run.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix batch_run
old = """    executed_nb_path = builder.build_notebook(
        raw_profile=raw_profile,
        cleaning_plan=cleaning_plan,
        engineering_plan=engineering_plan,
        cleaned_profile=cleaned_profile,
        analysis_plan=analysis_plan,
        llm_usage=[],
        raw_cleaning_json=cleaning_plan.model_dump_json(indent=2),
        raw_analysis_json=analysis_plan.model_dump_json(indent=2),
        output_path=os.path.join("temp", f.replace('.csv', '_Validation_Executed.ipynb'))
    )"""

new = """    nb_path = os.path.join("temp", f.replace('.csv', '_Validation.ipynb'))
    executed_nb_path = os.path.join("temp", f.replace('.csv', '_Validation_Executed.ipynb'))
    
    builder.build_notebook(
        raw_profile=raw_profile,
        cleaning_plan=cleaning_plan,
        engineering_plan=engineering_plan,
        cleaned_profile=cleaned_profile,
        analysis_plan=analysis_plan,
        llm_usage=[],
        raw_cleaning_json=cleaning_plan.model_dump_json(indent=2),
        raw_analysis_json=analysis_plan.model_dump_json(indent=2),
        output_path=nb_path
    )
    
    # Execute the notebook!
    builder.execute_notebook(nb_path, executed_nb_path)"""

text = text.replace(old, new)
with open('first_pass/batch_run.py', 'w', encoding='utf-8') as f:
    f.write(text)

# Fix test_opa
with open('first_pass/test_opa.py', 'r', encoding='utf-8') as f:
    text2 = f.read()

text2 = text2.replace(old, new)
with open('first_pass/test_opa.py', 'w', encoding='utf-8') as f:
    f.write(text2)
