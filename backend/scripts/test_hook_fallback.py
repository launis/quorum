import logging
import uuid

from backend.hooks.metrics import calculate_text_metrics_hook
from backend.models.state import WorkflowState

logging.basicConfig(level=logging.DEBUG)


def test_fallback():
    print("Testing Hook Fallback...")

    # Scene 1: Flattened Context (simulating what might be in DB)
    flat_context = {"history_text": "User: Hello.", "product_text": "Product.", "reflection_text": "Reflect."}

    state1 = WorkflowState(
        execution_id=uuid.uuid4(),
        workflow_id="wf_flat",
        status="running",
        execution_trace=[],
        context_variables=flat_context,
    )

    new_state1 = calculate_text_metrics_hook(state1)
    metrics1 = new_state1.context_variables.get("audit_metrics")
    if metrics1 and metrics1["word_count"] > 0:
        print("SUCCESS: Flat context worked!")
        print(metrics1)
    else:
        print("FAILURE: Flat context failed.")

    # Scene 2: Missing Inputs (empty)
    empty_context = {"some_other_key": "value"}

    state2 = WorkflowState(
        execution_id=uuid.uuid4(),
        workflow_id="wf_empty",
        status="running",
        execution_trace=[],
        context_variables=empty_context,
    )

    new_state2 = calculate_text_metrics_hook(state2)
    metrics2 = new_state2.context_variables.get("audit_metrics")
    if metrics2:
        print("SUCCESS: Empty context produced default metrics!")
        print(metrics2)
    else:
        print("FAILURE: Empty context result missing.")


if __name__ == "__main__":
    test_fallback()
