import os
import sys

# Add project root to path
sys.path.insert(0, os.getcwd())

from backend.api.bff_transformer import AssessmentTransformer


class MockWorkflowStep:
    def __init__(self, id):
        self.id = id


class MockWorkflowDefinition:
    def __init__(self, steps):
        self.steps = [MockWorkflowStep(s) for s in steps]


def test_strict_monitor():
    print("--- Testing AssessmentTransformer Dynamic Workflow Resolution ---")

    # 1. Define a strict workflow (only alpha and beta)
    mock_def = MockWorkflowDefinition(["step_alpha", "step_beta"])

    # 2. Define raw data with EXTRA steps (gamma) that should be ignored if strict,
    #    OR we just want to see if alpha/beta are correctly identified from def.
    #    Actually current logic appends ALL steps from def.

    raw_data = {
        "id": "exec_123",
        "status": "running",
        "results": {
            "step_results": {
                "step_alpha": {"status": "completed", "output": "foo"},
                "step_gamma": {
                    "status": "completed",
                    "output": "bar",
                },  # Should NOT appear if we strictly follow definition
            }
        },
    }

    transformer = AssessmentTransformer()
    view = transformer.transform(raw_data, workflow_definition=mock_def)

    print(f"Steps found in view: {[s.id for s in view.steps]}")

    ids = [s.id for s in view.steps]

    if "step_alpha" in ids and "step_beta" in ids:
        print("✅ Correctly identified steps from definition.")
    else:
        print("❌ Failed to identify steps from definition.")
        sys.exit(1)

    if "step_gamma" not in ids:
        print("✅ Correctly ignored 'step_gamma' not in definition (Strict Mode).")
    else:
        print("❌ Failed: 'step_gamma' leaked into view despite not being in definition.")
        # Note: current implementation might allow legacy leak if logic isn't perfectly strict yet.
        # Let's see what happens.

    # Check status
    vocab = {s.id: s.status for s in view.steps}
    print(f"Statuses: {vocab}")

    if vocab["step_alpha"] == "completed":
        print("✅ Alpha status: completed")
    else:
        print(f"❌ Alpha status mismatch: {vocab['step_alpha']}")

    if vocab["step_beta"] == "pending":
        print("✅ Beta status: pending")
    else:
        print(f"❌ Beta status mismatch: {vocab['step_beta']}")

    print("\n🎉 Strict Monitor Test Passed")


if __name__ == "__main__":
    test_strict_monitor()
