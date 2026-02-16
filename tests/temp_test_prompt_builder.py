import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.services.prompt_builder import PromptBuilder
from backend.database.repository import AbstractWorkflowRepository
from backend.services.agent_registry import AgentRegistry
from backend.exceptions import StepNotFoundError, AppException, ErrorCodes
from backend.models.state import WorkflowState

class TestPromptBuilder:

    @pytest.fixture
    def mock_repo(self):
        return AsyncMock(spec=AbstractWorkflowRepository)

    @pytest.fixture
    def mock_registry(self):
        return MagicMock(spec=AgentRegistry)

    @pytest.fixture
    def prompt_builder(self, mock_repo, mock_registry):
        return PromptBuilder(repository=mock_repo, agent_registry=mock_registry)

    @pytest.mark.asyncio
    async def test_construct_prompt_success(self, prompt_builder, mock_repo):
        """Test successful prompt construction."""
        step_id = "step-1"
        mock_repo.get_step_by_id.return_value = {
            "id": step_id,
            "execution_config": {"llm_prompts": ["prompt-1"]}
        }
        mock_repo.get_component_by_id.return_value = {
            "type": "prompt",
            "content": "Hello {{HISTORY_TEXT}}"
        }
        
        # Mock state for injection
        state = MagicMock(spec=WorkflowState)
        state.context_variables = {"inputs": {"history_text": "World"}}

        result = await prompt_builder.construct_prompt(step_id, current_state=state)
        
        assert "Hello World" in result
        print("\n[TEST] Construct Prompt: Success (Injection worked)")

    @pytest.mark.asyncio
    async def test_construct_prompt_step_not_found(self, prompt_builder, mock_repo):
        """Test Fail Fast for missing step."""
        mock_repo.get_step_by_id.return_value = None
        
        with pytest.raises(StepNotFoundError):
            await prompt_builder.construct_prompt("missing-step")
        print("\n[TEST] Fail Fast: StepNotFoundError caught")

    @pytest.mark.asyncio
    async def test_construct_prompt_fail_fast_on_error(self, prompt_builder, mock_repo):
        """Test Fail Fast on internal error."""
        step_id = "step-1"
        mock_repo.get_step_by_id.return_value = {"id": step_id}
        # Simulate repository error during component resolution
        mock_repo.get_component_by_id.side_effect = Exception("DB Connection Fail")
        
        # We need a prompt to trigger the loop
        mock_repo.get_step_by_id.return_value = {
            "id": step_id,
            "execution_config": {"llm_prompts": ["prompt-1"]}
        }
        
        with pytest.raises(AppException) as excinfo:
            await prompt_builder.construct_prompt(step_id)
            
        assert excinfo.value.status_code == 500
        assert excinfo.value.details["error_code"] == ErrorCodes.PROMPT_CONSTRUCTION_FAILED
        print("\n[TEST] Fail Fast: AppException caught for internal failure")

if __name__ == "__main__":
    # Simplified async runner for manual execution if needed
    import asyncio
    
    async def run_manual_tests():
        repo = AsyncMock(spec=AbstractWorkflowRepository)
        reg = MagicMock(spec=AgentRegistry)
        pb = PromptBuilder(repo, reg)
        
        t = TestPromptBuilder()
        await t.test_construct_prompt_step_not_found(pb, repo)
        # Note: mocking setup for success test is more complex manually, relying on pytest fixtures primarily.

    # pytest runner is preferred.
    pass
