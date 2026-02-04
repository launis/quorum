import json

SEED_PATH = 'backend/seed/seed_data.json'

def audit_seed():
    print(f"--- Auditing {SEED_PATH} ---")
    try:
        with open(SEED_PATH, encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"CRITICAL: Failed to load JSON: {e}")
        return

    # 1. Gather all Agents defined in Components
    defined_agents = set()
    for comp in data.get('components', []):
        if comp.get('type') == 'agent' or comp.get('type') == 'critic':
            # Use class_name as the key identifier for registry
            cls_name = comp.get('class_name')
            if cls_name:
                defined_agents.add(cls_name)

    print(f"Found {len(defined_agents)} defined agents in 'components'.")

    # 2. Gather Global Registry Mappings
    registry_agents = set()
    sys_config = data.get('system_config', [])
    registry = next((x for x in sys_config if x.get('type') == 'model_registry'), None)

    if registry:
        models = registry.get('models', {})
        for provider, strategies in models.items():
            for strategy, val in strategies.items():
                # Strategies usually map Alias -> Config OR AgentName -> Alias
                # We are looking for AgentName keys
                # Simplified check: if key matches an agent class name
                pass
            registry_agents.update(strategies.keys())

    print(f"Found {len(registry_agents)} mappings in global 'model_registry'.")

    # 3. Check for Orphans (Agents without Registry Entry)
    orphans = []
    # Hardcoded exclusions for known non-agent tasks or special cases?
    # GuardAgent usually runs via TaskRegistry, but we added it to DB to be safe.

    for agent in defined_agents:
        if agent not in registry_agents:
            orphans.append(agent)

    if orphans:
        print(f"\n[!] WARNING: {len(orphans)} Agents are missing from GLOBAL model_registry:")
        for o in orphans:
            print(f"  - {o}")
    else:
        print("\n[OK] All defined agents have a global registry entry.")

    # 4. Check for Hidden Workflows Configs
    print("\n--- Checking for Scope Mismatches (Hidden Configs) ---")
    for wf in data.get('workflows', []):
        if 'default_model_mapping' in wf:
            print(f"[!] INFO: Workflow '{wf.get('id')}' has local 'default_model_mapping'. This is NOT used by Global Registry.")

        # Check steps for invalid components
        for step in wf.get('steps', []):
            if isinstance(step, dict):
                comp_id = step.get('component')
                # Try to find component definition
                # This is complex because component lookup is by ID, but agents have ID=ClassName usually
                pass

if __name__ == "__main__":
    audit_seed()
