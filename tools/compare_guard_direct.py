
import json
import subprocess

# Current config (manually transcribed)
CURRENT_PROMPTS = [
    "GLOBAL_CONTEXT",
    "HEADER_MANDATES",
    "MANDATE_1",
    "HEADER_RULES",
    "RULE_1",
    "RULE_2",
    "OP_RULE_2",
    "HEADER_PROTOCOLS",
    "PROTOCOL_2",
    "INSTRUCTION_ANON",
    "HEADER_INSTRUCTIONS",
    "TASK_GUARD"
]

def compare_direct():
    print("Fetching historical seed data directly from git (a6e8ac0)...")
    try:
        # Get content directly from git using subprocess to avoid shell encoding issues
        json_content = subprocess.check_output(
            ['git', 'show', 'a6e8ac0:backend/database/seed_data.json'], 
            encoding='utf-8' # Git output is usually utf-8
        )
        data = json.loads(json_content)
    except Exception as e:
        print(f"Error fetching/parsing git data: {e}")
        return

    # Find step_guard
    steps = data.get('steps', [])
    guard_step = next((s for s in steps if s['id'] == 'step_guard'), None)
    
    if not guard_step:
        print("❌ step_guard not found in historical version!")
        return

    hist_prompts = guard_step.get('execution_config', {}).get('llm_prompts', [])
    print(f"✅ Found historical step_guard. Prompt count: {len(hist_prompts)}")
    print(f"Historical Prompts: {hist_prompts}")
    
    # Compare
    current_set = set(CURRENT_PROMPTS)
    hist_set = set(hist_prompts)
    
    missing_in_current = hist_set - current_set
    extra_in_current = current_set - hist_set
    
    print("\n--- COMPARISON RESULTS ---")
    if missing_in_current:
        print(f"⚠️  MISSING in Current (Present in Historical): {list(missing_in_current)}")
    else:
        print("✅ Nothing missing from historical version.")
        
    if extra_in_current:
        print(f"🆕 EXTRA in Current (New additions): {list(extra_in_current)}")

if __name__ == "__main__":
    compare_direct()
