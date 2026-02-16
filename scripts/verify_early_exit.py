import asyncio

from pydantic import BaseModel, ConfigDict, Field

from backend.core.engine import GraphEngine
from backend.core.registry import TaskRegistry
from backend.models.domain import GuardOutput, ReasoningTrace, SecurityCheck, TaintedDataContent
from backend.models.workflow import WorkflowDefinition, WorkflowStep


class MockInput(BaseModel):
    history_text: str | None = Field(default=None)
    model_config = ConfigDict(extra='allow')

# Mock Task Handler
async def mock_guard_handler(inputs: MockInput, execution_config: dict = None):
    history = inputs.history_text or ""
    print(f"\n[MockGuard] Executing... Input used: {history}")

    # Simulate a threat if history_text contains "THREAT"
    is_threat = "THREAT" in history

    return GuardOutput(
        reasoning_trace="Mock reasoning.",
        security_check=SecurityCheck(
            threat_detected=is_threat,
            risk_level="Critical" if is_threat else "Low",
            risk_score=3.0 if is_threat else 1.0,
            simulation_score=1.0,
            anonymized=False
        ),
        tainted_data=TaintedDataContent(
            chat_history="data",
            product_text="data",
            reflection_text="data",
            safe_data="DATA_CHECKED"
        )
    )

async def mock_next_step(inputs: dict):
    print("\n[MockNextStep] I SHOULD NOT RUN IF THREAT DETECTED!")
    return {"status": "I ran"}



# Register Mocks manually using the decorator
TaskRegistry.register_task(
    name="mock_guard",
    input_schema=MockInput,
    output_schema=GuardOutput
)(mock_guard_handler)

TaskRegistry.register_task(
    name="mock_next",
    input_schema=MockInput,
    output_schema=ReasoningTrace
)(mock_next_step)

async def main():
    engine = GraphEngine()

    # Define Workflow
    wf = WorkflowDefinition(
        id="test_early_exit",
        name="Test Early Exit",
        description="Testing conditional stop",
        steps=[
            WorkflowStep(
                id="step_1_guard",
                task_key="mock_guard",
                inputs={"history_text": "$inputs.history_text", "product_text": "foo", "reflection_text": "bar"}
            ),
            WorkflowStep(
                id="step_2_next",
                task_key="mock_next",
                inputs={}
            )
        ]
    )


    with open("verification.log", "w", encoding="utf-8") as f:
        f.write("--- TEST 1: NO THREAT ---\n")
        result_safe = await engine.execute_workflow(wf, {"inputs": {"history_text": "safe input"}})
        f.write(f"Status: {result_safe['status']}\n")
        trace_safe = [e['step_name'] for e in result_safe['execution_trace']]
        f.write(f"Executed steps: {trace_safe}\n")

        step_1 = next((e for e in result_safe['execution_trace'] if e['step_name'] == 'step_1_guard'), None)
        if step_1:
             f.write(f"Step 1 content: {step_1.get('content')}\n")

        if "step_2_next" not in trace_safe:
             f.write("FAIL: step_2_next missing in safe run!\n")

        f.write("\n--- TEST 2: THREAT DETECTED ---\n")
        result_threat = await engine.execute_workflow(wf, {"inputs": {"history_text": "THREAT detected"}})
        f.write(f"Status: {result_threat['status']}\n")
        trace_threat = [e['step_name'] for e in result_threat['execution_trace']]
        f.write(f"Executed steps: {trace_threat}\n")

        if result_threat['status'] == "stopped":
             f.write("PASS: Status is stopped.\n")
        else:
             f.write(f"FAIL: Status is {result_threat['status']}\n")

    print("Verification log written to verification.log")

if __name__ == "__main__":
    asyncio.run(main())
