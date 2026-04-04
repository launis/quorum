import pytest


@pytest.mark.asyncio
async def test_studio_workflow_blueprint_saving_valid() -> None:
    """Verify that a syntactically correct render_blueprint payload is accepted by the strict Router Pydantic typing."""
    # V2 Architecture note: We skip bringing up the full FastAPI app for a localized unit test of the model
    # and instead test the Pydantic serialization boundary directly since the Router logic is just `data: Workflow`.
    from backend_v2.models.v2_core import Workflow

    payload = {
        "id": "wf_1111222233334444",
        "slug": "wf_test_1",
        "name": "Test Workflow",
        "description": "Test description",
        "expected_inputs": [
            {
                "input_key": "doc",
                "label": {"translations": {"en": "Doc"}, "default_locale": "en"},
                "required": True,
                "input_modes": ["file"],
                "description": {"translations": {"en": "desc"}, "default_locale": "en"},
                "ai_description": "ai"
            }
        ],
        "status": "published",
        "version": 1,
        "default_profile_id": "default",
    }

    # Should validate perfectly
    wf = Workflow.model_validate(payload)
    assert wf.expected_inputs[0].ai_description == "ai"


@pytest.mark.asyncio
async def test_studio_workflow_blueprint_saving_invalid() -> None:
    """Verify that malformed GUI JSON structures are strictly rejected (Fail-Fast)."""
    from pydantic import ValidationError

    from backend_v2.models.v2_core import Workflow

    payload = {
        "id": "wf_test12345678",
        "slug": "wf_test_2",
        "name": "Test Workflow",
        "description": "Test description",
        "expected_inputs": [
            {
                "input_key": "doc",
                "label": {"translations": {"en": "Doc"}, "default_locale": "en"},
                "required": True,
                "input_modes": ["file"],
                "description": {"translations": {"en": "desc"}, "default_locale": "en"},
                "ai_description": "ai"
            }
        ],
        "invalid_extra_field_which_fails": True
    }

    # Should throw validation error immediately
    with pytest.raises(ValidationError) as exc_info:
        Workflow.model_validate(payload)

    assert "invalid_extra_field_which_fails" in str(exc_info.value)

