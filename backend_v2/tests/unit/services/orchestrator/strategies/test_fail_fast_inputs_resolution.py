from unittest.mock import AsyncMock
from backend_v2.services.orchestrator.strategies.llm_execution.context_builder import ContextBuilder


def test_context_builder_keyerror_reproduction():
    """Reproduces the KeyError when inputs are nested inside another 'inputs' dict due to StateProjector block_id logic."""
    input_mappings = {"product_text": "$inputs.product_text"}

    # This represents the correct state_data produced by llm.py line 88:
    # inputs_payload = {"product_text": "This is the product text"}
    # current_state["inputs"] = inputs_payload
    fixed_state_data = {
        "steps": [],
        "inputs": {"product_text": "This is the product text"},  # Correct flat structure
        "raw_inputs": {},
    }

    # This should now pass!
    llm_context_data, new_mappings = ContextBuilder.build(input_mappings=input_mappings, state_data=fixed_state_data)

    assert llm_context_data["inputs"]["product_text"] == "This is the product text"
