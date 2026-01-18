
import asyncio
import sys
import os
import json
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.path.abspath("c:/src/quorum"))

try:
    from backend.services.prompt_builder import PromptBuilder
    from backend.services.agent_registry import AgentRegistry
    from backend.database.repository import TinyDBRepository
    from backend.database.wrapper import TinyDBClient
    from backend.models.workflow import WorkflowDefinition
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

async def main():
    print("Initializing services for Patched Verification...")
    
    db_path = "c:/src/quorum/data/db.json"
    
    # 1. Initialize Real DB Client to read raw data
    try:
        db_client = TinyDBClient(db_path)
    except Exception as e:
        print(f"Failed to init DB client: {e}")
        return

    # 2. Extract Step Data Manually from Workflow 'sequential_audit_chain'
    # We know steps are embedded in workflows in this DB version
    workflows_table = db_client.table("workflows")
    # TinyDB stores as dict of { doc_id: content } if not using a specific query. 
    # Or db.all() returns list.
    all_workflows = workflows_table.all()
    
    target_workflow_id = "sequential_audit_chain"
    target_step_id = "step_guard"
    extracted_step = None
    
    print(f"Searching for workflow '{target_workflow_id}'...")
    found_wf = None
    for wf in all_workflows:
        if wf.get("id") == target_workflow_id:
            found_wf = wf
            break
            
    if not found_wf:
        # Fallback: try ID "1" if sequential_audit_chain is the ID field but doc ID is "1"
        # The view_file showed {"1": {"id": "sequential_audit_chain", ...}}
        # If TinyDB all() returns the values, we should have found it.
        print("Workflow not found by ID. Trying to inspect first workflow...")
        if all_workflows:
            first = all_workflows[0]
            print(f"First workflow ID: {first.get('id')}")
            found_wf = first # Let's just use the first one if it looks right
    
    if found_wf:
        print(f"Found workflow: {found_wf.get('name')}")
        steps = found_wf.get("steps", [])
        for s in steps:
            if s.get("id") == target_step_id:
                extracted_step = s
                print("Found 'step_guard' inside workflow steps.")
                break
    
    if not extracted_step:
        print("Error: Could not find 'step_guard' in workflow data. Cannot proceed.")
        return

    # 3. Setup MOCKED Repository that returns this step
    repo = MagicMock(spec=TinyDBRepository)
    
    async def mock_get_step_by_id(step_id):
        if step_id == target_step_id:
            return extracted_step
        return None
        
    repo.get_step_by_id.side_effect = mock_get_step_by_id
    
    # Needs get_component_by_id for PromptBuilder component resolution
    # We need a real lookup for components.
    # Let's use the REAL repository logic for components, but via a proxy or just copy the list.
    real_repo = TinyDBRepository(db_client)
    
    async def mock_get_component_by_id(comp_id):
        # Delegate to real DB for components
        return await real_repo.get_component_by_id(comp_id)

    async def mock_get_banned_phrases():
        return await real_repo.get_banned_phrases()
        
    repo.get_component_by_id.side_effect = mock_get_component_by_id
    repo.get_banned_phrases.side_effect = mock_get_banned_phrases

    # 4. Initialize Registry (Needs REAL Repository for components/models?)
    # Registry uses get_component_by_name / register_component / get_model_registry
    
    # FIX: Patch register_component which seems missing in TinyDBRepository
    async def mock_register_component(comp_data):
        # No-op for test
        pass
    real_repo.register_component = mock_register_component

    # We can pass the REAL repository to Registry, it doesn't use get_step_by_id.
    registry = AgentRegistry(real_repo)
    print("Discovering agents...")
    try:
        await registry.discover_and_register_agents()
    except Exception as e:
        print(f"Agent discovery warning: {e}")
        import traceback
        traceback.print_exc()

    # 5. Initialize PromptBuilder with Patched Repo
    builder = PromptBuilder(repo, registry)

    print(f"Constructing prompt for {target_step_id}...")
    try:
        # Debug: Check if components can be resolved
        print("Debugging Component Resolution:")
        config = extracted_step.get("execution_config", {})
        prompt_ids = config.get("llm_prompts", [])
        print(f"Prompt IDs to resolve: {prompt_ids}")
        for pid in prompt_ids:
            comp = await real_repo.get_component_by_id(pid)
            if comp:
                 print(f" [OK] Found {pid}")
            else:
                 print(f" [FAIL] Could not find {pid} in DB via real_repo.")

        prompt = await builder.construct_prompt(target_step_id)
        
        if not prompt:
            print("Error: Constructed prompt is empty.")
            return

        print("\n--- Prompt Verification ---")
        
        # Check for Language Instruction
        target_instruction = "KIELI: Kirjoita vastauksesi, analyysisi ja kaikki generoitava teksti AINA suomeksi"
        if target_instruction in prompt:
            print("[PASS] Strengthened Finnish Language Instruction FOUND.")
        else:
            print("[FAIL] Strengthened Finnish Language Instruction NOT found.")
            # Print nearby text if possible or just first 500 chars
            print(prompt[:500])

        # Check for English Schema (Reverted Domain)
        # Look for "True if a security threat was detected" (GuardAgent schema)
        target_english_desc = "True if a security threat was detected" 
        
        if target_english_desc in prompt:
             print("[PASS] English Schema Description FOUND (as expected).")
        else:
             print("[FAIL] English Schema Description NOT found.")
             # Dump partial prompt where schema should be
             if "uhka_havaittu" in prompt:
                print("(Partial) Schema structure found, but description missing or different.")
                idx = prompt.find("uhka_havaittu")
                print(prompt[idx:idx+300])
             else:
                print("(Fail) Schema block missing entirely.")

    except Exception as e:
        print(f"Error during verification: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
