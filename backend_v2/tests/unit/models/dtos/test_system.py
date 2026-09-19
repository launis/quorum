import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.system import ClientErrorPayload, HookListResponse


def test_hook_list_response_strictness() -> None:
    dto = HookListResponse(hooks=["hook_1", "hook_2"])
    assert dto.hooks == ["hook_1", "hook_2"]

    with pytest.raises(ValidationError):
        HookListResponse(hooks=["hook_1"], extra_field="fail")  # type: ignore


def test_client_error_payload_strictness() -> None:
    dto = ClientErrorPayload(
        session_id="usr_123",
        app_version="1.0.0",
        platform="android",
        locale="fi",
        error_message="Fatal crash",
        stack_trace="Traceback...",
        severity="fatal",
        context_data={"screen": "home"},
    )
    assert dto.error_message == "Fatal crash"
    assert dto.severity == "fatal"
    assert dto.context_data == {"screen": "home"}

    with pytest.raises(ValidationError):
        ClientErrorPayload(
            error_message="Fatal crash",
            extra="fail",  # type: ignore
        )


def test_system_config_dtos_and_discriminated_union() -> None:
    """Test SystemSettingsDTO and AnySystemConfig discriminated union validation."""
    from backend_v2.models.domain.system_config import ModelProfile, SystemConfigModelRegistry
    from backend_v2.models.dtos.system import (
        AnySystemConfigAdapter,
        SystemConfigCreateDTO,
        SystemConfigUpdateDTO,
        SystemConfigUpsertDTO,
        SystemSettingsDTO,
    )

    # 1. SystemSettingsDTO
    settings_dto = SystemSettingsDTO(environment="production", maintenance_mode=True)
    assert settings_dto.type == "system_settings"
    assert settings_dto.environment == "production"
    assert settings_dto.maintenance_mode is True

    # Extra forbid
    with pytest.raises(ValidationError) as exc:
        SystemSettingsDTO.model_validate({"type": "system_settings", "unknown": 123})
    assert "extra_forbidden" in str(exc.value) or "Extra inputs are not permitted" in str(exc.value)

    from backend_v2.models.enums import CognitiveTier

    # 2. AnySystemConfig discriminated union validation
    dummy_profile = ModelProfile(
        model_name="gemini-2.5-flash",
        provider="google",
        tpm_limit=1000,
        rpm_limit=10,
        temperature=1.0,
        max_tokens=2048,
    )
    model_reg = SystemConfigModelRegistry(
        id="sys_1234567890abcdef",
        name="Test Registry",
        type="model_registry",
        tier_definitions={
            CognitiveTier.FAST: dummy_profile,
            CognitiveTier.BALANCED: dummy_profile,
            CognitiveTier.DEEP: dummy_profile,
            CognitiveTier.REASONING: dummy_profile,
        },
    )
    validated_union = AnySystemConfigAdapter.validate_python(model_reg.model_dump(mode="python"))
    assert isinstance(validated_union, SystemConfigModelRegistry)
    assert validated_union.type == "model_registry"

    # Discriminated union fails on invalid type
    with pytest.raises(ValidationError):
        AnySystemConfigAdapter.validate_python({"type": "invalid_type", "id": "sys_123"})

    # 3. SystemConfigUpdateDTO
    update_dto = SystemConfigUpdateDTO(system_settings=settings_dto)
    assert update_dto.system_settings is not None
    assert update_dto.system_settings.maintenance_mode is True

    # 4. SystemConfigCreateDTO
    create_dto = SystemConfigCreateDTO(
        type="system_settings",
        content=settings_dto,
    )
    assert create_dto.type == "system_settings"

    # 5. SystemConfigUpsertDTO
    upsert_dto = SystemConfigUpsertDTO(
        id="sys_1234567890abcdef",
        type="system_settings",
        content=settings_dto,
    )
    assert upsert_dto.id == "sys_1234567890abcdef"
