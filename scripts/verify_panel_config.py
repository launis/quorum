
import json
import sys
from pathlib import Path

def verify_panel_config():
    seed_path = Path("c:/src/quorum/backend/seed/seed_data.json")
    if not seed_path.exists():
        print(f"FAILED: {seed_path} not found")
        sys.exit(1)
        
    try:
        with open(seed_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        components = data.get("components", [])
        system_config = data.get("system_config", [])
        
        # 1. Verify Component Exists
        prompt_comp = next((c for c in components if c["id"] == "PANEL_PROMPT_TEMPLATE"), None)
        if not prompt_comp:
            print("FAILED: PANEL_PROMPT_TEMPLATE not found in components")
            sys.exit(1)
            
        print("SUCCESS: PANEL_PROMPT_TEMPLATE found in components")
        print(f"Content Preview: {prompt_comp.get('content')[:50]}...")
        
        # 2. Verify Agent Config Info
        panel_config = next((c for c in system_config if c["id"] == "PanelAgent"), None)
        if not panel_config:
            # It might be in 'agents' list if that exists, but usually system_config has agents
            # Let's check where PanelAgent is defined.
            # In the file view it was in system_config.
            print("FAILED: PanelAgent config not found in system_config")
            sys.exit(1)
            
        llm_prompts = panel_config.get("llm_prompts", [])
        if "PANEL_PROMPT_TEMPLATE" not in llm_prompts:
             print("FAILED: PANEL_PROMPT_TEMPLATE not referenced in PanelAgent config")
             sys.exit(1)
             
        print("SUCCESS: PanelAgent references PANEL_PROMPT_TEMPLATE")
        
    except Exception as e:
        print(f"FAILED: Exception {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_panel_config()
