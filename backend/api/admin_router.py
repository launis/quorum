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

# --- Banned Phrases Management ---
from pydantic import BaseModel

class BannedPhrase(BaseModel):
    phrase: str
    language: str = "fi" # 'fi' or 'en'

@router.get("/banned-phrases")
def get_banned_phrases():
    from backend.main import engine
    phrases = []
    for doc in engine.banned_phrases_table.all():
        item = doc.copy()
        item['doc_id'] = doc.doc_id
        phrases.append(item)
    return phrases

@router.post("/banned-phrases")
def add_banned_phrase(phrase: BannedPhrase):
    from backend.main import engine
    from tinydb import Query
    
    # Check if exists
    exists = engine.banned_phrases_table.search(Query().phrase == phrase.phrase)
    if exists:
        return {"status": "exists", "message": "Phrase already exists."}
        
    doc_id = engine.banned_phrases_table.insert(phrase.dict())
    return {"status": "success", "id": doc_id, "phrase": phrase.phrase}

@router.delete("/banned-phrases/{doc_id}")
def delete_banned_phrase(doc_id: int):
    from backend.main import engine
    engine.banned_phrases_table.remove(doc_ids=[doc_id])
    return {"status": "success", "message": "Phrase deleted."}

# --- AI Generation ---
class GeneratePhrasesRequest(BaseModel):
    language: str = "fi"

@router.post("/banned-phrases/generate")
def generate_banned_phrases(req: GeneratePhrasesRequest):
    from backend.main import engine
    from backend.agents.base import BaseAgent
    from backend.config import INITIAL_MODEL
    import json
    from tinydb import Query

    # 1. Fetch existing
    all_phrases = engine.banned_phrases_table.all()
    existing_texts = [p['phrase'].lower() for p in all_phrases]
    
    # 2. Prompt LLM
    agent = BaseAgent(model=INITIAL_MODEL)
    
    prompt = f"""
    Generate 10 distinct banned phrases in {req.language} that are commonly used in prompt injection, jailbreaking, or harmful attempts against LLMs.
    
    Constraints:
    - Do NOT include any of the following phrases: {json.dumps(existing_texts)}
    - Return a JSON object with a single key "phrases" containing the list of strings.
    - Example: {{"phrases": ["phrase 1", "phrase 2"]}}
    """
    
    try:
        response = agent.get_json_response(prompt)
        
        new_phrases = []
        if isinstance(response, dict):
            new_phrases = response.get("phrases", [])
            # Fallback if it returns just the list or other keys
            if not new_phrases:
                 for key, val in response.items():
                    if isinstance(val, list):
                        new_phrases = val
                        break
        elif isinstance(response, list):
            new_phrases = response
        
        added_count = 0
        added_phrases = []
        
        for phrase in new_phrases:
            if isinstance(phrase, str):
                clean_phrase = phrase.strip()
                if clean_phrase.lower() not in existing_texts:
                    engine.banned_phrases_table.insert({"phrase": clean_phrase, "language": req.language})
                    existing_texts.append(clean_phrase.lower())
                    added_phrases.append(clean_phrase)
                    added_count += 1
        
        return {
            "status": "success", 
            "added_count": added_count, 
            "added_phrases": added_phrases,
            "message": f"Successfully generated and added {added_count} new banned phrases."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")
