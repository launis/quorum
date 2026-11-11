"""Unit tests for System domain Data Transfer Objects."""

import pytest
from pydantic import ValidationError

from backend_v2.models.domain.system_config import (
    ModelProfile,
    ProviderExtraParamsDTO,
    SystemConfigMCPGateways,
    SystemConfigModelRegistry,
)
from backend_v2.models.dtos.hook_delta import StepContextMetadataDTO
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
)
from backend_v2.models.dtos.trace import TraceEventMetadataDTO
from backend_v2.models.enums import CognitiveTier, LLMProvider


def test_safety_setting_dto_strictness_invalid() -> None:
    """Verify SafetySettingDTO valid instantiation and ISTQB negative boundaries."""
    dto = SafetySettingDTO(
        category="HARM_CATEGORY_HATE_SPEECH",
        threshold="BLOCK_LOW_AND_ABOVE",
    )
    assert dto.category == "HARM_CATEGORY_HATE_SPEECH"
    assert dto.threshold == "BLOCK_LOW_AND_ABOVE"

    with pytest.raises(ValidationError):
        SafetySettingDTO.model_validate_json(
            '{"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_LOW_AND_ABOVE", "extra": "forbidden"}'
        )

    with pytest.raises(ValidationError):
        SafetySettingDTO.model_validate_json('{"category": 123, "threshold": "BLOCK_LOW_AND_ABOVE"}')


def test_health_check_response_dto_strictness_invalid() -> None:
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

    with pytest.raises(ValidationError):
        HealthCheckResponseDTO.model_validate_json(
            '{"status": "ok", "version": "2.9.0", "environment": "production", '
            '"storage_backend": "POSTGRES", "gcp_region": "europe-north1", '
            '"primary_domain": "qrum.ai", "extra_field": "forbidden"}'
        )

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
        HealthCheckResponseDTO.model_validate_json(
            '{"status": "invalid_status", "version": "2.9.0", "environment": "production", '
            '"storage_backend": "POSTGRES", "gcp_region": "europe-north1", "primary_domain": "qrum.ai"}'
        )


def test_hook_list_response_strictness_invalid() -> None:
    """Verify HookListResponse valid instantiation and ISTQB negative boundaries."""
    dto = HookListResponse(hooks=["hook_1", "hook_2"])
    assert dto.hooks == ["hook_1", "hook_2"]

    with pytest.raises(ValidationError):
        HookListResponse.model_validate_json('{"hooks": ["hook_1"], "extra_field": "fail"}')

    with pytest.raises(ValidationError):
        HookListResponse.model_validate_json('{"hooks": [123]}')


def test_client_error_payload_strictness_invalid() -> None:
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

    with pytest.raises(ValidationError):
        ClientErrorPayload.model_validate_json('{"error_message": "Fatal crash", "extra": "fail"}')

    with pytest.raises(ValidationError):
        ClientErrorPayload.model_validate_json('{"severity": "fatal"}')


def test_strictness_config_dtos_strictness_invalid() -> None:
    """Verify StrictnessConfigDTO and StrictnessConfigListResponse valid and negative cases."""
    cfg = StrictnessConfigDTO(level=100, localization_key="strictness_high")
    assert cfg.level == 100
    assert cfg.localization_key == "strictness_high"

    resp = StrictnessConfigListResponse(configs=[cfg])
    assert len(resp.configs) == 1

    with pytest.raises(ValidationError):
        StrictnessConfigDTO.model_validate_json('{"level": "100", "localization_key": "strictness_high"}')

    with pytest.raises(ValidationError):
        StrictnessConfigListResponse.model_validate_json('{"configs": [], "extra": true}')


def test_system_config_dtos_and_discriminated_union_invalid() -> None:
    """Verify AnySystemConfig discriminated union and SystemConfig CRUD DTOs without SystemSettingsDTO."""
    dummy_profile = ModelProfile(
        model_name="gemini-2.5-flash",
        provider="ai_studio",
        tpm_limit=1000,
        rpm_limit=10,
        temperature=1.0,
        max_tokens=2048,
        allowed_tools=[],
        additional_params=ProviderExtraParamsDTO(),
    )
    model_reg = SystemConfigModelRegistry(
        id="sys_0195f3a0000070018234567890abcdef",
        name="Test Registry",
        type="model_registry",
        default_provider=LLMProvider.AI_STUDIO,
        tier_definitions={
            CognitiveTier.FAST: dummy_profile,
            CognitiveTier.BALANCED: dummy_profile,
            CognitiveTier.DEEP: dummy_profile,
            CognitiveTier.REASONING: dummy_profile,
        },
    )
    mcp_gw = SystemConfigMCPGateways(
        id="sys_0195f3a0000070018234567890abcde0",
        name="Test MCP Gateway",
        slug="test_mcp_gateway",
        type="mcp_gateways",
        tools=[],
    )
    validated_union = AnySystemConfigAdapter.validate_python(model_reg.model_dump(mode="python"))
    assert isinstance(validated_union, SystemConfigModelRegistry)
    assert validated_union.type == "model_registry"

    validated_mcp = AnySystemConfigAdapter.validate_python(mcp_gw.model_dump(mode="python"))
    assert isinstance(validated_mcp, SystemConfigMCPGateways)

    with pytest.raises(ValidationError):
        AnySystemConfigAdapter.validate_json(
            '{"type": "system_settings", "id": "sys_0195f3a0000070018234567890abcdef"}'
        )

    update_dto = SystemConfigUpdateDTO(model_registry=model_reg, mcp_gateways=mcp_gw)
    assert update_dto.model_registry is not None
    assert update_dto.mcp_gateways is not None

    with pytest.raises(ValidationError):
        SystemConfigUpdateDTO.model_validate_json('{"system_settings": {}}')

    create_dto = SystemConfigCreateDTO(
        type="mcp_gateways",
        content=mcp_gw,
    )
    assert create_dto.type == "mcp_gateways"

    with pytest.raises(ValidationError):
        SystemConfigCreateDTO(type="", content=mcp_gw)

    upsert_dto = SystemConfigUpsertDTO(
        id="sys_0195f3a0000070018234567890abcde0",
        type="mcp_gateways",
        content=mcp_gw,
    )
    assert upsert_dto.id == "sys_0195f3a0000070018234567890abcde0"

    with pytest.raises(ValidationError):
        SystemConfigUpsertDTO(type="", content=mcp_gw)


def test_closed_dtos_reject_unrecognized_extra_keys_invalid() -> None:
    """Verify HealthCheckResponseDTO, TraceEventMetadataDTO, and StepContextMetadataDTO forbid extra keys."""
    valid_step_meta = StepContextMetadataDTO(gvars={"language": "fi"}, doc_aliases=["doc_0"], dag_results={})
    assert valid_step_meta.gvars["language"] == "fi"

    with pytest.raises(ValidationError) as exc_health:
        HealthCheckResponseDTO.model_validate_json(
            '{"status": "ok", "version": "2.9.0", "environment": "production", '
            '"storage_backend": "POSTGRES", "gcp_region": "europe-north1", '
            '"primary_domain": "qrum.ai", "undeclared_extra": "rejected"}'
        )
    assert "extra_forbidden" in str(exc_health.value)

    with pytest.raises(ValidationError) as exc_trace:
        TraceEventMetadataDTO.model_validate_json('{"latency_ms": 12.0, "undeclared_extra": "rejected"}')
    assert "extra_forbidden" in str(exc_trace.value)

    with pytest.raises(ValidationError) as exc_step:
        StepContextMetadataDTO.model_validate_json('{"gvars": {"language": "fi"}, "undeclared_extra": "rejected"}')
    assert "extra_forbidden" in str(exc_step.value)
