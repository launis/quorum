import json
import os
import shutil
import subprocess
import tempfile
from typing import Any

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory

from backend_v2.models.dtos.atom_evaluation import ReasoningStepDTO
from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.enums import ExecutionStatus, VisualIntent
from backend_v2.models.v2_core import (
    I18nText,
    MatrixScorecardRowDTO,
    ReportDataDTO,
    ScorecardAtomDTO,
    Workflow,
)
from backend_v2.models.view.sdui import AnySduiBlock, MarkdownBlock, SduiMatrixTableBlock
from backend_v2.services.pdf_generator import PdfReportService


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
    results: list[Any] = []
    hydrated_references: dict[str, Any] = {}
    mcp_tool_audit: list[Any] = []
    matrix_visible_columns: list[str] = ["label", "score", "distribution", "row_explanation"]


class ScorecardAtomDTOFactory(ModelFactory[ScorecardAtomDTO]):
    __model__ = ScorecardAtomDTO
    exact_quotes: list[Any] = []
    visual_intent: VisualIntent = VisualIntent.SUCCESS
    __set_as_default_factory_for_type__ = True


class MatrixScorecardRowDTOFactory(ModelFactory[MatrixScorecardRowDTO]):
    __model__ = MatrixScorecardRowDTO
    score: float = 5.0
    scale_min: float = 0.0
    scale_max: float = 10.0
    normalized_score: float | None = None
    scorecard_atoms: dict[str, Any] = {}
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
    __set_as_default_factory_for_type__ = True

    @classmethod
    def _create_model(cls, *args: Any, **kwargs: Any) -> QuoteEvidenceDTO:
        kwargs.pop("_build_context", None)
        for arg in args:
            if isinstance(arg, dict):
                arg.pop("_build_context", None)
        return cls.__model__.model_validate(kwargs, context={"alias_engine": "dummy"})


@pytest.mark.asyncio
async def test_sdui_semantic_parity() -> None:
    """Phase 3: Automated Pytest E2E Orchestrator for SDUI Parity."""
    # Step 1: Verify flutter binary
    flutter_path = shutil.which("flutter")
    if not flutter_path:
        pytest.skip("Flutter SDK not found")

    # Step 2: Generate temp paths
    golden_fd, golden_path = tempfile.mkstemp(suffix=".json")
    os.close(golden_fd)

    dump_fd, dump_path = tempfile.mkstemp(suffix=".json")
    os.close(dump_fd)

    try:
        pdf_path = None

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

        new_layouts: list[AnySduiBlock] = [MarkdownBlock(text="# English test")]
        for layout in dto.inner_sdui_blocks:
            axes = list(getattr(layout, "axes", []))
            if getattr(layout, "preset_view", "") in ("radar_3d", "3d_matrix") or getattr(layout, "block_type", "") in (
                "radar_3d",
                "3d_matrix",
            ):
                while len(axes) < 3:
                    axes.append(MatrixScorecardRowDTOFactory.build())
            elif getattr(layout, "preset_view", getattr(layout, "block_type", "")) in (
                "matrix_2d",
                "2d_compare",
                "matrix_3d",
                "3d_matrix",
            ):
                while len(axes) < 2:
                    axes.append(MatrixScorecardRowDTOFactory.build())

            # Clear fields that break parity because Jinja explicitly ignores them or Flutter handles them differently.
            # 1. Polyfactory generates random exact_quotes for text blocks, which Jinja doesn't render.
            update_kwargs: dict[str, Any] = (
                {"exact_quotes": [], "citations": []} if hasattr(layout, "exact_quotes") else {}
            )
            if hasattr(layout, "matrix_column_labels"):
                update_kwargs["matrix_column_labels"] = {}
                update_kwargs["extension_labels"] = {}
            if hasattr(layout, "axes"):
                update_kwargs["axes"] = axes

            # Skip block types currently unsupported by Flutter SduiBlocksRenderer
            if getattr(layout, "block_type", "") in (
                "bullet_list",
                "hero_insight",
                "quote_card",
                "warning_card",
                "n_a_card",
                "3d_matrix",
                "2d_compare",
                "accordion",
            ):
                continue

            new_layouts.append(layout.model_copy(update=update_kwargs))

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

        with open(golden_path, "w", encoding="utf-8") as f_json:
            f_json.write(dto.model_dump_json(exclude_none=True))

        # Step 3: Run Flutter tests
        cmd = [
            flutter_path,
            "test",
            "test/features/execution/sdui_semantic_parity_test.dart",
            f"--dart-define=GOLDEN_PATH={golden_path}",
            f"--dart-define=DUMP_PATH={dump_path}",
        ]

        flutter_cwd = os.path.join(os.getcwd(), "client_app_v2")
        result = subprocess.run(cmd, cwd=flutter_cwd, capture_output=True, text=True, encoding="utf-8")
        assert result.returncode == 0, f"Flutter test failed: {result.stdout}\n{result.stderr}"

        pdf_service = PdfReportService()
        pdf_bytes = await pdf_service.generate_execution_pdf("mock_exec_id", report_dto=dto, locale="en")

        pdf_fd, pdf_path = tempfile.mkstemp(suffix=".pdf")
        os.close(pdf_fd)
        with open(pdf_path, "wb") as f_pdf:
            f_pdf.write(pdf_bytes)

        # Step 5: Extract PDF text
        import pymupdf4llm

        md_text = pymupdf4llm.to_markdown(pdf_path)

        # Step 6: Compare
        with open(dump_path, encoding="utf-8") as f_json_dump:
            flutter_text_sequence = json.load(f_json_dump)

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

        for flutter_str in flutter_text_sequence:
            for token in str(flutter_str).split("\n"):
                token = token.replace("*", "").strip()
                if not token:
                    continue
                assert token in cleaned_md, (
                    f"Flutter semantic token '{token}' missing from PDF output! PDF Context: {cleaned_md}"
                )

        # Verify authorized contextual override semantic parity between Flutter and PDF
        expected_override_token = "Parity Override Claim: Parity cognitive override observation text"
        assert expected_override_token in cleaned_md, (
            f"Contextual override text '{expected_override_token}' missing from PDF output! PDF Context: {cleaned_md}"
        )
        assert any(expected_override_token in clean_md(str(f_str)) for f_str in flutter_text_sequence), (
            f"Contextual override text '{expected_override_token}' missing from Flutter extracted tokens!"
        )

    finally:
        if os.path.exists(golden_path):
            os.remove(golden_path)
        if os.path.exists(dump_path):
            os.remove(dump_path)
        if pdf_path and os.path.exists(pdf_path):
            os.remove(pdf_path)
