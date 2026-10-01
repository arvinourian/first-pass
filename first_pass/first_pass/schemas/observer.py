from typing import Any, List, Dict
from pydantic import BaseModel

class NotebookPatch(BaseModel):
    cell_index: int
    rationale: str
    new_code: str

class ObserverResponse(BaseModel):
    patches: List[NotebookPatch]
