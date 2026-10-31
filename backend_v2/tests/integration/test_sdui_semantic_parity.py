"""Cross-Domain SDUI Semantic Parity & Heterogeneous Payload Integration Test Suite.

Verifies 1:1 semantic, structural, and typographic parity across Backend Python SDUI DTOs,
Jinja2 PDF templates, and Flutter Freezed models and widgets, alongside ISTQB Equivalence
Partitioning across SynthesisPayloadCompressor and SduiMapperService.
"""

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel, ConfigDict, TypeAdapter, ValidationError

from backend_v2.exceptions import AppException
from backend_v2.models.core_base import I18nText, generate_opaque_id, generate_uuid7
from backend_v2.models.domain.synthesis import DistilledEvaluation
from backend_v2.models.domain.system_config import MCPAuditTrace
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.atom_evaluation import ReasoningStepDTO, ReducedAtomDTO
from backend_v2.models.dtos.atom_result import AtomResultDTO, HydratedAtomDTO
from backend_v2.models.dtos.causal_discovery import (
    AntiFluffAuditDTO,
    CausalEdgeDTO,
    CausalNodeDTO,
    CausalRootCauseDiagnosisDTO,
    FairScoringBreakdownDTO,
)
from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO, ScorecardAtomDTO
from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.dtos.step_output import StepPayloadValue
from backend_v2.models.enums import (
    CausalRootCauseType,
    EntityPrefix,
    ExecutionStatus,
    SDUIComponentType,
    VisualIntent,
)
from backend_v2.models.view.sdui import (
    AnySduiBlock,
    MarkdownBlock,
    ParagraphBlock,
    SduiCausalGraphBlock,
    SduiMatrixSummaryTableBlock,
    SduiMatrixTableBlock,
    SduiMetrics1DBlock,
    SduiNACard,
)
from backend_v2.services.orchestrator.synthesis_payload_compressor import (
    SynthesisPayloadCompressor,
)
from backend_v2.services.pdf_generator import PdfReportService
from backend_v2.services.sdui.sdui_mapper_service import SduiMapperService


class SduiSemanticTokenDTO(BaseModel):
    """Pydantic V2 DTO representing a semantic text token extracted from Flutter widget rendering."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)
    text: str
    is_bold: bool = False
    is_italic: bool = False
    is_header: bool = False


class WorkflowFactory(ModelFactory[Workflow]):
    """Polyfactory generator for Workflow domain entities."""

    __model__ = Workflow
    __set_as_default_factory_for_type__ = True


class ReasoningStepDTOFactory(ModelFactory[ReasoningStepDTO]):
    """Polyfactory generator for ReasoningStepDTO instances."""

    __model__ = ReasoningStepDTO
    __set_as_default_factory_for_type__ = True


class I18nTextFactory(ModelFactory[I18nText]):
    """Polyfactory generator for I18nText localized strings."""

    __model__ = I18nText
    __set_as_default_factory_for_type__ = True

    @classmethod
    def translations(cls) -> dict[str, str]:
        """Return deterministic English and Finnish translation strings."""
        return {"en": "English test", "fi": "Finnish test"}


class ReportDataDTOFactory(ModelFactory[ReportDataDTO]):
    """Polyfactory generator for ReportDataDTO report payloads."""

    __model__ = ReportDataDTO

    @classmethod
    def results(cls) -> list[AtomResultDTO]:
        """Return empty default atom results list."""
        return []

    @classmethod
    def hydrated_references(cls) -> dict[str, HydratedAtomDTO]:
        """Return empty default hydrated references map."""
        return {}

    @classmethod
    def mcp_tool_audit(cls) -> list[MCPAuditTrace]:
        """Return empty default MCP audit trace list."""
        return []

    @classmethod
    def matrix_visible_columns(cls) -> list[str]:
        """Return default visible columns for matrix tables."""
        return ["label", "raw_score", "distribution", "row_explanation"]


class ScorecardAtomDTOFactory(ModelFactory[ScorecardAtomDTO]):
    """Polyfactory generator for ScorecardAtomDTO instances."""

    __model__ = ScorecardAtomDTO
    visual_intent: VisualIntent = VisualIntent.SUCCESS
    __set_as_default_factory_for_type__ = True

    @classmethod
    def exact_quotes(cls) -> list[QuoteEvidenceDTO]:
        """Return empty default quote evidence list."""
        return []


class MatrixScorecardRowDTOFactory(ModelFactory[MatrixScorecardRowDTO]):
    """Polyfactory generator for MatrixScorecardRowDTO instances."""

    __model__ = MatrixScorecardRowDTO
    score: float = 5.0
    scale_min: float = 0.0
    scale_max: float = 10.0
    normalized_score: float | None = None
    true_atoms: int | None = None
    total_atoms: int | None = None
    cited_web_citation: str | None = None
    cited_source_id: str | None = None
    cited_text_quote: str | None = None
    coaching: str | None = None
    falsification: str | None = None
    missing_context: str | None = None
    remediation_steps: str | None = None
    emotional_sentiment: str | None = None
    theory_link: str | None = None
    description: str | None = None
    semantic_reasoning: str | None = None
    score_display_label: str | None = "5.0 / 10.0"
    risk_flag: bool | None = None
    context_target: str | None = None
    context_target_label: I18nText | None = None
    __set_as_default_factory_for_type__ = True

    @classmethod
    def inner_sdui_blocks(cls) -> list[AnySduiBlock]:
        """Return empty default inner SDUI blocks list."""
        return []


class QuoteEvidenceDTOFactory(ModelFactory[QuoteEvidenceDTO]):
    """Polyfactory generator for QuoteEvidenceDTO instances."""

    __model__ = QuoteEvidenceDTO
    quote: str = "Test quote"
    is_verified: bool = True
    __set_as_default_factory_for_type__ = True

    @classmethod
    def verified_source_ids(cls) -> list[str]:
        """Return default verified source ID list."""
        return ["src_0"]

    @classmethod
    def unverified_aliases(cls) -> list[str]:
        """Return empty default unverified aliases list."""
        return []


def _clean_pdf_markdown(text: str) -> str:
    """Strip Markdown inline formatting markers for normalized text comparison.

    Args:
        text: Raw Markdown string extracted from PDF via pymupdf4llm.

    Returns:
        Cleaned plain-text string.
    """
    return (
        text.replace("<br>", " ")
        .replace("<br/>", " ")
        .replace("<br />", " ")
        .replace("**", "")
        .replace("*", "")
        .replace("_", "")
        .replace("### ", "")
        .replace("## ", "")
        .replace("# ", "")
    )


def _verify_semantic_token_parity(token: SduiSemanticTokenDTO, target_md: str, target_clean_md: str) -> None:
    """Assert that a semantic token extracted from Flutter is present and styled identically in PDF Markdown.

    Args:
        token: Semantic token extracted from Flutter widget tree.
        target_md: Normalized Markdown text with formatting preserved.
        target_clean_md: Cleaned plain text stripped of Markdown markers.

    Raises:
        AssertionError: If the token text or typographic styling is missing from the PDF output.
    """
    norm_token = re.sub(r"\s+", " ", token.text).strip()
    clean_token_str = token.text.replace("*", "").replace("_", "").strip()
    clean_token_str = re.sub(r"\s+", " ", clean_token_str).strip()
    norm_md = re.sub(r"\s+", " ", target_clean_md)
    if clean_token_str:
        assert clean_token_str in norm_md, (
            f"Token '{clean_token_str}' missing from PDF output! PDF Context: {target_clean_md[:300]}"
        )

    core_token = re.sub(r"^[\s*_]+|[\s*_]+$", "", norm_token)
    if not core_token:
        return

    if token.is_bold:
        is_in_bold = bool(
            re.search(r"\*\*[^\n|]*?" + re.escape(core_token) + r"[^\n|]*?\*\*", target_md)
            or re.search(r"__[^\n|]*?" + re.escape(core_token) + r"[^\n|]*?__", target_md)
            or re.search(r"^#{1,6}\s+.*" + re.escape(core_token), target_md, re.MULTILINE)
            or re.search(r"^\|.*" + re.escape(core_token) + r".*\|\s*\n\|[\s\-:|]+\|", target_md, re.MULTILINE)
        )
        assert is_in_bold, f"Bold token '{norm_token}' not styled as bold/heading/table-header in PDF Markdown!"

    if token.is_italic:
        is_in_italic = bool(
            re.search(r"(?<!_)_[^\n|_]*?" + re.escape(core_token) + r"[^\n|_]*?_(?!_)", target_md)
            or re.search(r"(?<!\*)\*[^\n|*]*?" + re.escape(core_token) + r"[^\n|*]*?\*(?!\*)", target_md)
        )
        assert is_in_italic, f"Italic token '{norm_token}' not styled as italic in PDF Markdown!"

    if token.is_header:
        is_in_header = bool(re.search(r"^#{1,6}\s+.*" + re.escape(core_token), target_md, re.MULTILINE))
        assert is_in_header, f"Header token '{norm_token}' not styled as header in PDF Markdown!"


@pytest.mark.asyncio
async def test_sdui_semantic_parity() -> None:
    """Phase 3: Automated Pytest E2E Orchestrator for SDUI Parity."""
    # Step 1: Verify flutter binary
    flutter_path = shutil.which("flutter")
    if not flutter_path:
        pytest.skip("Flutter SDK not found")

    # Step 2: Generate temp paths using RFC 9562 UUIDv7 SSOT
    temp_dir = Path(tempfile.gettempdir())
    run_id = generate_uuid7()
    golden_path = temp_dir / f"sdui_golden_{run_id}.json"
    dump_path = temp_dir / f"sdui_dump_{run_id}.json"
    pdf_path: Path | None = None

    try:
        # Generate dynamic SDUI mock using Polyfactory
        dto = ReportDataDTOFactory.build()
        dto = dto.model_copy(
            update={
                "profile_name": I18nText(translations={"en": "English test"}),
                "profile_description": None,
                "custom_preface_md": None,
                "user_name": None,
                "scoring_engine_name": None,
                "org_name": None,
            }
        )  # Clear random dicts and explicitly mock profile_name to prevent Jinja crashes and ensure parity

        new_layouts: list[AnySduiBlock] = [
            MarkdownBlock(text="# English test"),
            ParagraphBlock(
                text="Standard unstyled parity observation narrative text.",
                exact_quotes=[],
                citations=[],
            ),
        ]
        for layout in dto.inner_sdui_blocks:
            match layout:
                case SduiMatrixTableBlock() as table:
                    axes = list(table.axes)
                    new_layouts.append(
                        table.model_copy(
                            update={
                                "axes": axes,
                                "matrix_visible_columns": ["label", "raw_score"],
                                "matrix_column_labels": {
                                    "label": I18nText(translations={"en": "Dimension"}),
                                    "raw_score": I18nText(translations={"en": "Raw Score"}),
                                },
                                "extension_labels": {},
                            }
                        )
                    )
                case SduiMetrics1DBlock() as metrics:
                    new_layouts.append(metrics.model_copy(update={"title": None}))
                case MarkdownBlock() | ParagraphBlock():
                    new_layouts.append(layout.model_copy(update={"citations": []}))
                case _:
                    # Note: Filtered out of dynamic polyfactory run to prevent unrendered random fixture divergences;
                    # comprehensive rendering of all 19 blocks is verified deterministically in
                    # test_sdui_template_parity.py.
                    continue

        # Add deterministic authorized contextual override block to verify semantic parity
        override_atom = ScorecardAtomDTOFactory.build(
            atom_id="atm_parity_override",
            level=1,
            level_name="Foundation Level",
            claim_label="Parity Override Claim",
            exact_quotes=[],
            internal_logic_en=ReasoningStepDTO(
                step_1_identify_premise="Premise",
                step_2_scan_source="Source",
                step_3_evaluate_anti_patterns="AntiPatterns",
                step_4_final_conclusion="Conclusion",
            ),
            status=ExecutionStatus.PASSED,
            semantic_reasoning="Parity cognitive override observation text",
            contextual_override=True,
            chart_display_label="Parity Override",
            visual_intent=VisualIntent.WARNING,
        )
        override_axis = MatrixScorecardRowDTOFactory.build(
            block_id="axis_parity_override",
            name="Parity Strategic Leadership",
            label_i18n=I18nText(translations={"en": "Parity Strategic Leadership"}),
            row_explanation="Parity leadership explanation.",
            score=8.5,
            scale_min=0.0,
            scale_max=10.0,
            score_display_label="8.5 / 10.0",
            is_evaluative=True,
            allow_contextual_override=True,
            level_names={"1": "Foundation Level"},
            level_breakdown={"1": "1/1"},
            evaluated_atoms=[override_atom],
            context_target=None,
            context_target_label=None,
        )
        parity_matrix_block = SduiMatrixTableBlock(
            title=I18nText(translations={"en": "Parity Matrix Table"}),
            matrix_visible_columns=["label", "raw_score", "quotes"],
            matrix_column_labels={
                "label": I18nText(translations={"en": "Dimension"}),
                "raw_score": I18nText(translations={"en": "Raw Score"}),
                "quotes": I18nText(translations={"en": "Evidence"}),
            },
            axes=[override_axis],
            short_circuited_by_claims=[],
            falsified_warrant_claims=[],
        )
        new_layouts.append(parity_matrix_block)

        dto = dto.model_copy(update={"inner_sdui_blocks": new_layouts})

        golden_path.write_text(dto.model_dump_json(exclude_none=True), encoding="utf-8")

        # Step 3: Run Flutter tests
        cmd = [
            flutter_path,
            "test",
            "test/features/execution/sdui_semantic_parity_test.dart",
            f"--dart-define=GOLDEN_PATH={golden_path}",
            f"--dart-define=DUMP_PATH={dump_path}",
        ]

        flutter_cwd = Path.cwd() / "client_app_v2"
        result = subprocess.run(cmd, cwd=str(flutter_cwd), capture_output=True, text=True, encoding="utf-8")
        assert result.returncode == 0, f"Flutter test failed: {result.stdout}\n{result.stderr}"

        pdf_service = PdfReportService()
        pdf_bytes = await pdf_service.generate_execution_pdf("mock_exec_id", report_dto=dto, locale="en")

        pdf_path = temp_dir / f"sdui_pdf_{run_id}.pdf"
        pdf_path.write_bytes(pdf_bytes)

        # Step 5: Extract PDF text
        import pymupdf4llm

        pymupdf4llm.use_layout(True)
        try:
            md_text = pymupdf4llm.to_markdown(str(pdf_path))
        finally:
            pymupdf4llm.use_layout(False)

        # Step 6: Compare
        flutter_tokens = TypeAdapter(list[SduiSemanticTokenDTO]).validate_json(dump_path.read_text(encoding="utf-8"))
        assert len(flutter_tokens) > 0, "No semantic tokens extracted from Flutter!"

        cleaned_md = _clean_pdf_markdown(md_text)
        # Stitch adjacent identical markdown formatting tags across <br> or \n to allow multiline span matching
        stitched_md = re.sub(r"([*_]{1,2})\s*(?:<br\s*/?>|\n)\s*\1", " ", md_text)
        norm_md_text = re.sub(r"<br\s*/?>", " ", stitched_md)

        for token in flutter_tokens:
            _verify_semantic_token_parity(token, norm_md_text, cleaned_md)

        # Verify authorized contextual override semantic parity between Flutter and PDF
        expected_override_token = "Parity Override Claim: Parity cognitive override observation text"
        assert expected_override_token in cleaned_md, (
            f"Contextual override text '{expected_override_token}' missing from PDF output! PDF Context: {cleaned_md}"
        )
        assert any("Parity Override Claim" in t.text for t in flutter_tokens) and any(
            "Parity cognitive override observation text" in t.text for t in flutter_tokens
        ), f"Contextual override text '{expected_override_token}' missing from Flutter extracted tokens!"

        # ISTQB Negative Boundary Partitions (4 distinct scenarios with collision-free candidate filtering):
        # 1. Non-existent token:
        with pytest.raises(AssertionError):
            _verify_semantic_token_parity(
                SduiSemanticTokenDTO(text="NON_EXISTENT_PARITY_TOKEN_XYZ"),
                norm_md_text,
                cleaned_md,
            )

        # Find collision-free candidate unstyled token
        candidate_token: SduiSemanticTokenDTO | None = None
        for t in flutter_tokens:
            if not t.is_bold and not t.is_italic and not t.is_header:
                core_cand = re.sub(r"^[\s*_]+|[\s*_]+$", "", t.text).strip()
                if len(core_cand) < 3:
                    continue
                # Ensure the candidate does not match bold/header/italic patterns in norm_md_text
                is_cand_bold = bool(
                    re.search(r"\*\*[^\n|]*?" + re.escape(core_cand) + r"[^\n|]*?\*\*", norm_md_text)
                    or re.search(r"__[^\n|]*?" + re.escape(core_cand) + r"[^\n|]*?__", norm_md_text)
                    or re.search(r"^#{1,6}\s+.*" + re.escape(core_cand), norm_md_text, re.MULTILINE)
                    or re.search(
                        r"^\|.*" + re.escape(core_cand) + r".*\|\s*\n\|[\s\-:|]+\|", norm_md_text, re.MULTILINE
                    )
                )
                is_cand_italic = bool(
                    re.search(r"(?<!_)_[^\n|_]*?" + re.escape(core_cand) + r"[^\n|_]*?_(?!_)", norm_md_text)
                    or re.search(r"(?<!\*)\*[^\n|*]*?" + re.escape(core_cand) + r"[^\n|*]*?\*(?!\*)", norm_md_text)
                )
                is_cand_header = bool(re.search(r"^#{1,6}\s+.*" + re.escape(core_cand), norm_md_text, re.MULTILINE))
                if not is_cand_bold and not is_cand_header and not is_cand_italic:
                    candidate_token = t
                    break

        assert candidate_token is not None, "No collision-free candidate token found for negative partitions!"

        # 2. Unstyled text mutated to bold:
        with pytest.raises(AssertionError):
            _verify_semantic_token_parity(
                candidate_token.model_copy(update={"is_bold": True}),
                norm_md_text,
                cleaned_md,
            )

        # 3. Body text mutated to header:
        with pytest.raises(AssertionError):
            _verify_semantic_token_parity(
                candidate_token.model_copy(update={"is_header": True}),
                norm_md_text,
                cleaned_md,
            )

        # 4. Unstyled text mutated to italic:
        with pytest.raises(AssertionError):
            _verify_semantic_token_parity(
                candidate_token.model_copy(update={"is_italic": True}),
                norm_md_text,
                cleaned_md,
            )

    finally:
        golden_path.unlink(missing_ok=True)
        dump_path.unlink(missing_ok=True)
        if pdf_path:
            pdf_path.unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_sdui_semantic_parity_short_circuit_and_toulmin_fields_match_across_python_jinja_dart() -> None:
    """Positive: Verify 100% parity for short_circuited_by_claims and falsified_warrant_claims across Python, Jinja2 PDF, and Dart Freezed."""
    # Phase 4, Step 4.1: Cross-domain semantic parity for short_circuited_by_claims and falsified_warrant_claims
    flutter_path = shutil.which("flutter")
    if not flutter_path:
        pytest.skip("Flutter SDK not found")

    temp_dir = Path(tempfile.gettempdir())
    run_id = generate_uuid7()
    golden_path = temp_dir / f"sdui_lineage_golden_{run_id}.json"
    dump_path = temp_dir / f"sdui_lineage_dump_{run_id}.json"
    pdf_path: Path | None = None

    matrix_short_circuit_claim = "Matrix Prerequisite Financial Gate Short-Circuited"
    matrix_falsified_claim = "Matrix Warrant Rebutted By Cashflow Variance Evidence"
    causal_block_short_circuit_claim = "Causal Graph Prerequisite Gate Blocked"
    causal_block_falsified_claim = "Causal Graph Toulmin Warrant Falsified By Audit Counter-Evidence"
    node_short_circuit_claim = "Node Prerequisite Short-Circuited By Upstream Root Cause"
    node_falsified_claim = "Node Warrant Rebutted By Empirical Discrepancy"

    try:
        axis_row = MatrixScorecardRowDTOFactory.build(
            block_id=generate_opaque_id(EntityPrefix.PROMPT_BLOCK),
            name="Topological Governance Axis",
            label_i18n=I18nText(translations={"en": "Topological Governance Axis"}),
            row_explanation="Synthesized topological deficit explanation for governance axis.",
            score=4.0,
            scale_min=0.0,
            scale_max=10.0,
            score_display_label="4.0 / 10.0",
            is_evaluative=True,
            allow_contextual_override=False,
            level_names={"1": "Foundation Level"},
            level_breakdown={"1": "0/1"},
            evaluated_atoms=[],
            context_target=None,
            context_target_label=None,
        )

        matrix_block = SduiMatrixSummaryTableBlock(
            title=I18nText(translations={"en": "Topological Matrix Summary"}),
            matrix_visible_columns=["label", "raw_score", "row_explanation"],
            matrix_column_labels={
                "label": I18nText(translations={"en": "Dimension"}),
                "raw_score": I18nText(translations={"en": "Raw Score"}),
                "row_explanation": I18nText(translations={"en": "Explanation"}),
            },
            axes=[axis_row],
            short_circuited_by_claims=[matrix_short_circuit_claim],
            falsified_warrant_claims=[matrix_falsified_claim],
        )

        root_node_id = generate_opaque_id(EntityPrefix.TDA)
        child_node_id = generate_opaque_id(EntityPrefix.TDA)
        causal_block = SduiCausalGraphBlock(
            critical_path_nodes=[
                CausalNodeDTO(
                    node_id=root_node_id,
                    claim="Root Governance Control Deficit",
                    status=ExecutionStatus.FAILED,
                    blame_parent_ids=[],
                    dependent_child_ids=[child_node_id],
                    short_circuited_by_claims=[],
                    falsified_warrant_claims=[],
                ),
                CausalNodeDTO(
                    node_id=child_node_id,
                    claim="Downstream Compliance Verification Claim",
                    status=ExecutionStatus.N_A,
                    blame_parent_ids=[root_node_id],
                    dependent_child_ids=[],
                    short_circuited_by_claims=[node_short_circuit_claim],
                    falsified_warrant_claims=[node_falsified_claim],
                ),
            ],
            critical_edges=[
                CausalEdgeDTO(
                    source_id=root_node_id,
                    target_id=child_node_id,
                    reasoning="Root control deficit directly blocks downstream compliance verification.",
                )
            ],
            root_cause_diagnoses=[
                CausalRootCauseDiagnosisDTO(
                    failing_node_id=child_node_id,
                    root_cause_parent_id=root_node_id,
                    paragraph_ref="P1",
                    explanation="Downstream compliance blocked by root governance failure.",
                    penalty_points=2.0,
                    root_cause_type=CausalRootCauseType.NODE_FAILURE,
                    root_cause_claim="Root Governance Control Deficit",
                    failing_node_claim="Downstream Compliance Verification Claim",
                )
            ],
            anti_fluff_audit=AntiFluffAuditDTO(
                isolated_concept_count=0,
                cycle_detected=False,
                unsupported_claims_count=1,
                logical_cohesion_score=0.85,
                detected_hollow_terms=[],
            ),
            prescriptive_remediations=[],
            fair_scoring=FairScoringBreakdownDTO(
                independent_error_count=1,
                cascading_fault_count=1,
                raw_penalty_points=4.0,
                deduplicated_penalty_points=2.0,
                dampened_savings_points=2.0,
            ),
            intact_claims_count=0,
            total_claims_count=2,
            summary=I18nText(translations={"en": "Causal Topological Graph Summary"}),
            short_circuited_by_claims=[causal_block_short_circuit_claim],
            falsified_warrant_claims=[causal_block_falsified_claim],
        )

        # Verify Python SDUI DTO serialization keys and values
        dumped_matrix = matrix_block.model_dump(mode="json")
        assert dumped_matrix["short_circuited_by_claims"] == [matrix_short_circuit_claim]
        assert dumped_matrix["falsified_warrant_claims"] == [matrix_falsified_claim]

        dumped_causal = causal_block.model_dump(mode="json")
        assert dumped_causal["short_circuited_by_claims"] == [causal_block_short_circuit_claim]
        assert dumped_causal["falsified_warrant_claims"] == [causal_block_falsified_claim]
        assert dumped_causal["critical_path_nodes"][1]["short_circuited_by_claims"] == [node_short_circuit_claim]
        assert dumped_causal["critical_path_nodes"][1]["falsified_warrant_claims"] == [node_falsified_claim]

        # Build ReportDataDTO containing both matrix_block and causal_block for SduiMapperService and PDF verification
        dto_with_causal = ReportDataDTOFactory.build().model_copy(
            update={
                "execution_id": generate_opaque_id(EntityPrefix.EXECUTION),
                "profile_name": I18nText(translations={"en": "Topological Parity Report"}),
                "profile_description": None,
                "custom_preface_md": None,
                "user_name": None,
                "scoring_engine_name": None,
                "org_name": None,
                "short_circuited_by_claims": [matrix_short_circuit_claim, causal_block_short_circuit_claim],
                "falsified_warrant_claims": [matrix_falsified_claim, causal_block_falsified_claim],
                "inner_sdui_blocks": [
                    MarkdownBlock(text="# Topological Parity Report"),
                    matrix_block,
                    causal_block,
                ],
            }
        )

        # Verify SduiMapperService anchors short-circuit and Toulmin lineage inline with zero SduiNACard orphans
        mapper = SduiMapperService()
        mapped_view = mapper.map_report_to_sdui(dto_with_causal, execution_id=dto_with_causal.execution_id, lang="en")
        assert not any(isinstance(b, SduiNACard) for b in mapped_view.inner_sdui_blocks)
        mapped_matrix_blocks = [b for b in mapped_view.inner_sdui_blocks if isinstance(b, SduiMatrixTableBlock)]
        mapped_causal_blocks = [b for b in mapped_view.inner_sdui_blocks if isinstance(b, SduiCausalGraphBlock)]
        assert len(mapped_matrix_blocks) == 1
        assert len(mapped_causal_blocks) == 1
        assert matrix_short_circuit_claim in mapped_matrix_blocks[0].short_circuited_by_claims
        assert matrix_falsified_claim in mapped_matrix_blocks[0].falsified_warrant_claims
        assert causal_block_short_circuit_claim in mapped_causal_blocks[0].short_circuited_by_claims
        assert causal_block_falsified_claim in mapped_causal_blocks[0].falsified_warrant_claims

        # Build tripartite parity DTO (MarkdownBlock + SduiMatrixSummaryTableBlock) for 1:1 Flutter <-> PDF token verification
        dto = dto_with_causal.model_copy(
            update={
                "inner_sdui_blocks": [
                    MarkdownBlock(text="# Topological Parity Report"),
                    matrix_block,
                ],
            }
        )

        # Write golden JSON and run Flutter Freezed + Widget semantic parity test
        golden_path.write_text(dto.model_dump_json(exclude_none=True), encoding="utf-8")
        cmd = [
            flutter_path,
            "test",
            "test/features/execution/sdui_semantic_parity_test.dart",
            f"--dart-define=GOLDEN_PATH={golden_path}",
            f"--dart-define=DUMP_PATH={dump_path}",
        ]
        flutter_cwd = Path.cwd() / "client_app_v2"
        result = subprocess.run(cmd, cwd=str(flutter_cwd), capture_output=True, text=True, encoding="utf-8")
        assert result.returncode == 0, f"Flutter lineage parity test failed: {result.stdout}\n{result.stderr}"

        # Render Jinja2 HTML & PDF via PdfReportService for both matrix_block and causal_block
        pdf_service = PdfReportService()
        rendered_html = await pdf_service.generate_execution_html(
            dto_with_causal.execution_id, report_dto=dto_with_causal, locale="en"
        )
        for expected_html_claim in (
            matrix_short_circuit_claim,
            matrix_falsified_claim,
            causal_block_short_circuit_claim,
            causal_block_falsified_claim,
        ):
            assert expected_html_claim in rendered_html, (
                f"Lineage claim '{expected_html_claim}' missing from Jinja2 HTML output!"
            )

        pdf_bytes = await pdf_service.generate_execution_pdf(
            dto_with_causal.execution_id, report_dto=dto_with_causal, locale="en"
        )
        pdf_path = temp_dir / f"sdui_lineage_pdf_{run_id}.pdf"
        pdf_path.write_bytes(pdf_bytes)

        import pymupdf4llm

        pymupdf4llm.use_layout(True)
        try:
            md_text = pymupdf4llm.to_markdown(str(pdf_path))
        finally:
            pymupdf4llm.use_layout(False)

        flutter_tokens = TypeAdapter(list[SduiSemanticTokenDTO]).validate_json(dump_path.read_text(encoding="utf-8"))
        cleaned_md = _clean_pdf_markdown(md_text)
        stitched_md = re.sub(r"([*_]{1,2})\s*(?:<br\s*/?>|\n)\s*\1", " ", md_text)
        norm_md_text = re.sub(r"<br\s*/?>", " ", stitched_md)

        for token in flutter_tokens:
            _verify_semantic_token_parity(token, norm_md_text, cleaned_md)

        for expected_pdf_claim in (
            matrix_short_circuit_claim,
            matrix_falsified_claim,
            causal_block_short_circuit_claim,
            causal_block_falsified_claim,
        ):
            assert expected_pdf_claim in cleaned_md, (
                f"Lineage claim '{expected_pdf_claim}' missing from Jinja2 PDF output!"
            )

        for expected_flutter_claim in (
            matrix_short_circuit_claim,
            matrix_falsified_claim,
        ):
            assert any(expected_flutter_claim in t.text for t in flutter_tokens), (
                f"Lineage claim '{expected_flutter_claim}' missing from Flutter rendered tokens!"
            )

    finally:
        golden_path.unlink(missing_ok=True)
        dump_path.unlink(missing_ok=True)
        if pdf_path:
            pdf_path.unlink(missing_ok=True)


def test_sdui_semantic_parity_missing_template_binding_fails_fast() -> None:
    """Negative: Verify simulated unrendered SDUI field on SduiMatrixSummaryTableBlock raises AssertionError."""
    # Phase 4, Step 4.1: Negative test contract for missing template binding on SduiMatrixSummaryTableBlock
    matrix_block = SduiMatrixSummaryTableBlock(
        title=I18nText(translations={"en": "Matrix Block"}),
        matrix_visible_columns=["label", "raw_score"],
        matrix_column_labels={
            "label": I18nText(translations={"en": "Dimension"}),
            "raw_score": I18nText(translations={"en": "Score"}),
        },
        axes=[],
        short_circuited_by_claims=["Unrendered Short Circuit Claim Token 404"],
        falsified_warrant_claims=["Unrendered Toulmin Warrant Claim Token 404"],
    )
    simulated_pdf_markdown = "# Matrix Block\n\n| Dimension | Score |\n| --- | --- |\n"
    cleaned_simulated_md = _clean_pdf_markdown(simulated_pdf_markdown)

    with pytest.raises(AssertionError, match="Unrendered Short Circuit Claim Token 404"):
        _verify_semantic_token_parity(
            SduiSemanticTokenDTO(text=matrix_block.short_circuited_by_claims[0]),
            simulated_pdf_markdown,
            cleaned_simulated_md,
        )

    with pytest.raises(AssertionError, match="Unrendered Toulmin Warrant Claim Token 404"):
        _verify_semantic_token_parity(
            SduiSemanticTokenDTO(text=matrix_block.falsified_warrant_claims[0]),
            simulated_pdf_markdown,
            cleaned_simulated_md,
        )

    # Boundary/Negative Pydantic strict validation on SduiMatrixSummaryTableBlock
    with pytest.raises(ValidationError):
        SduiMatrixSummaryTableBlock.model_validate(
            {
                "block_type": "matrix_summary",
                "axes": [],
                "short_circuited_by_claims": "not_a_list",
            }
        )


def test_sdui_semantic_parity_invalid_token_dto_rejected_negative() -> None:
    """Negative: Verify that SduiSemanticTokenDTO, MCPAuditTrace, and SduiMapperService reject malformed payloads."""
    with pytest.raises(ValidationError):
        SduiSemanticTokenDTO.model_validate_json('{"text": "valid", "extra_field": "forbidden"}')

    with pytest.raises(ValidationError):
        MCPAuditTrace.model_validate_json(
            '{"step_id": "stp_0195f3a0000070018234567890abcdef", "tool_id": "mcp_tavily_search", '
            '"query": "q", "raw_result_summary": "r", "timestamp_utc": "2026-10-25T12:00:00Z", '
            '"extra_field": "forbidden"}'
        )

    mapper = SduiMapperService()
    dto = ReportDataDTOFactory.build().model_copy(update={"execution_id": ""})
    with pytest.raises(AppException) as exc_empty_lang:
        mapper.map_report_to_sdui(dto, execution_id="exe_0195f3a0000070018234567890abcdef", lang="   ")
    assert exc_empty_lang.value.status_code == 400

    with pytest.raises(AppException) as exc_empty_exec:
        mapper.map_report_to_sdui(dto, execution_id="   ", lang="en")
    assert exc_empty_exec.value.status_code == 400


def test_sdui_heterogeneous_payload_equivalence_partitions() -> None:
    """Verify all 4 ISTQB Equivalence Partitions across SynthesisPayloadCompressor and SduiMapperService."""
    # Phase 4, Step 4.1: Heterogeneous payload equivalence partitioning (JSON/DTO, List, String/Markdown, Scalars/Falsy)
    atom_id_1 = generate_opaque_id(EntityPrefix.TDA)
    atom_id_2 = generate_opaque_id(EntityPrefix.TDA)
    blocker_id = generate_opaque_id(EntityPrefix.TDA)

    # Partition 1: Structured JSON / DTO
    eval_dto_1 = ReducedAtomDTO(
        tda_id=atom_id_1,
        status=ExecutionStatus.N_A,
        reasoning="Prerequisite failed; atom short-circuited.",
        source_quotes=None,
        short_circuit_reason_tda_ids=[blocker_id],
        depends_on_tda_ids=[blocker_id],
        is_inverse_evidence=False,
    )
    compressed_dto = SynthesisPayloadCompressor.compress_synthesis_payload(eval_dto_1)
    assert atom_id_1 in compressed_dto
    assert blocker_id in compressed_dto

    # Partition 2: List collections
    eval_dto_2 = ReducedAtomDTO(
        tda_id=atom_id_2,
        status=ExecutionStatus.FAILED,
        reasoning="Failed due to inverse evidence.",
        source_quotes=("Verbatim toxic pattern quote from document.",),
        short_circuit_reason_tda_ids=[],
        depends_on_tda_ids=[],
        is_inverse_evidence=True,
    )
    list_payload: StepPayloadValue = [eval_dto_1, eval_dto_2]
    compressed_list = SynthesisPayloadCompressor.compress_synthesis_payload(list_payload)
    assert atom_id_1 in compressed_list
    assert atom_id_2 in compressed_list
    assert "Verbatim toxic pattern quote from document." in compressed_list

    distilled_1 = DistilledEvaluation(
        atom_id=atom_id_1,
        status=ExecutionStatus.N_A.value,
        semantic_reasoning="Prerequisite failed; atom short-circuited.",
        exact_quotes=[],
        depends_on_tda_ids=[blocker_id],
        short_circuit_reason_tda_ids=[blocker_id],
        topological_out_degree=3,
    )
    distilled_2 = DistilledEvaluation(
        atom_id=atom_id_2,
        status=ExecutionStatus.FAILED.value,
        is_inverse_evidence=True,
        semantic_reasoning="Failed due to inverse evidence.",
        exact_quotes=["Verbatim toxic pattern quote from document."],
        depends_on_tda_ids=[],
        short_circuit_reason_tda_ids=[],
        topological_out_degree=5,
    )
    stratified = SynthesisPayloadCompressor._prune_and_stratify_evaluations([distilled_1, distilled_2], limit=0)
    assert len(stratified) == 2

    # Partition 3: Pure String / Markdown
    markdown_payload = "## Synthesis Section\n\n- Topological root cause verified."
    compressed_md = SynthesisPayloadCompressor.compress_synthesis_payload(markdown_payload)
    assert compressed_md == markdown_payload

    mapper = SduiMapperService()
    report_dto = ReportDataDTOFactory.build().model_copy(
        update={
            "execution_id": generate_opaque_id(EntityPrefix.EXECUTION),
            "results": [
                AtomResultDTO(
                    tda_id=atom_id_1,
                    status=ExecutionStatus.N_A,
                    extensions={},
                    depends_on_tda_ids=[blocker_id],
                    short_circuit_reason_tda_ids=[blocker_id],
                )
            ],
            "hydrated_references": {
                blocker_id: HydratedAtomDTO(
                    sdui_component=SDUIComponentType.BOOLEAN_CARD,
                    resolved_claim="Prerequisite Audit Gate Claim",
                )
            },
            "inner_sdui_blocks": [
                MarkdownBlock(text=markdown_payload),
                SduiMatrixTableBlock(
                    title=I18nText(translations={"en": "Matrix"}),
                    axes=[],
                    short_circuited_by_claims=[],
                    falsified_warrant_claims=[],
                ),
            ],
        }
    )
    mapped_view = mapper.map_report(report_dto, execution_id=report_dto.execution_id, lang="en")
    matrix_blocks = [b for b in mapped_view.inner_sdui_blocks if isinstance(b, SduiMatrixTableBlock)]
    assert len(matrix_blocks) == 1
    assert any("Prerequisite Audit Gate Claim" in c for c in matrix_blocks[0].short_circuited_by_claims)

    # Partition 4: Scalars/Primitives (int, float, bool) and Falsy inputs ("", "   ", [], None)
    assert SynthesisPayloadCompressor.compress_synthesis_payload(42) == "42"
    assert SynthesisPayloadCompressor.compress_synthesis_payload(0) == "0"
    assert SynthesisPayloadCompressor.compress_synthesis_payload(3.14) == "3.14"
    assert SynthesisPayloadCompressor.compress_synthesis_payload(False) == "False"
    assert SynthesisPayloadCompressor.compress_synthesis_payload(True) == "True"

    falsy_inputs: list[StepPayloadValue] = ["", "   ", [], None]
    for falsy_input in falsy_inputs:
        with pytest.raises(AppException) as exc_info:
            SynthesisPayloadCompressor.compress_synthesis_payload(falsy_input)
        assert exc_info.value.status_code == 400
