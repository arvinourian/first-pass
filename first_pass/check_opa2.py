import json
with open('temp/opa data - philadelphia_sfh_modeling_Validation_Executed.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source'])
        outputs = cell.get('outputs', [])
        for out in outputs:
            text = out.get('text', '')
            if isinstance(text, list): text = ''.join(text)
            if 'Error executing' in text:
                print(f"Cell {i} Caught Exception")
                print('--- Code ---')
                print(source)
                print('------------')
