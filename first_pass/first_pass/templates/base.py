from pydantic import BaseModel
from typing import List, Any, Optional
from first_pass.schemas import DataProfile

class AnalysisTemplate:
    id: str = ""
    
    @classmethod
    def get_params_schema(cls) -> Any:
        return {}
        
    @classmethod
    def check_preconditions(cls, columns: List[str], params: dict, profile: DataProfile) -> Optional[str]:
        """Return an error string if preconditions fail, else None."""
        return None
        
    @classmethod
    def generate_code(cls, columns: List[str], params: dict) -> str:
        return ""
