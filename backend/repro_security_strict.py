import asyncio
import logging
import sys
import os
from unittest.mock import AsyncMock

# Ensure backend can be imported
sys.path.append(os.getcwd())

from backend.models.state import WorkflowState, InputData
from backend.hooks.security import check_banned_phrases_hook
from backend.exceptions import SecurityViolationError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_repro():
    logger.info("--- Starting Repro: Strict Security ---")
    
    # Mock Repository
    mock_repo = AsyncMock()
    # Return a banned phrase
    mock_repo.get_banned_phrases.return_value = [{"phrase": "badword"}]
    
    # Create State with Banned Phrase
    inputs = InputData(
        history_text="Some normal text containing badword.", 
        product_text="Product info", 
        reflection_text="Reflection"
    )
    
    state = WorkflowState(
        execution_id="test_exec_sec_strict_001",
        inputs=inputs,
        aux_data={}
    )
    
    logger.info("Created mock state with banned phrase 'badword'.")
    
    try:
        # Run Hook
        await check_banned_phrases_hook(state, repository=mock_repo)
        
        # If we get here, it FAILED to raise exception
        logger.error("TEST FAILED: Hook did NOT raise SecurityViolationError as expected.")
        sys.exit(1)
            
    except SecurityViolationError as e:
        logger.info(f"Caught expected SecurityViolationError: {e}")
        logger.info("TEST RESULT: PASSED (Strict security confirmed - Exception raised)")
        sys.exit(0)
    except Exception as e:
        logger.error(f"TEST FAILED: Unexpected exception type: {type(e)} - {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_repro())
