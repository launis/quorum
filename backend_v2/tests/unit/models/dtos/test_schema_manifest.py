"""Unit and ISTQB boundary test suite for GeneratedSchemaManifestDTO."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.schema_manifest import GeneratedSchemaManifestDTO


def test_generated_schema_manifest_default_initialization() -> None:
    """Verifies default initialization sets schemas to empty mapping."""
    manifest = GeneratedSchemaManifestDTO()
    assert manifest.schemas == {}
    assert len(manifest) == 0
    assert list(manifest.keys()) == []
    assert list(manifest.items()) == []
    assert list(manifest.values()) == []


def test_generated_schema_manifest_mapping_interface() -> None:
    """Verifies dictionary-like access (__contains__, __getitem__, __len__, keys, items, values)."""
    schema_a = {"type": "object", "properties": {"score": {"type": "number"}}}
    schema_b = {"type": "object", "properties": {"summary": {"type": "string"}}}
    manifest = GeneratedSchemaManifestDTO(
        schemas={
            "stp_extract_01": schema_a,
            "stp_synthesis_02": schema_b,
        }
    )

    assert len(manifest) == 2
    assert "stp_extract_01" in manifest
    assert "stp_synthesis_02" in manifest
    assert "stp_non_existent" not in manifest

    assert manifest["stp_extract_01"] == schema_a
    assert manifest["stp_synthesis_02"] == schema_b

    assert set(manifest.keys()) == {"stp_extract_01", "stp_synthesis_02"}
    assert len(list(manifest.items())) == 2
    assert len(list(manifest.values())) == 2

    with pytest.raises(KeyError):
        _ = manifest["missing_step"]


def test_generated_schema_manifest_frozen_immutability() -> None:
    """Verifies that GeneratedSchemaManifestDTO rejects in-place attribute mutations."""
    manifest = GeneratedSchemaManifestDTO(schemas={"stp_1": {"type": "object"}})
    with pytest.raises(ValidationError):
        manifest.schemas = {"stp_2": {"type": "string"}}  # type: ignore[misc]


def test_generated_schema_manifest_extra_fields_forbidden() -> None:
    """Negative boundary: Extra fields are strictly rejected under extra='forbid'."""
    with pytest.raises(ValidationError):
        GeneratedSchemaManifestDTO.model_validate({"schemas": {}, "unauthorized_param": "forbidden"})


def test_generated_schema_manifest_serialization_roundtrip() -> None:
    """Verifies full-duplex serialization parity with JSON roundtrip."""
    original = GeneratedSchemaManifestDTO(
        schemas={
            "stp_eval": {
                "title": "AtomEvaluationResult",
                "type": "object",
                "properties": {"score": {"type": "number"}},
                "required": ["score"],
            }
        }
    )
    dumped = original.model_dump(mode="json")
    rehydrated = GeneratedSchemaManifestDTO.model_validate(dumped)
    assert rehydrated == original
    assert rehydrated["stp_eval"] == original["stp_eval"]
