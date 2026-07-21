import json

import pytest

from backend_v2.models.state import StepOutputDTO
from backend_v2.services.orchestrator.strategies.llm_execution.context_builder import ContextBuilder


def test_context_builder_json_serialization_crash():
    # Simulate the exact scenario that crashed the execution
    # A step (sr_aaaaaaaaaaaaaaaa) which has a payload containing nested StepOutputDTO objects
    nested_dto = StepOutputDTO(step_id="sr_previous", block_id="blk_1", data_type="text", payload="some text")

    dtos = [
        StepOutputDTO(
            step_id="sr_aaaaaaaaaaaaaaaa",
            block_id="steps",
            data_type="text",
            payload=[nested_dto],  # The payload is a list of Pydantic models
        )
    ]

    output_profile = None
    schema_type = "TEXT"
    schema_map = {"sr_aaaaaaaaaaaaaaaa": "TEXT"}

    # Run _process_trace_dtos which calls _project_compressed
    result = ContextBuilder._process_trace_dtos(dtos, output_profile, schema_type, schema_map)

    # Try to JSON serialize the result, just like _prune_step_dtos does
    try:
        json.dumps(result, ensure_ascii=False)
    except TypeError as e:
        pytest.fail(f"JSON serialization failed, bug is present! Error: {e}")
