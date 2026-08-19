"""Regression test for metric_mappings retention in OutputProfileResponseDTO.

Validates that OutputProfileResponseDTO does NOT exclude metric_mappings when serialized,
preventing Flutter and API clients from wiping metric_mappings on profile updates.
"""

from typing import Any

from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.dtos.output_profile import (
    OutputProfileCreateDTO,
    OutputProfileResponseDTO,
)
from backend_v2.models.v2_core import I18nText


def test_output_profile_response_dto_serializes_metric_mappings() -> None:
    """OutputProfileResponseDTO must serialize metric_mappings in JSON output.

    Previously, `metric_mappings` had `exclude=True` in OutputProfileResponseDTO,
    which stripped the dictionary from all API responses. When the Flutter UI
    saved the profile, it sent back an empty map, wiping out variance/authenticity
    translation keys in the database and causing execution rendering crashes.
    """
    db_profile_dict: dict[str, Any] = {
        "id": "prf_5d6e7f8091a2b3c4",
        "slug": "test_profile",
        "workflow_id": "wf_9d68c573802341db",
        "name": {"default_locale": "fi", "translations": {"fi": "Testi", "en": "Test"}},
        "layouts": [],
        "metric_mappings": {
            "variance_mechanical": {
                "default_locale": "fi",
                "translations": {"fi": "Mekaaninen", "en": "Mechanical"},
            },
            "variance_cognitive": {
                "default_locale": "fi",
                "translations": {"fi": "Kognitiivinen", "en": "Cognitive"},
            },
        },
    }

    # 1. Hydrate into OutputProfileResponseDTO
    dto = OutputProfileResponseDTO.model_validate(db_profile_dict, strict=False)

    # 2. Serialize to JSON dict (simulating FastAPI response serialization)
    serialized = dto.model_dump(mode="json")

    # 3. Assert metric_mappings is NOT stripped
    assert "metric_mappings" in serialized, (
        "metric_mappings was excluded from serialized OutputProfileResponseDTO JSON response!"
    )
    assert "variance_mechanical" in serialized["metric_mappings"], (
        "variance_mechanical key is missing from serialized metric_mappings!"
    )


def test_output_profile_roundtrip_preserves_metric_mappings() -> None:
    """Simulates GET -> Flutter Edit -> PUT roundtrip to ensure metric_mappings is preserved."""
    db_profile = OutputProfile(
        id="prf_5d6e7f8091a2b3c4",
        slug="test_profile",
        workflow_id="wf_9d68c573802341db",
        name=I18nText(default_locale="fi", translations={"fi": "Testi", "en": "Test"}),
        target_block_order=[],
        metric_mappings={
            "variance_mechanical": I18nText(
                default_locale="fi",
                translations={"fi": "Mekaaninen", "en": "Mechanical"},
            ),
        },
    )

    # 1. API GET response serialization
    response_dto = OutputProfileResponseDTO.model_validate(db_profile.model_dump(mode="json"), strict=False)
    api_get_json = response_dto.model_dump(mode="json")

    # 2. Flutter client parses api_get_json and sends back PUT payload
    # If api_get_json dropped metric_mappings, Flutter would have sent {}
    put_payload = api_get_json

    # 3. Backend receives PUT payload in OutputProfileCreateDTO
    create_dto = OutputProfileCreateDTO.model_validate(put_payload)
    saved_profile = OutputProfile.model_validate(create_dto.model_dump())

    # 4. Verify metric_mappings is preserved
    assert "variance_mechanical" in saved_profile.metric_mappings
