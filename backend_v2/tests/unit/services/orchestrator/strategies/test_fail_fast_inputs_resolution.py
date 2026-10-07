from backend_v2.core.hook_registry import HookState
from backend_v2.models.dtos.hook_state import ExecutionInputsDTO
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.services.orchestrator.strategies.llm_execution.context_builder import ContextBuilder


def test_context_builder_keyerror_reproduction():
    """Reproduces the KeyError when inputs are nested inside another 'inputs' dict due to StateProjector block_id logic."""
    input_mappings = {"product_text": "$inputs.product_text"}

    fixed_state_data = HookState(
        execution_id="exc_123",
        workflow_id="wf_123",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(
            raw_inputs={"product_text": "This is the product text"},
        ),
    )

    # This should now pass!
    llm_context_data, new_mappings = ContextBuilder.build(input_mappings=input_mappings, state_data=fixed_state_data)

    assert llm_context_data["inputs"]["product_text"] == "This is the product text"

