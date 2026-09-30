import os
import time
from typing import Any, Dict, List
import json
from pydantic import BaseModel

# Try importing google.genai
try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

# Global token tracking
llm_usage_logs: List[Dict[str, Any]] = []

def get_client():
    if not genai:
        raise ImportError("google-genai is not installed")
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    return genai.Client(api_key=api_key)

def track_usage(stage: str, model: str, input_tokens: int, output_tokens: int, latency_ms: int):
    # Fallback dummy pricing if not in pricing.yaml
    cost_per_m_in = 0.50
    cost_per_m_out = 1.50
    cost = (input_tokens / 1_000_000 * cost_per_m_in) + (output_tokens / 1_000_000 * cost_per_m_out)
    
    log = {
        "stage": stage,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "latency_ms": latency_ms,
        "cost": round(cost, 6)
    }
    llm_usage_logs.append(log)
    return log

def count_tokens(text: str, model: str = "gemini-3.8-flash") -> int:
    client = get_client()
    for attempt in range(4):
        try:
            response = client.models.count_tokens(model=model, contents=text)
            return response.total_tokens
        except Exception as e:
            err_str = str(e)
            if "429" in err_str and attempt < 3:
                time.sleep(20)
            elif "503" in err_str and attempt < 3:
                time.sleep(2 ** attempt)
            else:
                raise

def generate_plan(stage: str, prompt: str, schema: Any, model: str = "gemini-3.8-flash") -> str:
    client = get_client()
    
    start_time = time.time()
    response = None
    for attempt in range(4):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=schema,
                    temperature=0.0
                ),
            )
            break
        except Exception as e:
            err_str = str(e)
            if "429" in err_str and attempt < 3:
                time.sleep(20)
            elif "503" in err_str and attempt < 3:
                time.sleep(2 ** attempt)
            else:
                raise

    latency = int((time.time() - start_time) * 1000)
    
    usage = response.usage_metadata
    in_tokens = usage.prompt_token_count if usage else 0
    out_tokens = usage.candidates_token_count if usage else 0
    
    track_usage(
        stage=stage,
        model=model,
        input_tokens=in_tokens,
        output_tokens=out_tokens,
        latency_ms=latency
    )
    
    return response.text

def get_embedding(text: str, model: str = "gemini-embedding-2-preview", stage: str = "embedding") -> List[float]:
    client = get_client()
    
    start_time = time.time()
    tokens = count_tokens(text, model="gemini-3.8-flash")
    
    response = None
    for attempt in range(4):
        try:
            response = client.models.embed_content(
                model=model,
                contents=text,
            )
            break
        except Exception as e:
            err_str = str(e)
            if "429" in err_str and attempt < 3:
                time.sleep(20)
            elif "503" in err_str and attempt < 3:
                time.sleep(2 ** attempt)
            else:
                raise
            
    latency = int((time.time() - start_time) * 1000)
    
    track_usage(
        stage=stage,
        model=model,
        input_tokens=tokens,
        output_tokens=0,
        latency_ms=latency
    )
    
    return response.embeddings[0].values
