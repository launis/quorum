import json
import os
from datetime import datetime
from pathlib import Path

SEED_DATA_PATH = Path(r"c:\src\quorum\backend_v2\seed\seed_data.json")
BACKUP_DIR = Path(r"c:\src\quorum\backend_v2\seed\backups")
WORKFLOW_ID = "wf_9d68c573802341db"
XAI_REPORTER_NODE_ID = "sr_5f3dd7712a7f4bb3"
SCORING_ENGINE_NODE_ID = "sr_2fa56dc36614469a"

def apply_patch():
    # 1. Create a timestamped backup
    if not BACKUP_DIR.exists():
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"seed_data_epic11_patch_{timestamp}.json"
    
    print(f"Luetaan tiedostoa: {SEED_DATA_PATH}")
    with open(SEED_DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Luodaan varmuuskopio: {backup_path}")
    with open(backup_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # 2. Modify Task Blueprints (The Source of Truth for Models)
    # Etsitään kaikki Task Blueprintit, joita Workflow käyttää, ja päivitetään niiden `expected_inputs`
    # vastaamaan V2-arkkitehtuurin yksinkertaistettua `["inputs"]` mandaattia, 
    # MIKÄLI ne yrittävät käyttää V1 legacy ("document", "context") arvoja.
    modified_blueprints = set()
    
    workflow_found = False
    for workflow in data.get("workflows", []):
        if workflow.get("id") == WORKFLOW_ID:
            workflow_found = True
            print(f"Löydettiin workflow: {WORKFLOW_ID} ({workflow['name']['default_locale']})")
            
            for step in workflow.get("steps", []):
                node_id = step.get("id")
                bp_id = step.get("task_blueprint")
                
                # Vaihe 14: XAI Reporter
                if node_id == XAI_REPORTER_NODE_ID:
                    print(f"Päivitetään XAI Reporter ({node_id}) input_mappings -> {{'context': '$steps'}}")
                    step["input_mappings"] = {
                        "context": "$steps"
                    }
                
                # Vaihe 15: Scoring Engine (Tuomari/Judge)
                elif node_id == SCORING_ENGINE_NODE_ID:
                    print(f"Päivitetään Scoring Engine ({node_id}) input_mappings -> {{'results': '$steps.{XAI_REPORTER_NODE_ID}.outputs'}}")
                    step["input_mappings"] = {
                        "results": f"$steps.{XAI_REPORTER_NODE_ID}.outputs"
                    }
                    
                # Muut solmut: Niiden input_mappings pidetään alkuperäisenä ({"inputs": "$inputs"}).
                else:
                    if bp_id:
                        modified_blueprints.add(bp_id)
            break

    if not workflow_found:
        print(f"VIRHE: Workflowta ID:llä {WORKFLOW_ID} ei löytynyt.")
        return

    # Siivotaan V1-legacyn jäänteet Task Blueprinteista, jotta PromptCompiler generoi LLM:lle täsmälleen 
    # identtisen XML-kehyksen kuin ennenkin, mutta UI:n pudotusvalikot matchaavat 100%.
    for bp in data.get("steps", []):
        if bp.get("id") in modified_blueprints:
            expected = bp.get("expected_inputs", [])
            # Jos Blueprint odottaa legacy-syötteitä mutta solmu aikoo tuutata kaiken V2 $inputs -muodossa:
            if expected != ["inputs"] and bp.get("id") not in ["sp_192910b5f5a34c79", "sp_d245365e4a274b9e"]:
                print(f"Korjataan Blueprint {bp.get('id')} expected_inputs -> ['inputs'] (Oli: {expected})")
                bp["expected_inputs"] = ["inputs"]

    # 3. Save the modified seed data
    print(f"Tallennetaan korjattu tiedosto: {SEED_DATA_PATH}")
    with open(SEED_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        # Adding trailing newline for POSIX/Editor formatting
        f.write('\n')
        
    print("\nVALMIS! Mandaatin mukaiset input_mappings lisätty. Voit nyt ajaa seedaus-skriptin:")
    print("uv run python backend_v2\\seed\\run_seed.py local")

if __name__ == "__main__":
    apply_patch()
