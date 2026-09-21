"""Unit and ISTQB boundary test suite for InjectedTheoryManifestDTO."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.theory_manifest import InjectedTheoryManifestDTO


def test_injected_theory_manifest_default_initialization() -> None:
    """Verifies default initialization sets theories to empty dict."""
    manifest = InjectedTheoryManifestDTO()
    assert manifest.theories == {}
    assert isinstance(manifest.theories, dict)


def test_injected_theory_manifest_with_valid_data() -> None:
    """Verifies proper construction and field access with populated theories."""
    theories_map = {
        "blk_theory_01": "Kahneman System 1 and System 2 cognitive processing theory.",
        "blk_theory_02": "Bloom Taxonomy cognitive complexity levels.",
    }
    manifest = InjectedTheoryManifestDTO(theories=theories_map)
    assert len(manifest.theories) == 2
    assert manifest.theories["blk_theory_01"] == theories_map["blk_theory_01"]
    assert manifest.theories["blk_theory_02"] == theories_map["blk_theory_02"]


def test_injected_theory_manifest_frozen_immutability() -> None:
    """Verifies that InjectedTheoryManifestDTO rejects in-place attribute mutations."""
    manifest = InjectedTheoryManifestDTO(theories={"th_1": "Theory text"})
    with pytest.raises(ValidationError):
        manifest.theories = {"th_2": "New theory"}  # type: ignore[misc]


def test_injected_theory_manifest_extra_fields_forbidden() -> None:
    """Negative boundary: Extra fields are strictly rejected under extra='forbid'."""
    with pytest.raises(ValidationError):
        InjectedTheoryManifestDTO.model_validate({"theories": {}, "unexpected_extra": 123})


def test_injected_theory_manifest_type_strictness() -> None:
    """Negative boundary: Non-string values or invalid mappings trigger ValidationError."""
    with pytest.raises(ValidationError):
        InjectedTheoryManifestDTO.model_validate({"theories": "not_a_dict"})

    with pytest.raises(ValidationError):
        InjectedTheoryManifestDTO.model_validate({"theories": {"th_1": 12345}})


def test_injected_theory_manifest_serialization_roundtrip() -> None:
    """Verifies full-duplex serialization parity with JSON roundtrip."""
    original = InjectedTheoryManifestDTO(
        theories={"blk_abc123": "Localized Finnish theory snippet: Käyttäytymistieteellinen viitekehys."}
    )
    dumped = original.model_dump(mode="json")
    rehydrated = InjectedTheoryManifestDTO.model_validate(dumped)
    assert rehydrated == original
    assert rehydrated.theories["blk_abc123"] == original.theories["blk_abc123"]
