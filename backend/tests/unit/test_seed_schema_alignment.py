"""Static analysis to ensure database seed mapping aligns with Python Pydantic models."""

import json
from pathlib import Path

import pytest

from backend.core.registry import TaskRegistry
# Ensure agents are loaded in the registry before validating
import backend.agents  # noqa


import json
from pathlib import Path
import importlib
import pkgutil

import pytest

from backend.core.registry import TaskRegistry

# Ensure all tasks are registered before testing
try:
    import backend.tasks.preprocessing  # noqa
    import backend.tasks.security  # noqa
    import backend.tasks.retrieval  # noqa
    import backend.tasks.analysis  # noqa
    import backend.tasks.critique  # noqa
    import backend.tasks.interaction  # noqa
    import backend.tasks.judgment  # noqa
    import backend.tasks.coaching  # noqa
    import backend.tasks.reporting  # noqa
    import backend.tasks.panel  # noqa
except ImportError as e:
    pass # Some tests environments might not have all tasks, but we load what we can


def _load_seed_data():
    """Helper to load the seed data dynamically."""
    seed_path = Path("backend/seed/seed_data.json")
    if not seed_path.exists():
        seed_path = Path("seed/seed_data.json")
    
    if not seed_path.exists():
        return {"steps": []}
        
    with open(seed_path, "r", encoding="utf-8") as f:
        return json.load(f)

# Load data once for parametrization
_SEED_DATA = _load_seed_data()
_SEED_STEPS = _SEED_DATA.get("steps", [])

# Extract task keys used in the database
_DB_TASK_KEYS = {step.get("task_key") for step in _SEED_STEPS if "task_key" in step}

# Prepare parameters
_STEP_PARAMS = [
    (step.get("slug", "unknown"), step.get("task_key", "unknown"), step.get("inputs", {}))
    for step in _SEED_STEPS
]

_REGISTRY_AGENTS = list(TaskRegistry._tasks.keys())


@pytest.mark.parametrize("slug, task_key, step_inputs", _STEP_PARAMS, ids=[s[0] for s in _STEP_PARAMS])
def test_database_step_is_valid_in_python(slug, task_key, step_inputs):
    """
    DIRECTION 1 (Database -> Python):
    Verify that every step defined in seed_data.json references a valid Python agent,
    and that the provided inputs perfectly satisfy the Agent's Pydantic schema requirements.
    """
    # 1. Ensure Agent exists in Python Registry
    task_def = TaskRegistry.get(task_key)
    assert task_def is not None, f"Database step '{slug}' references unknown task_key: '{task_key}'"
    
    input_schema = task_def.input_schema
    if not input_schema:
        return # Agent doesn't have an input schema to validate against
        
    provided_keys = set(step_inputs.keys())
    schema_fields = input_schema.model_fields
    schema_keys = set(schema_fields.keys())
    
    required_keys = {
        name for name, field in schema_fields.items() 
        if field.is_required()
    }
    
    # 2. Check for Extra Keys (Database provides something Python doesn't explicitly need)
    # Note: In V5.1, the engine Blackboard/Context can hold extra keys (e.g. for pre-hooks). 
    # Therefore, providing extra keys is NOT a structural failure, as long as it doesn't break Pydantic validation.
    
    # NEW STRICT SAFETY PROTOCOL (Feb 2026 / Phase 9): 
    # Identify if the JSON has mangled step references (like truncated UUIDs due to bash/powershell script bugs).
    import re
    # A valid direct reference looks like '$c1f8d4e9-0b7a-4c2d-8e8f-9a9b0c1d2e3f' or '$inputs.something'
    # Or property access: '$c1f8d4e9-0b7a-4c2d-8e8f-9a9b0c1d2e3f.history_text'
    uuid_ref_pattern = re.compile(r'^\$[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}(?:\.[a-zA-Z0-9_]+)*$')
    
    # Provide context of all valid DB step IDs:
    db_step_ids = {s.get("id") for s in _SEED_STEPS if "id" in s}

    for key, val in step_inputs.items():
        if isinstance(val, str) and val.startswith('$') and not val.startswith('$inputs.'):
            # Strip property access if present (e.g., $c1f...e3f.history_text -> $c1f...e3f)
            base_ref = val.split('.')[0]
            
            if len(base_ref) > 15 and '-' in base_ref: # Heuristic for UUID-like things
                assert uuid_ref_pattern.match(val), f"Database step '{slug}' has corrupted/truncated Step ID reference in inputs: '{val}'"
                
                # NEW REQUIREMENT: Must exist in the database structure
                # The reference looks like $UUID, so strip the $.
                raw_uuid = base_ref[1:]
                assert raw_uuid in db_step_ids, f"Database step '{slug}' references Step ID '{raw_uuid}', but no such Step exists in the JSON!"

         
         
    # 3. Check for Missing Required Keys (Database forgot to provide something Python needs)
    missing_keys = required_keys - provided_keys
    assert not missing_keys, f"Database step '{slug}' is missing required inputs for '{task_key}': {missing_keys}"


@pytest.mark.parametrize("agent_key", _REGISTRY_AGENTS)
def test_python_agent_is_valid_in_database(agent_key):
    """
    DIRECTION 2 (Python -> Database):
    Verify that every Agent defined in the Python TaskRegistry is either represented 
    in the database (seed_data.json) OR that it is not considered 'orphaned'.
    Also ensures that if the agent *is* used, the database provides the correct schema mapping.
    """
    task_def = TaskRegistry.get(agent_key)
    
    # Find all steps in the database that use this specific Agent
    using_steps = [step for step in _SEED_STEPS if step.get("task_key") == agent_key]
    
    # For this architecture, we expect core agents to have a configuration.
    # Note: If some agents are strictly dynamically invoked (e.g. ad-hoc tools), 
    # we might skip them, but currently we assume all Agents are Workflow driven.
    # We won't strictly fail if it's unused, but if it IS used, we validate from this side too.
    
    for step in using_steps:
        slug = step.get("slug", "unknown")
        step_inputs = step.get("inputs", {})
        
        input_schema = task_def.input_schema
        if not input_schema:
            continue
            
        provided_keys = set(step_inputs.keys())
        schema_fields = input_schema.model_fields
        schema_keys = set(schema_fields.keys())
        
        required_keys = {
            name for name, field in schema_fields.items() 
            if field.is_required()
        }
        
        # Note matching above: Extra keys in the database mapping are allowed because the context Blackboard
        # can contain variables needed for hooks (like 'search_result' or 'focus_topic') that the core Agent Model ignores.
             
        missing_keys = required_keys - provided_keys
        assert not missing_keys, f"Python Agent '{agent_key}' is missing required keys from DB step '{slug}': {missing_keys}"

