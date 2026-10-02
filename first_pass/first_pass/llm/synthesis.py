import json
from first_pass.llm.client import generate_plan
from pydantic import BaseModel, Field
from typing import List

class NotebookSynthesis(BaseModel):
    markdown: str

class CellInterpretation(BaseModel):
    cell_index: int
    markdown: str = Field(description="A 2-3 sentence deeply analytical interpretation of the chart or output.")

class NotebookInterpretations(BaseModel):
    interpretations: List[CellInterpretation]

def generate_key_takeaways(notebook_path: str, user_text: str = "") -> str:
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
        
    text_content = ""
    for cell in nb.get('cells', []):
        if cell['cell_type'] == 'markdown':
            text_content += "".join(cell['source']) + "\\n\\n"
        elif cell['cell_type'] == 'code':
            for out in cell.get('outputs', []):
                if out.get('output_type') == 'execute_result' and 'text/plain' in out.get('data', {}):
                    p = out['data']['text/plain']
                    if isinstance(p, list): p = ''.join(p)
                    text_content += p + "\\n"
                elif out.get('output_type') == 'stream':
                    t = out.get('text', '')
                    if isinstance(t, list): t = ''.join(t)
                    text_content += t + "\\n"
                    
    if len(text_content) > 100000:
        text_content = text_content[:100000]
        
    sys_prompt = "You are a Senior Data Consultant. Review this generated Exploratory Data Analysis notebook and write a concise, bulleted 'Key Takeaways' section summarizing the most critical business insights found in the data. Format it elegantly in Markdown. DO NOT INCLUDE A TITLE OR HEADER (e.g. do not write '## Key Takeaways'), just provide the bullet points directly."
    
    prompt = f"{sys_prompt}\\n\\nNotebook Extracts:\\n{text_content}"
    
    try:
        response_text = generate_plan("pass5_synthesis", prompt, NotebookSynthesis)
        plan = NotebookSynthesis.model_validate_json(response_text)
        md = plan.markdown.strip()
        lines = md.split('\n')
        while lines and lines[0].strip().startswith('#'):
            lines.pop(0)
        md = '\n'.join(lines).strip()
        return "## Key Takeaways\\n\\n" + md
    except Exception as e:
        print(f"Error generating synthesis: {e}")
        return "## Key Takeaways\\n* Synthesis generation failed."

def generate_interpretations(notebook_path: str, user_text: str = "") -> List[CellInterpretation]:
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
        
    # Build a multimodal payload of code and outputs to interpret
    contents = ["You are a Senior Data Consultant. I am providing you with the executed cells of a Jupyter Notebook. Read the code, look at the charts, and write a 2-3 sentence markdown interpretation for each code cell that produces a meaningful output (chart or table). Focus heavily on the INTENTION and BUSINESS IMPACT of the plot. Return a JSON list mapping cell_index to your interpretation."]
    
    for i, cell in enumerate(nb.get('cells', [])):
        if cell['cell_type'] != 'code': continue
        
        has_output = False
        cell_contents = [f"--- Cell {i} ---", f"Code:\\n```python\\n{''.join(cell['source'])}\\n```"]
        
        for out in cell.get('outputs', []):
            if out.get('output_type') == 'execute_result' and 'text/plain' in out.get('data', {}):
                has_output = True
                p = out['data']['text/plain']
                if isinstance(p, list): p = ''.join(p)
                cell_contents.append(f"Output:\\n{p}")
            elif out.get('output_type') == 'stream':
                has_output = True
                t = out.get('text', '')
                if isinstance(t, list): t = ''.join(t)
                cell_contents.append(f"Output:\\n{t}")
            elif out.get('output_type') == 'display_data' and 'image/png' in out.get('data', {}):
                has_output = True
                import base64
                from google.genai import types
                img_b64 = out['data']['image/png'].strip()
                cell_contents.append(types.Part.from_bytes(data=base64.b64decode(img_b64), mime_type="image/png"))
                
        if has_output:
            contents.extend(cell_contents)
            
    try:
        response_text = generate_plan("pass5_interpretations", contents, NotebookInterpretations)
        plan = NotebookInterpretations.model_validate_json(response_text)
        return plan.interpretations
    except Exception as e:
        print(f"Error generating interpretations: {e}")
        return []
