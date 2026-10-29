"""Unit tests for AliasEngine and AliasManifest.

Tests the core aliasing pipeline including serialization boundary
(to_manifest/from_manifest), namespace isolation, and negative Fail-Fast boundaries.
"""

from typing import Annotated, Literal

import pytest
from pydantic import Field, ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.enums import DEFAULT_ALIAS_LITERALS
from backend_v2.utils.alias_engine import AliasEngine, AliasManifest


class TestAliasEngineCore:
    """Tests for core AliasEngine operations."""

    def test_generate_alias_registers_mapping(self) -> None:
        """Verify register creates correct alias and registers in map."""
        engine = AliasEngine()
        alias = engine.register("tda_0195f3a0000070008123456789abcdef", prefix="a")

        assert alias == "a0"
        assert engine.alias_map["a0"] == "tda_0195f3a0000070008123456789abcdef"

    def test_register_idempotent_reverse_lookup(self) -> None:
        """Verify registering the same real_id twice returns the existing alias."""
        engine = AliasEngine()
        first = engine.register("tda_0195f3a0000070008123456789abcdef", prefix="a")
        second = engine.register("tda_0195f3a0000070008123456789abcdef", prefix="a")

        assert first == "a0"
        assert second == "a0"
        assert len(engine.alias_map) == 1

    def test_register_inferred_prefix(self) -> None:
        """Verify register infers the prefix correctly from the real ID."""
        engine = AliasEngine()
        alias1 = engine.register("tda_0195f3a0000070008123456789abcdef")
        alias2 = engine.register("doc_xyz")
        alias3 = engine.register("MX-123")
        alias4 = engine.register("plainid")

        assert alias1 == "tda0"
        assert alias2 == "doc0"
        assert alias3 == "MX-0"
        assert alias4 == "item0"

        assert engine.alias_map["tda0"] == "tda_0195f3a0000070008123456789abcdef"
        assert engine.alias_map["doc0"] == "doc_xyz"
        assert engine.alias_map["MX-0"] == "MX-123"
        assert engine.alias_map["item0"] == "plainid"

    def test_generate_alias_multiple_prefixes_no_collision(self) -> None:
        """Verify different prefixes coexist in the same alias_map without collision."""
        engine = AliasEngine()
        engine.register("tda_0195f3a0000070008123456789abcdef", prefix="a")
        engine.register("tda_0195f3a00000700f8edcba9876543210", prefix="a")
        engine.register("doc_xyz", prefix="src_")
        engine.register("doc_uvw", prefix="src_")

        assert len(engine.alias_map) == 4
        assert engine.alias_map["a0"] == "tda_0195f3a0000070008123456789abcdef"
        assert engine.alias_map["a1"] == "tda_0195f3a00000700f8edcba9876543210"
        assert engine.alias_map["src_0"] == "doc_xyz"
        assert engine.alias_map["src_1"] == "doc_uvw"

    def test_resolve_alias_returns_real_id_and_empty_passthrough(self) -> None:
        """Verify resolve_alias returns the real ID, empty string, or unknown non-prefix string."""
        engine = AliasEngine()
        engine.register("tda_0195f3a0000070008123456789abcdef", prefix="a")
        assert engine.resolve_alias("a0") == "tda_0195f3a0000070008123456789abcdef"
        assert engine.resolve_alias("") == ""
        assert engine.resolve_alias("nonexistent") == "nonexistent"

    def test_resolve_alias_negative_hallucinated_atom_prefix_raises(self) -> None:
        """Verify resolve_alias raises AppException(422) on hallucinated atom alias matching active prefix."""
        engine = AliasEngine()
        engine.register("tda_0195f3a0000070008123456789abcdef", prefix="a")

        with pytest.raises(AppException) as exc_info:
            engine.resolve_alias("a99")
        assert exc_info.value.status_code == 422
        assert exc_info.value.details == {"error_code": ErrorCodes.VALIDATION_FAILED.value}

    def test_resolve_alias_negative_hallucinated_delimited_prefix_raises(self) -> None:
        """Verify resolve_alias raises AppException(422) on hallucinated delimited prefix alias (e.g. DOC-1)."""
        engine = AliasEngine(alias_map={"DOC-0": "doc_0195f3a0000070008123456789abcdef", "custom_key": "val"})

        with pytest.raises(AppException) as exc_info:
            engine.resolve_alias("DOC-1")
        assert exc_info.value.status_code == 422
        assert exc_info.value.details == {"error_code": ErrorCodes.VALIDATION_FAILED.value}


class TestAliasManifest:
    """Tests for AliasManifest serialization boundary."""

    def test_to_manifest_creates_snapshot(self) -> None:
        """Verify to_manifest produces a correct Pydantic snapshot."""
        engine = AliasEngine()
        engine.register("doc_xyz", prefix="doc")
        engine.source_document_aliases.append("doc0")

        manifest = engine.to_manifest()

        assert isinstance(manifest, AliasManifest)
        assert manifest.alias_map == {"doc0": "doc_xyz"}
        assert manifest.source_document_aliases == ["doc0"]

    def test_from_manifest_reconstructs_engine(self) -> None:
        """Verify from_manifest produces a functional AliasEngine."""
        manifest = AliasManifest(
            alias_map={"src_0": "doc_xyz", "src_1": "doc_uvw"},
            source_document_aliases=["src_0", "src_1"],
        )

        engine = AliasEngine.from_manifest(manifest)

        assert engine.alias_map["src_0"] == "doc_xyz"
        assert engine.alias_map["src_1"] == "doc_uvw"
        assert engine.source_document_aliases == ["src_0", "src_1"]

    def test_roundtrip_manifest_preserves_state(self) -> None:
        """Verify to_manifest → from_manifest roundtrip preserves full state."""
        original = AliasEngine()
        original.register("doc_a", prefix="doc")
        original.register("doc_b", prefix="doc")
        original.source_document_aliases = ["doc0", "doc1"]

        manifest = original.to_manifest()
        reconstructed = AliasEngine.from_manifest(manifest)

        assert reconstructed.alias_map == original.alias_map
        assert reconstructed.source_document_aliases == original.source_document_aliases

    def test_manifest_isolation_from_original_engine(self) -> None:
        """Verify manifest creates deep copies, not references."""
        engine = AliasEngine()
        engine.register("doc_a", prefix="doc")

        manifest = engine.to_manifest()

        # Mutating original should not affect manifest
        engine.register("doc_b", prefix="doc")

        assert "doc1" not in manifest.alias_map

    def test_from_manifest_then_add_atoms(self) -> None:
        """Verify upstream source docs and local atom aliases coexist after reconstruction."""
        upstream = AliasEngine()
        upstream.register("doc_xyz", prefix="doc")
        upstream.register("doc_uvw", prefix="doc")
        upstream.source_document_aliases = ["doc0", "doc1"]
        manifest = upstream.to_manifest()

        downstream = AliasEngine.from_manifest(manifest)
        downstream.register("tda_0195f3a0000070008123456789abcdef", prefix="a")
        downstream.register("tda_0195f3a00000700f8edcba9876543210", prefix="a")

        assert len(downstream.alias_map) == 4
        assert downstream.alias_map["doc0"] == "doc_xyz"
        assert downstream.alias_map["doc1"] == "doc_uvw"
        assert downstream.alias_map["a0"] == "tda_0195f3a0000070008123456789abcdef"
        assert downstream.alias_map["a1"] == "tda_0195f3a00000700f8edcba9876543210"

    def test_manifest_serialization_json(self) -> None:
        """Verify manifest serializes cleanly to JSON for step_metadata transport."""
        engine = AliasEngine()
        engine.register("doc_xyz", prefix="doc")
        engine.source_document_aliases.append("doc0")

        manifest = engine.to_manifest()
        json_data = manifest.model_dump(mode="json")

        assert type(json_data) is dict
        assert json_data["alias_map"] == {"doc0": "doc_xyz"}
        assert json_data["source_document_aliases"] == ["doc0"]

        restored = AliasManifest.model_validate(json_data)
        assert restored.alias_map == manifest.alias_map

    def test_manifest_negative_extra_fields_forbidden(self) -> None:
        """Verify AliasManifest rejects extra fields with ValidationError."""
        with pytest.raises(ValidationError):
            AliasManifest.model_validate({"alias_map": {}, "unexpected_field": "banned"})

    def test_manifest_negative_invalid_type_rejected(self) -> None:
        """Verify AliasManifest strict mode rejects non-string alias_map values."""
        with pytest.raises(ValidationError):
            AliasManifest.model_validate({"alias_map": {"a0": 123}})


class TestAliasManifestEdgeCases:
    """Edge case tests for AliasManifest and AliasEngine helpers."""

    def test_empty_manifest(self) -> None:
        """Verify empty manifest creates empty engine."""
        manifest = AliasManifest.model_validate({})
        engine = AliasEngine.from_manifest(manifest)

        assert engine.alias_map == {}
        assert engine.source_document_aliases == []

    def test_empty_engine_to_manifest(self) -> None:
        """Verify empty engine produces valid empty manifest."""
        engine = AliasEngine()
        manifest = engine.to_manifest()

        assert manifest.alias_map == {}
        assert manifest.source_document_aliases == []

    def test_build_quote_ids_literal_includes_dynamic_keys(self) -> None:
        """Verify that dynamic keys are included in the generated Literal type."""
        literal_type = AliasEngine.build_quote_ids_literal(
            None, None, allowed_dynamic_keys=["prior_analysis", "inputs"]
        )
        valid_choices = AliasEngine.extract_literal_values(literal_type)

        assert "inputs" in valid_choices
        assert "prior_analysis" in valid_choices

    def test_build_doc_ids_literal(self) -> None:
        """Test build_doc_ids_literal generation."""
        lit = AliasEngine.build_doc_ids_literal(["doc_1", "doc_2"], allowed_dynamic_keys=["input_x"])
        choices = AliasEngine.extract_literal_values(lit)
        assert "doc_1" in choices
        assert "input_x" in choices

    def test_build_atom_ids_literal(self) -> None:
        """Test build_atom_ids_literal generation."""
        lit = AliasEngine.build_atom_ids_literal(["a0", "a1"], allowed_dynamic_keys=["meta"])
        choices = AliasEngine.extract_literal_values(lit)
        assert "a0" in choices
        assert "meta" in choices

    def test_text_replace_alias(self) -> None:
        """Test text_replace_alias substitution."""
        engine = AliasEngine()
        res = engine.text_replace_alias('id="real_123"', "real_123", "a0")
        assert res == 'id="a0"'
        assert engine.text_replace_alias("", "", "a0") == ""

    def test_hydrate_reasoning_text(self) -> None:
        """Test hydrate_reasoning_text with matching and non-matching aliases."""
        engine = AliasEngine()
        engine.register("tda_0195f3a0000070008123456789abcdef", prefix="a")
        engine.register("tda_0195f3a00000700f8edcba9876543210", prefix="a")
        text = "See atom 'a0' and \"a0\" and `a0` and standalone a0 here."
        hydrated = engine.hydrate_reasoning_text(text)
        assert "tda_0195f3a0000070008123456789abcdef" in hydrated
        assert engine.hydrate_reasoning_text("") == ""

    def test_hydrate_and_filter_aliases(self) -> None:
        """Test hydrate_and_filter_aliases in-place mutations including DEFAULT_ALIAS_LITERALS."""
        engine = AliasEngine()
        engine.register("tda_0195f3a0000070008123456789abcdef", prefix="a")
        default_lit = next(iter(DEFAULT_ALIAS_LITERALS))

        data = {
            "atom_id": "a0",
            "default_scalar": default_lit,
            "source_id": "unknown_alias",
            "sources": ["a0", default_lit, "unknown_source", 123],
            "nested": {
                "atom_id": "a0",
                "other_field": "keep_me",
            },
            "list_of_dicts": [
                {"atom_id": "a0"},
                {"atom_id": "hallucinated_a99"},
            ],
        }

        engine.hydrate_and_filter_aliases(data, {"atom_id", "default_scalar", "source_id", "sources"})
        assert data["atom_id"] == "tda_0195f3a0000070008123456789abcdef"
        assert data["default_scalar"] == default_lit
        assert data["source_id"] is None
        assert data["sources"] == ["tda_0195f3a0000070008123456789abcdef", default_lit, 123]
        assert data["nested"]["atom_id"] == "tda_0195f3a0000070008123456789abcdef"
        assert data["list_of_dicts"][0]["atom_id"] == "tda_0195f3a0000070008123456789abcdef"
        assert data["list_of_dicts"][1]["atom_id"] is None

    def test_is_valid_source_id(self) -> None:
        """Test is_valid_source_id validation checks across all branches."""
        engine = AliasEngine()
        engine.register("doc_abc", prefix="doc")
        default_lit = next(iter(DEFAULT_ALIAS_LITERALS))

        assert engine.is_valid_source_id("doc0", allowed_dynamic_keys=["meta"])
        assert engine.is_valid_source_id(default_lit, allowed_dynamic_keys=[])
        assert engine.is_valid_source_id("meta", allowed_dynamic_keys=["meta"])
        assert engine.is_valid_source_id("mcp_custom_1", allowed_dynamic_keys=[], allowed_mcp_prefixes=["mcp_"])
        assert engine.is_valid_source_id("tavily_search_1", allowed_dynamic_keys=[], allowed_mcp_prefixes=["other_"])
        assert not engine.is_valid_source_id("", allowed_dynamic_keys=[])
        assert not engine.is_valid_source_id("invalid_src", allowed_dynamic_keys=[])

    def test_extract_literal_values_annotated_and_non_literal(self) -> None:
        """Test extract_literal_values on Annotated[Literal[...], ...] and non-literal types."""
        annotated_lit = Annotated[Literal["a0", "a1"], Field(description="Atom alias")]
        assert AliasEngine.extract_literal_values(annotated_lit) == ["a0", "a1"]
        assert AliasEngine.extract_literal_values(str) == []
