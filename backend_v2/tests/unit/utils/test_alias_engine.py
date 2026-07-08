"""Unit tests for AliasEngine and AliasManifest.

Tests the core aliasing pipeline including serialization boundary
(to_manifest/from_manifest) and namespace isolation.
"""

from backend_v2.utils.alias_engine import AliasEngine, AliasManifest


class TestAliasEngineCore:
    """Tests for core AliasEngine operations."""

    def test_generate_alias_registers_mapping(self) -> None:
        """Verify generate_alias creates correct alias and registers in map."""
        engine = AliasEngine()
        alias = engine.register("tda_abc123", prefix="a")

        assert alias == "a0"
        assert engine.alias_map["a0"] == "tda_abc123"

    def test_register_inferred_prefix(self) -> None:
        """Verify register infers the prefix correctly from the real ID."""
        engine = AliasEngine()
        alias1 = engine.register("tda_abc123")
        alias2 = engine.register("doc_xyz")
        alias3 = engine.register("MX-123")
        alias4 = engine.register("plainid")

        assert alias1 == "tda0"
        assert alias2 == "doc0"
        assert alias3 == "MX-0"
        assert alias4 == "item0"

        assert engine.alias_map["tda0"] == "tda_abc123"
        assert engine.alias_map["doc0"] == "doc_xyz"
        assert engine.alias_map["MX-0"] == "MX-123"
        assert engine.alias_map["item0"] == "plainid"

    def test_generate_alias_multiple_prefixes_no_collision(self) -> None:
        """Verify different prefixes coexist in the same alias_map without collision."""
        engine = AliasEngine()
        engine.register("tda_abc", prefix="a")
        engine.register("tda_def", prefix="a")
        engine.register("doc_xyz", prefix="src_")
        engine.register("doc_uvw", prefix="src_")

        assert len(engine.alias_map) == 4
        assert engine.alias_map["a0"] == "tda_abc"
        assert engine.alias_map["a1"] == "tda_def"
        assert engine.alias_map["src_0"] == "doc_xyz"
        assert engine.alias_map["src_1"] == "doc_uvw"

    def test_resolve_alias_returns_real_id(self) -> None:
        """Verify resolve_alias returns the correct real ID or raises/returns original."""
        engine = AliasEngine()
        engine.register("tda_abc", prefix="a")
        assert engine.resolve_alias("a0") == "tda_abc"
        # Should return original string if not matching a known prefix
        assert engine.resolve_alias("nonexistent") == "nonexistent"
        # Should raise AppException for hallucinated alias (matches 'a' prefix but not found)
        import pytest

        from backend_v2.exceptions import AppException

        with pytest.raises(AppException) as exc_info:
            engine.resolve_alias("a99")
        assert exc_info.value.status_code == 422

    def test_hydrate_dict_list_replaces_aliases(self) -> None:
        """Verify hydrate_dict_list replaces aliases in-place."""
        engine = AliasEngine()
        engine.register("tda_real_1", prefix="a")
        engine.register("tda_real_2", prefix="a")

        items = [{"atom_id": "a0", "score": 5}, {"atom_id": "a1", "score": 3}]
        count = engine.hydrate_dict_list(items, field_name="atom_id")

        assert count == 2
        assert items[0]["atom_id"] == "tda_real_1"
        assert items[1]["atom_id"] == "tda_real_2"

    def test_hydrate_dict_list_skips_unknown_aliases(self) -> None:
        """Verify unknown aliases are left untouched during hydration."""
        engine = AliasEngine()
        engine.register("tda_real", prefix="a")

        items = [{"atom_id": "a0"}, {"atom_id": "unknown_alias"}]
        count = engine.hydrate_dict_list(items, field_name="atom_id")

        assert count == 1
        assert items[1]["atom_id"] == "unknown_alias"


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

        assert "doc_1" not in manifest.alias_map

    def test_from_manifest_then_add_atoms(self) -> None:
        """Verify the core use case: upstream source docs + local atom aliases unified."""
        # Phase 2: llm.py exports source doc aliases
        upstream = AliasEngine()
        upstream.register("doc_xyz", prefix="doc")
        upstream.register("doc_uvw", prefix="doc")
        upstream.source_document_aliases = ["doc0", "doc1"]
        manifest = upstream.to_manifest()

        # Phase 3: chunk_worker.py reconstructs and adds atom aliases
        downstream = AliasEngine.from_manifest(manifest)
        downstream.register("tda_abc", prefix="a")
        downstream.register("tda_def", prefix="a")

        # Both namespaces coexist in val_context
        assert len(downstream.alias_map) == 4
        assert downstream.alias_map["doc0"] == "doc_xyz"
        assert downstream.alias_map["doc1"] == "doc_uvw"
        assert downstream.alias_map["a0"] == "tda_abc"
        assert downstream.alias_map["a1"] == "tda_def"

    def test_manifest_serialization_json(self) -> None:
        """Verify manifest serializes cleanly to JSON for step_metadata transport."""
        engine = AliasEngine()
        engine.register("doc_xyz", prefix="doc")
        engine.source_document_aliases.append("doc0")

        manifest = engine.to_manifest()
        json_data = manifest.model_dump(mode="json")

        assert isinstance(json_data, dict)
        assert json_data["alias_map"] == {"doc0": "doc_xyz"}
        assert json_data["source_document_aliases"] == ["doc0"]

        # Verify deserialization roundtrip
        restored = AliasManifest.model_validate(json_data)
        assert restored.alias_map == manifest.alias_map


class TestAliasManifestEdgeCases:
    """Edge case tests for AliasManifest."""

    def test_empty_manifest(self) -> None:
        """Verify empty manifest creates empty engine."""
        manifest = AliasManifest()
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

        assert "inputs" in valid_choices, "'inputs' missing from QuoteIdsLiteral choices!"
        assert "prior_analysis" in valid_choices, "'prior_analysis' missing from QuoteIdsLiteral choices!"
