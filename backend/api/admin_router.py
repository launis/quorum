from fastapi import APIRouter, HTTPException, BackgroundTasks
import subprocess
import os
import sys
from backend.config import BASE_DIR
from backend.agents.base import BaseAgent

router = APIRouter(prefix="/admin", tags=["Admin"])

SCRIPTS_DIR = os.path.join(os.path.dirname(BASE_DIR), "scripts")

def run_script(script_name: str, args: list = []):
    """
    Helper to run a script from the scripts directory.
    """
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"Script not found: {script_path}")
    
    # Use the same python interpreter
    cmd = [sys.executable, script_path] + args
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result

@router.post("/docs/update")
def update_documentation(background_tasks: BackgroundTasks, ai_enhanced: bool = False):
    """
    Triggers the documentation update script.
    """
    def _run_update():
        args = ["--ai"] if ai_enhanced else []
        try:
            res = run_script("update_docs.py", args)
            print(f"Docs Update Output: {res.stdout}")
            if res.returncode != 0:
                print(f"Docs Update Error: {res.stderr}")
        except Exception as e:
            print(f"Docs Update Failed: {e}")

    background_tasks.add_task(_run_update)
    return {"status": "started", "message": "Documentation update started in background."}

@router.post("/import/rules")
def import_rules(background_tasks: BackgroundTasks):
    """
    Triggers the rules import script.
    """
    def _run_import():
        try:
            res = run_script("import_rules.py")
            print(f"Rules Import Output: {res.stdout}")
            if res.returncode != 0:
                print(f"Rules Import Error: {res.stderr}")
        except Exception as e:
            print(f"Rules Import Failed: {e}")

    background_tasks.add_task(_run_import)
    return {"status": "started", "message": "Rules import started in background."}

@router.post("/import/references")
def import_references(background_tasks: BackgroundTasks):
    """
    Triggers the references import script.
    """
    def _run_import():
        try:
            res = run_script("import_references.py")
            print(f"References Import Output: {res.stdout}")
            if res.returncode != 0:
                print(f"References Import Error: {res.stderr}")
        except Exception as e:
            print(f"References Import Failed: {e}")

    background_tasks.add_task(_run_import)
    return {"status": "started", "message": "References import started in background."}

@router.post("/export/seed-data")
def export_seed_data(background_tasks: BackgroundTasks):
    """
    Triggers the seed data export script (DB -> seed_data.json).
    """
    def _run_export():
        try:
            res = run_script("update_seed_data.py")
            print(f"Seed Data Export Output: {res.stdout}")
            if res.returncode != 0:
                print(f"Seed Data Export Error: {res.stderr}")
        except Exception as e:
            print(f"Seed Data Export Failed: {e}")

    background_tasks.add_task(_run_export)
    return {"status": "started", "message": "Seed data export started in background."}

@router.post("/self-test")
def run_self_test():
    """
    Runs a quick self-test of the LLM connection and Database.
    Returns a health report.
    """
    report = {
        "llm_status": "unknown",
        "db_status": "unknown",
        "details": {}
    }
    
    # 1. Test LLM
    try:
        agent = BaseAgent(model="gemini-1.5-flash")
        response = agent._call_llm("Hello, reply with 'OK' if you can hear me.")
        if response:
            report["llm_status"] = "ok"
            report["details"]["llm_response"] = response
        else:
            report["llm_status"] = "failed"
            report["details"]["llm_error"] = "Empty response"
    except Exception as e:
        report["llm_status"] = "error"
        report["details"]["llm_error"] = str(e)
        
    # 2. Test DB (Implicitly tested by API availability, but let's check write/read if needed)
    # For now, just checking if we can read components
    try:
        from backend.main import engine
        count = len(engine.components_table.all())
        report["db_status"] = "ok"
        report["details"]["component_count"] = count
    except Exception as e:
        report["db_status"] = "error"
        report["details"]["db_error"] = str(e)
        
    return report
