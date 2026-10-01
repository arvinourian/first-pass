import json
with open('temp/opa data - philadelphia_sfh_modeling_Validation_Executed.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source'])
        outputs = cell.get('outputs', [])
        for out in outputs:
            if out.get('output_type') == 'error':
                print(f"Cell {i} Error: {out.get('ename')}: {out.get('evalue')}")
                print('--- Code ---')
                print(source)
                print('------------')
