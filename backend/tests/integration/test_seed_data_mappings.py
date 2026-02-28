import json
import os
import pytest
from backend.core.registry import TaskRegistry

# Import all agent modules so they register themselves
import backend.agents.analyst
import backend.agents.critics
import backend.agents.guard
import backend.agents.logician
import backend.agents.retrieval
import backend.agents.xai
import backend.agents.falsifier
import backend.agents.causal_analyst
import backend.agents.detector
import backend.agents.interaction
import backend.agents.judge
import backend.agents.coach
import backend.agents.panel
import backend.agents.overseer
import backend.agents.profiler

SEED_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "seed", "seed_data.json")

def read_seed_data():
    with open(SEED_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def test_all_workflows_input_mappings():
    \"\"\"
    Validates that every step inside seed_data.json correctly maps ALL required fields 
    defined in its respective Agent's Pydantic input schema. 
    This prevents 'NoneType' or missing field errors at runtime.
    \"\"\"
    data = read_seed_data()
    workflows = data.get("workflows", [])
    
    assert len(workflows) > 0, "No workflows found in seed_data.json"
    
    for workflow in workflows:
        workflow_id = workflow.get("id")
        for step in workflow.get("steps", []):
            task_key = step.get("task_key")
            step_name = step.get("name", task_key)
            inputs = step.get("inputs", {})
            
            task_def = TaskRegistry.get(task_key)
            assert task_def is not None, f"Task '{task_key}' not found in registry. Did you import the agent module?"
            
            input_schema = task_def.input_schema
            
            # Check every required field in the schema
            for field_name, field_info in input_schema.model_fields.items():
                if field_info.is_required():
                    assert field_name in inputs, (
                        f"Workflow {workflow_id} -> Step '{step_name}': "
                        f"Missing REQUIRED mapping for '{field_name}'. "
                        f"Mismatched seed_data.json vs {input_schema.__name__} schema."
                    )
            
            # Also check if any mapped inputs are pointing to naked local variables instead of $inputs
            for k, v in inputs.items():
                if isinstance(v, str) and v.startswith("$") and not v.startswith("$inputs.") and not v.startswith("$config.") and not v.startswith("$sys."):
                    # Look up if this step references a previous step's output
                    # Valid mappings: $step_id, $inputs.field, $config.field
                    # If it's a naked string like $history_text, fail fast.
                    if len(v) > 1 and v[1] != "-" and not "-" in v:
                        pytest.fail(
                            f"Workflow {workflow_id} -> Step '{step_name}': "
                            f"Dangerous mapping detected '{k}': '{v}'. "
                            f"Did you mean '$inputs.{v[1:]}'?"
                        )
