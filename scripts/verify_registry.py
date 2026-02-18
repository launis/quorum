import sys
import os
sys.path.append(os.getcwd())
import logging
from backend.core.registry import TaskRegistry
# Import tasks to trigger registration
from backend.tasks import critique, analysis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_registry():
    logger.info("Verifying Task Registry...")
    
    try:
        task_def = TaskRegistry.get("falsifier")
        if not task_def:
             logger.error("FAILURE: Task 'falsifier' not found in registry.")
             logger.info(f"Available keys: {list(TaskRegistry._tasks.keys())}")
             return

        agent_class_name = task_def.metadata.get("agent_class")
        logger.info(f"Task 'falsifier' maps to: {agent_class_name}")
        
        if agent_class_name == "LogicalFalsifierAgent":
            logger.info("SUCCESS: Registry is correct.")
        else:
            logger.error(f"FAILURE: Expected LogicalFalsifierAgent, got {agent_class_name}")

    except Exception as e:
        logger.error(f"FAILURE: Unexpected error: {e}")


if __name__ == "__main__":
    verify_registry()
