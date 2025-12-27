from pydantic import BaseModel
from typing import Optional, List, Any

class OllamaResponse(BaseModel):
    """
    Standard Ollama API response schema.
    Cognitive Role: Standardizes the output format from cognitive nodes (Cortex/Cerebellum)
    to ensure the Orchestrator can parse reasoning steps consistently.
    """
    model: str
    created_at: str
    response: str
    done: bool
    context: Optional[List[int]] = None
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    prompt_eval_duration: Optional[int] = None
    eval_count: Optional[int] = None
    eval_duration: Optional[int] = None
