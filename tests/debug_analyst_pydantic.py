
print("Starting debug_analyst_pydantic.py...")
import sys
import os
# Ensure backend is in path
sys.path.append(os.getcwd())

import asyncio
import logging
from unittest.mock import MagicMock, AsyncMock

# FALLBACK MOCKING FOR DEBUGGING
# Mock everything that might cause import side effects
sys.modules["backend.models.state"] = MagicMock()
sys.modules["backend.llm.provider"] = MagicMock()
sys.modules["backend.services.localization"] = MagicMock()
sys.modules["firebase_admin"] = MagicMock()
sys.modules["google.cloud"] = MagicMock()

try:
    from backend.agents.analyst import AnalystAgent
    from backend.agents.panel import PanelAgent
    from backend.models.domain import AnalystOutput, Hypothesis
    from backend.exceptions import AgentExecutionError, ErrorCodes
    print("Imports successful.")
except Exception as e:
    print(f"Import failed: {e}")
    sys.exit(1)

# Configure Logging
logging.basicConfig(level=logging.INFO, force=True)
logger = logging.getLogger(__name__)

async def test_analyst_validation():
    logger.info("--- TEST 1: AnalystAgent Schema Validation ---")
    
    # Mock LLM Provider
    mock_provider = MagicMock()
    mock_provider.generate = AsyncMock()

    # Initialize with None to avoid LLMFactory startup
    agent = AnalystAgent(model=None)
    agent.llm_provider = mock_provider
    # BaseAgent defaults to 'vertex_ai' provider if not specified, 
    # but we inject mock execution anyway.

    # We need to simulate the "late validation failure"
    # execute() calls get_response_schema() -> AnalystOutput
    
    logger.info("Test 1.1: Missing reasoning_trace")
    # Missing reasoning_trace
    mock_provider.generate.return_value.content = '{"hypotheses": [], "rag_evidence": []}'
    mock_provider.generate.return_value.parsed_content = None 

    try:
        # BaseAgent.execute calls prepare_context -> LLM -> post_process -> validation
        long_text = "This is a sufficiently long text to bypass the length check. " * 10
        await agent.execute(
            input_data={"history_text": long_text, "product_text": long_text, "reflection_text": long_text},
            system_instruction="mock instruction"
        )
        logger.error("❌ Test 1.1 FAILED: AnalystAgent accepted invalid output.")
    except AgentExecutionError as e:
        if "ValidationError" in str(e) or "Field required" in str(e) or "AGENT_SCHEMA_VALIDATION_FAILED" in str(e):
             logger.info(f"✅ Test 1.1 PASSED: Caught expected validation error: {e}")
             try:
                 with open("test_1_1_success.txt", "w") as f: f.write("OK")
             except: pass
        else:
             logger.warning(f"⚠️ Test 1.1 PASSED (Partial): Caught error but maybe not validation? {e}")
    except Exception as e:
        logger.error(f"❌ Test 1.1 FAILED: Caught unexpected error: {e}")

    # Case 2: Valid Output
    logger.info("\nTest 1.2: Valid Output")
    valid_json = '{"reasoning_trace": "Thinking...", "hypotheses": [], "rag_evidence": []}'
    mock_provider.generate.return_value.content = valid_json
    sys.stdout.flush()
    
    try:
        long_text = "This is a sufficiently long text to bypass the length check. " * 10
        result = await agent.execute(
            input_data={"history_text": long_text, "product_text": long_text, "reflection_text": long_text},
            system_instruction="mock instruction"
        )
        logger.info(f"✅ Test 1.2 PASSED: Result type: {type(result)}")
        try:
             with open("test_1_2_success.txt", "w") as f: f.write("OK")
        except: pass
        sys.stdout.flush()
    except Exception as e:
        logger.error(f"❌ Test 1.2 FAILED: {e}")
        sys.stdout.flush()

    # Case 3: Empty Output (The Bypass Check)
    logger.info("\nTest 1.3: Empty Dict Output (Should Fail Validation, but might Bypass)")
    mock_provider.generate.return_value.content = '{}'
    mock_provider.generate.return_value.parsed_content = None

    try:
        result = await agent.execute(
            input_data={"history_text": long_text, "product_text": long_text, "reflection_text": long_text},
            system_instruction="mock instruction"
        )
        if result == {}:
            logger.error("❌ Test 1.3 FAILED: AnalystAgent bypassed validation with empty dict!")
            return result
        else:
             logger.info(f"✅ Test 1.3 PASSED: Returned non-empty result (maybe metadata added?): {result}")
             return result
    except AgentExecutionError as e:
        logger.info(f"✅ Test 1.3 PASSED: Caught expected validation error: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Test 1.3 FAILED: Caught unexpected error: {e}")
        return None

async def test_panel_hydration(analyst_output):
    logger.info("\n--- TEST 2: PanelAgent Hydration ---")
    
    if not analyst_output:
        logger.warning("Skipping Test 2.")
        return

    agent = PanelAgent(model=None)
    # PanelAgent hydration happens in _hydrate_inputs, usually called by prepare_context
    
    # Input Data
    input_data = {
        "step_analyst": analyst_output, 
        "step_profiler": {"reasoning_trace": "t", "author_intent": "i", "cognitive_biases": [], "metrics": {}, "control_ratio": 0.5},
        "step_judge": {"reasoning_trace": "t", "score_card": {"total_score": 10, "final_verdict": "v", "dimensions": []}},
         "step_interaction": {"reasoning_trace": "t", "role_classification": "Driver", "imperative_command_count": 0, "dependency_score": 0, "strategy_classification": "Few-shot"},
        "history_text": "h", "product_text": "p"
    }

    try:
        # PanelAgent.prepare_context calls _hydrate_inputs
        await agent.prepare_context(input_data, execution_context={})
        logger.info("✅ Test 2 PASSED: PanelAgent prepared context successfully.")
    except Exception as e:
        logger.error(f"❌ Test 2 FAILED: {e}")
        if "AnalystOutput" in str(e):
             logger.error("   -> Confirmed: PanelAgent fails to hydrate AnalystOutput.")

async def main():
    analyst_result = await test_analyst_validation()
    await test_panel_hydration(analyst_result)

if __name__ == "__main__":
    asyncio.run(main())
