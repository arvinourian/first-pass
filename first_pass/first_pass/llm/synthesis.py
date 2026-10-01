import json
from first_pass.llm.client import generate_plan
from pydantic import BaseModel

class NotebookSynthesis(BaseModel):
    markdown: str

def generate_key_takeaways(notebook_path: str, user_text: str = "") -> str:
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
        
    text_content = ""
    for cell in nb.get('cells', []):
        if cell['cell_type'] == 'markdown':
            text_content += "".join(cell['source']) + "\n\n"
        elif cell['cell_type'] == 'code':
            for out in cell.get('outputs', []):
                if out.get('output_type') == 'execute_result' and 'text/plain' in out.get('data', {}):
                    text_content += out['data']['text/plain'] + "\n"
                elif out.get('output_type') == 'stream':
                    text_content += out.get('text', '') + "\n"
                    
    # Truncate if too huge
    if len(text_content) > 100000:
        text_content = text_content[:100000]
        
    sys_prompt = "You are a Senior Data Consultant. Review this generated Exploratory Data Analysis notebook and write a concise, bulleted 'Key Takeaways' section summarizing the most critical business insights found in the data. Format it elegantly in Markdown."
    
    prompt = f"{sys_prompt}\n\nNotebook Extracts:\n{text_content}"
    
    try:
        response_text = generate_plan("pass5_synthesis", prompt, NotebookSynthesis)
        plan = NotebookSynthesis.model_validate_json(response_text)
        return "## Key Takeaways\n" + plan.markdown
    except Exception as e:
        print(f"Error generating synthesis: {e}")
        return "## Key Takeaways\n* Synthesis generation failed."
