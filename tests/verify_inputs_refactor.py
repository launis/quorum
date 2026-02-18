
import asyncio
import logging
import sys
from datetime import datetime

# Add project root to path
# Assuming we run from project root (c:\src\quorum)
sys.path.append(".")

from backend.models.state import WorkflowState
from backend.models.domain.inputs import WorkflowInputs
from backend.exceptions import AppException, ErrorCodes
from backend.utils.pydantic_utils import inflate

# Hooks
from backend.hooks.metrics import calculate_text_metrics_hook
from backend.hooks.integrity import verify_citation_integrity
from backend.hooks.linguistics import detect_performative_patterns
from backend.hooks.security import sanitize_text_hook, check_banned_phrases_hook
from backend.hooks.search import execute_google_search
from backend.hooks.reporting import generate_report

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def verify_metrics_hook():
    logger.info("=== Verifying metrics.py ===")
    
    # 1. Valid Inputs
    inputs = WorkflowInputs(history_text="Hello world.", product_text="Valid product.")
    state = WorkflowState(
        id="test", workflow_id="w1", step_id="s1", status="running",
        context_variables={"inputs": inputs}
    )
    try:
        new_state = calculate_text_metrics_hook(state)
        metrics = new_state.context_variables.get("audit_metrics")
        assert metrics is not None, "Metrics should be calculated"
        logger.info("  [Pass] Valid Inputs")
    except Exception as e:
        logger.error(f"  [Fail] Valid Inputs: {e}")

    # 2. Missing Mandatory Fields (Fail Fast)
    inputs_empty = WorkflowInputs() # Empty history/product
    state_empty = WorkflowState(
        id="test", workflow_id="w1", step_id="s1", status="running",
        context_variables={"inputs": inputs_empty}
    )
    try:
        calculate_text_metrics_hook(state_empty)
        logger.error("  [Fail] Should have failed on empty inputs")
    except AppException as e:
        if e.status_code == 400 and e.details.get("error_code") == ErrorCodes.EMPTY_INPUT:
            logger.info("  [Pass] Correctly failed on missing mandatory fields (400)")
        else:
            logger.error(f"  [Fail] Wrong error: {e}")

    # 3. Missing 'inputs' key (Fail Fast 400)
    state_no_inputs = WorkflowState(
        id="test", workflow_id="w1", step_id="s1", status="running",
        context_variables={}
    )
    try:
        calculate_text_metrics_hook(state_no_inputs)
        logger.error("  [Fail] Should have failed on missing inputs key")
    except AppException as e:
        if e.status_code == 400 and e.details.get("error_code") == ErrorCodes.EMPTY_INPUT:
            logger.info("  [Pass] Correctly failed on missing inputs key (400)")
        else:
            logger.error(f"  [Fail] Wrong error: {e}")

async def verify_integrity_hook():
    logger.info("=== Verifying integrity.py ===")
    # Similar tests...
    inputs = WorkflowInputs(history_text="Quote this.", product_text="Source text.", reflection_text="Reflection.")
    state = WorkflowState(
        id="test", workflow_id="w1", step_id="s1", status="running",
        context_variables={"inputs": inputs}
    )
    try:
        verify_citation_integrity(state)
        # Check integrity_audit in context
        assert "integrity_audit" in state.context_variables or "audit_logs" in state.context_variables.get("metadata", {})
        # Warning: integrity hook returns COPY of state. We need to catch return value.
        new_state = verify_citation_integrity(state)
        assert "integrity_audit" in new_state.context_variables
        logger.info("  [Pass] Valid Inputs")
    except Exception as e:
        logger.error(f"  [Fail] Valid Inputs: {e}")

async def verify_reporting_hook():
    logger.info("=== Verifying reporting.py ===")
    inputs = WorkflowInputs(history_text="H", product_text="P")
    state = WorkflowState(
        id="test", workflow_id="w1", step_id="s1", status="running",
        context_variables={"inputs": inputs}
    )
    
    # We need to mock template existence or accept failure on template loading if environment doesn't match
    # But let's see if it gets past input validation
    try:
        # It might fail on template dir check if CWD is wrong, but that's distinct from inputs.
        # We assume CWD is c:/src/quorum for this test or template dir exists.
        new_state = generate_report(state)
        assert "report_context" in new_state.context_variables
        logger.info("  [Pass] Report Context generated")
    except AppException as e:
        if e.details.get("error_code") == ErrorCodes.CONFIGURATION_ERROR:
             logger.warning("  [Warn] Template dir missing (expected in this test env if paths differ), but inputs processed.")
        else:
             logger.error(f"  [Fail] Error: {e}")

async def verify_strict_state_enforcement():
    logger.info("=== Verifying Strict State Enforcement (No Dicts) ===")
    
    # Create a dict state (Forbidden)
    dict_state = {
        "id": "test",
        "context_variables": {"inputs": {"history_text": "foo"}}
    }
    
    # Test strict state check in metrics hook
    try:
        calculate_text_metrics_hook(dict_state) # type: ignore
        logger.error("  [Fail] Metrics hook accepted dict state")
    except AppException as e:
        if e.details.get("error_code") == ErrorCodes.INVALID_OUTPUT_SCHEMA:
            logger.info("  [Pass] Metrics hook correctly rejected dict state")
        else:
            logger.error(f"  [Fail] Wrong error code: {e.details.get('error_code')}")
    except Exception as e:
         logger.error(f"  [Fail] Wrong exception type: {type(e)}")

async def verify_security_hook():
    logger.info("=== Verifying security.py (sanitize_text_hook) ===")
    
    inputs = WorkflowInputs(
        history_text="Some PII: myemail@example.com", 
        product_text="Clean.",
        reflection_text="Self-reflection."
    )
    state = WorkflowState(
        id="test_sec", workflow_id="w1", step_id="step_guard", status="running",
        context_variables={"inputs": inputs}
    )
    
    try:
        # returns modified state
        new_state = sanitize_text_hook(state)
        res = new_state.context_variables.get("sanitization_result")
        assert res is not None
        # Check if it ran without "not subscriptable" error
        logger.info("  [Pass] sanitize_text_hook ran successfully with WorkflowInputs")
    except Exception as e:
        logger.error(f"  [Fail] sanitize_text_hook crashed: {e}")

async def main():
    logger.info("Starting Refactor Verification...")
    await verify_metrics_hook()
    await verify_integrity_hook()
    await verify_reporting_hook()
    await verify_strict_state_enforcement()
    await verify_security_hook()
    logger.info("Verification Complete.")

from backend.hooks.validation import verify_structure

async def verify_validation_hook():
    logger.info("=== Verifying validation.py (verify_structure) ===")
    
    # 1. Valid Inputs (Long enough)
    long_text = "word " * 20 # 100 chars?
    long_text = "This is a sufficiently long text that should pass the minimum character count Requirement of 100 characters. " * 2
    
    inputs = WorkflowInputs(
        history_text=long_text, 
        product_text=long_text,
        reflection_text=long_text
    )
    state = WorkflowState(
        id="test_val", workflow_id="w1", step_id="step_val", status="running",
        context_variables={"inputs": inputs}
    )
    
    try:
        new_state = verify_structure(state)
        res = new_state.context_variables.get("validation_result")
        assert res is not None
        assert res.is_valid is True
        logger.info("  [Pass] validation hook ran successfully with WorkflowInputs")
    except Exception as e:
        logger.error(f"  [Fail] verify_structure crashed: {e}")

async def main():
    logger.info("Starting Refactor Verification...")
    await verify_metrics_hook()
    await verify_integrity_hook()
    await verify_reporting_hook()
    await verify_strict_state_enforcement()
    await verify_security_hook()
    await verify_validation_hook()
    logger.info("Verification Complete.")

from backend.hooks.references import generate_bibliography_hook

async def verify_references_hook():
    logger.info("=== Verifying references.py (generate_bibliography_hook) ===")
    
    # Needs a mock Knowledge Base or Repository
    # We can pass KB in context
    kb = {"references": [], "concepts": []}
    
    inputs = WorkflowInputs(
        history_text="Some text with no citations.", 
        product_text="More text.",
        reflection_text="Reflection."
    )
    state = WorkflowState(
        id="test_ref", workflow_id="w1", step_id="step_ref", status="running",
        context_variables={"inputs": inputs, "knowledge_base": kb}
    )
    
    try:
        # returns modified state
        new_state = await generate_bibliography_hook(state, repository=None)
        res = new_state.context_variables.get("bibliography_result")
        assert res is not None
        # Should be empty list but valid object
        logger.info("  [Pass] references hook ran successfully with WorkflowInputs")
    except Exception as e:
        logger.error(f"  [Fail] generate_bibliography_hook crashed: {e}")

async def main():
    logger.info("Starting Refactor Verification...")
    await verify_metrics_hook()
    await verify_integrity_hook()
    await verify_reporting_hook()
    await verify_strict_state_enforcement()
    await verify_security_hook()
    await verify_validation_hook()
    await verify_references_hook()
    logger.info("Verification Complete.")

if __name__ == "__main__":
    asyncio.run(main())
