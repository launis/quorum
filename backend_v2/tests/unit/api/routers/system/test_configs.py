"""Unit tests for backend_v2/api/routers/system/configs.py router."""

import pytest
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from backend_v2.api.routers.system.configs import (
    build_strictness_config,
    get_strictness_configurations,
    router,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.main import app_exception_handler
from backend_v2.models.dtos.system import StrictnessConfigDTO, StrictnessConfigListResponse
from backend_v2.models.enums import StrictnessAnchor

app = FastAPI()
app.include_router(router)


@app.exception_handler(AppException)
async def _test_app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Delegate AppException formatting to canonical RFC 7807 handler."""
    return await app_exception_handler(request, exc)


client = TestClient(app)


def test_router_metadata_and_strictness_endpoint_200() -> None:
    """Test GET /configs/strictness returns HTTP 200 with canonical strictness configurations."""
    assert router.prefix == "/configs"
    response = client.get("/configs/strictness")
    assert response.status_code == status.HTTP_200_OK

    validated = StrictnessConfigListResponse.model_validate(response.json())
    assert len(validated.configs) == 4
    assert validated.configs == [
        StrictnessConfigDTO(level=StrictnessAnchor.NONE.value, localization_key="strictnessFree"),
        StrictnessConfigDTO(level=StrictnessAnchor.STANDARD.value, localization_key="strictnessNormal"),
        StrictnessConfigDTO(level=StrictnessAnchor.STRICT.value, localization_key="strictnessStrict"),
        StrictnessConfigDTO(level=StrictnessAnchor.ABSOLUTE.value, localization_key="strictnessAbsolute"),
    ]


@pytest.mark.asyncio
async def test_get_strictness_configurations_direct_call() -> None:
    """Test direct invocation of get_strictness_configurations returns typed response DTO."""
    result = await get_strictness_configurations()
    assert isinstance(result, StrictnessConfigListResponse)
    assert [cfg.level for cfg in result.configs] == [
        StrictnessAnchor.NONE.value,
        StrictnessAnchor.STANDARD.value,
        StrictnessAnchor.STRICT.value,
        StrictnessAnchor.ABSOLUTE.value,
    ]


@pytest.mark.parametrize(
    ("level", "localization_key"),
    [
        (StrictnessAnchor.NONE.value, "strictnessFree"),
        (StrictnessAnchor.ABSOLUTE.value, "strictnessAbsolute"),
    ],
)
def test_build_strictness_config_valid_boundaries(level: int, localization_key: str) -> None:
    """Test build_strictness_config succeeds on exact min (0) and max (100) boundary values."""
    dto = build_strictness_config(level=level, localization_key=localization_key)
    assert dto.level == level
    assert dto.localization_key == localization_key


@pytest.mark.parametrize(
    "invalid_level",
    [
        StrictnessAnchor.NONE.value - 1,
        StrictnessAnchor.ABSOLUTE.value + 1,
    ],
)
def test_build_strictness_config_out_of_bounds_raises_app_exception(invalid_level: int) -> None:
    """Test build_strictness_config raises AppException on min-1 (-1) and max+1 (101) boundary values."""
    with pytest.raises(AppException) as exc_info:
        build_strictness_config(level=invalid_level, localization_key="strictnessCustom")

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.parametrize("blank_key", ["", "   "])
def test_build_strictness_config_blank_localization_key_raises_app_exception(blank_key: str) -> None:
    """Test build_strictness_config raises AppException when localization_key is empty or whitespace."""
    with pytest.raises(AppException) as exc_info:
        build_strictness_config(level=StrictnessAnchor.STANDARD.value, localization_key=blank_key)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_get_strictness_configurations_reraises_app_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test get_strictness_configurations re-raises upstream AppException untouched."""

    def _raise_validation_error(level: int, localization_key: str) -> StrictnessConfigDTO:
        raise AppException(
            message="Simulated validation failure",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

    monkeypatch.setattr(
        "backend_v2.api.routers.system.configs.build_strictness_config",
        _raise_validation_error,
    )

    with pytest.raises(AppException) as exc_info:
        await get_strictness_configurations()

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_get_strictness_configurations_translates_unexpected_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test get_strictness_configurations translates unexpected exceptions to INTERNAL_SERVER_ERROR."""

    def _raise_runtime_error(level: int, localization_key: str) -> StrictnessConfigDTO:
        raise RuntimeError("Unexpected failure")

    monkeypatch.setattr(
        "backend_v2.api.routers.system.configs.build_strictness_config",
        _raise_runtime_error,
    )

    with pytest.raises(AppException) as exc_info:
        await get_strictness_configurations()

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc_info.value.details["error_code"] == ErrorCodes.INTERNAL_SERVER_ERROR.value
