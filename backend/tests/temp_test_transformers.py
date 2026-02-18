
from datetime import datetime, UTC
from uuid import uuid4
from backend.models.state import WorkflowState, TraceEvent
from backend.models.domain.execution import ExecutionRecord

def test_models_only():
    print("Testing Pydantic Models Instantiation...")
    try:
        # 1. TraceEvent
        print("1. Creating TraceEvent...")
        event = TraceEvent(
            step_name="step_judge",
            event_type="output",
            content={"total_score": 3.5},
            timestamp=datetime.now(UTC)
        )
        print("   TraceEvent OK")

        # 2. WorkflowState
        print("2. Creating WorkflowState...")
        state = WorkflowState(
            execution_id=uuid4(),
            workflow_id="wf-test",
            status="completed",
            execution_trace=[event]
        )
        print("   WorkflowState OK")

        # 3. ExecutionRecord
        print("3. Creating ExecutionRecord with Nested State...")
        record = ExecutionRecord(
            id=str(state.execution_id),
            status="completed",
            results=state, # Pydantic Object
            workflow_id="wf-test",
            created_at=datetime.now(UTC)
        )

        print("   ExecutionRecord OK")
        
        # 4. Transformer Logic
        from backend.api.transformers.report_core import ReportTransformer
        print("4. Instantiating Transformer...")
        transformer = ReportTransformer()
        print("   Transformer OK")
        
        print("5. Transforming WorkflowState directly...")
        view = transformer.transform(state)
        print(f"   Transform State Result ID: {view.view_id}")
        
        print("6. Transforming ExecutionRecord...")
        view_rec = transformer.transform(record)
        print(f"   Transform Record Result ID: {view_rec.view_id}")

    except Exception as e:
        print(f"TRANSFORM FAILURE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_models_only()

