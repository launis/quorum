import asyncio
import logging
import sys
import os

# Add project root
sys.path.append(os.getcwd())

from backend.database.wrapper import TinyDBClient
from backend.database.repository import TinyDBRepository
from backend.services.agent_registry import AgentRegistry
from backend.services.prompt_builder import PromptBuilder
from backend.core.registry import TaskRegistry

# Import the task definition to register the 'judge' key
import backend.tasks.judgment 

async def main():
    logging.basicConfig(level=logging.INFO)
    
    # 1. Setup Repo
    db = TinyDBClient("data/db.json")
    repo = TinyDBRepository(db)
    
    # 2. Setup Services
    registry = AgentRegistry(repo)
    builder = PromptBuilder(repo, registry)
    
    step_id = "step_judge"
    print(f"--- Testing Preview for {step_id} ---")
    
    try:
        # 3. Call Preview
        result = await builder.preview_step_prompt(step_id)
        
        print("\n[RESULT]")
        print(f"Agent Class: {result.get('agent_class')}")
        print(f"User Prompt: {result.get('user_prompt')[:100]}...") # Truncate for display
        
        if result.get("user_prompt") == "Template Logic Not Available":
            print("\n[FAIL] User Prompt is still the fallback message.")
        else:
            print("\n[SUCCESS] User Prompt resolved!")
            
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
