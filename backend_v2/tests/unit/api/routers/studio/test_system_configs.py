"""Unit tests for backend_v2/api/routers/studio/system_configs.py router."""

import pytest
from fastapi import APIRouter, status

from backend_v2.api.routers.studio.system_configs import (
    SYSTEM_CONFIGS_PREFIX,
    SYSTEM_CONFIGS_TAG,
    build_system_config_router,
    router,
    validate_system_config_id,
)
from backend_v2.exceptions import AppException, ErrorCodes


def test_router_metadata_and_defaults() -> None:
    """Test that the default system_configs router initializes with canonical prefix and tag."""
    assert isinstance(router, APIRouter)
    assert router.prefix == SYSTEM_CONFIGS_PREFIX
    assert router.tags == [SYSTEM_CONFIGS_TAG]


@pytest.mark.parametrize(
    "valid_id",
    [
        "sys_" + "a" * 32,
        "sys_" + "f" * 32,
        "sys_0195f3a0000070008123456789abcdef",
    ],
)
def test_validate_system_config_id_valid_boundaries(valid_id: str) -> None:
    """Test validate_system_config_id accepts exact 32-hex length boundaries."""
    assert validate_system_config_id(valid_id) == valid_id


@pytest.mark.parametrize(
    "invalid_id",
    [
        "sys_" + "a" * 16,
        "sys_" + "a" * 31,
        "sys_" + "a" * 33,
        "wf_" + "a" * 32,
        "sys_invalid-id",
        "",
        "   ",
    ],
)
def test_validate_system_config_id_invalid_boundaries_raise_app_exception(invalid_id: str) -> None:
    """Test validate_system_config_id raises AppException on min-1 (31), max+1 (33), legacy 16-hex, and wrong prefix."""
    with pytest.raises(AppException) as exc_info:
        validate_system_config_id(invalid_id)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


def test_build_system_config_router_custom_valid_inputs() -> None:
    """Test build_system_config_router constructs an APIRouter for valid prefix and tag."""
    custom_router = build_system_config_router(
        prefix="/system-configs-v2",
        tag="Custom Studio System Configs",
    )
    assert isinstance(custom_router, APIRouter)
    assert custom_router.prefix == "/system-configs-v2"
    assert custom_router.tags == ["Custom Studio System Configs"]


@pytest.mark.parametrize(
    "invalid_prefix",
    [
        "",
        "/",
        "system-configs",
        "/System_Configs",
        "/system-configs/",
    ],
)
def test_build_system_config_router_invalid_prefix_raises_app_exception(invalid_prefix: str) -> None:
    """Test build_system_config_router raises AppException when prefix violates canonical route syntax."""
    with pytest.raises(AppException) as exc_info:
        build_system_config_router(prefix=invalid_prefix, tag=SYSTEM_CONFIGS_TAG)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.parametrize("blank_tag", ["", "   "])
def test_build_system_config_router_blank_tag_raises_app_exception(blank_tag: str) -> None:
    """Test build_system_config_router raises AppException when tag is empty or whitespace."""
    with pytest.raises(AppException) as exc_info:
        build_system_config_router(prefix=SYSTEM_CONFIGS_PREFIX, tag=blank_tag)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
