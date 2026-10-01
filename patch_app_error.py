import os

with open('first_pass/app.py', 'r', encoding='utf-8') as f:
    text = f.read()

patch = """            try:
                idx = get_index()
            except Exception as e:
                st.error(f"**API Error during Initialization:**\\n{e}\\n\\nPlease check your Gemini API key billing and credits.")
                st.stop()"""

text = text.replace("            idx = get_index()", patch)

with open('first_pass/app.py', 'w', encoding='utf-8') as f:
    f.write(text)
