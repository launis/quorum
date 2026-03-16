import pytest


@pytest.mark.asyncio
async def test_studio_workflow_blueprint_saving_valid() -> None:
    """Verify that a syntactically correct render_blueprint payload is accepted by the strict Router Pydantic typing."""
    # V2 Architecture note: We skip bringing up the full FastAPI app for a localized unit test of the model
    # and instead test the Pydantic serialization boundary directly since the Router logic is just `data: Workflow`.
    from backend_v2.models.v2_core import Workflow

    payload = {
        "id": "wf_test_1",
        "slug": "wf_test_1",
        "name": "Test Workflow",
        "description": "Test description",
        "expected_inputs": [{"input_key": "doc", "label": {"translations": {"en": "Doc"}, "default_locale": "en"}, "required": True, "input_modes": ["file"], "description": {"translations": {"en": "desc"}, "default_locale": "en"}, "ai_description": {"translations": {"en": "ai"}, "default_locale": "en"}}],
        "render_blueprint": {
            "version": "1.0",
            "components": [
                {
                    "type": "1d_gauge",
                    "data_path": "$steps.test.score",
                    "title": "Gauge 1"
                },
                {
                    "type": "header",
                    "title": "My Header"
                }
            ]
        }
    }

    # Should validate perfectly
    wf = Workflow.model_validate(payload)
    assert wf.render_blueprint is not None
    assert len(wf.render_blueprint.components) == 2
    assert wf.render_blueprint.components[0].type == "1d_gauge"


@pytest.mark.asyncio
async def test_studio_workflow_blueprint_saving_invalid() -> None:
    """Verify that malformed GUI JSON structures are strictly rejected (Fail-Fast)."""
    from pydantic import ValidationError

    from backend_v2.models.v2_core import Workflow

    payload = {
        "id": "wf_test_2",
        "slug": "wf_test_2",
        "name": "Test Workflow",
        "description": "Test description",
        "expected_inputs": [{"input_key": "doc", "label": {"translations": {"en": "Doc"}, "default_locale": "en"}, "required": True, "input_modes": ["file"], "description": {"translations": {"en": "desc"}, "default_locale": "en"}, "ai_description": {"translations": {"en": "ai"}, "default_locale": "en"}}],
        "render_blueprint": {
            "version": "1.0",
            "components": [
                {
                    "type": "1d_gauge",
                    # MISSING REQUIRED 'data_path' FIELD
                    "title": "Gauge 1"
                }
            ]
        }
    }

    # Should throw validation error immediately
    with pytest.raises(ValidationError) as exc_info:
        Workflow.model_validate(payload)

    assert "data_path" in str(exc_info.value)
    assert "Input should be a valid string" in str(exc_info.value) or "Field required" in str(exc_info.value)

