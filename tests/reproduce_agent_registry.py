
import asyncio
import sys
import logging
from pathlib import Path

# Add backend to path
sys.path.append(str(Path.cwd()))

from backend.database.repository import UnifiedWorkflowRepository
from backend.services.agent_registry import AgentRegistry
from backend.database.tinydb_driver import TinyDBDriver
from backend.database.wrapper import TinyDBClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_registry():
    # Ensure we use the local DB we just seeded
    db_path = r"c:\src\quorum\data\db.json"
    
    print(f"Testing Registry against {db_path}...")
    
    client = TinyDBClient(db_path)
    driver = TinyDBDriver(client)
    repo = UnifiedWorkflowRepository(driver)
    registry = AgentRegistry(repo)
    
    # 1. Check if Registry is loaded
    try:
        reg_entry = await repo.get_model_registry()
        print(f"Model Registry Loaded: {bool(reg_entry)}")
        if reg_entry:
            models = reg_entry.get("models", {})
            print(f"Keys: {list(models.keys())}")
            
            # 2. Try to resolve specific agents
            agents_to_test = ["GuardAgent", "PanelAgent", "RetrievalAgent"]
            
            for agent in agents_to_test:
                try:
                    print(f"Resolving {agent}...")
                    config = await registry.resolve_model_config(agent)
                    print(f"✅ {agent}: {config.model_name} (Provider: {config.provider})")
                except Exception as e:
                    print(f"❌ {agent} Resolved (Errors expected if config incomplete): {e}")
                    
        else:
            print("❌ Registry is empty!")

    except Exception as e:
        print(f"Error accessing repo: {e}")

if __name__ == "__main__":
    asyncio.run(test_registry())
