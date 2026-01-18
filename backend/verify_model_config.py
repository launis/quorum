import asyncio
import logging
import sys
import os

# Ensure backend can be imported
sys.path.append(os.getcwd())

from backend.database.repository import TinyDBRepository
from backend.services.agent_registry import AgentRegistry

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

async def verify():
    # Initialize Repository and Registry
    # Assuming running from c:/src/quorum
    db_path = "data/db.json"
    if not os.path.exists(db_path):
        logger.error(f"Database not found at {db_path}")
        return

    # Instantiate Client first (Wrapper)
    from backend.database.wrapper import TinyDBClient
    client = TinyDBClient(db_path)
    
    # Pass client to Repository
    repo = TinyDBRepository(client)
    registry = AgentRegistry(repo)
    
    # Define Expectations based on the implementation plan
    # Strict = 0.0, Precise = 0.2, Deep = 0.5, Fast = 0.7
    expectations = {
        "GuardAgent":           {"temp": 0.0, "profile": "vertex_ai/gemini-2.5-flash"}, # strict
        "RetrievalAgent":       {"temp": 0.0, "profile": "vertex_ai/gemini-2.5-flash"}, # strict
        "AnalystAgent":         {"temp": 0.2, "profile": "vertex_ai/gemini-2.5-pro"},   # precise
        "FactualOverseerAgent": {"temp": 0.2, "profile": "vertex_ai/gemini-2.5-pro"},   # precise
        "LogicianAgent":        {"temp": 0.2, "profile": "vertex_ai/gemini-2.5-pro"},   # precise
        "LogicalFalsifierAgent":{"temp": 0.2, "profile": "vertex_ai/gemini-2.5-pro"},   # precise
        "ArchivistAgent":       {"temp": 0.2, "profile": "vertex_ai/gemini-2.5-pro"},   # precise
        "CoachAgent":           {"temp": 0.5, "profile": "vertex_ai/gemini-2.5-pro"},   # deep (unchanged)
        "JudgeAgent":           {"temp": 0.5, "profile": "vertex_ai/gemini-2.5-pro"},   # deep (unchanged)
        "PanelAgent":           {"temp": 0.5, "profile": "vertex_ai/gemini-2.5-pro"},   # deep (unchanged)
    }

    logger.info("--- Starting Model Configuration Verification ---")
    
    success_count = 0
    failure_count = 0

    for agent_name, expected in expectations.items():
        try:
            # Resolve config using the registry logic
            config = await registry.resolve_model_config(agent_name)
            
            actual_temp = config.get("temperature")
            actual_model = config.get("model_name")
            
            # Validation
            start_msg = f"Checking {agent_name}: "
            errors = []
            
            if actual_temp != expected["temp"]:
                errors.append(f"Temp mismatch (Expected {expected['temp']}, Got {actual_temp})")
            
            if actual_model != expected["profile"]:
                errors.append(f"Model mismatch (Expected {expected['profile']}, Got {actual_model})")
                
            if errors:
                logger.error(f"{start_msg} FAILED | {', '.join(errors)}")
                failure_count += 1
            else:
                logger.info(f"{start_msg} PASS | Temp: {actual_temp} | Model: {actual_model}")
                success_count += 1

        except Exception as e:
            logger.error(f"Checking {agent_name}: CRITICAL ERROR | {e}")
            failure_count += 1

    logger.info("-" * 30)
    logger.info(f"Verification Complete. PASS: {success_count}, FAIL: {failure_count}")

    if failure_count > 0:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(verify())
