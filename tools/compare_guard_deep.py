
import json
import subprocess
import difflib

# Current config IDs
GUARD_COMPONENT_IDS = [
    "GLOBAL_CONTEXT",
    "HEADER_MANDATES",
    "MANDATE_1",
    "HEADER_RULES",
    "RULE_1",
    "RULE_2",
    "OP_RULE_2",
    "HEADER_PROTOCOLS",
    "PROTOCOL_2", # Validointi
    "INSTRUCTION_ANON",
    "HEADER_INSTRUCTIONS",
    "TASK_GUARD"
]

CURRENT_SEED_FILE = "backend/database/seed_data.json"

def get_component_map(data):
    # Flatten components from 'system_config', 'steps' etc if needed, 
    # but mostly they are in 'system_config' or 'components' list.
    comp_map = {}
    
    # Check 'components' list
    for c in data.get('components', []):
        if 'id' in c: comp_map[c['id']] = c.get('content', '')
        
    # Check 'system_config' list (legacy or mixed)
    for c in data.get('system_config', []):
        if 'id' in c: comp_map[c['id']] = c.get('content', '')
        
    return comp_map

def compare_deep():
    print("Loading CURRENT seed data...")
    with open(CURRENT_SEED_FILE, 'r', encoding='utf-8') as f:
        current_data = json.load(f)
    current_map = get_component_map(current_data)

    print("Fetching HISTORICAL seed data (a6e8ac0)...")
    try:
        json_content = subprocess.check_output(
            ['git', 'show', 'a6e8ac0:backend/database/seed_data.json'], 
            encoding='utf-8'
        )
        hist_data = json.loads(json_content)
    except Exception as e:
        print(f"Error fetching git data: {e}")
        return
    hist_map = get_component_map(hist_data)
    
    print("\n--- DEEP CONTENT COMPARISON ---")
    
    for cid in GUARD_COMPONENT_IDS:
        curr_txt = current_map.get(cid, "MISSING_IN_CURRENT")
        hist_txt = hist_map.get(cid, "MISSING_IN_HISTORICAL")
        
        if curr_txt != hist_txt:
            print(f"\n⚠️  DIFFERENCE FOUND IN: {cid}")
            if len(str(curr_txt)) > 200 or len(str(hist_txt)) > 200:
                print("  (Content too long to show full diff, showing summary)")
                print(f"  Current Length: {len(str(curr_txt))}")
                print(f"  History Length: {len(str(hist_txt))}")
            else:
                print(f"  Current: {curr_txt}")
                print(f"  History: {hist_txt}")
        else:
            print(f"✅ {cid}: Identical")

if __name__ == "__main__":
    compare_deep()
