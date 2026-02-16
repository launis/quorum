import logging

from backend.hooks.metrics import calculate_text_metrics_hook
from backend.models.state import WorkflowState

logging.basicConfig(level=logging.DEBUG)

def test_hook():
    print("Testing Hook...")

    # Mock State
    initial_context = {
        "inputs": {
            "history_text": "User: Hello.\nAI: Hi there.",
            "product_text": "Product stuff.",
            "reflection_text": "Reflection stuff."
        }
    }

    state = WorkflowState(
        execution_id="123", # UUID mock? Pydantic expects UUID.
        workflow_id="wf_1",
        status="running",
        execution_trace=[],
        context_variables=initial_context
    )

    # Run Hook
    new_state = calculate_text_metrics_hook(state)

    # Check Result
    metrics = new_state.context_variables.get("audit_metrics")
    if metrics:
        print("SUCCESS: Metrics found!")
        print(metrics)
    else:
        print("FAILURE: Metrics missing.")

if __name__ == "__main__":
    # UUID workaround
    import uuid

    from backend.models.state import WorkflowState

    # Pydantic validation needs valid UUID
    initial_context = {
        "inputs": {
            "history_text": "User: Hello.\nAI: Hi there.",
            "product_text": "Product stuff.",
            "reflection_text": "Reflection stuff."
        }
    }

    state = WorkflowState(
        execution_id=uuid.uuid4(),
        workflow_id="wf_1",
        status="running",
        execution_trace=[],
        context_variables=initial_context
    )

    new_state = calculate_text_metrics_hook(state)
    metrics = new_state.context_variables.get("audit_metrics")

    if metrics:
         print(f"SUCCESS: {metrics}")
    else:
         print("FAILURE")
