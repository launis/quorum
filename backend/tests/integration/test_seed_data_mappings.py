import json
import os
import pytest
from backend.core.registry import TaskRegistry

# Import all agent modules so they register themselves
import backend.tasks.analysis
import backend.tasks.critique
import backend.tasks.security
import backend.tasks.reporting
import backend.tasks.coaching
import backend.tasks.judgment
import backend.tasks.panel
import backend.tasks.interaction
import backend.tasks.retrieval

SEED_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "seed", "seed_data.json")

def read_seed_data():
    with open(SEED_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def test_all_workflows_input_mappings():
    """
    Validates that every step inside seed_data.json correctly maps ALL required fields 
    defined in its respective Agent's Pydantic input schema. 
    This prevents 'NoneType' or missing field errors at runtime.
    """
    data = read_seed_data()
    workflows = data.get("workflows", [])
    all_steps = data.get("steps", [])
    
    assert len(all_steps) > 0, "No steps found in seed_data.json"
    
    for step in all_steps:
        workflow_id = "GlobalStep"
        task_key = step.get("task_key")
        
        if not task_key:
            continue
            
        step_name = step.get("name", task_key)
        inputs = step.get("inputs", {})
        task_def = TaskRegistry.get(task_key)
        assert task_def is not None, f"Task '{task_key}' not found in registry. Did you import the task module?"
        
        input_schema = task_def.input_schema
        
        # Check every required field in the schema
        for field_name, field_info in input_schema.model_fields.items():
            if field_info.is_required():
                assert field_name in inputs, (
                    f"Workflow {workflow_id} -> Step '{step_name}': "
                    f"Missing REQUIRED mapping for '{field_name}'. "
                    f"Mismatched seed_data.json vs {input_schema.__name__} schema."
                )
        
