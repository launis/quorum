
import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath("c:/src/quorum"))

try:
    from backend.services.prompt_builder import PromptBuilder
    from backend.services.agent_registry import AgentRegistry
    from backend.database.repository import TinyDBRepository
    from backend.database.wrapper import TinyDBClient
    from backend.settings import get_settings
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

async def main():
    print("Initializing services...")
    
    db_path = "c:/src/quorum/data/db.json"
    
    # 1. Initialize DB Client
    try:
        db_client = TinyDBClient(db_path)
    except Exception as e:
        print(f"Failed to init DB client: {e}")
        return

    # 2. Initialize Repository
    repo = TinyDBRepository(db_client)

    # 3. Initialize Registry
    # FIX: Pass repository to constructor
    registry = AgentRegistry(repo)
    
    # FIX: Load agents so schema examples can be generated
    print("Discovering and registering agents...")
    try:
        await registry.discover_and_register_agents()
    except Exception as e:
        print(f"Agent discovery failed (non-fatal for prompt text check, but fatal for schema example): {e}")
        # Proceeding might result in missing schema, but let's try.

    # 4. Initialize PromptBuilder
    builder = PromptBuilder(repo, registry)

    # Test step_guard matches "GuardAgent". 
    # Check if 'step_guard' exists in DB or if we need to mock it.
    # The PromptBuilder calls repo.get_step_by_id(step_id).
    # If step_guard is part of a workflow in db.json but not a standalone step record, get_step_by_id might fail 
    # if it only looks at 'steps' table.
    # In TinyDB, 'steps' table is separate. 
    # Let's check if 'step_guard' is in the 'steps' table.
    
    step_record = await repo.get_step_by_id("step_guard")
    if not step_record:
        print("Warning: 'step_guard' not found in 'steps' table via get_step_by_id.")
        print("Attempting to find it in 'workflows' table to manually patch for test...")
        # Hack: Create a fake step record if missing, using data from db.json known structure
        # We know step_guard has:
        # component: "GuardAgent"
        # execution_config: { llm_prompts: ["system_guard_main", "instruction_language_fi"] }
        
        # We can construct a mock step data for PromptBuilder logic test if real one misses.
        # But PromptBuilder.construct_prompt calls repo.get_step_by_id(step_id) internally.
        # So we can't easily mock it unless we insert it into DB or mock the repo.
        # Let's hope it exists or insert it temporarily?
        # Inserting into prod DB is risky.
        # Better: Mock the repository.get_step_by_id method?
        # Or Just trust it works if previous attempts didn't complain about "Step not found" (they crashed before).
        pass

    print("Constructing prompt for step_guard...")
    try:
        prompt = await builder.construct_prompt("step_guard")
        
        if not prompt:
            print("Error: Prompt is empty! (step_guard might not be found)")
            print("Trying fallback: 'step_analyst'...")
            prompt = await builder.construct_prompt("step_analyst")
            
        if not prompt:
             print("Error: Prompt is still empty. Cannot verify.")
             return

        print("\n--- Prompt Verification ---")
        
        # Check for Language Instruction
        target_instruction_snippet = "KIELI: Kirjoita vastauksesi, analyysisi ja kaikki generoitava teksti AINA suomeksi"
        
        if target_instruction_snippet in prompt:
            print("[PASS] Strengthened Finnish Language Instruction FOUND.")
        else:
            print("[FAIL] Strengthened Finnish Language Instruction NOT found.")
            print(f"Prompt length: {len(prompt)}")

        # Check for English Schema (Reverted Domain)
        target_english_desc = "True if a security threat was detected" 
        
        if target_english_desc in prompt:
             print("[PASS] English Schema Description FOUND (as expected/requested).")
        else:
             print("[FAIL] English Schema Description NOT found.")
             if "uhka_havaittu" in prompt:
                 print("(Partial) Schema fields present.")
             else:
                 print("(Fail) Schema block missing entirely.")

    except Exception as e:
        print(f"Error during verification: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
