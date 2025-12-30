import json
import os
import sys
import re

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED_DATA_PATH = os.path.join(BASE_DIR, "backend", "database", "seed_data.json")
MOCK_RESPONSES_PATH = os.path.join(BASE_DIR, "data", "mock_responses.json")
BACKEND_MOCK_LLM_PATH = os.path.join(BASE_DIR, "backend", "llm", "mock.py")

# Step Renaming Map
STEP_MAPPING = {
    "step_1": "step_guard",
    "step_2": "step_analyst",
    "step_profiler": "step_profiler", # No change
    "step_3": "step_logician",
    "step_4": "step_falsifier",
    "step_5": "step_overseer", # Was Step 5 in seed but logically Overseer
    "step_6": "step_causal",
    "step_7": "step_detector",
    "step_archivist": "step_archivist", # No change
    "step_8": "step_judge",
    "step_coach": "step_coach", # No change
    "step_9": "step_xai"
}

# New Components
HEADER_COMPONENT = {
    "id": "HEADER_TEXT",
    "type": "static_text",
    "name": "Raportin Otsikko",
    "content": "# Kognitiivinen Arviointiraportti (v2)\n\n**Järjestelmä:** Cognitive Quorum Assessment Engine\n**Versio:** 2.0 (Data-Driven)\n**Päiväys:** {{ date }}\n\n---"
}

DISCLAIMER_COMPONENT = {
    "id": "DISCLAIMER_TEXT",
    "type": "static_text",
    "name": "Vastuuvapauslauseke",
    "content": "> **Vastuuvapauslauseke:** Tämä raportti on generoitu tekoälyavusteisesti (AI-Assisted). Se perustuu syötettyyn aineistoon ja määriteltyihin kognitiivisiin sääntöihin."
}

def load_json(path):
    if not os.path.exists(path):
        print(f"Error: {path} not found.")
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Saved {path}")

def fix_seed_data():
    print("--- Fixing Seed Data ---")
    data = load_json(SEED_DATA_PATH)
    if not data: return False

    components = data.get("components", [])
    steps = data.get("steps", [])
    workflows = data.get("workflows", [])

    # 1. Add Components
    ids = {c["id"] for c in components}
    if HEADER_COMPONENT["id"] not in ids:
        components.insert(0, HEADER_COMPONENT)
    if DISCLAIMER_COMPONENT["id"] not in ids:
        components.insert(1, DISCLAIMER_COMPONENT)
    
    # 2. Fix Context Template (Inject Step ID)
    context_comp = next((c for c in components if c["id"] == "template_context_now"), None)
    if context_comp:
        # Check if we already injected STEP_ID
        if "STEP_ID:" not in context_comp["content"]:
            print("Injecting STEP_ID into template_context_now...")
            # Insert it right after TILANNEKUVA
            context_comp["content"] = context_comp["content"].replace(
                "### TILANNEKUVA (CONTEXT_NOW) ###\n", 
                "### TILANNEKUVA (CONTEXT_NOW) ###\nSTEP_ID: {{CURRENT_STEP_ID}}\n"
            )

    # 3. Rename Steps and Update contents
    id_map = STEP_MAPPING
    
    # Update Workflow references first
    for wf in workflows:
        new_step_list = []
        for step_id in wf.get("steps", []):
            new_step_list.append(id_map.get(step_id, step_id))
        wf["steps"] = new_step_list
        
        # Update default_model_mapping
        if "default_model_mapping" in wf:
            new_mapping = {}
            for k, v in wf["default_model_mapping"].items():
                new_mapping[id_map.get(k, k)] = v
            wf["default_model_mapping"] = new_mapping

    # Update Steps definitions
    for step in steps:
        old_id = step["id"]
        new_id = id_map.get(old_id, old_id)
        step["id"] = new_id
        
        # Ensure name is descriptive (optional, mostly they are good)
        
        prompts = step["execution_config"].get("llm_prompts", [])
        
        # 4. Ensure template_context_now is first
        if "template_context_now" not in prompts:
            prompts.insert(0, "template_context_now")
        elif prompts[0] != "template_context_now":
            prompts.remove("template_context_now")
            prompts.insert(0, "template_context_now")
            
        # 5. Add Headers to XAI (step_xai / step_9)
        if new_id == "step_xai":
            if "HEADER_TEXT" not in prompts:
                prompts.insert(0, "HEADER_TEXT") # Before context? No, usually Context first, but Header text is static content output? 
                # Actually, HEADER_TEXT is likely intended to be part of the PROMPT to tell LLM to include it, 
                # OR it's a static text output. 
                # seed_data says type: static_text.
                # If it's static_text, it shouldn't be in llm_prompts if the engine doesn't handle it.
                # But wait, fix_seed.py (Step 5) adds it to prompts.
                # Let's add it to prompts so it's available in context or output generation instructions.
                pass 
                
            # Re-insert cleanly
            prompts = [p for p in prompts if p not in ["HEADER_TEXT", "DISCLAIMER_TEXT"]]
            # Order: Context, Header (if needed as instruct), Instructions...
            # Actually, "HEADER_TEXT" content starts with "# Kognitiivinen...".
            # If we want the LLM to seeing it, it's fine.
            prompts.append("HEADER_TEXT") 
            prompts.append("DISCLAIMER_TEXT")
        
        step["execution_config"]["llm_prompts"] = prompts

    # --- Coach Config Update (New Field) ---
    coach_config = next((c for c in components if c["id"] == "COACH_OUTPUT_CONFIG"), None)
    if coach_config:
        if "lopputuloksen_kehitysehdotukset" not in coach_config["content"]:
            coach_config["content"].append("lopputuloksen_kehitysehdotukset")
            print("Updated COACH_OUTPUT_CONFIG.")

    # --- Coach Instruction Update ---
    coach_instr = next((c for c in components if c["id"] == "instruction_coach"), None)
    if coach_instr:
        if "lopputuloksen_kehitysehdotukset" not in coach_instr["content"]:
            coach_instr["content"] += "\n4. Anna konkreettisia parannusehdotuksia itse lopputuotteeseen (esim. tekstiin) ja kirjaa ne kenttään 'lopputuloksen_kehitysehdotukset'."
            print("Updated instruction_coach.")

    data["components"] = components
    data["steps"] = steps
    data["workflows"] = workflows
    
    save_json(SEED_DATA_PATH, data)
    return True

def fix_mock_responses():
    print("--- Fixing Mock Responses ---")
    data = load_json(MOCK_RESPONSES_PATH)
    if not data: return False
    
    key_map = {
        "guard_agent": "step_guard",
        "analyst_agent": "step_analyst",
        "logician_agent": "step_logician",
        "falsifier_agent": "step_falsifier",
        "fact_checker_agent": "step_overseer", 
        "causal_agent": "step_causal",
        "performativity_agent": "step_detector", 
        "judge_agent": "step_judge",
        "xai_agent": "step_xai",
        "profiler_agent": "step_profiler",
        "archivist_agent": "step_archivist",
        "coach_agent": "step_coach"
    }
    
    for old_key, new_key in key_map.items():
        if old_key in data:
            data[new_key] = data[old_key]
            if "metadata" in data[new_key]:
                data[new_key]["metadata"]["agentti"] = new_key
                
    # --- Update Coach Mock Data ---
    if "step_coach" in data:
        data["step_coach"]["lopputuloksen_kehitysehdotukset"] = [
            "Tiivistä johdantoa.", 
            "Lisää konkreettisia esimerkkejä kappaleeseen 2."
        ]
        # Ensure 'kehityskohteet_konkreettisesti' matches new schema (list of objects, not strings if it changed?)
        # Domain schema says: list[Kehitysehdotus]
        # Previous mock data might have been different or non-existent?
        # Let's ensure it has the correct structure
        data["step_coach"]["kehityskohteet_konkreettisesti"] = [
            {
                "kohde": "Argumentaatio",
                "ongelma": "Perusteet heikkoja",
                "ratkaisuehdotus": "Lisää lähteitä",
                "hyoty": "Uskottavuus paranee"
            }
        ]

    # --- Update Profiler Mock Data (Schema check) ---
    if "step_profiler" in data:
        # Schema: ProfilerAnalysis
        # intentio_analyysi, tunnetila_ja_savy, tunnistetut_vinoumat, psykologinen_profiili, manipulaatio_yritykset
        # Check if they exist, if not add defaults
        defaults = {
            "intentio_analyysi": "Vaikuttaminen.",
            "tunnetila_ja_savy": "Neutraali.",
            "tunnistetut_vinoumat": ["Ei havaittu."],
            "psykologinen_profiili": "Analyyttinen.",
            "manipulaatio_yritykset": "Ei havaittu."
        }
        for k, v in defaults.items():
            if k not in data["step_profiler"]:
                data["step_profiler"][k] = v

    # --- Update Archivist Mock Data (Schema check) ---
    if "step_archivist" in data:
        # Schema: CaseLawContext
        # linjakkuus_analyysi, poikkeamat_linjasta, suositus_tuomarille, viitatut_ennakkotapaukset
        defaults = {
            "linjakkuus_analyysi": "Linjassa.",
            "poikkeamat_linjasta": "Ei ole.",
            "suositus_tuomarille": "Hyväksy.",
            "viitatut_ennakkotapaukset": ["Case-001"]
        }
        for k, v in defaults.items():
            if k not in data["step_archivist"]:
                data["step_archivist"][k] = v
    
    save_json(MOCK_RESPONSES_PATH, data)
    return True

def fix_mock_llm_logic():
    print("--- Fixing Mock LLM Logic ---")
    if not os.path.exists(BACKEND_MOCK_LLM_PATH):
        print("Mock LLM path not found.")
        return
        
    with open(BACKEND_MOCK_LLM_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Inject logic to look for STEP_ID in prompt
    # We look for `def _identify_prompt_type(self, prompt: str, system_instruction: str) -> str:`
    
    marker = 'def _identify_prompt_type(self, prompt: str, system_instruction: str) -> str:'
    
    if "STEP_ID:" in content:
        print("Mock LLM logic already patched.")
        return

    # Patching
    # We want to insert a check at the TOP of _identify_prompt_type
    
    patch = """
        # 0. Check for explicit STEP_ID injected into prompt
        import re
        step_id_match = re.search(r"STEP_ID: (\w+)", prompt)
        if step_id_match:
            return step_id_match.group(1)
        
        # Also check system instruction just in case
        if system_instruction:
            step_id_match_sys = re.search(r"STEP_ID: (\w+)", system_instruction)
            if step_id_match_sys:
                return step_id_match_sys.group(1)
"""
    
    parts = content.split(marker)
    if len(parts) == 2:
        new_content = parts[0] + marker + patch + parts[1]
        with open(BACKEND_MOCK_LLM_PATH, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Patched mock.py with STEP_ID regex.")
    else:
        print("Could not find patch location in mock.py")

if __name__ == "__main__":
    if fix_seed_data() and fix_mock_responses():
        fix_mock_llm_logic()
        
        # Run Seed DB script
        print("--- Running seed_mock_db.py ---")
        import subprocess
        subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "seed_mock_db.py")])
        print("All Done.")
