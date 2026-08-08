from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.exceptions import AppException
from backend_v2.services.blueprint import BlueprintTransformer


@pytest.mark.asyncio
async def test_blueprint_variance_validation_crash():
    exec_repo = AsyncMock()
    identity_repo = AsyncMock()

    # OutputProfile with variance_validation but missing performativity_detector_step_id
    profile_dict = {
        "id": "prf_5d6e7f8091a2b3c4",
        "slug": "test",
        "workflow_id": "wf_test",
        "name": {"default_locale": "en", "translations": {"en": "Test Profile"}},
        "visible_workflow_extensions": ["variance_validation"],
        "content_blocks": [],
        "layouts": [],
        "visible_metadata": ["date"],
        "scoring_strategy": "PURE_MATH",
        "strictness_level": 100,
        "performativity_detector_step_id": None  # The root cause of the crash
    }

    output_profile_repo = AsyncMock()
    output_profile_repo.get_all_output_profiles.return_value = [profile_dict]

    exec_repo.get_execution_profile.return_value = None

    execution = MagicMock()
    execution.id = "exe_123"
    execution.workflow_id = "wf_test"
    execution.created_by = "usr_123"
    execution.organization_id = "org_123"
    execution.context_variables = {}

    from backend_v2.models.state import TraceEvent
    # Trace with 0 performative phrases
    event_mock = TraceEvent(
        event_type="decision",
        content={"step_linguistics": {"performative_patterns": []}},
        step_name="test_step"
    )
    execution.execution_trace = [event_mock]
    execution.step_states = {}

    exec_repo.get_execution.return_value = execution
    exec_repo.get_execution_results.return_value = []

    workflow_mock = MagicMock()
    workflow_mock.default_scoring_strategy.value = "PURE_MATH"
    exec_repo.get_workflow.return_value = workflow_mock

    identity_repo.get_organization_model.return_value = MagicMock(name="Test Org")
    identity_repo.get_user.return_value = {"name": "Test User"}

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
        await transformer.build_report_dto("exe_123", "prf_5d6e7f8091a2b3c4", "en")
    except AppException as e:
        if "Strict Fail-Fast Enforced: 'variance_validation' requested but authenticity_score" in e.message:
            pytest.fail(f"Bug reproduced! Raised AppException: {e.message}")
        else:
            raise e
