from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.exceptions import AppException
from backend_v2.services.blueprint import BlueprintTransformer


@pytest.mark.asyncio
async def test_blueprint_sdui_missing_synthesis_md():
    # Setup mocks
    exec_repo = AsyncMock()
    identity_repo = AsyncMock()

    # Mock OutputProfile with a synthesis block
    profile_dict = {
        "id": "prf_1234567890abcdef",
        "slug": "test",
        "workflow_id": "wf_test",
        "name": {"default_locale": "en", "translations": {"en": "Test Profile"}},
        "synthesis": {"synthesis_block_id": "blk_123", "system_prompt": "Prompt", "length_constraint": 100},
        "content_blocks": [{"id": "blk_123", "block_type": "markdown", "text": ""}],
        "layouts": [],
        "visible_metadata": ["date"],
        "scoring_strategy": "PURE_MATH",
        "strictness_level": 100,
    }

    output_profile_repo = AsyncMock()
    output_profile_repo.get_all_output_profiles.return_value = [profile_dict]

    exec_repo.get_execution_profile.return_value = None  # No cache

    # Mock Execution without any synthesis_md in execution_trace
    execution = MagicMock()
    execution.id = "exe_123"
    execution.workflow_id = "wf_test"
    execution.created_by = "usr_123"
    execution.organization_id = "org_123"
    import datetime

    execution.created_at = datetime.datetime.now(datetime.timezone.utc)
    execution.execution_trace = []  # NO synthesis completion event!
    execution.step_states = {}
    execution.profile_syntheses = {}
    execution.metadata = {}

    exec_repo.get_execution.return_value = execution
    exec_repo.get_execution_results.return_value = []

    # Workflow object
    workflow_mock = MagicMock()
    workflow_mock.default_scoring_strategy.value = "PURE_MATH"
    exec_repo.get_workflow.return_value = workflow_mock

    identity_repo.get_organization_model.return_value = MagicMock(name="Test Org")
    org_mock = MagicMock()
    org_mock.name = "Test Org"
    identity_repo.get_organization_model.return_value = org_mock
    identity_repo.get_user.return_value = {"name": "Test User"}

    # Run the transformer
    transformer = BlueprintTransformer(
        exec_repo=exec_repo,
        identity_repo=identity_repo,
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=output_profile_repo,
        system_repo=AsyncMock(),
    )

    try:
        dto = await transformer.build_report_dto("exe_123", "prf_1234567890abcdef", "en")

        # Verify the block was kept
        assert any(b.get("id") == "blk_123" for b in dto.content_blocks), "Content block was dropped!"
    except AppException as e:
        if "Synthesis mapping failed" in e.message:
            pytest.fail(f"Bug reproduced! Raised AppException: {e.message}")
        else:
            raise e
