from unittest.mock import AsyncMock

import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.v2_core import ExecutionRecord
from backend_v2.services.blueprint import BlueprintTransformer


@pytest.fixture
def mock_repo():
    """Provides a mocked workflow repository."""
    repo = AsyncMock()

    # Default mocks for repo setup
    repo.get_workflow_by_id.return_value = {
        "name": {
            "default_locale": "en",
            "translations": {"en": "Mock Workflow", "fi": "Testi Työnkulku"}
        }
    }

    repo.get_all_prompt_blocks.return_value = [
        {
            "id": "matrix_logic1234",
            "label": {"translations": {"fi": "Logiikka", "en": "Logic"}},
            "scales": [
                {"score": 0, "name": {"translations": {"fi": "Nolla", "en": "Zero"}}},
                {"score": 100, "name": {"translations": {"fi": "Täysi", "en": "Full"}}}
            ]
        },
        {
            "id": "matrix_emot12345",
            "label": {"translations": {"fi": "Tunteet", "en": "Emotions"}},
            "scales": [
                {"score": 1},
                {"score": 5}
            ]
        }
    ]

    repo.get_all_steps.return_value = [
        {
            "id": "step_logic",
            "title": {"translations": {"fi": "Looginen Askel", "en": "Logical Step"}}
        }
    ]

    return repo


@pytest.mark.asyncio
async def test_pydantic_validation_fails_on_missing_default_blueprint(mock_repo):
    # Setup execution without 'default' key in render_blueprints
    mock_repo.get_execution.return_value = ExecutionRecord(
        id="testexec_00000001",
        workflow_id="wf_1",
        status=ExecutionStatus.COMPLETED,
        render_blueprints={"wrong_key": {}},
        metadata={"target_locale": "fi"}
    )

    transformer = BlueprintTransformer(mock_repo)

    with pytest.raises(AppException) as exc:
        await transformer.build_render_payload("testexec_00000001")

    assert exc.value.status_code == 400
    assert exc.value.details["error_code"].value == "VALIDATION_FAILED"
    assert "missing render_blueprints['default']" in exc.value.message


@pytest.mark.asyncio
async def test_pydantic_validation_fails_on_invalid_component_type(mock_repo):
    # Setup execution with invalid component type "himmeli"
    mock_repo.get_execution.return_value = ExecutionRecord(
        id="testexec_00000002",
        workflow_id="wf_1",
        status=ExecutionStatus.COMPLETED,
        render_blueprints={
            "default": {
                "version": "1.0",
                "components": [
                    {"type": "himmeli"}
                ]
            }
        },
        metadata={"target_locale": "fi"}
    )

    transformer = BlueprintTransformer(mock_repo)

    with pytest.raises(AppException) as exc:
        await transformer.build_render_payload("testexec_00000002")

    assert exc.value.status_code == 400
    assert exc.value.details["error_code"].value == "VALIDATION_FAILED"
    assert "Invalid render_blueprint structure" in exc.value.message


@pytest.mark.asyncio
async def test_data_mapping_calculates_correct_visual_pct(mock_repo):
    mock_repo.get_execution.return_value = ExecutionRecord(
        id="testexec_00000003",
        workflow_id="wf_1",
        status=ExecutionStatus.COMPLETED,
        results={
            "steps": {
                "logic": {"matrix_logic1234": 75.0} # 75% out of max 100
            }
        },
        render_blueprints={
            "default": {
                "version": "1.0",
                "components": [
                    {
                        "type": "1d_gauge",
                        "data_path": "$results.steps.logic.matrix_logic1234",
                        "title": "Gauge Test"
                    }
                ]
            }
        },
        metadata={"target_locale": "en"}
    )

    transformer = BlueprintTransformer(mock_repo)
    payload = await transformer.build_render_payload("testexec_00000003")

    components = payload["blueprint"]["components"]
    assert len(components) == 1

    gauge = components[0]
    assert gauge["value"] == 75.0
    assert gauge["scale_max"] == 100.0
    assert gauge["visual_pct"] == 75.0
    assert gauge["display_value_only"] == "75.0"


@pytest.mark.asyncio
async def test_graceful_degradation_on_missing_data(mock_repo):
    # The path $steps.missing.score does not exist in results
    mock_repo.get_execution.return_value = ExecutionRecord(
        id="testexec_00000004",
        workflow_id="wf_1",
        status=ExecutionStatus.COMPLETED,
        results={},
        render_blueprints={
            "default": {
                "version": "1.0",
                "components": [
                    {
                        "type": "1d_gauge",
                        "data_path": "$results.steps.missing.matrix_logic1234",
                        "title": "Missing Test"
                    }
                ]
            }
        },
        metadata={"target_locale": "en"}
    )

    transformer = BlueprintTransformer(mock_repo)
    # Missing data should NOT crash the generic endpoint, but return a payload with nulls/NAs
    payload = await transformer.build_render_payload("testexec_00000004")

    gauge = payload["blueprint"]["components"][0]
    assert gauge.get("value") is None
    assert gauge.get("display_value") == "N/A"
    assert gauge.get("visual_pct") == 0.0


@pytest.mark.asyncio
async def test_translation_doctrine_leaves_static_keys_untouched(mock_repo):
    mock_repo.get_execution.return_value = ExecutionRecord(
        id="testexec_00000005",
        workflow_id="wf_1",
        status=ExecutionStatus.COMPLETED,
        results={},
        render_blueprints={
            "default": {
                "version": "1.0",
                "components": [
                    {
                        "type": "header",
                        "title": "report.complaint.header"
                    }
                ]
            }
        },
        metadata={"target_locale": "fi"}
    )

    transformer = BlueprintTransformer(mock_repo)
    payload = await transformer.build_render_payload("testexec_00000005")

    header = payload["blueprint"]["components"][0]
    # Static keys must be passed to UI untouched for Flutter to translate using .arb
    assert header["title"] == "report.complaint.header"

@pytest.mark.asyncio
async def test_translation_doctrine_resolves_dynamic_block_labels(mock_repo):
    mock_repo.get_execution.return_value = ExecutionRecord(
        id="testexec_00000006",
        workflow_id="wf_1",
        status=ExecutionStatus.COMPLETED,
        results={
            "steps": {"logic": {"matrix_logic1234": 100}}
        },
        render_blueprints={
            "default": {
                "version": "1.0",
                "components": [
                    {
                        "type": "1d_gauge",
                        "data_path": "$results.steps.logic.matrix_logic1234"
                        # Omitting "title" forces it to fetch dynamic block title
                    }
                ]
            }
        },
        metadata={"target_locale": "fi"}
    )

    transformer = BlueprintTransformer(mock_repo)
    payload = await transformer.build_render_payload("testexec_00000006")

    gauge = payload["blueprint"]["components"][0]
    # It should have resolved the title "Logiikka" and scale_text "Täysi" from the database mock
    assert gauge["title"] == "Logiikka"
    assert gauge["scale_text"] == "Täysi"

    # Test English override via accept_language param
    payload_en = await transformer.build_render_payload("testexec_00000006", accept_language="en")
    gauge_en = payload_en["blueprint"]["components"][0]
    assert gauge_en["title"] == "Logic"
    assert gauge_en["scale_text"] == "Full"

