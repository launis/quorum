import asyncio
import logging
import sys
import os
from unittest.mock import AsyncMock, MagicMock

# Ensure backend can be imported
sys.path.append(os.getcwd())

from backend.models.state import WorkflowState, InputData
from backend.hooks.security import check_banned_phrases_hook

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_repro():
    logger.info("--- Starting Repro: Lax Security ---")
    
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
        execution_id="test_exec_sec_001",
        inputs=inputs,
        aux_data={}
    )
    
    logger.info("Created mock state with banned phrase 'badword'.")
    
    try:
        # Run Hook
        updated_state = await check_banned_phrases_hook(state, repository=mock_repo)
        
        # Check results
        detected = updated_state.aux_data.get("banned_phrases_detected", [])
        threat_flag = updated_state.aux_data.get("security_threat", False)
        
        if "badword" in detected and threat_flag:
            logger.info("Hook correctly detected 'badword' and set threat flag.")
            logger.info("TEST RESULT: PASSED (Lax behavior confirmed - Detected but NO exception raised)")
        else:
            logger.error(f"TEST FAILED: Detection missing? detected={detected} flag={threat_flag}")
            
    except Exception as e:
        logger.error(f"TEST FAILED: Unexpected exception raised: {type(e)} - {e}")

if __name__ == "__main__":
    asyncio.run(run_repro())
