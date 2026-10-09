"""Unit tests for ExportService covering Excel and flat CSV exports."""

from __future__ import annotations

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
    PersonaPromptBlock,
    ProtocolPromptBlock,
    SystemRulePromptBlock,
)
from backend_v2.models.dtos.atom_result import AtomResultDTO, ErrorDetailsDTO, HydratedAtomDTO
from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.enums import ExecutionStatus, LaxSDUIComponentType
from backend_v2.models.view.sdui import ParagraphBlock, SduiRadarChartBlock
from backend_v2.services.export_service import ExportService, _extract_claim_rule
from backend_v2.tests.fakes.in_memory_repositories import (
    InMemoryComponentRepository,
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


def test_extract_claim_rule() -> None:
    lbl = I18nText(translations={"fi": "L", "en": "L"})
    desc = I18nText(translations={"fi": "D", "en": "D"})
    scale = MatrixScale(score=1, ai_label="L1", claims=[])

    matrix_block = MatrixPromptBlock(
        id="blk_1111111111111111",
        slug="matrix_slug",
        label=lbl,
        description=desc,
        scales=[scale],
        ai_description="Matrix rule",
    )
    assert _extract_claim_rule(matrix_block) == "Matrix rule"

    rule_block = SystemRulePromptBlock(
        id="blk_2222222222222222",
        slug="rule_slug",
        label=lbl,
        description=desc,
        instruction_text="Rule text",
    )
    assert _extract_claim_rule(rule_block) == "Rule text"

    persona_block = PersonaPromptBlock(
        id="blk_3333333333333333",
        slug="persona_slug",
        label=lbl,
        description=desc,
        role_enforcement="Persona text",
    )
    assert _extract_claim_rule(persona_block) == "Persona text"

    protocol_block = ProtocolPromptBlock(
        id="blk_4444444444444444",
        slug="proto_slug",
        label=lbl,
        description=desc,
        protocol_instructions="Protocol text",
    )
    assert _extract_claim_rule(protocol_block) == "Protocol text"

    assert _extract_claim_rule(None) == ""


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
    bytes_out, filename = await service.export_excel(
        execution=exec_record,
        report_dto=report_dto,
        matrices=_build_sample_matrix_rows(1),
        locale="fi",
        components=[matrix_block],
    )

    assert filename == "execution_export_exe_0123456789abcdef.xlsx"
    assert len(bytes_out) > 0
    assert bytes_out.startswith(b"PK")


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

    bytes_out, filename = await service.export_excel(
        execution=exec_record,
        report_dto=report_dto,
        matrices=_build_sample_matrix_rows(1),
        locale="en",
    )

    assert filename == "execution_export_exe_0123456789abcdef.xlsx"
    assert len(bytes_out) > 0
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
            await service.export_excel(
                execution=exec_record, report_dto=report_dto, matrices=[matching_matrix]
            )

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.INTERNAL_SERVER_ERROR.value


def test_export_flat_csv_success() -> None:
    service = ExportService()
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED)
    report_dto = _build_sample_report_dto()

    csv_bytes, filename = service.export_flat_csv(
        execution=exec_record,
        report_dto=report_dto,
        execution_id="exe_custom_999",
    )

    assert filename == "execution_export_exe_custom_999.csv"
    assert len(csv_bytes) > 0
    csv_text = csv_bytes.decode("utf-8")
    assert "execution_id" in csv_text or "status" in csv_text


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

    excel_bytes, filename = await service.export_excel(
        execution=exec_record,
        report_dto=report_dto,
        matrices=[axis],
        locale="fi",
    )

    assert filename == "execution_export_exe_0123456789abcdef.xlsx"
    assert len(excel_bytes) > 0


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

    excel_bytes, filename = await service.export_excel(
        execution=exec_record,
        report_dto=report_dto,
        matrices=[axis_custom],
        locale="en",
        components=[component_block, tda_matched_block, unmatched_block],
        execution_id="exe_custom_export_123",
    )

    assert filename == "execution_export_exe_custom_export_123.xlsx"
    assert len(excel_bytes) > 0


def test_export_flat_csv_default_execution_id() -> None:
    """Test flat CSV export without explicit execution_id."""
    service = ExportService()
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED)
    report_dto = _build_sample_report_dto()

    csv_bytes, filename = service.export_flat_csv(
        execution=exec_record,
        report_dto=report_dto,
    )

    assert filename == "execution_export_exe_0123456789abcdef.csv"
    assert len(csv_bytes) > 0


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

    excel_bytes, _ = await service.export_excel(
        execution=exec_record,
        report_dto=report_dto,
        matrices=matrices,
        locale="fi",
    )

    excel_file = io.BytesIO(excel_bytes)
    summary_df = pd.read_excel(excel_file, sheet_name="Yhteenveto")
    raw_df = pd.read_excel(excel_file, sheet_name="Raakadata")

    assert len(summary_df) == 9
    for i, row in enumerate(summary_df.itertuples(), 1):
        assert row.Matriisi == f"Matriisi {i}"
        assert row.Arvosana == 4.0
        assert row.Maksimi == 5.0

    assert len(raw_df) == 2
    assert "Väitetyyppi" in raw_df.columns
    assert "Tulos (Status)" in raw_df.columns

    pos_row = raw_df[raw_df["Kriteeri (UI)"] == "Competence claim"].iloc[0]
    assert pos_row["Väitetyyppi"] == "Positiivinen kyvykkyys"
    assert pos_row["Tulos (Status)"] == 1

    inv_row = raw_df[raw_df["Kriteeri (UI)"] == "Fallacy absence claim"].iloc[0]
    assert inv_row["Väitetyyppi"] == "Virhedetektori / Anti-pattern"
    assert inv_row["Tulos (Status)"] == "Puhdas"


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

    bytes_out, _ = await service.export_excel(
        execution=exec_record,
        report_dto=report_dto,
        matrices=matrices,
        locale="fi",
    )

    raw_df = pd.read_excel(io.BytesIO(bytes_out), sheet_name="Raakadata")
    assert len(raw_df) == 1
    row = raw_df.iloc[0]
    assert row["Matriisi"] == "Aktiivinen ohjaus (Performatiivisuus ja Goodhartin Laki)"
    assert row["Väitetyyppi"] == "Virhedetektori / Anti-pattern"
    assert row["Tulos (Status)"] == "Puhdas"
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

    bytes_out, _ = await service.export_excel(
        execution=exec_record,
        report_dto=report_dto,
        matrices=matrices,
        locale="fi",
    )

    raw_df = pd.read_excel(io.BytesIO(bytes_out), sheet_name="Raakadata")
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
