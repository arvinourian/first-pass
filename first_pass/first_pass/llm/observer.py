import json
import base64
from typing import List, Dict, Any
from first_pass.llm.client import generate_plan
from first_pass.schemas import ObserverResponse

def generate_patches(cells: List[dict], user_text: str = "") -> ObserverResponse:
    sys_prompt = "You are an expert Data Science Observer. You are reviewing the executed cells of a Jupyter Notebook. Visually inspect the charts and review any code exceptions/errors."
    sys_prompt += "\nOutput a JSON list of patches. If a cell has a visually cluttered plot (e.g. legends blocking data, squished axis labels), output a patch with `cell_index` and the corrected `new_code`. If a cell threw an exception, output a patch fixing it. If everything is perfect, output an empty patches list."
    
    contents = [sys_prompt]
    if user_text:
        contents.append(f"User Instructions: {user_text}")
        
    for i, cell in enumerate(cells):
        if cell['cell_type'] != 'code': continue
        source = "".join(cell.get('source', []))
        outputs = cell.get('outputs', [])
        
        has_error = False
        has_image = False
        error_text = ""
        
        for out in outputs:
            if out.get('output_type') == 'error':
                has_error = True
                error_text += f"{out.get('ename')}: {out.get('evalue')}\n"
            elif out.get('output_type') == 'display_data' and 'image/png' in out.get('data', {}):
                has_image = True
                
        if not has_error and not has_image:
            continue
            
        contents.append(f"--- Cell {i} ---")
        contents.append(f"Code:\n```python\n{source}\n```")
        
        if has_error:
            contents.append(f"Exception:\n{error_text}")
            
        if has_image:
            from google.genai import types
            for out in outputs:
                if out.get('output_type') == 'display_data' and 'image/png' in out.get('data', {}):
                    img_b64 = out['data']['image/png'].strip()
                    contents.append(
                        types.Part.from_bytes(data=base64.b64decode(img_b64), mime_type="image/png")
                    )
                    
    try:
        response_text = generate_plan("observer", contents, ObserverResponse)
        plan = ObserverResponse.model_validate_json(response_text)
        return plan
    except Exception as e:
        print(f"Observer error: {e}")
        return ObserverResponse(patches=[])
