with open('first_pass/first_pass/ingest.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("pd.read_csv(filepath, header=None, nrows=50, on_bad_lines='skip')", 
                    "pd.read_csv(filepath, header=None, nrows=50, on_bad_lines='skip', low_memory=False)")
text = text.replace("pd.read_csv(filepath, header=header_idx, on_bad_lines='skip')", 
                    "pd.read_csv(filepath, header=header_idx, on_bad_lines='skip', low_memory=False)")

with open('first_pass/first_pass/ingest.py', 'w', encoding='utf-8') as f:
    f.write(text)
