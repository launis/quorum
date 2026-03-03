from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.agents.base import BaseAgent
from backend.core.registry import TaskRegistry
from backend.models.domain.agent import ModelConfig
from backend.models.domain.base import ReasoningTrace, ReasoningTraceDTO


class MockDTO(ReasoningTraceDTO):
    model_config = {"extra": "allow"}
    thought_process: str = "mock thought process"
    conclusion: str = "mock conclusion"
    confidence_score: float = 0.99
    result: str = "success"

# Add mock output model
class MockOutput(ReasoningTrace, MockDTO):
    pass


# Mock Agent for Testing
class MockGuardAgent(BaseAgent):
    """A mock agent that mirrors the real GuardAgent but reports its config."""

    DTO_SCHEMA = MockDTO
    OUTPUT_SCHEMA = MockOutput

    async def execute(
        self, input_data: dict, execution_context: dict | None = None, system_instruction: str | None = None, **kwargs
    ) -> dict:
        # Return the kwargs so we can inspect what was passed
        combined_kwargs = kwargs.copy()
        combined_kwargs["system_instruction"] = system_instruction
        combined_kwargs["input_data"] = input_data
        return {
            "thought_process": "mock thought process",
            "conclusion": "mock conclusion",
            "confidence_score": 0.99,
            "received_kwargs": combined_kwargs,
            "status": "success",
            "result": "success"
        }


@pytest.mark.asyncio
async def test_agent_wrapper_propagates_temperature():
    """Verify that agent_wrapper correctly extracts 'temperature' from Registry and passes it to Agent."""
    # 1. Setup Mock Registry & Config
    # This simulates what AgentRegistry.resolve_model_config() returns from the DB
    mock_db_config = ModelConfig(
        model_name="mock-model-v1",
        provider="mock",
        is_active=True,
        tpm_limit=5000,
        rpm_limit=100,
        temperature=0.42,  # Critical Value < 1.0
        max_tokens=1234,
        top_p=0.9,
    )

    # 2. Mock Internal Dependencies
    # We mock get_async_repository to avoid DB connection
    # We mock AgentRegistry to return our specific config.
    # Since agent_wrapper imports it from backend.services.agent_registry, we patch it THERE or use sys.modules.
    with (
        patch("backend.dependencies.get_async_repository", new_callable=AsyncMock),
        patch("backend.services.agent_registry.AgentRegistry") as MockRegistryClass,
        patch("backend.services.component_registry.ComponentRegistry") as MockComponentRegistry,
    ):  # Prevent prompt resolution errors
        # Setup Registry Mock
        mock_registry_instance = MockRegistryClass.return_value
        mock_registry_instance.resolve_model_config = AsyncMock(return_value=mock_db_config)

        # Component Registry returns our TEMPLATE
        mock_instance = MagicMock()
        mock_instance.resolve_prompts = AsyncMock(return_value="Mock System Instruction")
        MockComponentRegistry.resolve_prompts_map = AsyncMock(return_value={"mock_key": "Mock System Instruction"})
        MockComponentRegistry.return_value = mock_instance

        # 3. Register the Mock Agent
        # This triggers the specific logic in TaskRegistry.register_agent that creates the 'agent_wrapper'
        TaskRegistry.register_agent(
            task_keys=["test_task_integrity"],
            agent_cls=MockGuardAgent,
            output_model=MockOutput,  # MockOutput instead of dict
        )

        task_def = TaskRegistry.get("test_task_integrity")
        assert task_def is not None, "Task registration failed"

        # 4. Execute the Wrapper
        # This runs the 'agent_wrapper' function inside registry.py
        wrapper_func = task_def.handler

        input_data = MagicMock()
        input_data.model_dump.return_value = {"some": "input"}

        # Call the wrapper!
        try:
            result = await wrapper_func(
                input_data=input_data,
                execution_config={"some_override": "allowed"},  # Optional: test mixed config
            )
        except Exception as e:
            print(f"Wrapper execution failed with: {e}")
            import traceback

            traceback.print_exc()
            raise

        # 5. Assertions
        received_kwargs = result.received_kwargs

        print(f"\nDebug: Received Kwargs: {received_kwargs}")

        # CRITICAL ASSERTION: Did 'temperature' make it?
        assert "temperature" in received_kwargs, "Temperature was DROPPED by agent_wrapper!"
        assert received_kwargs["temperature"] == 0.42, (
            f"Temperature mismatch! Expected 0.42, got {received_kwargs['temperature']}"
        )

        # Verify other integrity items
        assert received_kwargs["max_tokens"] == 1234
        assert received_kwargs["top_p"] == 0.9

        # Verify step config merge
        assert received_kwargs["some_override"] == "allowed"

        print("SUCCESS: Configuration flow is intact.")


async def test_prompt_substitution():
    """Verify that variable variables like {{HISTORY_TEXT}} are actually replaced."""
    # 1. Setup Mock Prompt with Placeholders

    mock_db_config = ModelConfig(
        model_name="mock", provider="mock", is_active=True, tpm_limit=5000, rpm_limit=100, temperature=0.1
    )

    with (
        patch("backend.dependencies.get_async_repository", new_callable=AsyncMock),
        patch("backend.services.agent_registry.AgentRegistry") as MockRegistryClass,
        patch("backend.services.component_registry.ComponentRegistry") as MockComponentRegistry,
        patch("backend.agents.base.LLMFactory") as MockLLMFactory,
    ):
        # Registry returns simple config
        mock_registry_instance = MockRegistryClass.return_value
        mock_registry_instance.resolve_model_config = AsyncMock(return_value=mock_db_config)

        # Component Registry returns our TEMPLATE
        mock_instance = MagicMock()
        mock_instance.resolve_prompts = AsyncMock(return_value="Analyzed: {{HISTORY_TEXT}}")
        MockComponentRegistry.resolve_prompts_map = AsyncMock(return_value={"SOME_KEY": "Analyzed: {{HISTORY_TEXT}}"})
        MockComponentRegistry.return_value = mock_instance

        # Registry returns simple config
        mock_registry_instance = MockRegistryClass.return_value
        mock_registry_instance.resolve_model_config = AsyncMock(return_value=mock_db_config)

        # Mock Factory creation
        MockLLMFactory.create_provider.return_value = MagicMock()

        # 3. Register Mock Agent
        TaskRegistry.register_agent(["test_prompt_integ"], MockGuardAgent, MockOutput)
        task_def = TaskRegistry.get("test_prompt_integ")
        assert task_def is not None
        wrapper_func = task_def.handler

        # 4. Input with DATA
        input_dict = MagicMock()
        input_dict.model_dump.return_value = {"history_text": "CRITICAL_DATA_FOUND"}

        # 5. Execute with 'llm_prompts' key to trigger substitution logic
        # MUST BE INSIDE WITH BLOCK because resolving happens here
        result = await wrapper_func(input_data=input_dict, execution_config={"llm_prompts": ["SOME_KEY"]})

        # 6. Verify System Instruction
        kwargs = result.received_kwargs
        sys_instr = kwargs.get("system_instruction", "")

        # assert "CRITICAL_DATA_FOUND" in sys_instr, f"Variable {{HISTORY_TEXT}} was NOT substituted! Got: '{sys_instr}'"
        if "CRITICAL_DATA_FOUND" not in sys_instr:
            import json

            # Default to str representation if not serializable
            try:
                debug_kwargs = json.dumps(kwargs, default=str)
            except Exception:
                debug_kwargs = str(kwargs)
            raise AssertionError(
                f"{{HISTORY_TEXT}} NOT substituted! Got: '{sys_instr}'. Kwargs keys: {list(kwargs.keys())}. Kwargs: {debug_kwargs}"
            )
        assert "{{HISTORY_TEXT}}" not in sys_instr, "Placeholder {{HISTORY_TEXT}} leaked into final prompt!"
        print("SUCCESS: Prompt Variable Substitution is active.")


if __name__ == "__main__":
    import asyncio
    import os
    import sys

    # Add project root to sys.path
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

    try:
        print("--- TEST 1: Config Propagation ---")
        asyncio.run(test_agent_wrapper_propagates_temperature())
        print("\n--- TEST 2: Prompt Substitution ---")
        asyncio.run(test_prompt_substitution())
        print("\nALL INTEGRITY TESTS PASSED.")
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
