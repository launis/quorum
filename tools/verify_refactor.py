from backend.models.state import InputData, WorkflowState
from backend.services.state_presenter import StatePresenter


def verify():
    print("Initializing WorkflowState...")
    state = WorkflowState(
        execution_id="test-refactor", inputs=InputData(history_text="hist", product_text="prod", reflection_text="refl")
    )
    print(f"State initialized. Version: {state.version}")
    assert state.version == 1

    print("Flattening state...")
    flat = StatePresenter.flatten_state(state)
    print("Flattened successfully.")

    # Check key fields
    assert flat["System_Status"]["execution_id"] == "test-refactor"
    assert flat["System_Status"]["version"] == "2.0"
    assert "Report" in flat
    assert "Raw_Steps" in flat

    print("SUCCESS: Refactoring verified.")


if __name__ == "__main__":
    verify()
