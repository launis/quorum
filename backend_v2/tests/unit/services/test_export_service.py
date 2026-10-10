"""Unit tests for ExportService covering Excel and flat CSV exports."""

from __future__ import annotations

import csv
import io
from unittest.mock import patch

import pandas as pd
import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import ExecutionRecord, ExecutionStepState
from backend_v2.models.domain.matrix import MatrixClaim, MatrixScale, TDAAssertion
from backend_v2.models.domain.prompt_blocks import (
    MatrixPromptBlock,
    SystemRulePromptBlock,
)
from backend_v2.models.dtos.atom_evaluation import ReasoningStepDTO
from backend_v2.models.dtos.atom_result import AtomResultDTO, ErrorDetailsDTO, HydratedAtomDTO
from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO, ScorecardAtomDTO
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.enums import (
    ExecutionStatus,
    LaxSDUIComponentType,
    ReportAtomColumn,
    ReportSheetKey,
    VisualIntent,
)
from backend_v2.models.view.sdui import ParagraphBlock, SduiRadarChartBlock
from backend_v2.services.export_service import ExportService
from backend_v2.services.localization import LocalizationService, ReportHeaderResolver
from backend_v2.tests.fakes.in_memory_repositories import (
    InMemoryPromptBlockRepository,
)


def _build_sample_execution(
    status: ExecutionStatus = ExecutionStatus.PASSED, has_atoms: bool = True
) -> ExecutionRecord:
    step_states: dict[str, ExecutionStepState] = {}
    if has_atoms:
        step_states["stp_0123456789abcdef"] = ExecutionStepState(
            id="stp_0123456789abcdef",
            label="Matrix Step Label",
            status=ExecutionStatus.PASSED,
        )

    return ExecutionRecord(
        id="exe_0123456789abcdef",
        workflow_id="wor_0123456789abcdef",
        organization_id="org_0123456789abcdef",
        target_locale="fi",
        status=status,
        step_states=step_states,
    )


def _build_sample_report_dto(has_atoms: bool = True) -> ReportDataDTO:
    axis = MatrixScorecardRowDTO(
        block_id="blk_0123456789abcdef",
        name="Axis 1",
        label_i18n=I18nText(translations={"fi": "Akseli 1", "en": "Axis 1"}),
        score=4.5,
        scale_max=5.0,
        row_explanation="Explanation for row 1",
        is_evaluative=True,
    )
    chart = SduiRadarChartBlock(axes=[axis])
    results: list[AtomResultDTO] = []
    hydrated_references: dict[str, HydratedAtomDTO] = {}
    if has_atoms:
        results = [
            AtomResultDTO(
                tda_id="tda_0123456789abcdef",
                matrix_id="blk_0123456789abcdef",
                status=ExecutionStatus.PASSED,
                source_quote="Verbatim quote from source document",
                evaluation_reasoning="Reasoning with several words here",
            )
        ]
        hydrated_references = {
            "tda_0123456789abcdef": HydratedAtomDTO(
                sdui_component=LaxSDUIComponentType.BOOLEAN_CARD,
                resolved_claim="Claim Label",
            )
        }
    return ReportDataDTO(
        workflow_id="wor_0123456789abcdef",
        execution_id="exe_0123456789abcdef",
        profile_id="prof_0123456789abcdef",
        global_score=4.5,
        has_warning=False,
        inner_sdui_blocks=[chart],
        results=results,
        hydrated_references=hydrated_references,
    )


def _build_sample_matrix_rows(n: int = 1) -> list[MatrixScorecardRowDTO]:
    """Helper to construct valid MatrixScorecardRowDTO test instances."""
    return [
        MatrixScorecardRowDTO(
            block_id=f"blk_matrix_{i:04d}",
            name=f"Matrix {i}",
            label_i18n=I18nText(translations={"fi": f"Matriisi {i}", "en": f"Matrix {i}"}),
            score=4.0,
            scale_max=5.0,
            row_explanation=f"Row explanation {i}",
            is_evaluative=True,
        )
        for i in range(1, n + 1)
    ]


@pytest.mark.asyncio
async def test_export_excel_success_fi() -> None:
    service = ExportService()
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED)
    report_dto = _build_sample_report_dto()

    lbl = I18nText(translations={"fi": "L", "en": "L"})
    desc = I18nText(translations={"fi": "D", "en": "D"})
    scale = MatrixScale(score=1, ai_label="L1", claims=[])
    matrix_block = MatrixPromptBlock(
        id="blk_0123456789abcdef",
        slug="m_slug",
        label=lbl,
        description=desc,
        scales=[scale],
        ai_description="Operational rule",
    )
    payload = await service.export_excel(
        execution=exec_record,
        report_dto=report_dto,
        matrices=_build_sample_matrix_rows(1),
        locale="fi",
        components=[matrix_block],
    )

    assert payload.filename == "execution_export_exe_0123456789abcdef.xlsx"
    assert len(payload.content_bytes) > 0
    assert payload.content_bytes.startswith(b"PK")


@pytest.mark.asyncio
async def test_export_excel_success_en_with_prompt_block_repo() -> None:
    prompt_block_repo = InMemoryPromptBlockRepository()
    lbl = I18nText(translations={"fi": "L", "en": "L"})
    desc = I18nText(translations={"fi": "D", "en": "D"})
    scale = MatrixScale(score=1, ai_label="L1", claims=[])
    matrix_block = MatrixPromptBlock(
        id="blk_0123456789abcdef",
        slug="m_slug",
        label=lbl,
        description=desc,
        scales=[scale],
        ai_description="English operational rule",
    )
    await prompt_block_repo.create_prompt_block(matrix_block)

    service = ExportService(prompt_block_repo=prompt_block_repo)
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED)
    report_dto = _build_sample_report_dto()

    payload = await service.export_excel(
        execution=exec_record,
        report_dto=report_dto,
        matrices=_build_sample_matrix_rows(1),
        locale="en",
    )

    assert payload.filename == "execution_export_exe_0123456789abcdef.xlsx"
    assert len(payload.content_bytes) > 0
    assert prompt_block_repo._call_counts["get_all_prompt_blocks"] == 1


@pytest.mark.asyncio
async def test_export_excel_fails_non_passed_status() -> None:
    service = ExportService()
    exec_record = _build_sample_execution(status=ExecutionStatus.FAILED)

    with pytest.raises(AppException) as exc_info:
        await service.export_excel(execution=exec_record, report_dto=None, matrices=_build_sample_matrix_rows(1))

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "Execution must be in PASSED state" in exc_info.value.message


@pytest.mark.asyncio
async def test_export_excel_fails_no_scoreable_atoms() -> None:
    service = ExportService()
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED, has_atoms=False)

    with pytest.raises(AppException) as exc_info:
        await service.export_excel(execution=exec_record, report_dto=None, matrices=_build_sample_matrix_rows(1))

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "Execution has no scoreable atoms" in exc_info.value.message


@pytest.mark.asyncio
async def test_export_excel_fails_when_report_dto_has_no_atoms() -> None:
    service = ExportService()
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED, has_atoms=False)
    report_dto = _build_sample_report_dto(has_atoms=False)

    with pytest.raises(AppException) as exc_info:
        await service.export_excel(execution=exec_record, report_dto=report_dto, matrices=_build_sample_matrix_rows(1))

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "Execution has no scoreable atoms" in exc_info.value.message


@pytest.mark.asyncio
async def test_export_excel_writer_error() -> None:
    service = ExportService()
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED)
    report_dto = _build_sample_report_dto()
    matching_matrix = MatrixScorecardRowDTO(
        block_id="blk_0123456789abcdef",
        name="Axis 1",
        label_i18n=I18nText(translations={"fi": "Akseli 1", "en": "Axis 1"}),
        score=4.5,
        scale_max=5.0,
        row_explanation="Explanation for row 1",
        is_evaluative=True,
    )

    with patch("pandas.ExcelWriter", side_effect=RuntimeError("Disk failure")):
        with pytest.raises(AppException) as exc_info:
            await service.export_excel(execution=exec_record, report_dto=report_dto, matrices=[matching_matrix])

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.INTERNAL_SERVER_ERROR.value


@pytest.mark.asyncio
async def test_export_flat_csv_success() -> None:
    service = ExportService()
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED)
    report_dto = _build_sample_report_dto()
    matching_matrix = MatrixScorecardRowDTO(
        block_id="blk_0123456789abcdef",
        name="Axis 1",
        label_i18n=I18nText(translations={"fi": "Akseli 1", "en": "Axis 1"}),
        score=4.5,
        scale_max=5.0,
        row_explanation="Explanation for row 1",
        is_evaluative=True,
    )
    matrices = [matching_matrix]

    payload = await service.export_flat_csv(
        execution=exec_record,
        report_dto=report_dto,
        matrices=matrices,
        locale="fi",
        execution_id="exe_custom_999",
    )

    assert payload.filename == "execution_export_exe_custom_999.csv"
    csv_text = payload.content_bytes.decode("utf-8-sig")
    reader = list(csv.reader(io.StringIO(csv_text)))
    assert len(reader[0]) == 17
    assert len(reader) - 1 == len(report_dto.results)
    assert "Logiikkamatriisi" in reader[0]
    assert "Arviointikriteeri" in reader[0]


@pytest.mark.asyncio
async def test_export_excel_with_report_dto_results_atoms() -> None:
    """Regression test proving failure when atoms are passed in report_dto.results.

    During real runtime DAG execution, ExecutionRecord.step_states has empty scorecard_atoms={}.
    The evaluated atoms exist exclusively as AtomResultDTOs inside report_dto.results and
    hydrated_references. ExportService must extract raw data rows from report_dto.results
    instead of failing with 'Execution has no scoreable atoms'.
    """
    from backend_v2.models.dtos.atom_result import AtomResultDTO, HydratedAtomDTO
    from backend_v2.models.enums import ExecutionStatus

    service = ExportService()
    # Real execution has empty scorecard_atoms in step_states
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED, has_atoms=False)

    atom_result = AtomResultDTO(
        tda_id="tda_0123456789abcdef",
        matrix_id="blk_0123456789abcdef",
        status=ExecutionStatus.PASSED,
        source_quote="Verbatim quote from source document",
        evaluation_reasoning="Sound reasoning based on evidence.",
    )
    hydrated_ref = HydratedAtomDTO(
        sdui_component="boolean_card",
        resolved_claim="The organization follows clear strategy guidelines.",
    )

    axis = MatrixScorecardRowDTO(
        block_id="blk_0123456789abcdef",
        name="Strategy Matrix",
        label_i18n=I18nText(translations={"fi": "Strategiamatriisi", "en": "Strategy Matrix"}),
        score=4.0,
        scale_max=5.0,
        row_explanation="Solid strategic alignment.",
        is_evaluative=True,
    )
    chart = SduiRadarChartBlock(axes=[axis])

    report_dto = ReportDataDTO(
        workflow_id="wor_0123456789abcdef",
        execution_id="exe_0123456789abcdef",
        profile_id="prof_0123456789abcdef",
        global_score=4.0,
        has_warning=False,
        inner_sdui_blocks=[chart],
        results=[atom_result],
        hydrated_references={"tda_0123456789abcdef": hydrated_ref},
    )

    payload = await service.export_excel(
        execution=exec_record,
        report_dto=report_dto,
        matrices=[axis],
        locale="fi",
    )

    assert payload.filename == "execution_export_exe_0123456789abcdef.xlsx"
    assert len(payload.content_bytes) > 0


@pytest.mark.asyncio
async def test_export_excel_with_all_extensions_and_blocks() -> None:
    """Test Excel export with non-matrix blocks, None labels, all atom extensions, and custom ID."""
    service = ExportService()
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED, has_atoms=False)

    axis_custom = MatrixScorecardRowDTO(
        block_id="blk_aaaaaaaaaaaaaaaa",
        name="Custom Axis",
        label_i18n=I18nText(translations={"en": "Custom Axis"}),
        score=3.0,
        scale_max=5.0,
        row_explanation="Axis with custom label",
        is_evaluative=True,
    )
    chart = SduiRadarChartBlock(axes=[axis_custom])
    text_block = ParagraphBlock(text="Informational text")

    atom_with_extensions = AtomResultDTO(
        tda_id="tda_bbbbbbbbbbbbbbbb",
        matrix_id="blk_aaaaaaaaaaaaaaaa",
        status=ExecutionStatus.FAILED,
        source_quote=None,
        evaluation_reasoning="Failed check due to missing policy.",
        extensions={
            "internalized_rule": "Strict rule",
            "confidence": "0.85",
            "source_id": "src_custom",
            "falsification": "Refuted claim",
        },
    )
    atom_system_error = AtomResultDTO(
        tda_id="tda_cccccccccccccccc",
        matrix_id="blk_aaaaaaaaaaaaaaaa",
        status=ExecutionStatus.SYSTEM_ERROR,
        source_quote=None,
        evaluation_reasoning=None,
        error_details=ErrorDetailsDTO(error_code="SYSTEM_ERROR", message="System execution failure."),
    )
    hydrated_ref_with_quote = HydratedAtomDTO(
        sdui_component=LaxSDUIComponentType.BOOLEAN_CARD,
        resolved_claim="Resolved Claim with Quote",
        source_quote="Quote from hydrated reference",
    )

    component_block = SystemRulePromptBlock(
        id="blk_dddddddddddddddd",
        slug="comp_slug",
        label=I18nText(translations={"fi": "Komponentti", "en": "Component"}),
        description=I18nText(translations={"fi": "D", "en": "D"}),
        instruction_text="Component rule instruction",
    )
    tda_matched_block = SystemRulePromptBlock(
        id="tda_eeeeeeeeeeeeeeee",
        slug="tda_slug",
        label=I18nText(translations={"fi": "TDA Block", "en": "TDA Block"}),
        description=I18nText(translations={"fi": "D", "en": "D"}),
        instruction_text="TDA matched instruction",
    )
    unmatched_block = SystemRulePromptBlock(
        id="blk_0000000000000000",
        slug="unmatched_slug",
        label=I18nText(translations={"fi": "Tuntematon", "en": "Unknown"}),
        description=I18nText(translations={"fi": "D", "en": "D"}),
        instruction_text="Unmatched instruction",
    )

    atom_with_comp_matrix = AtomResultDTO(
        tda_id="tda_eeeeeeeeeeeeeeee",
        matrix_id="blk_dddddddddddddddd",
        status=ExecutionStatus.PASSED,
        source_quote="Explicit quote",
        evaluation_reasoning="Evaluation passed smoothly.",
    )
    atom_unmatched = AtomResultDTO(
        tda_id="tda_ffffffffffffffff",
        matrix_id="blk_0000000000000000",
        status=ExecutionStatus.PASSED,
        source_quote="Unknown quote",
        evaluation_reasoning="Evaluation for unknown block.",
    )

    report_dto = ReportDataDTO(
        workflow_id="wor_0123456789abcdef",
        execution_id="exe_0123456789abcdef",
        profile_id="prof_0123456789abcdef",
        global_score=3.5,
        has_warning=False,
        inner_sdui_blocks=[text_block, chart],
        results=[atom_with_extensions, atom_system_error, atom_with_comp_matrix, atom_unmatched],
        hydrated_references={
            "tda_bbbbbbbbbbbbbbbb": hydrated_ref_with_quote,
            "tda_cccccccccccccccc": HydratedAtomDTO(
                sdui_component=LaxSDUIComponentType.BOOLEAN_CARD,
                resolved_claim="Claim for system error",
            ),
            "tda_eeeeeeeeeeeeeeee": HydratedAtomDTO(
                sdui_component=LaxSDUIComponentType.BOOLEAN_CARD,
                resolved_claim="Claim for component matrix",
            ),
            "tda_ffffffffffffffff": HydratedAtomDTO(
                sdui_component=LaxSDUIComponentType.BOOLEAN_CARD,
                resolved_claim="Claim for unknown block",
            ),
        },
    )

    payload = await service.export_excel(
        execution=exec_record,
        report_dto=report_dto,
        matrices=[axis_custom],
        locale="en",
        components=[component_block, tda_matched_block, unmatched_block],
        execution_id="exe_custom_export_123",
    )

    assert payload.filename == "execution_export_exe_custom_export_123.xlsx"
    assert len(payload.content_bytes) > 0


@pytest.mark.asyncio
async def test_export_flat_csv_default_execution_id() -> None:
    """Test flat CSV export without explicit execution_id."""
    service = ExportService()
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED)
    report_dto = _build_sample_report_dto()
    matching_matrix = MatrixScorecardRowDTO(
        block_id="blk_0123456789abcdef",
        name="Axis 1",
        label_i18n=I18nText(translations={"fi": "Akseli 1", "en": "Axis 1"}),
        score=4.5,
        scale_max=5.0,
        row_explanation="Explanation for row 1",
        is_evaluative=True,
    )
    matrices = [matching_matrix]

    payload = await service.export_flat_csv(
        execution=exec_record,
        report_dto=report_dto,
        matrices=matrices,
        locale="fi",
    )

    assert payload.filename == "execution_export_exe_0123456789abcdef.csv"
    assert len(payload.content_bytes) > 0
    csv_text = payload.content_bytes.decode("utf-8-sig")
    assert "Logiikkamatriisi" in csv_text


@pytest.mark.asyncio
async def test_export_excel_fails_when_matrices_empty() -> None:
    """Test that empty matrices list triggers Fail-Fast AppException(400, VALIDATION_FAILED)."""
    service = ExportService()
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED)
    report_dto = _build_sample_report_dto()

    with pytest.raises(AppException) as exc_info:
        await service.export_excel(
            execution=exec_record,
            report_dto=report_dto,
            matrices=[],
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "Execution has no evaluative matrices for Excel export." in exc_info.value.message


@pytest.mark.asyncio
async def test_export_excel_emits_exact_9_rows_summary_and_claim_classifications() -> None:
    """Test that export_excel emits exactly 9 matrix summary rows and explicit claim classifications."""
    import io

    import pandas as pd

    service = ExportService()
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED)

    matrices = _build_sample_matrix_rows(9)

    atom_positive = AtomResultDTO(
        tda_id="tda_pos_001",
        matrix_id="blk_matrix_0001",
        status=ExecutionStatus.PASSED,
        source_quote="Positive quote",
        evaluation_reasoning="Demonstrated positive competence.",
        is_inverse_evidence=False,
    )
    atom_inverse = AtomResultDTO(
        tda_id="tda_inv_001",
        matrix_id="blk_matrix_0002",
        status=ExecutionStatus.PASSED,
        source_quote=None,
        evaluation_reasoning="No fallacy detected.",
        is_inverse_evidence=True,
    )

    report_dto = ReportDataDTO(
        workflow_id="wor_0123456789abcdef",
        execution_id="exe_0123456789abcdef",
        profile_id="prof_0123456789abcdef",
        global_score=4.0,
        has_warning=False,
        inner_sdui_blocks=[],
        results=[atom_positive, atom_inverse],
        hydrated_references={
            "tda_pos_001": HydratedAtomDTO(
                sdui_component=LaxSDUIComponentType.BOOLEAN_CARD,
                resolved_claim="Competence claim",
            ),
            "tda_inv_001": HydratedAtomDTO(
                sdui_component=LaxSDUIComponentType.BOOLEAN_CARD,
                resolved_claim="Fallacy absence claim",
            ),
        },
    )

    payload = await service.export_excel(
        execution=exec_record,
        report_dto=report_dto,
        matrices=matrices,
        locale="fi",
    )

    excel_file = io.BytesIO(payload.content_bytes)
    summary_df = pd.read_excel(excel_file, sheet_name="Yhteenveto")
    raw_df = pd.read_excel(excel_file, sheet_name="Raakadata")

    assert len(summary_df) == 9
    assert len(summary_df) == len(matrices)
    for i in range(len(summary_df)):
        assert summary_df["Logiikkamatriisi"].iloc[i] == f"Matriisi {i + 1}"
        assert summary_df["Pisteet (raaka)"].iloc[i] == 4.0
        assert summary_df["Asteikon maksimi"].iloc[i] == 5.0

    assert len(raw_df) == 2
    assert len(raw_df) == len(report_dto.results)
    assert "Väitetyyppi" in raw_df.columns
    assert "Tulos (Status)" in raw_df.columns
    assert "Arviointikriteeri" in raw_df.columns

    pos_row = raw_df[raw_df["Arviointikriteeri"] == "Competence claim"].iloc[0]
    assert pos_row["Väitetyyppi"] == "Positiivinen kyvykkyys"
    assert pos_row["Tulos (Status)"] == 1

    inv_row = raw_df[raw_df["Arviointikriteeri"] == "Fallacy absence claim"].iloc[0]
    assert inv_row["Väitetyyppi"] == "Virhedetektori / Anti-pattern"
    assert inv_row["Tulos (Status)"] == 1
    assert "Falsifiointi" not in raw_df.columns
    assert "Sisäistetty sääntö" not in raw_df.columns


@pytest.mark.asyncio
async def test_export_excel_with_prompt_block_repo_resolves_matrix_names_and_inverse_claims_positive() -> None:
    prompt_block_repo = InMemoryPromptBlockRepository()
    lbl = I18nText(
        translations={
            "fi": "Aktiivinen ohjaus (Performatiivisuus ja Goodhartin Laki)",
            "en": "Active Steering (Performativity and Goodhart's Law)",
        }
    )
    desc = I18nText(translations={"fi": "Kuvaus", "en": "Description"})
    scale = MatrixScale(score=1, ai_label="L1", claims=[])
    matrix_block = MatrixPromptBlock(
        id="blk_53f32679aa514fcb",
        slug="active_steering",
        label=lbl,
        description=desc,
        scales=[scale],
        ai_description="Operational rule for active steering",
    )
    await prompt_block_repo.create_prompt_block(matrix_block)

    service = ExportService(prompt_block_repo=prompt_block_repo)
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED)
    matrices = _build_sample_matrix_rows(1)

    atom_inv = AtomResultDTO(
        tda_id="tda_53f32679aa514fcb0000000000000000",
        matrix_id="blk_53f32679aa514fcb",
        status=ExecutionStatus.PASSED,
        source_quote=None,
        evaluation_reasoning="No performativity error detected in leadership steering.",
        is_inverse_evidence=True,
    )

    report_dto = ReportDataDTO(
        workflow_id="wor_0123456789abcdef",
        execution_id="exe_0123456789abcdef",
        profile_id="prof_0123456789abcdef",
        global_score=4.0,
        has_warning=False,
        inner_sdui_blocks=[],
        results=[atom_inv],
        hydrated_references={
            "tda_53f32679aa514fcb0000000000000000": HydratedAtomDTO(
                sdui_component=LaxSDUIComponentType.BOOLEAN_CARD,
                resolved_claim="Goodhartin laki vältetty",
            )
        },
    )

    payload = await service.export_excel(
        execution=exec_record,
        report_dto=report_dto,
        matrices=matrices,
        locale="fi",
    )

    raw_df = pd.read_excel(io.BytesIO(payload.content_bytes), sheet_name="Raakadata")
    assert len(raw_df) == 1
    row = raw_df.iloc[0]
    assert row["Matriisi"] == "Aktiivinen ohjaus (Performatiivisuus ja Goodhartin Laki)"
    assert row["Väitetyyppi"] == "Virhedetektori / Anti-pattern"
    assert row["Tulos (Status)"] == 1
    assert prompt_block_repo._call_counts["get_all_prompt_blocks"] == 1


@pytest.mark.asyncio
async def test_export_excel_with_failed_inverse_claim_emits_status_zero_negative() -> None:
    prompt_block_repo = InMemoryPromptBlockRepository()
    tda_id = "tda_99999999aaaaaaaa0000000000000000"
    tda = TDAAssertion(
        tda_id=tda_id,
        inverse_evidence=True,
        aggregation_mode="EXISTS",
        concept_description="Detect steering error or performative bias",
    )
    claim = MatrixClaim(
        label=I18nText(translations={"fi": "Virhevapaa ohjaus", "en": "Error-free steering"}),
        tda_assertions=[tda],
    )
    scale = MatrixScale(score=1, ai_label="L1", claims=[claim])
    matrix_block = MatrixPromptBlock(
        id="blk_0000000000000001",
        slug="matrix_0001",
        label=I18nText(translations={"fi": "Matriisi 1", "en": "Matrix 1"}),
        description=I18nText(translations={"fi": "Kuvaus 1", "en": "Desc 1"}),
        scales=[scale],
        ai_description="Operational rule for matrix 1",
    )
    await prompt_block_repo.create_prompt_block(matrix_block)

    service = ExportService(prompt_block_repo=prompt_block_repo)
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED)
    matrices = [
        MatrixScorecardRowDTO(
            block_id="blk_0000000000000001",
            name="Matrix 1",
            label_i18n=I18nText(translations={"fi": "Matriisi 1", "en": "Matrix 1"}),
            score=4.0,
            scale_max=5.0,
            row_explanation="Row explanation 1",
            is_evaluative=True,
        )
    ]

    atom_failed = AtomResultDTO(
        tda_id=tda_id,
        matrix_id="blk_0000000000000001",
        status=ExecutionStatus.FAILED,
        source_quote=None,
        evaluation_reasoning="Performative bias was detected in steering.",
        is_inverse_evidence=False,
    )

    report_dto = ReportDataDTO(
        workflow_id="wor_0123456789abcdef",
        execution_id="exe_0123456789abcdef",
        profile_id="prof_0123456789abcdef",
        global_score=4.0,
        has_warning=False,
        inner_sdui_blocks=[],
        results=[atom_failed],
        hydrated_references={
            tda_id: HydratedAtomDTO(
                sdui_component=LaxSDUIComponentType.BOOLEAN_CARD,
                resolved_claim="Virhevapaa ohjaus",
            )
        },
    )

    payload = await service.export_excel(
        execution=exec_record,
        report_dto=report_dto,
        matrices=matrices,
        locale="fi",
    )

    raw_df = pd.read_excel(io.BytesIO(payload.content_bytes), sheet_name="Raakadata")
    assert len(raw_df) == 1
    row = raw_df.iloc[0]
    assert row["Väitetyyppi"] == "Virhedetektori / Anti-pattern"
    assert row["Tulos (Status)"] == 0


@pytest.mark.asyncio
async def test_export_excel_missing_matrix_in_repo_raises_fail_fast_negative() -> None:
    prompt_block_repo = InMemoryPromptBlockRepository()
    service = ExportService(prompt_block_repo=prompt_block_repo)
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED)
    matrices = _build_sample_matrix_rows(1)

    unknown_atom = AtomResultDTO(
        tda_id="tda_0123456789abcdef0000000000000000",
        matrix_id="blk_unknown_99999999",
        status=ExecutionStatus.PASSED,
        source_quote="Some valid quote",
        evaluation_reasoning="Evaluation succeeded.",
    )

    report_dto = ReportDataDTO(
        workflow_id="wor_0123456789abcdef",
        execution_id="exe_0123456789abcdef",
        profile_id="prof_0123456789abcdef",
        global_score=4.0,
        has_warning=False,
        inner_sdui_blocks=[],
        results=[unknown_atom],
        hydrated_references={
            "tda_0123456789abcdef0000000000000000": HydratedAtomDTO(
                sdui_component=LaxSDUIComponentType.BOOLEAN_CARD,
                resolved_claim="Some claim",
            )
        },
    )

    with pytest.raises(AppException) as exc_info:
        await service.export_excel(
            execution=exec_record,
            report_dto=report_dto,
            matrices=matrices,
            locale="fi",
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value
    assert "Strict Fail-Fast: Matrix block 'blk_unknown_99999999'" in exc_info.value.message


@pytest.mark.asyncio
async def test_export_excel_tab1_ssot_localization() -> None:
    """Verify Tab 1 columns match ReportHeaderResolver SSOT headers in both fi and en."""
    service = ExportService()
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED)
    report_dto = _build_sample_report_dto()
    matrices = [
        MatrixScorecardRowDTO(
            block_id="blk_0123456789abcdef",
            name="Axis 1",
            label_i18n=I18nText(translations={"fi": "Akseli 1", "en": "Axis 1"}),
            score=4.5,
            scale_max=5.0,
            row_explanation="Explanation for row 1",
            is_evaluative=True,
        ),
        MatrixScorecardRowDTO(
            block_id="blk_matrix_0002",
            name="Matrix 2",
            label_i18n=I18nText(translations={"fi": "Matriisi 2", "en": "Matrix 2"}),
            score=4.0,
            scale_max=5.0,
            row_explanation="Explanation for row 2",
            is_evaluative=True,
        ),
    ]

    for locale in ["fi", "en"]:
        payload = await service.export_excel(
            execution=exec_record,
            report_dto=report_dto,
            matrices=matrices,
            locale=locale,
        )
        sheet_name = ReportHeaderResolver.get_sheet_name(ReportSheetKey.SUMMARY, locale=locale)
        df = pd.read_excel(io.BytesIO(payload.content_bytes), sheet_name=sheet_name)
        expected_headers = list(ReportHeaderResolver.get_all_matrix_headers(locale=locale).values())
        assert list(df.columns) == expected_headers
        assert len(df) == len(matrices)


@pytest.mark.asyncio
async def test_export_excel_tab2_ssot_localization() -> None:
    """Verify Tab 2 headers match ReportAtomColumn SSOT headers and result_status is strictly binary."""
    service = ExportService()
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED)
    report_dto = _build_sample_report_dto()
    matching_matrix = MatrixScorecardRowDTO(
        block_id="blk_0123456789abcdef",
        name="Axis 1",
        label_i18n=I18nText(translations={"fi": "Akseli 1", "en": "Axis 1"}),
        score=4.5,
        scale_max=5.0,
        row_explanation="Explanation for row 1",
        is_evaluative=True,
    )
    matrices = [matching_matrix]

    for locale in ["fi", "en"]:
        payload = await service.export_excel(
            execution=exec_record,
            report_dto=report_dto,
            matrices=matrices,
            locale=locale,
        )
        sheet_name = ReportHeaderResolver.get_sheet_name(ReportSheetKey.RAW_DATA, locale=locale)
        df = pd.read_excel(io.BytesIO(payload.content_bytes), sheet_name=sheet_name)
        expected_headers = ReportHeaderResolver.get_all_atom_headers(locale=locale)
        assert list(df.columns) == expected_headers
        assert len(df) == len(report_dto.results)
        status_header = ReportHeaderResolver.get_atom_column_header(ReportAtomColumn.RESULT_STATUS, locale=locale)
        for status_val in df[status_header]:
            assert status_val in (0, 1)


@pytest.mark.asyncio
async def test_export_flat_csv_fails_non_passed_status() -> None:
    service = ExportService()
    exec_record = _build_sample_execution(status=ExecutionStatus.FAILED)
    with pytest.raises(AppException) as exc_info:
        await service.export_flat_csv(execution=exec_record, report_dto=None, matrices=[])
    assert exc_info.value.status_code == 400
    assert "Execution must be in PASSED state" in exc_info.value.message


@pytest.mark.asyncio
async def test_export_flat_csv_fails_when_no_atoms() -> None:
    service = ExportService()
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED, has_atoms=False)
    report_dto = _build_sample_report_dto(has_atoms=False)
    with pytest.raises(AppException) as exc_info:
        await service.export_flat_csv(execution=exec_record, report_dto=report_dto, matrices=[])
    assert exc_info.value.status_code == 400
    assert "Execution has no scoreable atoms" in exc_info.value.message


@pytest.mark.asyncio
async def test_export_excel_with_scorecard_atoms_and_rich_matrix_metadata() -> None:
    service = ExportService()
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED)

    scorecard_atom = ScorecardAtomDTO(
        atom_id="tda_eval_001",
        claim_label="Claim label from scorecard",
        level=2,
        level_name="Level Two",
        extracted_facts={},
        exact_quotes=[],
        internal_logic_en=ReasoningStepDTO(
            step_1_identify_premise="Premise",
            step_2_scan_source="Scan",
            step_3_evaluate_anti_patterns="Anti-pattern",
            step_4_final_conclusion="Conclusion",
        ),
        status=ExecutionStatus.PASSED,
        semantic_reasoning="Semantic reason",
        contextual_override=False,
        chart_display_label="Chart display label",
        visual_intent=VisualIntent.NEUTRAL,
    )
    rich_matrix = MatrixScorecardRowDTO(
        block_id="blk_rich_0001",
        name="Rich Matrix",
        label_i18n=I18nText(translations={"fi": "Rikas matriisi", "en": "Rich Matrix"}),
        context_target="ctx_tgt_plain",
        context_target_label=I18nText(translations={"fi": "Kohteen nimike", "en": "Target title"}),
        score=3.5,
        scale_max=None,
        normalized_score=70.0,
        level_breakdown={"L1": "1", "L2": "2"},
        true_atoms=3,
        total_atoms=4,
        cited_text_quote="Direct citation quote from matrix",
        cited_source_title="Source Title Doc",
        cited_source_id="src_doc_01",
        row_explanation="Explanation for rich matrix",
        evaluated_atoms=[scorecard_atom],
        is_evaluative=True,
    )

    atom_without_matrix_id = AtomResultDTO(
        tda_id="tda_eval_001",
        matrix_id=None,
        status=ExecutionStatus.PASSED,
        source_quote="Verbatim quote for atom without matrix_id",
        evaluation_reasoning="Reasoning for atom without matrix_id",
    )
    atom_with_ref_quote = AtomResultDTO(
        tda_id="tda_eval_002",
        matrix_id="blk_rich_0001",
        status=ExecutionStatus.PASSED,
        source_quote=None,
        evaluation_reasoning="Reasoning with ref quote fallback",
        is_inverse_evidence=True,
    )

    report_dto = ReportDataDTO(
        workflow_id="wor_0123456789abcdef",
        execution_id="exe_0123456789abcdef",
        profile_id="prof_0123456789abcdef",
        global_score=3.5,
        has_warning=False,
        inner_sdui_blocks=[],
        results=[atom_without_matrix_id, atom_with_ref_quote],
        hydrated_references={
            "tda_eval_001": HydratedAtomDTO(
                sdui_component=LaxSDUIComponentType.BOOLEAN_CARD,
                resolved_claim="Claim for eval 1",
            ),
            "tda_eval_002": HydratedAtomDTO(
                sdui_component=LaxSDUIComponentType.BOOLEAN_CARD,
                resolved_claim="Claim for eval 2",
                source_quote="Hydrated fallback quote",
            ),
        },
    )

    payload = await service.export_excel(
        execution=exec_record,
        report_dto=report_dto,
        matrices=[rich_matrix],
        locale="fi",
    )
    assert len(payload.content_bytes) > 0


@pytest.mark.asyncio
async def test_export_excel_atom_missing_matrix_id_and_parent_fails_fast() -> None:
    service = ExportService()
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED)
    orphan_atom = AtomResultDTO(
        tda_id="tda_orphan_999",
        matrix_id=None,
        status=ExecutionStatus.PASSED,
        source_quote="Quote",
        evaluation_reasoning="Reason",
    )
    report_dto = ReportDataDTO(
        workflow_id="wor_0123456789abcdef",
        execution_id="exe_0123456789abcdef",
        profile_id="prof_0123456789abcdef",
        global_score=3.5,
        has_warning=False,
        inner_sdui_blocks=[],
        results=[orphan_atom],
        hydrated_references={
            "tda_orphan_999": HydratedAtomDTO(
                sdui_component=LaxSDUIComponentType.BOOLEAN_CARD,
                resolved_claim="Orphan claim",
            )
        },
    )
    rich_matrix = MatrixScorecardRowDTO(
        block_id="blk_rich_0001",
        name="Rich Matrix",
        label_i18n=I18nText(translations={"fi": "Rikas matriisi", "en": "Rich Matrix"}),
        score=3.5,
        scale_max=5.0,
        row_explanation="Explanation",
        evaluated_atoms=[],
        is_evaluative=True,
    )
    with pytest.raises(AppException) as exc_info:
        await service.export_excel(
            execution=exec_record,
            report_dto=report_dto,
            matrices=[rich_matrix],
            locale="fi",
        )
    assert exc_info.value.status_code == 404
    assert "Strict Fail-Fast: Matrix block for atom 'tda_orphan_999' not found" in exc_info.value.message


@pytest.mark.asyncio
async def test_export_flat_csv_resolves_matrix_from_prompt_block_repo() -> None:
    """Regression test: export_flat_csv must resolve matrix blocks from prompt_block_repo.

    When an atom belongs to an informational or secondary matrix block not included
    in the evaluative 'matrices' list (e.g. blk_53f32679aa514fcb), export_flat_csv
    must resolve the matrix metadata instead of crashing with 404 RESOURCE_NOT_FOUND.
    """
    prompt_block_repo = InMemoryPromptBlockRepository()
    lbl = I18nText(translations={"fi": "Aktiivinen ohjaus", "en": "Active Control"})
    tda_assertion = TDAAssertion(
        tda_id="tda_135ee4d2f4e28b3305cbae57482e34b0",
        inverse_evidence=False,
        aggregation_mode="ALL_MUST_COMPLY",
        concept_description="Active steering assertion",
    )
    claim = MatrixClaim(
        label=I18nText(translations={"fi": "Väite 1", "en": "Claim 1"}),
        tda_assertions=[tda_assertion],
    )
    scale = MatrixScale(score=1, ai_label="L1", claims=[claim])
    desc = I18nText(translations={"fi": "Kuvaus", "en": "Description"})
    informational_block = MatrixPromptBlock(
        id="blk_53f32679aa514fcb",
        slug="m_slug",
        label=lbl,
        description=desc,
        scales=[scale],
        ai_description="English operational rule",
        is_evaluative=False,
    )
    await prompt_block_repo.create_prompt_block(informational_block)
    service = ExportService(prompt_block_repo=prompt_block_repo)
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED)
    atom_result = AtomResultDTO(
        tda_id="tda_135ee4d2f4e28b3305cbae57482e34b0",
        matrix_id="blk_53f32679aa514fcb",
        status=ExecutionStatus.PASSED,
        source_quote="Verbatim quote",
        evaluation_reasoning="Evaluation reasoning",
    )
    report_dto = ReportDataDTO(
        workflow_id="wor_0123456789abcdef",
        execution_id="exe_0123456789abcdef",
        profile_id="prof_0123456789abcdef",
        global_score=4.0,
        has_warning=False,
        inner_sdui_blocks=[],
        results=[atom_result],
        hydrated_references={
            "tda_135ee4d2f4e28b3305cbae57482e34b0": HydratedAtomDTO(
                sdui_component=LaxSDUIComponentType.BOOLEAN_CARD,
                resolved_claim="Väite 1",
            )
        },
    )
    evaluative_matrix = MatrixScorecardRowDTO(
        block_id="blk_eval_0001",
        name="Evaluative Matrix",
        label_i18n=I18nText(translations={"fi": "Arvioiva", "en": "Evaluative"}),
        score=4.0,
        scale_max=5.0,
        row_explanation="Explanation",
        is_evaluative=True,
    )
    payload = await service.export_flat_csv(
        execution=exec_record,
        report_dto=report_dto,
        matrices=[evaluative_matrix],
        locale="fi",
    )
    assert payload is not None
    csv_text = payload.content_bytes.decode("utf-8-sig")
    assert "Aktiivinen ohjaus" in csv_text
    assert "L1" in csv_text


@pytest.mark.asyncio
async def test_informational_matrix_parity_excel_and_csv() -> None:
    """Verify informational matrices (is_evaluative=False) have complete parity in Excel and CSV.

    Scores, levels, level names, and atom rows are computed and exported identically,
    while global_score average remains driven solely by evaluative matrices.
    """
    prompt_block_repo = InMemoryPromptBlockRepository()
    info_block = MatrixPromptBlock(
        id="blk_1111222233334444",
        slug="info_slug",
        label=I18nText(translations={"fi": "Informaatiomatriisi", "en": "Informational Matrix"}),
        description=I18nText(translations={"fi": "Kuvaus", "en": "Desc"}),
        scales=[
            MatrixScale(
                score=3,
                ai_label="Taso 3",
                name=I18nText(translations={"fi": "Taso 3 Nimi", "en": "Level 3 Name"}),
                claims=[],
            )
        ],
        ai_description="Info rule",
        is_evaluative=False,
    )
    await prompt_block_repo.create_prompt_block(info_block)

    service = ExportService(prompt_block_repo=prompt_block_repo)
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED)

    info_scorecard_atom = ScorecardAtomDTO(
        atom_id="tda_1111222233334444",
        claim_label="Informaatioväite",
        level=3,
        level_name="Taso 3 Nimi",
        extracted_facts={},
        exact_quotes=[],
        internal_logic_en=ReasoningStepDTO(
            step_1_identify_premise="Premise",
            step_2_scan_source="Scan",
            step_3_evaluate_anti_patterns="Anti-pattern",
            step_4_final_conclusion="Conclusion",
        ),
        status=ExecutionStatus.PASSED,
        semantic_reasoning="Reasoning for info atom",
        contextual_override=False,
        chart_display_label="Chart label",
        visual_intent=VisualIntent.NEUTRAL,
    )

    eval_scorecard_atom = ScorecardAtomDTO(
        atom_id="tda_5555666677778888",
        claim_label="Arviointiväite",
        level=5,
        level_name="Taso 5 Nimi",
        extracted_facts={},
        exact_quotes=[],
        internal_logic_en=ReasoningStepDTO(
            step_1_identify_premise="Premise",
            step_2_scan_source="Scan",
            step_3_evaluate_anti_patterns="Anti-pattern",
            step_4_final_conclusion="Conclusion",
        ),
        status=ExecutionStatus.PASSED,
        semantic_reasoning="Reasoning for eval atom",
        contextual_override=False,
        chart_display_label="Chart label",
        visual_intent=VisualIntent.NEUTRAL,
    )

    eval_matrix = MatrixScorecardRowDTO(
        block_id="blk_5555666677778888",
        name="Eval Matrix",
        label_i18n=I18nText(translations={"fi": "Arvioiva Matriisi", "en": "Evaluative Matrix"}),
        score=5.0,
        scale_max=5.0,
        normalized_score=100.0,
        level_breakdown={"L5": "1"},
        row_explanation="Evaluative explanation",
        evaluated_atoms=[eval_scorecard_atom],
        is_evaluative=True,
    )

    info_matrix = MatrixScorecardRowDTO(
        block_id="blk_1111222233334444",
        name="Info Matrix",
        label_i18n=I18nText(translations={"fi": "Informaatiomatriisi", "en": "Informational Matrix"}),
        score=3.0,
        scale_max=5.0,
        normalized_score=60.0,
        level_breakdown={"L3": "1"},
        row_explanation="Informational explanation",
        evaluated_atoms=[info_scorecard_atom],
        is_evaluative=False,
    )

    atom_eval = AtomResultDTO(
        tda_id="tda_5555666677778888",
        matrix_id="blk_5555666677778888",
        status=ExecutionStatus.PASSED,
        source_quote="Eval quote",
        evaluation_reasoning="Eval reasoning",
    )
    atom_info = AtomResultDTO(
        tda_id="tda_1111222233334444",
        matrix_id="blk_1111222233334444",
        status=ExecutionStatus.PASSED,
        source_quote="Info quote",
        evaluation_reasoning="Info reasoning",
    )

    report_dto = ReportDataDTO(
        workflow_id="wor_0123456789abcdef",
        execution_id="exe_0123456789abcdef",
        profile_id="prof_0123456789abcdef",
        global_score=5.0,
        has_warning=False,
        inner_sdui_blocks=[],
        results=[atom_eval, atom_info],
        hydrated_references={
            "tda_5555666677778888": HydratedAtomDTO(
                sdui_component=LaxSDUIComponentType.BOOLEAN_CARD,
                resolved_claim="Arviointiväite",
            ),
            "tda_1111222233334444": HydratedAtomDTO(
                sdui_component=LaxSDUIComponentType.BOOLEAN_CARD,
                resolved_claim="Informaatioväite",
            ),
        },
    )

    all_matrices = [eval_matrix, info_matrix]

    excel_payload = await service.export_excel(
        execution=exec_record,
        report_dto=report_dto,
        matrices=all_matrices,
        locale="fi",
        all_matrices=all_matrices,
    )
    import openpyxl

    wb = openpyxl.load_workbook(io.BytesIO(excel_payload.content_bytes))
    sheet1 = wb[LocalizationService.translate("export_sheet_summary", "fi")]
    sheet1_rows = list(sheet1.iter_rows(values_only=True))
    assert len(sheet1_rows) == 3
    matrix_names = [row[1] for row in sheet1_rows[1:]]
    assert "Arvioiva Matriisi" in matrix_names
    assert "Informaatiomatriisi" in matrix_names

    sheet2 = wb[LocalizationService.translate("export_sheet_raw_data", "fi")]
    sheet2_rows = list(sheet2.iter_rows(values_only=True))
    assert len(sheet2_rows) == 3
    raw_levels = [row[2] for row in sheet2_rows[1:]]
    assert 5 in raw_levels
    assert 3 in raw_levels
    raw_level_names = [row[3] for row in sheet2_rows[1:]]
    assert "Taso 5 Nimi" in raw_level_names
    assert "Taso 3 Nimi" in raw_level_names

    csv_payload = await service.export_flat_csv(
        execution=exec_record,
        report_dto=report_dto,
        matrices=all_matrices,
        locale="fi",
        all_matrices=all_matrices,
    )
    csv_text = csv_payload.content_bytes.decode("utf-8-sig")
    assert "Arvioiva Matriisi" in csv_text
    assert "Informaatiomatriisi" in csv_text
    assert "Taso 5 Nimi" in csv_text
    assert "Taso 3 Nimi" in csv_text
