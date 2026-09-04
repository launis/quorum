import re
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel, ConfigDict, TypeAdapter

from backend_v2.models.dtos.atom_evaluation import ReasoningStepDTO
from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO, ScorecardAtomDTO
from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.enums import ExecutionStatus, VisualIntent
from backend_v2.models.v2_core import (
    AtomResultDTO,
    HydratedAtomDTO,
    I18nText,
    MCPAuditTrace,
    ReportDataDTO,
    Workflow,
)
from backend_v2.models.view.sdui import (
    AnySduiBlock,
    MarkdownBlock,
    ParagraphBlock,
    SduiMatrixTableBlock,
    SduiMetrics1DBlock,
)
from backend_v2.services.pdf_generator import PdfReportService


class SduiSemanticTokenDTO(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)
    text: str
    is_bold: bool = False
    is_italic: bool = False
    is_header: bool = False


class WorkflowFactory(ModelFactory[Workflow]):
    __model__ = Workflow
    __set_as_default_factory_for_type__ = True


class ReasoningStepDTOFactory(ModelFactory[ReasoningStepDTO]):
    __model__ = ReasoningStepDTO
    __set_as_default_factory_for_type__ = True


class I18nTextFactory(ModelFactory[I18nText]):
    __model__ = I18nText
    __set_as_default_factory_for_type__ = True

    @classmethod
    def translations(cls) -> dict[str, str]:
        return {"en": "English test", "fi": "Finnish test"}


class ReportDataDTOFactory(ModelFactory[ReportDataDTO]):
    __model__ = ReportDataDTO
    results: list[AtomResultDTO] = []
    hydrated_references: dict[str, HydratedAtomDTO] = {}
    mcp_tool_audit: list[MCPAuditTrace] = []
    matrix_visible_columns: list[str] = ["label", "score", "distribution", "row_explanation"]


class ScorecardAtomDTOFactory(ModelFactory[ScorecardAtomDTO]):
    __model__ = ScorecardAtomDTO
    exact_quotes: list[QuoteEvidenceDTO] = []
    visual_intent: VisualIntent = VisualIntent.SUCCESS
    __set_as_default_factory_for_type__ = True


class MatrixScorecardRowDTOFactory(ModelFactory[MatrixScorecardRowDTO]):
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


class QuoteEvidenceDTOFactory(ModelFactory[QuoteEvidenceDTO]):
    __model__ = QuoteEvidenceDTO
    quote: str = "Test quote"
    verified_source_ids: list[str] = ["src_0"]
    unverified_aliases: list[str] = []
    is_verified: bool = True
    __set_as_default_factory_for_type__ = True


@pytest.mark.asyncio
async def test_sdui_semantic_parity() -> None:
    """Phase 3: Automated Pytest E2E Orchestrator for SDUI Parity."""
    # Step 1: Verify flutter binary
    flutter_path = shutil.which("flutter")
    if not flutter_path:
        pytest.skip("Flutter SDK not found")

    # Step 2: Generate temp paths
    temp_dir = Path(tempfile.gettempdir())
    golden_path = temp_dir / f"sdui_golden_{uuid.uuid4().hex[:8]}.json"
    dump_path = temp_dir / f"sdui_dump_{uuid.uuid4().hex[:8]}.json"
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
                                "matrix_visible_columns": ["label", "quotes"],
                                "matrix_column_labels": {
                                    "label": I18nText(translations={"en": "Dimension"}),
                                    "quotes": I18nText(translations={"en": "Text Observation"}),
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
                    # comprehensive rendering of all 17 blocks is verified deterministically in test_sdui_template_parity.py.
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
            matrix_visible_columns=["label", "quotes"],
            matrix_column_labels={
                "label": I18nText(translations={"en": "Dimension"}),
                "quotes": I18nText(translations={"en": "Text Observation"}),
            },
            axes=[override_axis],
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

        pdf_path = temp_dir / f"sdui_pdf_{uuid.uuid4().hex[:8]}.pdf"
        pdf_path.write_bytes(pdf_bytes)

        # Step 5: Extract PDF text
        import pymupdf4llm

        md_text = pymupdf4llm.to_markdown(str(pdf_path))

        # Step 6: Compare
        flutter_tokens = TypeAdapter(list[SduiSemanticTokenDTO]).validate_json(dump_path.read_text(encoding="utf-8"))
        assert len(flutter_tokens) > 0, "No semantic tokens extracted from Flutter!"

        # Parity Check: Every semantic text block visible in Flutter MUST be present in the generated PDF.
        # This proves the Dumb Painter architecture is in perfect sync with Jinja PDF.
        def clean_md(text: str) -> str:
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

        cleaned_md = clean_md(md_text)
        # Stitch adjacent identical markdown formatting tags across <br> or \n to allow multiline span matching
        stitched_md = re.sub(r"([*_]{1,2})\s*(?:<br\s*/?>|\n)\s*\1", " ", md_text)
        norm_md_text = re.sub(r"<br\s*/?>", " ", stitched_md)

        def verify_token_parity(token: SduiSemanticTokenDTO, target_md: str, target_clean_md: str) -> None:
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

        for token in flutter_tokens:
            verify_token_parity(token, norm_md_text, cleaned_md)

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
            verify_token_parity(
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
            verify_token_parity(
                candidate_token.model_copy(update={"is_bold": True}),
                norm_md_text,
                cleaned_md,
            )

        # 3. Body text mutated to header:
        with pytest.raises(AssertionError):
            verify_token_parity(
                candidate_token.model_copy(update={"is_header": True}),
                norm_md_text,
                cleaned_md,
            )

        # 4. Unstyled text mutated to italic:
        with pytest.raises(AssertionError):
            verify_token_parity(
                candidate_token.model_copy(update={"is_italic": True}),
                norm_md_text,
                cleaned_md,
            )

    finally:
        golden_path.unlink(missing_ok=True)
        dump_path.unlink(missing_ok=True)
        if pdf_path:
            pdf_path.unlink(missing_ok=True)
