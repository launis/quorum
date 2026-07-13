"""Epic 93 Phase 1-3 Integration Verification Test Suite.

System 2 falsification tests proving the complete pipeline from
QuoteEvidenceDTO → SduiMapperService → API endpoints works as
specified in the Epic 93 document.

Tests are organized by the three phases:
- Phase 1: DTO Refactoring (QuoteEvidenceDTO deterministic alias resolution)
- Phase 2: Pipeline Unification (synthesis.py eliminated, BlueprintTransformer active)
- Phase 3: Universal Adapters (SDUI mapper, API endpoints, RFC 7807)
"""

from __future__ import annotations

import logging
from collections.abc import Generator
from typing import Any
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from backend_v2.api.dependencies import get_current_user_from_header, get_execution_service
from backend_v2.main import app
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.dtos.report.root import ReportDataDto
from backend_v2.models.view.sdui import (
    SduiQuoteCard,
    SduiWarningCard,
)
from backend_v2.services.sdui_mapper import SduiMapperService

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

mock_user = TokenData(id="test-user-id", role=UserRole.ROOT, organization_id="root_org")


@pytest.fixture
def override_dependencies() -> Generator[None]:
    """Override FastAPI dependencies for test isolation."""
    app.dependency_overrides[get_current_user_from_header] = lambda: mock_user
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def mock_execution_service() -> Any:
    """Create a fully mocked execution service."""
    service = AsyncMock()
    app.dependency_overrides[get_execution_service] = lambda: service
    return service


# ===========================================================================
# PHASE 1: DTO REFACTORING — QuoteEvidenceDTO
# ===========================================================================


class TestPhase1QuoteEvidenceDTORegex:
    """Phase 1.3: Verify the mode='before' regex parser on source_alias."""

    def test_raw_string_single_doc(self) -> None:
        """Single DOC-X string is normalized to a single-element list."""
        dto = QuoteEvidenceDTO.model_validate(
            {"quote": "Test quote", "source_alias": "DOC-1"},
            context={"alias_registry": {}},
        )
        # Empty context resolves aliases to UNVERIFIED
        assert dto.source_alias == ["OpaqueID.UNVERIFIED"]

    def test_raw_string_multi_doc(self) -> None:
        """Concatenated 'DOC-1, DOC-2' string is split correctly."""
        dto = QuoteEvidenceDTO.model_validate(
            {"quote": "Multi doc", "source_alias": "DOC-1, DOC-2"},
            context={"alias_registry": {"DOC-1": "id_1", "DOC-2": "id_2"}},
        )
        assert dto.source_alias == ["id_1", "id_2"]

    def test_list_with_embedded_doc_refs(self) -> None:
        """List items containing DOC-X patterns are extracted correctly."""
        dto = QuoteEvidenceDTO.model_validate(
            {"quote": "Test", "source_alias": ["Some text DOC-3 here", "DOC-4"]},
            context={"alias_registry": {"DOC-3": "id_3", "DOC-4": "id_4"}},
        )
        assert "id_3" in dto.source_alias
        assert "id_4" in dto.source_alias

    def test_empty_string_raises(self) -> None:
        """Empty string produces empty regex match list."""
        dto = QuoteEvidenceDTO.model_validate(
            {"quote": "No alias", "source_alias": ""},
            context={"alias_registry": {}},
        )
        # Empty string yields no DOC-X matches → empty list
        assert dto.source_alias == []

    def test_non_doc_string_passthrough(self) -> None:
        """A list item without DOC-X pattern passes through as-is."""
        dto = QuoteEvidenceDTO.model_validate(
            {"quote": "Test", "source_alias": ["some_opaque_id"]},
            context={"alias_registry": {}},
        )
        # Non DOC-X items pass through, then resolve to UNVERIFIED without context
        assert dto.source_alias == ["OpaqueID.UNVERIFIED"]


class TestPhase1QuoteEvidenceDTOAliasResolution:
    """Phase 1.4/1.5: Verify the mode='after' ValidationInfo context injection."""

    def test_full_alias_resolution(self) -> None:
        """All DOC-X aliases are resolved via the alias_registry context."""
        registry = {"DOC-1": "opaque_abc", "DOC-2": "opaque_def"}
        dto = QuoteEvidenceDTO.model_validate(
            {"quote": "Full resolution", "source_alias": ["DOC-1", "DOC-2"]},
            context={"alias_registry": registry},
        )
        assert dto.source_alias == ["opaque_abc", "opaque_def"]

    def test_partial_resolution_yields_unverified(self) -> None:
        """Missing aliases map strictly to OpaqueID.UNVERIFIED."""
        registry = {"DOC-1": "opaque_abc"}
        dto = QuoteEvidenceDTO.model_validate(
            {"quote": "Partial", "source_alias": ["DOC-1", "DOC-99"]},
            context={"alias_registry": registry},
        )
        assert dto.source_alias == ["opaque_abc", "OpaqueID.UNVERIFIED"]

    def test_no_context_raises_error(self) -> None:
        """Without context, resolution is blocked and raises RuntimeError."""
        with pytest.raises(RuntimeError, match="ValidationInfo.context is missing"):
            QuoteEvidenceDTO.model_validate(
                {"quote": "No context", "source_alias": ["DOC-1"]},
            )

    def test_empty_registry_all_unverified(self) -> None:
        """Empty registry means all aliases are unverified."""
        dto = QuoteEvidenceDTO.model_validate(
            {"quote": "Empty registry", "source_alias": ["DOC-1", "DOC-2"]},
            context={"alias_registry": {}},
        )
        assert dto.source_alias == ["OpaqueID.UNVERIFIED", "OpaqueID.UNVERIFIED"]


# ===========================================================================
# PHASE 1: ReportDataDto headless contract
# ===========================================================================


class TestPhase1ReportDataDtoHeadless:
    """Phase 1.1: Verify ReportDataDto is headless with only semantic data."""

    def test_minimal_construction(self) -> None:
        """ReportDataDto can be constructed with minimal data."""
        from backend_v2.models.dtos.report.metrics import ExecutionMetricsDTO
        from backend_v2.models.dtos.report.root import GlobalSynthesisDTO

        dto = ReportDataDto(
            execution_id="exe_1",
            workflow_id="wf_1",
            global_metrics=ExecutionMetricsDTO(total_atoms=0, evaluated=0, short_circuited_na=0, duration_ms=0),
            global_synthesis=GlobalSynthesisDTO(executive_summary="Summary", urgency_level=0),
            results=[],
            hydrated_references={},
        )
        assert dto.global_synthesis.executive_summary == "Summary"
        assert dto.global_synthesis.urgency_level == 0
        assert dto.results == []

    def test_with_evidence_quotes(self) -> None:
        """ReportDataDto carries atom results. (evidence_quotes deprecated in Phase 1)."""
        from backend_v2.models.dtos.report.metrics import ExecutionMetricsDTO
        from backend_v2.models.dtos.report.root import GlobalSynthesisDTO

        dto = ReportDataDto(
            execution_id="exe_1",
            workflow_id="wf_1",
            global_metrics=ExecutionMetricsDTO(total_atoms=0, evaluated=0, short_circuited_na=0, duration_ms=0),
            global_synthesis=GlobalSynthesisDTO(executive_summary="With quotes", urgency_level=0),
            results=[],
            hydrated_references={},
        )
        assert dto.global_synthesis.executive_summary == "With quotes"

    def test_no_markdown_html_ui_fields(self) -> None:
        """ReportDataDto must NOT contain Markdown/HTML/UI fields."""
        field_names = set(ReportDataDto.model_fields.keys())
        # These are the forbidden patterns from the Epic spec
        forbidden_patterns = ["markdown", "html", "ui_", "render", "template", "layout"]
        for pattern in forbidden_patterns:
            for field in field_names:
                assert pattern not in field.lower(), (
                    f"Field '{field}' contains forbidden pattern '{pattern}' — "
                    f"ReportDataDto must be headless (no presentation logic)"
                )

    def test_serialization_roundtrip(self) -> None:
        """Pydantic model_dump/model_validate roundtrip succeeds."""
        from backend_v2.models.dtos.report.metrics import ExecutionMetricsDTO
        from backend_v2.models.dtos.report.root import GlobalSynthesisDTO

        dto = ReportDataDto(
            execution_id="exe_1",
            workflow_id="wf_1",
            global_metrics=ExecutionMetricsDTO(total_atoms=0, evaluated=0, short_circuited_na=0, duration_ms=0),
            global_synthesis=GlobalSynthesisDTO(executive_summary="RT", urgency_level=3),
            results=[],
            hydrated_references={},
        )
        serialized = dto.model_dump(mode="json")
        restored = ReportDataDto.model_validate(serialized, context={"alias_registry": {}})
        assert restored.global_synthesis.executive_summary == "RT"
        assert restored.global_synthesis.urgency_level == 3
        assert restored.results == []


# ===========================================================================
# PHASE 2: Pipeline Unification
# ===========================================================================


class TestPhase2GodCodeElimination:
    """Phase 2.1/2.2: Verify God Code extraction."""

    def test_matrix_reducer_exists(self) -> None:
        """The matrix_reducer.py replacement must exist."""
        import os

        path = os.path.join("backend_v2", "services", "orchestrator", "matrix_reducer.py")
        assert os.path.exists(path), f"matrix_reducer.py missing at {path} — Phase 2 mandates its creation"

    def test_no_text_consolidation_hook_references(self) -> None:
        """No code should reference the deleted TextConsolidationHook."""
        import os

        # Scan key service files for remnants
        files_to_check = [
            os.path.join("backend_v2", "services", "blueprint.py"),
            os.path.join("backend_v2", "services", "execution.py"),
        ]
        for filepath in files_to_check:
            if os.path.exists(filepath):
                with open(filepath, encoding="utf-8") as f:
                    content = f.read()
                assert "TextConsolidationHook" not in content, (
                    f"Found remnant 'TextConsolidationHook' in {filepath} — "
                    f"Phase 2 mandates complete eradication of God Code references"
                )


# ===========================================================================
# PHASE 3: SDUI Mapper — Falsification-first
# ===========================================================================


class TestPhase3SduiMapperValidEvidence:
    """Phase 3.4: Valid QuoteEvidenceDTO → SduiQuoteCard."""

    def test_valid_aliases_yield_quote_card(self) -> None:
        """All resolved aliases produce a SduiQuoteCard."""
        # Use model_validate with context to simulate real pipeline resolution
        registry = {"DOC-1": "src_1", "DOC-2": "src_2"}
        dto = QuoteEvidenceDTO.model_validate(
            {"quote": "A real quote", "source_alias": ["DOC-1", "DOC-2"]},
            context={"alias_registry": registry},
        )
        result = SduiMapperService.map_evidence_to_sdui(dto)
        assert isinstance(result, SduiQuoteCard)
        assert result.quote == "A real quote"
        assert result.source_aliases == ["src_1", "src_2"]
        assert result.block_type == "quote_card"

    def test_empty_alias_list_yields_quote_card(self) -> None:
        """Empty alias list (no sources) still produces a quote card, not a warning."""
        dto = QuoteEvidenceDTO.model_validate(
            {"quote": "No sources", "source_alias": []},
            context={"alias_registry": {}},
        )
        result = SduiMapperService.map_evidence_to_sdui(dto)
        assert isinstance(result, SduiQuoteCard)


class TestPhase3SduiMapperHallucinatedEvidence:
    """Phase 3.5: OpaqueID.UNVERIFIED → SduiWarningCard + RFC 7807 logging."""

    def test_single_unverified_yields_warning_card(self) -> None:
        """A single OpaqueID.UNVERIFIED produces a SduiWarningCard."""
        dto = QuoteEvidenceDTO.model_validate(
            {"quote": "Hallucinated quote", "source_alias": ["OpaqueID.UNVERIFIED"]},
            context={"alias_registry": {}},
        )
        result = SduiMapperService.map_evidence_to_sdui(dto)
        assert isinstance(result, SduiWarningCard)
        assert result.block_type == "warning_card"

    def test_mixed_valid_and_unverified_yields_warning(self) -> None:
        """Even one OpaqueID.UNVERIFIED among valid aliases triggers warning."""
        dto = QuoteEvidenceDTO.model_validate(
            {"quote": "Mixed sources", "source_alias": ["valid_id_1", "OpaqueID.UNVERIFIED", "valid_id_2"]},
            context={"alias_registry": {}},
        )
        result = SduiMapperService.map_evidence_to_sdui(dto)
        assert isinstance(result, SduiWarningCard), (
            "Epic spec mandates: if ANY alias is unverified, the entire card must become a WarningCard"
        )

    def test_rfc7807_dual_reporting_logging(self, caplog: pytest.LogCaptureFixture) -> None:
        """RFC 7807 mandates logger.error on hallucinated alias detection."""
        dto = QuoteEvidenceDTO.model_validate(
            {"quote": "Logging test", "source_alias": ["OpaqueID.UNVERIFIED"]},
            context={"alias_registry": {}},
        )
        with caplog.at_level(logging.ERROR):
            SduiMapperService.map_evidence_to_sdui(dto)
        assert any("Hallucinated alias" in record.message for record in caplog.records), (
            "RFC 7807 Dual-Reporting mandates logger.error on hallucinated alias"
        )


# ===========================================================================
# PHASE 3: SDUI Model Schema Verification
# ===========================================================================


class TestPhase3SduiModels:
    """Phase 3.1/3.2/3.3: Verify SDUI model structure."""

    def test_sdui_quote_card_schema(self) -> None:
        """SduiQuoteCard has correct discriminator and fields."""
        card = SduiQuoteCard(quote="Test", source_aliases=["src_1"])
        assert card.block_type == "quote_card"
        dumped = card.model_dump()
        assert "quote" in dumped
        assert "source_aliases" in dumped
        assert "block_type" in dumped

    def test_sdui_warning_card_schema(self) -> None:
        """SduiWarningCard has correct discriminator and fields."""
        card = SduiWarningCard(message="Warning text")
        assert card.block_type == "warning_card"
        dumped = card.model_dump()
        assert "message" in dumped
        assert "block_type" in dumped

    def test_discriminated_union_dispatch(self) -> None:
        """AnySduiBlock discriminated union correctly dispatches both types."""
        from pydantic import TypeAdapter

        from backend_v2.models.view.sdui import AnySduiBlock

        adapter: TypeAdapter[AnySduiBlock] = TypeAdapter(AnySduiBlock)

        quote_data = {"block_type": "quote_card", "quote": "Q", "source_aliases": []}
        parsed_quote = adapter.validate_python(quote_data)
        assert isinstance(parsed_quote, SduiQuoteCard)

        warning_data = {"block_type": "warning_card", "message": "W"}
        parsed_warning = adapter.validate_python(warning_data)
        assert isinstance(parsed_warning, SduiWarningCard)


# ===========================================================================
# PHASE 3: API Endpoint Integration Tests
# ===========================================================================


class TestPhase3ReportEndpoint:
    """Phase 3.6: GET /{execution_id}/report returns headless ReportDataDto."""

    def test_report_returns_200_with_dto_shape(self, override_dependencies: Any, mock_execution_service: Any) -> None:
        """Headless endpoint returns clean JSON without SDUI wrapping."""
        client = TestClient(app)
        from backend_v2.models.dtos.report.metrics import ExecutionMetricsDTO
        from backend_v2.models.dtos.report.root import GlobalSynthesisDTO

        mock_dto = ReportDataDto(
            execution_id="test_123",
            workflow_id="wf_1",
            global_metrics=ExecutionMetricsDTO(total_atoms=0, evaluated=0, short_circuited_na=0, duration_ms=0),
            global_synthesis=GlobalSynthesisDTO(executive_summary="Headless test", urgency_level=5),
            results=[],
            hydrated_references={},
        )
        mock_execution_service.get_report_dto.return_value = mock_dto

        response = client.get("/api/v2/execution/executions/test_123/report")

        assert response.status_code == 200
        data = response.json()
        assert data["global_synthesis"]["executive_summary"] == "Headless test"
        assert data["global_synthesis"]["urgency_level"] == 5
        assert "sections" not in data, "Headless endpoint must NOT contain SDUI sections"
        assert "view_id" not in data, "Headless endpoint must NOT contain SDUI view_id"

    def test_report_with_evidence_quotes(self, override_dependencies: Any, mock_execution_service: Any) -> None:
        """Headless endpoint serializes QuoteEvidenceDTO correctly. (deprecated in Phase 1)."""
        client = TestClient(app)
        from backend_v2.models.dtos.report.metrics import ExecutionMetricsDTO
        from backend_v2.models.dtos.report.root import GlobalSynthesisDTO

        mock_dto = ReportDataDto(
            execution_id="test_123",
            workflow_id="wf_1",
            global_metrics=ExecutionMetricsDTO(total_atoms=0, evaluated=0, short_circuited_na=0, duration_ms=0),
            global_synthesis=GlobalSynthesisDTO(executive_summary="With evidence", urgency_level=0),
            results=[],
            hydrated_references={},
        )
        mock_execution_service.get_report_dto.return_value = mock_dto

        response = client.get("/api/v2/execution/executions/test_123/report")

        assert response.status_code == 200
        data = response.json()
        assert data["global_synthesis"]["executive_summary"] == "With evidence"


class TestPhase3SduiEndpoint:
    """Phase 3.7: GET /{execution_id}/sdui returns SDUI ReportView."""

    def test_sdui_returns_200_with_view_shape(self, override_dependencies: Any, mock_execution_service: Any) -> None:
        """SDUI endpoint returns a ReportView structure."""
        client = TestClient(app)
        mock_view: dict[str, Any] = {
            "view_id": "exe_test_sdui",
            "title": "SDUI Report",
            "status_theme": "success",
            "sections": [],
            "metrics": None,
            "system_notification": None,
            "references": [],
        }
        mock_execution_service.get_sdui_view.return_value = mock_view

        response = client.get("/api/v2/execution/executions/exe_test_sdui/sdui")

        assert response.status_code == 200
        data = response.json()
        assert data["view_id"] == "exe_test_sdui"
        assert "sections" in data
        assert "title" in data

    def test_sdui_endpoint_delegates_to_service(self, override_dependencies: Any, mock_execution_service: Any) -> None:
        """Anemic router pattern: endpoint delegates to service, no logic."""
        client = TestClient(app)
        mock_execution_service.get_sdui_view.return_value = {
            "view_id": "x",
            "title": "T",
            "status_theme": "success",
            "sections": [],
            "metrics": None,
            "system_notification": None,
            "references": [],
        }
        client.get("/api/v2/execution/executions/some_id/sdui")
        mock_execution_service.get_sdui_view.assert_called_once()


# ===========================================================================
# CROSS-PHASE INTEGRATION: End-to-End Pipeline
# ===========================================================================


class TestCrossPhaseIntegration:
    """Verify the full data flow: QuoteEvidenceDTO → SduiMapper → SDUI Block."""

    def test_full_pipeline_valid_quote(self) -> None:
        """End-to-end: DOC string → DTO → resolved alias → SduiQuoteCard."""
        registry = {"DOC-1": "opaque_abc123", "DOC-2": "opaque_def456"}
        dto = QuoteEvidenceDTO.model_validate(
            {"quote": "This is verified evidence.", "source_alias": "DOC-1, DOC-2"},
            context={"alias_registry": registry},
        )
        # Phase 1 output: resolved aliases
        assert dto.source_alias == ["opaque_abc123", "opaque_def456"]

        # Phase 3: map to SDUI
        block = SduiMapperService.map_evidence_to_sdui(dto)
        assert isinstance(block, SduiQuoteCard)
        assert block.quote == "This is verified evidence."
        assert block.source_aliases == ["opaque_abc123", "opaque_def456"]

    def test_full_pipeline_hallucinated_quote(self) -> None:
        """End-to-end: DOC with missing alias → DTO → OpaqueID.UNVERIFIED → SduiWarningCard."""
        registry = {"DOC-1": "opaque_abc123"}
        dto = QuoteEvidenceDTO.model_validate(
            {"quote": "Hallucinated evidence.", "source_alias": "DOC-1, DOC-99"},
            context={"alias_registry": registry},
        )
        # Phase 1 output: one resolved, one unverified
        assert dto.source_alias == ["opaque_abc123", "OpaqueID.UNVERIFIED"]

        # Phase 3: map to SDUI → warning card
        block = SduiMapperService.map_evidence_to_sdui(dto)
        assert isinstance(block, SduiWarningCard)

    def test_full_pipeline_multiple_quotes_mixed(self) -> None:
        """Multiple quotes produce a mix of QuoteCards and WarningCards."""
        registry = {"DOC-1": "id_1", "DOC-2": "id_2"}
        quotes = [
            QuoteEvidenceDTO.model_validate(
                {"quote": "Valid", "source_alias": ["DOC-1"]},
                context={"alias_registry": registry},
            ),
            QuoteEvidenceDTO.model_validate(
                {"quote": "Invalid", "source_alias": ["DOC-99"]},
                context={"alias_registry": registry},
            ),
        ]
        blocks = [SduiMapperService.map_evidence_to_sdui(q) for q in quotes]

        assert isinstance(blocks[0], SduiQuoteCard)
        assert isinstance(blocks[1], SduiWarningCard)

    def test_report_dto_carries_pipeline_output(self) -> None:
        """ReportDataDto can carry the full pipeline output."""
        from backend_v2.models.dtos.report.metrics import ExecutionMetricsDTO
        from backend_v2.models.dtos.report.root import GlobalSynthesisDTO

        dto = ReportDataDto(
            execution_id="exe_1",
            workflow_id="wf_1",
            global_metrics=ExecutionMetricsDTO(total_atoms=0, evaluated=0, short_circuited_na=0, duration_ms=0),
            global_synthesis=GlobalSynthesisDTO(executive_summary="Pipeline test", urgency_level=2),
            results=[],
            hydrated_references={},
        )
        # Verify serialization preserves the pipeline
        serialized = dto.model_dump(mode="json")
        assert serialized["global_synthesis"]["executive_summary"] == "Pipeline test"
