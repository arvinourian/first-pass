with open('first_pass/app.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_cb = """        with col_t2:
            enable_engineering = st.checkbox("Enable Feature Engineering (Pass 2)", value=True, help="Mathematically transforms data before analysis.")
"""

new_cb = """        with col_t2:
            enable_engineering = st.checkbox("Enable Feature Engineering (Pass 2)", value=True, help="Mathematically transforms data before analysis.")
        with col_t3:
            enable_observer = st.checkbox("Enable Multimodal Observer (Pass 4)", value=True, help="Iteratively patches syntax errors and visual chart layouts using a multimodal vision model.")
"""

text = text.replace(old_cb, new_cb)

old_exec = "builder.execute_notebook(nb_path, executed_nb_path)"
new_exec = "builder.execute_notebook(nb_path, executed_nb_path, enable_observer=enable_observer)"

text = text.replace(old_exec, new_exec)

with open('first_pass/app.py', 'w', encoding='utf-8') as f:
    f.write(text)
