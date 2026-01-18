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
    logger.info("--- Starting Repro: Strict Validation ---")
    
    # Create State with Short Inputs (< 100 chars)
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
        verify_structure(state)
        
        # If we get here, it FAILED to raise exception
        logger.error("TEST FAILED: Hook did NOT raise ValueError as expected.")
        sys.exit(1)
            
    except ValueError as e:
        logger.info(f"Caught expected ValueError: {e}")
        logger.info("TEST RESULT: PASSED (Strict validation confirmed - Exception raised)")
        sys.exit(0)
    except Exception as e:
        logger.error(f"TEST FAILED: Unexpected exception type: {type(e)} - {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_repro()
