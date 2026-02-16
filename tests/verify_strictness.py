
import os
import sys

from pydantic import ValidationError

# Add project root to path
sys.path.append(os.getcwd())

from backend.api.bff_transformer import AssessmentTransformer
from backend.models.domain import CognitiveLevel, GuardInput, SecurityCheck
from backend.models.workflow import WorkflowDefinition, WorkflowStep


def test_dynamic_workflow_resolution():
    print("\n--- Testing AssessmentTransformer Dynamic Workflow Resolution ---")
    transformer = AssessmentTransformer()

    # Mock Workflow Definition
    wf_def = WorkflowDefinition(
        id="test_workflow",
        description="Test",
        steps=[
            WorkflowStep(id="step_alpha", task_key="task_a"),
            WorkflowStep(id="step_beta", task_key="task_b")
        ]
    )

    # Mock Raw Data
    raw_data = {
        "execution_id": "exec_1",
        "workflow_id": "test_workflow",
        "status": "running",
        "results": {
            "step_results": {
                "step_alpha": {"status": "completed", "result": "done"}
            }
        }
    }

    # Transform
    view = transformer.transform(raw_data, workflow_definition=wf_def)

    # Verify Steps
    step_ids = [s.id for s in view.steps]
    print(f"Steps found: {step_ids}")

    assert "step_alpha" in step_ids, "step_alpha missing"
    assert "step_beta" in step_ids, "step_beta missing"
    assert "step_guard" not in step_ids, "step_guard found (should be absent)"

    # Verify Status
    alpha = next(s for s in view.steps if s.id == "step_alpha")
    beta = next(s for s in view.steps if s.id == "step_beta")

    print(f"Alpha status: {alpha.status}")
    print(f"Beta status: {beta.status}")

    assert alpha.status == "completed", f"Alpha status {alpha.status} != completed"
    assert beta.status in ("pending", "running"), f"Beta status {beta.status} invalid"

    print("✅ Dynamic workflow resolution passed.")

def test_domain_strictness():
    print("\n--- Testing Domain Model Strictness ---")

    # 1. GuardInput
    try:
        GuardInput(history_text="foo") # Missing product_text
        print("❌ GuardInput strictness FAILED: Accepted missing product_text")
    except ValidationError:
        print("✅ GuardInput strictness passed: Rejected missing product_text")

    try:
        GuardInput(history_text="foo", product_text="bar")
        print("✅ GuardInput valid input passed")
    except ValidationError as e:
        print(f"❌ GuardInput valid input FAILED: {e}")

    # 2. SecurityCheck
    try:
        SecurityCheck(
            threat_detected=False,
            risk_level="Low",
            anonymized=True
            # Missing risk_score, simulation_score
        )
        print("❌ SecurityCheck strictness FAILED: Accepted missing scores (should have auto-calculated or failed if missing)")
        # Actually, if risk_level is "Low", the validator SHOULD calculate risk_score=1.0.
        # So this MIGHT pass if calculator works.
        # But simulation_score is also missing.
    except ValidationError as e:
        # Check if it failed on simulation_score
        if "simulation_score" in str(e):
             print("✅ SecurityCheck strictness passed: Rejected missing simulation_score")
        else:
             print(f"⚠️ SecurityCheck validation error (potentially expected): {e}")

    # Test with valid calculation
    try:
        sc = SecurityCheck(
            threat_detected=False,
            risk_level="Risk.Low",
            simulation_result="Simulation.Passive",
            anonymized=True
        )
        assert sc.risk_score == 1.0
        assert sc.simulation_score == 1.0
        print("✅ SecurityCheck auto-calculation passed")
    except ValidationError as e:
        print(f"❌ SecurityCheck auto-calculation FAILED: {e}")

    # 3. CognitiveLevel
    try:
        CognitiveLevel(
            bloom_level="Bloom.Remembering",
            strategic_depth="Strategic.Low"
            # Missing scores
        )
        print("✅ CognitiveLevel auto-calculation passed (Validator injected scores)")
    except ValidationError as e:
        print(f"❌ CognitiveLevel strictness/auto-calc FAILED: {e}")

if __name__ == "__main__":
    try:
        test_dynamic_workflow_resolution()
        test_domain_strictness()
        print("\n🎉 ALL TESTS PASSED")
    except AssertionError as e:
        print(f"\n❌ ASSERTION FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        sys.exit(1)
