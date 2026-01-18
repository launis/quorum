import logging
import sys
import os

# Ensure backend can be imported
sys.path.append(os.getcwd())

from backend.models.state import WorkflowState, InputData
from backend.hooks.validation import verify_structure

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_repro():
    logger.info("--- Starting Repro: Lax Validation ---")
    
    # Create State with Short Inputs (< 100 chars)
    # This should trigger the warning in verify_structure
    inputs = InputData(
        history_text="Short history", 
        product_text="Short product", 
        reflection_text="Short reflection"
    )
    
    state = WorkflowState(
        execution_id="test_exec_001",
        inputs=inputs,
        aux_data={}
    )
    
    logger.info("Created mock state with short inputs.")
    
    try:
        # Run Hook
        updated_state = verify_structure(state)
        
        # Check if execution continued (it returned state)
        if updated_state:
            logger.info("Hook returned state successfully (Execution Continued).")
            
        # Check for warnings
        warnings = updated_state.aux_data.get("structural_warnings", [])
        if warnings:
            logger.info(f"Warnings found in aux_data: {warnings}")
            logger.info("TEST RESULT: PASSED (Lax validation confirmed - Warnings present but no crash)")
        else:
            logger.error("TEST FAILED: No warnings generated?")
            
    except Exception as e:
        logger.error(f"TEST FAILED: Unexpected crash occurred: {e}")

if __name__ == "__main__":
    run_repro()
