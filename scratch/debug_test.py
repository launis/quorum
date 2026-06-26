import asyncio
from unittest.mock import AsyncMock
from types import SimpleNamespace
from backend_v2.services.blueprint import BlueprintTransformer
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.v2_core import ExecutionRecord

def dict_to_obj(d):
    if isinstance(d, dict):
        return SimpleNamespace(**{k: dict_to_obj(v) for k, v in d.items()})
    elif isinstance(d, list):
        return [dict_to_obj(v) for v in d]
    return d

async def run():
    mock_workflow_repo = AsyncMock()
    mock_system_repo = AsyncMock()
    mock_exec_repo = AsyncMock()

    mock_exec_repo.get_execution_record.return_value = ExecutionRecord(
        id="exe_0000000000000005",
        status=ExecutionStatus.COMPLETED,
        workflow_id="wf_1234abcd1234abcd",
        raw_inputs=WorkflowInputs(),
    )

    mock_workflow_repo.get_workflow.return_value = dict_to_obj(
        {
            "id": "wf_1234abcd1234abcd",
            "slug": "wf_1",
            "name": {"default_locale": "en", "translations": {"en": "Mock", "fi": "Mock"}},
            "expected_inputs": [{"id": "doc1", "type": "document", "scan_for_performative_patterns": True}],
            "default_profile_id": "prf_dddd1111dddd1111",
            "output_profiles": {
                "prf_dddd1111dddd1111": {
                    "name": {"default_locale": "en", "translations": {"en": "Default", "fi": "Default"}},
                    "layouts": [],
                }
            },
        }
    )

    mock_comp_repo = AsyncMock()
    mock_comp_repo.get_all_output_profiles_models.return_value = [
        SimpleNamespace(
            id="prf_dddd1111dddd1111",
            name=SimpleNamespace(default_locale="en", translations={"en": "Default", "fi": "Default"}),
            scoring_strategy=None,
            synthesis=None,
            custom_preface=None,
            visible_metadata=None,
        )
    ]

    transformer = BlueprintTransformer(
        exec_repo=mock_exec_repo,
        workflow_repo=mock_workflow_repo,
        comp_repo=mock_comp_repo,
        identity_repo=AsyncMock(),
        system_repo=mock_system_repo,
    )

    await transformer.build_report_dto("exe_0000000000000005", accept_language="en")

if __name__ == "__main__":
    asyncio.run(run())
