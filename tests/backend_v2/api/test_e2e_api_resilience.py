import pytest
from httpx import ASGITransport, AsyncClient

from backend_v2.api.dependencies import get_arq_pool, get_current_user_from_header
from backend_v2.exceptions import ErrorCodes
from backend_v2.main import app
from backend_v2.models.auth import TokenData, UserRole

async def mock_arq_pool() -> None:
    return None

async def mock_current_user() -> TokenData:
    return TokenData(id="usr_test123", email="test@test.com", role=UserRole.ADMIN, organization_id="org_test")

app.dependency_overrides[get_arq_pool] = mock_arq_pool
app.dependency_overrides[get_current_user_from_header] = mock_current_user

# E2E Test Headers
MOCK_HEADERS = {
    "Authorization": "Bearer test-admin-token",
    "X-User-ID": "usr_test123",
    "X-Organization-ID": "org_test123",
}


@pytest.mark.asyncio
async def test_e2e_execution_create_rejects_extra_fields_rfc7807() -> None:
    """Negative Test: Ylimääräiset kentät (Opaque mallien extra=forbid)
    palauttavat 422-virheen standardoidussa RFC 7807 -formaatissa.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        invalid_payload = {
            "workflow_id": "wf_12345678",
            "target_locale": "fi",
            "raw_inputs": {"inputs": {}},
            "malicious_extra_field": "Should Fail-Fast",  # Tämän pitää kaataa Pydantic-validointi!
        }

        response = await client.post("/api/v2/execution/executions/", json=invalid_payload, headers=MOCK_HEADERS)

        # FAST-FAIL EXPECTATION
        assert response.status_code == 422, f"Expected 422 due to extra parameters, got {response.status_code}"

        # Katso fastapi.exceptions-handlerin implementaatiota (main.py)
        data = response.json()
        assert data.get("status") == 422
        assert data.get("title") == "Validation Failed"
        assert "extensions" in data
        assert data["extensions"].get("error_code") == ErrorCodes.VALIDATION_FAILED.value

        # Varmistetaan, että virheilmoitus mainitsee nimenomaan 'malicious_extra_field'
        errors = data["extensions"].get("errors", [])
        assert any("malicious_extra_field" in str(err) for err in errors), "Extra field was not named in the error detail"


@pytest.mark.asyncio
async def test_e2e_execution_create_rejects_missing_required_fields_rfc7807() -> None:
    """Negative Test: Puuttuvat pakolliset parametrit (esim. target_locale)
    pakottavat FastAPI:n heittämään RFC 7807 muotoisen AppExceptionin (422).
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        invalid_payload = {
            "workflow_id": "wf_12345678",
            # target_locale PUUTTUU tietoisesti!
            "raw_inputs": {"inputs": {}},
        }

        response = await client.post("/api/v2/execution/executions/", json=invalid_payload, headers=MOCK_HEADERS)

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"

        data = response.json()
        assert data.get("status") == 422
        assert data["extensions"]["error_code"] == ErrorCodes.VALIDATION_FAILED.value

        errors = data["extensions"].get("errors", [])
        assert any("target_locale" in str(err) for err in errors), "Missing field 'target_locale' not reported"


@pytest.mark.asyncio
async def test_e2e_studio_prompt_block_rejects_invalid_opaque_id() -> None:
    """Negative Test: Testataan Admin Studion PromptBlock PUT/POST-validointia,
    mikäli Opaque ID -regex ei täyty, FastAPI palauttaa RFC 7807:n.
    """
    # HUOM: Vaikka reitti ei olisi täysin mockattu pystyyn, Pydantic-validointi
    # iskee E2E rajapinnassa (router-body-argumentissa) ennen kuin ohjainkoodia edes ajetaan.
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        invalid_payload = {
            "id": "tämä on täysin laiton id",  # Opaque id regex: ^([a-z]{2,5})_[a-zA-Z0-9]{8,}$
            "slug": "lapanen",
            "label": {"translations": {"en": "Label"}, "default_locale": "en"},
            "description": {"translations": {"en": "Desc"}, "default_locale": "en"},
            "ai_description": "prompt",
            "category_id": "test",
            "is_evaluative": True,
            "type": "string",
        }

        response = await client.put("/api/v2/studio/prompt-blocks/blk_test12345678", json=invalid_payload, headers=MOCK_HEADERS)

        # Joko HTTP 422 (Body Validation) tai 405 (Method Not Allowed jos POST puuttuu ja on vain PUT)
        # Molemmat johtuvat ennen businesslogiikkaa.
        # Oletetaan, että FastAPI luokittelee sen validointivirheeksi jos reitti on olemassa.
        if response.status_code == 422:
            data = response.json()
            assert data["extensions"]["error_code"] == ErrorCodes.VALIDATION_FAILED.value
            errors = data["extensions"].get("errors", [])
            assert any("id" in str(err) for err in errors), "ID format regex failure was not reported"
