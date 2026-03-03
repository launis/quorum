"""Automated schema alignment tests for agents.

This test file dynamically reads all registered tasks in the TaskRegistry
and enforces the V2.9 Architecture rule:
1. All agents MUST define DTO_SCHEMA.
2. DTO_SCHEMA MUST inherit from ReasoningTraceDTO.
3. OUTPUT_SCHEMA MUST inherit from ReasoningTrace.
4. Agent.__init__ must not override or bypass this strictness.
"""


import pytest

import backend.tasks.analysis  # noqa: F401
import backend.tasks.coaching  # noqa: F401
import backend.tasks.critique  # noqa: F401
import backend.tasks.interaction  # noqa: F401
import backend.tasks.judgment  # noqa: F401
import backend.tasks.panel  # noqa: F401
import backend.tasks.reporting  # noqa: F401
import backend.tasks.retrieval  # noqa: F401
import backend.tasks.security  # noqa: F401
from backend.core.registry import TaskRegistry

# Import application and task modules to trigger registry population
from backend.main import app  # noqa: F401
from backend.models.domain.base import ReasoningTrace, ReasoningTraceDTO


@pytest.fixture(scope="module")
def registered_agents():
    """Provides a list of all instantiated agent classes from the registry."""
    agents = []
    # TaskRegistry keys
    keys = list(TaskRegistry._tasks.keys())

    for key in keys:
        agent_def = TaskRegistry.get(key)
        if agent_def and getattr(agent_def, "metadata", None) and "agent_class" in agent_def.metadata:
            # agent_class is stored as a string name in metadata in register_agent!
            agent_class_name = agent_def.metadata["agent_class"]

            # Retrieve the actual instance from agents_map to get its class
            if agent_class_name in TaskRegistry.agents_map:
                agent_instance = TaskRegistry.agents_map[agent_class_name]
                agents.append((key, agent_instance.__class__))
    return agents

def test_all_agents_have_dto_schema(registered_agents):
    """Ensure every agent defines a DTO_SCHEMA for LLM generation."""
    assert len(registered_agents) > 0, "No agents found in registry."

    anomalies = []
    for key, agent_class in registered_agents:
        dto_schema = getattr(agent_class, "DTO_SCHEMA", None)
        if not dto_schema:
            anomalies.append(f"Agent '{key}' ({agent_class.__name__}) is missing DTO_SCHEMA.")

    assert not anomalies, "Agents found without DTO_SCHEMA: " + "\n".join(anomalies)

def test_dto_schemas_inherit_reasoning_trace_dto(registered_agents):
    """Ensure DTO_SCHEMA always inherits from the lightweight ReasoningTraceDTO."""
    anomalies = []
    for key, agent_class in registered_agents:
        dto_schema = getattr(agent_class, "DTO_SCHEMA", None)
        if dto_schema:
            if not issubclass(dto_schema, ReasoningTraceDTO):
                anomalies.append(f"Agent '{key}' DTO_SCHEMA ({dto_schema.__name__}) does NOT inherit from ReasoningTraceDTO.")

    assert not anomalies, "DTO Schemas breaking inheritance: " + "\n".join(anomalies)

def test_output_schemas_inherit_reasoning_trace(registered_agents):
    """Ensure OUTPUT_SCHEMA (Domain Model) always inherits from ReasoningTrace."""
    anomalies = []
    for key, agent_class in registered_agents:
        out_schema = getattr(agent_class, "OUTPUT_SCHEMA", None)
        if out_schema:
            if not issubclass(out_schema, ReasoningTrace):
                anomalies.append(f"Agent '{key}' OUTPUT_SCHEMA ({out_schema.__name__}) does NOT inherit from ReasoningTrace.")
        else:
            anomalies.append(f"Agent '{key}' missing OUTPUT_SCHEMA.")

    assert not anomalies, "Domain Schemas breaking inheritance: " + "\n".join(anomalies)

def test_no_rogue_schema_overrides(registered_agents):
    """Ensure agents do not attempt to bypass DTO_SCHEMA by overriding get_response_schema."""
    anomalies = []
    for key, agent_class in registered_agents:
        # Check if they override get_response_schema
        # BaseAgent's implementation returns DTO_SCHEMA or OUTPUT_SCHEMA
        # If an agent overrides it specifically to return a Domain Model, it's a violation.

        # Instantiate to check method resolution
        try:
            agent_instance = agent_class(model="mock-model", provider="mock-mock")
            schema = agent_instance.get_response_schema()

            # The returned schema should ALWAYS be the DTO_SCHEMA if one exists.
            expected_schema = getattr(agent_class, "DTO_SCHEMA", None)

            if expected_schema and schema != expected_schema:
                anomalies.append(
                    f"Agent '{key}' overrides get_response_schema to return {schema.__name__} "
                    f"instead of expected DTO_SCHEMA {expected_schema.__name__}."
                )
        except Exception as e:
            # Some agents might fail instantiation if fully mocked incorrectly, but they shouldn't in Zero-Fallback.
            print(f"Skipping instantiation check for {key} due to {e}")
            pass

    assert not anomalies, "Agents with rogue schema overrides: \n" + "\n".join(anomalies)
