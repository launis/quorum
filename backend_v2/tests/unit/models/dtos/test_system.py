"""Unit tests for System domain Data Transfer Objects."""

import pytest
from pydantic import ValidationError

from backend_v2.models.domain.system_config import ModelProfile, SystemConfigModelRegistry
from backend_v2.models.dtos.system import (
    AnySystemConfigAdapter,
    ClientErrorPayload,
    HealthCheckResponseDTO,
    HookListResponse,
    SafetySettingDTO,
    StrictnessConfigDTO,
    StrictnessConfigListResponse,
    SystemConfigCreateDTO,
    SystemConfigUpdateDTO,
    SystemConfigUpsertDTO,
    SystemSettingsDTO,
)
from backend_v2.models.enums import CognitiveTier


def test_safety_setting_dto_strictness() -> None:
    """Verify SafetySettingDTO valid instantiation and ISTQB negative boundaries."""
    dto = SafetySettingDTO(
        category="HARM_CATEGORY_HATE_SPEECH",
        threshold="BLOCK_LOW_AND_ABOVE",
    )
    assert dto.category == "HARM_CATEGORY_HATE_SPEECH"
    assert dto.threshold == "BLOCK_LOW_AND_ABOVE"

    # ISTQB Negative 1: Unrecognized extra field rejected (extra="forbid")
    with pytest.raises(ValidationError):
        SafetySettingDTO.model_validate(
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_LOW_AND_ABOVE",
                "extra": "forbidden",
            }
        )

    # ISTQB Negative 2: Non-string type violation rejected (strict=True)
    with pytest.raises(ValidationError):
        SafetySettingDTO.model_validate(
            {
                "category": 123,
                "threshold": "BLOCK_LOW_AND_ABOVE",
            }
        )


def test_health_check_response_dto_strictness() -> None:
    """Verify HealthCheckResponseDTO valid instantiation and ISTQB negative boundaries."""
    dto = HealthCheckResponseDTO(
        status="ok",
        version="2.9.0",
        environment="production",
        storage_backend="POSTGRES",
        gcp_region="europe-north1",
        primary_domain="qrum.ai",
    )
    assert dto.status == "ok"
    assert dto.version == "2.9.0"
    assert dto.environment == "production"
    assert dto.storage_backend == "POSTGRES"
    assert dto.gcp_region == "europe-north1"
    assert dto.primary_domain == "qrum.ai"

    # ISTQB Negative 1: Extra unrecognized field rejected (extra="forbid")
    with pytest.raises(ValidationError):
        HealthCheckResponseDTO.model_validate(
            {
                "status": "ok",
                "version": "2.9.0",
                "environment": "production",
                "storage_backend": "POSTGRES",
                "gcp_region": "europe-north1",
                "primary_domain": "qrum.ai",
                "extra_field": "forbidden",
            }
        )

    # ISTQB Negative 2: Empty version string (min_length=1) or invalid status literal rejected
    with pytest.raises(ValidationError):
        HealthCheckResponseDTO(
            status="ok",
            version="",
            environment="production",
            storage_backend="POSTGRES",
            gcp_region="europe-north1",
            primary_domain="qrum.ai",
        )
    with pytest.raises(ValidationError):
        HealthCheckResponseDTO.model_validate(
            {
                "status": "invalid_status",
                "version": "2.9.0",
                "environment": "production",
                "storage_backend": "POSTGRES",
                "gcp_region": "europe-north1",
                "primary_domain": "qrum.ai",
            }
        )


def test_hook_list_response_strictness() -> None:
    """Verify HookListResponse valid instantiation and ISTQB negative boundaries."""
    dto = HookListResponse(hooks=["hook_1", "hook_2"])
    assert dto.hooks == ["hook_1", "hook_2"]

    # ISTQB Negative 1: Extra field rejected
    with pytest.raises(ValidationError):
        HookListResponse.model_validate({"hooks": ["hook_1"], "extra_field": "fail"})

    # ISTQB Negative 2: Non-string list elements rejected (strict=True)
    with pytest.raises(ValidationError):
        HookListResponse.model_validate({"hooks": [123]})


def test_client_error_payload_strictness() -> None:
    """Verify ClientErrorPayload valid instantiation and ISTQB negative boundaries."""
    dto = ClientErrorPayload(
        session_id="usr_0195f3a0000070018234567890abcdef",
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

    # ISTQB Negative 1: Extra field rejected
    with pytest.raises(ValidationError):
        ClientErrorPayload.model_validate(
            {
                "error_message": "Fatal crash",
                "extra": "fail",
            }
        )

    # ISTQB Negative 2: Missing required error_message rejected
    with pytest.raises(ValidationError):
        ClientErrorPayload.model_validate({"severity": "fatal"})


def test_strictness_config_dtos_strictness() -> None:
    """Verify StrictnessConfigDTO and StrictnessConfigListResponse valid and negative cases."""
    cfg = StrictnessConfigDTO(level=100, localization_key="strictness_high")
    assert cfg.level == 100
    assert cfg.localization_key == "strictness_high"

    resp = StrictnessConfigListResponse(configs=[cfg])
    assert len(resp.configs) == 1

    # ISTQB Negative 1: String coerced to int rejected under strict=True
    with pytest.raises(ValidationError):
        StrictnessConfigDTO.model_validate({"level": "100", "localization_key": "strictness_high"})

    # ISTQB Negative 2: Extra field on list response rejected
    with pytest.raises(ValidationError):
        StrictnessConfigListResponse.model_validate({"configs": [], "extra": True})


def test_system_config_dtos_and_discriminated_union() -> None:
    """Test SystemSettingsDTO and AnySystemConfig discriminated union validation."""
    # 1. SystemSettingsDTO
    settings_dto = SystemSettingsDTO(environment="production", maintenance_mode=True)
    assert settings_dto.type == "system_settings"
    assert settings_dto.environment == "production"
    assert settings_dto.maintenance_mode is True

    # ISTQB Negative 1: Extra forbid
    with pytest.raises(ValidationError) as exc:
        SystemSettingsDTO.model_validate({"type": "system_settings", "unknown": 123})
    assert "extra_forbidden" in str(exc.value) or "Extra inputs are not permitted" in str(exc.value)

    # ISTQB Negative 2: Invalid environment literal
    with pytest.raises(ValidationError):
        SystemSettingsDTO.model_validate({"type": "system_settings", "environment": "staging"})

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
        id="sys_0195f3a0000070018234567890abcdef",
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

    # Discriminated union fails on invalid type discriminator
    with pytest.raises(ValidationError):
        AnySystemConfigAdapter.validate_python({"type": "invalid_type", "id": "sys_0195f3a0000070018234567890abcdef"})

    # 3. SystemConfigUpdateDTO
    update_dto = SystemConfigUpdateDTO(system_settings=settings_dto)
    assert update_dto.system_settings is not None
    assert update_dto.system_settings.maintenance_mode is True

    with pytest.raises(ValidationError):
        SystemConfigUpdateDTO.model_validate({"unknown_section": {}})

    # 4. SystemConfigCreateDTO
    create_dto = SystemConfigCreateDTO(
        type="system_settings",
        content=settings_dto,
    )
    assert create_dto.type == "system_settings"

    # ISTQB Boundary: Empty type string (min_length=1) rejected
    with pytest.raises(ValidationError):
        SystemConfigCreateDTO(type="", content=settings_dto)

    # 5. SystemConfigUpsertDTO
    upsert_dto = SystemConfigUpsertDTO(
        id="sys_0195f3a0000070018234567890abcdef",
        type="system_settings",
        content=settings_dto,
    )
    assert upsert_dto.id == "sys_0195f3a0000070018234567890abcdef"

    with pytest.raises(ValidationError):
        SystemConfigUpsertDTO(type="", content=settings_dto)
