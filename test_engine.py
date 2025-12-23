
import asyncio
import logging
import sys
import json
from datetime import datetime

# Set path to root
sys.path.append('.')

from backend.core.engine import WorkflowEngine
from backend.models.state import WorkflowState
from backend.database.wrapper import get_db_client

# Configure logging to stdout
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TestEngine")

async def run_test():
    logger.info("Initializing WorkflowEngine...")
    # Pass a valid path string to satisfy the signature
    engine = WorkflowEngine(db_path="backend/database/db_mock.json")
    
    # Create an execution
    workflow_id = "sequential_audit_chain"
    inputs = {"history_text": "This is a test prompt for the AI to audit."}
    
    logger.info(f"Creating execution for workflow: {workflow_id}")
    try:
        execution_id = await engine.create_execution(workflow_id, inputs)
        logger.info(f"Execution ID created: {execution_id}")
        
        # Run execution
        logger.info("Starting execution...")
        result = await engine.run_execution(execution_id, inputs)
        
        logger.info("Execution finished.")
        
        # Check result
        if result:
            logger.info("Result returned by run_execution. Checking Raw_Steps...")
            
            # Specifically check Raw_Steps
            raw_steps = result.get("Raw_Steps", {})
            logger.info(f"Raw_Steps keys found: {list(raw_steps.keys())}")
            
            expected_steps = ["step_guard", "step_analyst", "step_profiler"]
            missing = [s for s in expected_steps if not raw_steps.get(s)]
            
            if not missing:
                logger.info("SUCCESS: All critical steps found in Raw_Steps!")
                # Optional: Print snippet of one step
                if raw_steps.get("step_guard"):
                    print("Guard Step Dump Snippet:", str(raw_steps["step_guard"])[:100])
            else:
                logger.error(f"FAILURE: Missing steps in Raw_Steps: {missing}")
                print("Full Raw_Steps keys:", raw_steps.keys())
        else:
            logger.error("Result is None!")
            
    except Exception as e:
        logger.exception("Exception during test execution:")

if __name__ == "__main__":
    asyncio.run(run_test())
