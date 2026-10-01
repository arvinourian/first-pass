import json
with open('temp/opa data - philadelphia_sfh_modeling_Validation_Executed.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)
for i, cell in enumerate(nb['cells'][:6]):
    if cell['cell_type'] == 'code':
        print(f"Cell {i}:\n{''.join(cell['source'])}\n")
