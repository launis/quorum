"""
Script to verify that all agents in a workflow persist their data correctly to the top-level state.
Simulates a chain or inspects the mocked database for the latest execution.
"""
import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from tinydb import TinyDB, Query
import json

async def verify_integrity():
    # DIRECT DB ACCESS (Bypass Backend Complexities)
    db_path = os.path.join(os.path.dirname(__file__), "..", "data", "db_mock.json") # or db.json
    
    if not os.path.exists(db_path):
         # Try live db
         db_path = os.path.join(os.path.dirname(__file__), "..", "data", "db.json")
    
    print(f"Reading DB: {db_path}")
    
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            executions = data.get("_default", {})
            # TinyDB stores as dict of dicts {"1": {...}, "2": {...}}
            executions_list = list(executions.values())
    except Exception:
        # Fallback if manual load fails
        db = TinyDB(db_path)
        executions_list = db.all()
    
    if not executions_list:
        print("No executions found.")
        return

    # Sort by timestamp (naive) or ID
    executions_list.sort(key=lambda x: x.get('start_time', ''), reverse=False)
    latest_exec = executions_list[-1]

    print(f"Inspecting Execution ID: {latest_exec.get('id')}")
    
    results = latest_exec.get("results", {})
    
    # Updated Checklist based on Audit
    # We expect these keys to be present in 'results' dictionary (which mirrors WorkflowState fields)
    full_checklist = [
        "step_guard",     # GuardAgent
        "step_analyst",   # AnalystAgent
        "step_profiler",  # ProfilerAgent
        "step_panel",     # PanelAgent (Composite)
        "step_logician",  # Copied from Panel
        "step_falsifier", # Copied from Panel
        "step_overseer",  # Copied from Panel
        "step_causal",    # Copied from Panel
        "step_detector",  # Copied from Panel
        "step_judge",     # JudgeAgent (CRITICAL - Fixed recently)
        "step_coach",     # CoachAgent
        "step_reporter"  # XAIReporterAgent
    ]
    
    missing = []
    present = []
    
    for key in full_checklist:
        val = results.get(key)
        if val:
            # Deep Check: Is it empty dict or actual data?
            if isinstance(val, dict) and not val:
                 print(f"[WARN] Key '{key}' exists but is EMPTY dict.")
                 missing.append(key)
            else:
                 present.append(key)
        else:
            missing.append(key)
            
    print("\n--- Integrity Report ---")
    print(f"Present Steps: {len(present)}/{len(full_checklist)}")
    for p in present:
        print(f" [x] {p}")
        
    print(f"\nMissing Steps: {len(missing)}/{len(full_checklist)}")
    for m in missing:
        print(f" [ ] {m}")
        
    # Source Leakage Check
    # Check if 'inputs' text appears in 'step_reporter' 
    inputs = latest_exec.get("inputs", {})
    history_text = inputs.get("history_text", "")
    
    report_step = results.get("step_reporter", {})
    if report_step:
        report_str = str(report_step)
        if len(history_text) > 50 and history_text[:50] in report_str:
             print("\n[WARNING] Source Leakage Detected: Input text found in Reporter output!")
        else:
             print("\n[OK] No Source Leakage detected in Reporter output.")

    # Top Level Hoisting Check
    hoisted_report = latest_exec.get("Report") or results.get("Report")
    if hoisted_report:
         print(f"[OK] Report Hoisting Active (Top Level Report Found).")
    else:
         print(f"[FAIL] Report Hoisting Missing (No 'Report' key at top level).")

if __name__ == "__main__":
    asyncio.run(verify_integrity())
