import json
import os
import uuid
from datetime import datetime
import streamlit as st

TELEMETRY_FILE = "telemetry.jsonl"

def get_client_ip():
    try:
        # In newer streamlit versions, context is available
        if hasattr(st, 'context') and hasattr(st.context, 'headers'):
            headers = st.context.headers
            if "X-Forwarded-For" in headers:
                return headers["X-Forwarded-For"].split(',')[0].strip()
            elif "X-Real-IP" in headers:
                return headers["X-Real-IP"]
    except Exception:
        pass
    return "Unknown"

def _append_log(log_data: dict):
    # Ensure telemetry file exists
    if not os.path.exists(TELEMETRY_FILE):
        with open(TELEMETRY_FILE, 'w', encoding='utf-8') as f:
            pass # Create empty file
            
    with open(TELEMETRY_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_data) + "\n")

def log_event(event_type: str, run_id: str, **kwargs):
    """
    event_type: "RUN_START", "RUN_SUCCESS", "RUN_ERROR", "DOWNLOAD"
    """
    log_data = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "run_id": run_id,
        "ip_address": get_client_ip(),
    }
    log_data.update(kwargs)
    
    try:
        _append_log(log_data)
    except Exception as e:
        print(f"Failed to write telemetry: {e}")
