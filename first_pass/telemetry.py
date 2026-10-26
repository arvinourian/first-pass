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


def load_telemetry_events(filepath: str = TELEMETRY_FILE) -> list:
    """Loads all structured JSONL telemetry events from disk."""
    if not os.path.exists(filepath):
        return []
    events = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return events


def get_telemetry_summary(filepath: str = TELEMETRY_FILE) -> dict:
    """Computes production observability metrics from telemetry.jsonl."""
    events = load_telemetry_events(filepath)
    starts = [e for e in events if e.get("event_type") == "RUN_START"]
    successes = [e for e in events if e.get("event_type") == "RUN_SUCCESS"]
    errors = [e for e in events if e.get("event_type") == "RUN_ERROR"]
    downloads = [e for e in events if e.get("event_type") == "DOWNLOAD"]

    completed_runs = len(successes) + len(errors)
    success_rate = (len(successes) / completed_runs * 100.0) if completed_runs > 0 else 100.0

    durations = [float(e["duration"]) for e in successes if "duration" in e]
    costs = [float(e["cost"]) for e in successes if "cost" in e]

    # Estimate tokens from cost when historical logs recorded 0 before total_tokens fix
    # Blended rate ~$0.65 / 1M tokens (85% input @ $0.50/1M + 15% output @ $1.50/1M)
    tokens_list = []
    for e in successes:
        tok = int(e.get("tokens_used", 0) or 0)
        if tok == 0 and e.get("cost", 0) > 0:
            tok = int(round(float(e["cost"]) / 0.00000065))
        tokens_list.append(tok)

    downloaded_run_ids = {e.get("run_id") for e in downloads if e.get("run_id")}
    successful_run_ids = {e.get("run_id") for e in successes if e.get("run_id")}
    conversion_rate = (
        len(downloaded_run_ids & successful_run_ids) / len(successful_run_ids) * 100.0
        if successful_run_ids
        else 0.0
    )

    return {
        "total_events": len(events),
        "runs_started": len(starts),
        "runs_succeeded": len(successes),
        "runs_failed": len(errors),
        "run_success_rate_pct": round(success_rate, 2),
        "failure_rate_pct": round(100.0 - success_rate, 2),
        "mean_duration_sec": round(sum(durations) / len(durations), 2) if durations else 0.0,
        "min_duration_sec": round(min(durations), 2) if durations else 0.0,
        "max_duration_sec": round(max(durations), 2) if durations else 0.0,
        "mean_cost_usd": round(sum(costs) / len(costs), 6) if costs else 0.0,
        "min_cost_usd": round(min(costs), 6) if costs else 0.0,
        "max_cost_usd": round(max(costs), 6) if costs else 0.0,
        "mean_tokens_per_run": int(round(sum(tokens_list) / len(tokens_list))) if tokens_list else 0,
        "total_downloads": len(downloads),
        "download_conversion_rate_pct": round(conversion_rate, 2),
    }
