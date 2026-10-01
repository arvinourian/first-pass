with open('first_pass/first_pass/schemas.py', 'a', encoding='utf-8') as f:
    f.write("\nclass NotebookPatch(BaseModel):\n    cell_index: int\n    rationale: str\n    new_code: str\n")
    f.write("\nclass ObserverResponse(BaseModel):\n    patches: List[NotebookPatch]\n")
