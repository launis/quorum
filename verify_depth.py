
import asyncio
import logging
import sys
import json
from datetime import datetime

# Set path to root
sys.path.append('.')

from backend.core.engine import WorkflowEngine
from backend.models.state import WorkflowState

# Configure logging to stdout
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TestEngine")

def calculate_depth(d, level=0):
    if not isinstance(d, dict) and not isinstance(d, list):
        return level
    
    max_depth = level
    if isinstance(d, dict):
        for k, v in d.items():
            max_depth = max(max_depth, calculate_depth(v, level + 1))
    elif isinstance(d, list):
        for item in d:
            max_depth = max(max_depth, calculate_depth(item, level)) # List itself doesn't add key depth, but item structure does
            
    return max_depth

async def run_test():
    engine = WorkflowEngine(db_path="backend/database/db_mock.json")
    workflow_id = "sequential_audit_chain"
    inputs = {"history_text": "Audit me."}
    
    logger.info("Starting execution...")
    try:
        execution_id = await engine.create_execution(workflow_id, inputs)
        result = await engine.run_execution(execution_id, inputs)
        
        # Analyze Depth excluding Raw_Steps
        curated_result = result.copy()
        if "Raw_Steps" in curated_result:
            del curated_result["Raw_Steps"]
            
        logger.info("Analyzing JSON Depth for 'Curated' sections...")
        depth = calculate_depth(curated_result)
        logger.info(f"Max JSON Depth: {depth}")
        
        # Print sections
        print(json.dumps(curated_result, indent=2, ensure_ascii=False))
        
        if depth > 4: # Allowing 4 for strict list item field access (Root->Domain->List->Object->Key)
             logger.warning(f"Depth {depth} might be improved, but check structure.")
        else:
             logger.info("Depth check PASSED.")

    except Exception as e:
        logger.exception("Error")

if __name__ == "__main__":
    asyncio.run(run_test())
