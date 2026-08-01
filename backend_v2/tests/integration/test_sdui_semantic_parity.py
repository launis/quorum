import json
import os
import shutil
import subprocess
import tempfile
from typing import Any

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory

from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.v2_core import (
    I18nText,
    MatrixScorecardRowDTO,
    ReportDataDTO,
    ScorecardAtomDTO,
    Workflow,
)


class WorkflowFactory(ModelFactory[Workflow]):
    __model__ = Workflow
    __set_as_default_factory_for_type__ = True


class I18nTextFactory(ModelFactory[I18nText]):
    __model__ = I18nText
    __set_as_default_factory_for_type__ = True

    @classmethod
    def translations(cls) -> dict[str, str]:
        return {"en": "English test", "fi": "Finnish test"}

    @classmethod
    def default_locale(cls) -> str:
        return "en"


class ReportDataDTOFactory(ModelFactory[ReportDataDTO]):
    __model__ = ReportDataDTO
    results: list[Any] = []
    hydrated_references: dict[str, Any] = {}
    mcp_tool_audit: list[Any] = []
    matrix_visible_columns: list[str] = ["label", "score", "distribution", "row_explanation"]


class ScorecardAtomDTOFactory(ModelFactory[ScorecardAtomDTO]):
    __model__ = ScorecardAtomDTO
    exact_quotes: list[Any] = []
    __set_as_default_factory_for_type__ = True


class MatrixScorecardRowDTOFactory(ModelFactory[MatrixScorecardRowDTO]):
    __model__ = MatrixScorecardRowDTO
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
                "profile_name": I18nText(default_locale="en", translations={"en": "English test"}),
            }
        )  # Clear random dicts and explicitly mock profile_name to prevent Jinja crashes and ensure parity

        new_layouts = []
        for layout in dto.layouts:
            axes = list(layout.axes)
            if layout.preset_view in ("radar_3d", "3d_matrix"):
                while len(axes) < 3:
                    axes.append(MatrixScorecardRowDTOFactory.build())
            elif layout.preset_view in ("matrix_2d", "2d_compare", "matrix_3d", "3d_matrix"):
                while len(axes) < 2:
                    axes.append(MatrixScorecardRowDTOFactory.build())
            new_layouts.append(layout.model_copy(update={"synthesis_blocks": None, "axes": axes}))

        dto = dto.model_copy(update={"layouts": new_layouts})

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

        # Step 4: Generate PDF
        from unittest.mock import AsyncMock

        from backend_v2.services.pdf_generator import PdfReportService

        exec_repo = AsyncMock()
        exec_repo.get_execution.return_value = AsyncMock(
            metadata={"target_locale": "en"}, workflow_id="mock_workflow_id"
        )
        workflow_repo = AsyncMock()

        mock_wf = WorkflowFactory.build(
            expected_inputs=[], steps=[], name=I18nText(default_locale="en", translations={"en": "mock_wf"})
        )
        workflow_repo.get_workflow_by_id.return_value = mock_wf.model_dump(mode="json")

        pdf_service = PdfReportService(exec_repo=exec_repo, workflow_repo=workflow_repo)
        pdf_bytes = await pdf_service.generate_execution_pdf("mock_exec_id", report_dto=dto)

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
            return text.replace("**", "").replace("_", "").replace("### ", "").replace("## ", "").replace("# ", "")

        cleaned_md = clean_md(md_text)

        for flutter_str in flutter_text_sequence:
            for token in str(flutter_str).split("\n"):
                token = token.strip()
                if not token:
                    continue
                assert token in cleaned_md, (
                    f"Flutter semantic token '{token}' missing from PDF output! PDF Context: {cleaned_md}"
                )

    finally:
        if os.path.exists(golden_path):
            os.remove(golden_path)
        if os.path.exists(dump_path):
            os.remove(dump_path)
        if pdf_path and os.path.exists(pdf_path):
            os.remove(pdf_path)
