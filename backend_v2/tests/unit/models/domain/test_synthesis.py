import pytest
from pydantic import ValidationError

from backend_v2.models.domain.synthesis import SynthesisMetadataDTO, SynthesisStepDataDTO


def test_synthesis_metadata_dto_valid() -> None:
    data = {
        "target_locale": "fi",
        "token_usage": {"prompt_tokens": 10, "completion_tokens": 0, "total_tokens": 10},
        "step_results": [],
        "profile_id": "prof_1",
        "target_profile_id": "prof_2",
        "matrix_sampling_strategy": 1,
    }
    model = SynthesisMetadataDTO.model_validate(data)
    assert model.target_locale == "fi"
    assert model.token_usage.prompt_tokens == 10


def test_synthesis_metadata_dto_forbids_extra() -> None:
    data = {"target_locale": "fi", "invalid_extra_field": "test"}
    with pytest.raises(ValidationError) as exc:
        SynthesisMetadataDTO.model_validate(data)
    assert "Extra inputs are not permitted" in str(exc.value)


def test_synthesis_metadata_dto_accepts_workflow_version() -> None:
    data = {
        "target_locale": "fi",
        "step_results": [],
        "workflow_version": 1,
    }
    model = SynthesisMetadataDTO.model_validate(data)
    assert model.workflow_version == 1


def test_synthesis_step_data_dto_valid() -> None:
    data = {"reasoning_trace": {"thought_process": "thinking", "conclusion": "acting", "confidence_score": 0.9}}
    model = SynthesisStepDataDTO.model_validate(data)
    assert model.reasoning_trace is not None
    assert model.reasoning_trace.thought_process == "thinking"


def test_synthesis_step_data_dto_accepts_orchestrator_fields() -> None:
    data = {
        "reasoning_trace": {"thought_process": "thinking", "conclusion": "acting", "confidence_score": 0.9},
        "execution_id": "exe_123",
        "timestamp_isot": "2026-05-04T19:19:08.299332+00:00",
        "unix_time": 1714850348,
        "v2_engine": True,
    }
    # SynthesisStepDataDTO must successfully validate these explicitly defined orchestrator metadata fields.
    model = SynthesisStepDataDTO.model_validate(data)
    assert model.reasoning_trace is not None
    assert model.execution_id == "exe_123"


def test_synthesis_step_data_dto_forbids_extra_fields() -> None:
    data = {
        "reasoning_trace": {"thought_process": "thinking", "conclusion": "acting", "confidence_score": 0.9},
        "invalid_extra_field": 1337,
        "another_field": "value",
    }
    with pytest.raises(ValidationError):
        SynthesisStepDataDTO.model_validate(data)


def test_base_matrix_xai() -> None:
    from backend_v2.models.domain.synthesis import BaseMatrixXAI

    xai = BaseMatrixXAI(semantic_reasoning="Good explanation")
    assert xai.semantic_reasoning == "Good explanation"


def test_distilled_evaluation() -> None:
    from backend_v2.models.domain.synthesis import DistilledEvaluation

    de = DistilledEvaluation(
        atom_id="atm_123",
        exact_quotes=["quote 1"],
        semantic_reasoning="reasoning",
        extensions={"ext1": True},
    )
    assert de.atom_id == "atm_123"
    assert de.exact_quotes == ["quote 1"]


def test_base_tda_extraction_valid_and_coerce() -> None:
    from backend_v2.models.domain.synthesis import BaseTDAExtraction
    from backend_v2.models.dtos.quote_evidence import LLMExtractedQuote

    quote = LLMExtractedQuote(text="Extracted text here")
    ext = BaseTDAExtraction(
        exact_quotes=[quote],
        localized_anchors_found=["avainsana"],
        contextual_override=False,
        semantic_reasoning="Reasoning text",
    )
    assert len(ext.exact_quotes) == 1
    assert ext.contextual_override is False

    # None coerced to []
    ext_none = BaseTDAExtraction(
        exact_quotes=None,  # type: ignore[arg-type]
        localized_anchors_found=[],
        contextual_override=False,
        semantic_reasoning="Reasoning",
    )
    assert ext_none.exact_quotes == []


def test_base_tda_extraction_override_validation() -> None:
    from backend_v2.models.domain.synthesis import BaseTDAExtraction
    from backend_v2.models.dtos.quote_evidence import LLMExtractedQuote

    quote = LLMExtractedQuote(text="Some text")
    # contextual_override=True with exact_quotes raises ValueError
    with pytest.raises(ValueError, match="cannot be combined with exact_quotes"):
        BaseTDAExtraction(
            exact_quotes=[quote],
            localized_anchors_found=[],
            contextual_override=True,
            semantic_reasoning="Reasoning",
        )

    # contextual_override=False with [CONTEXTUAL_OVERRIDE_APPLIED] quote raises ValueError
    quote_override = LLMExtractedQuote(text="[CONTEXTUAL_OVERRIDE_APPLIED]")
    with pytest.raises(ValueError, match="Cross-validation failed"):
        BaseTDAExtraction(
            exact_quotes=[quote_override],
            localized_anchors_found=[],
            contextual_override=False,
            semantic_reasoning="Reasoning",
        )


def test_matrix_synthesis_group_cardinality() -> None:
    from backend_v2.models.core_base import I18nText
    from backend_v2.models.domain.synthesis import MatrixSynthesisGroup
    from backend_v2.models.enums import PresetView

    title = I18nText(translations={"en": "Title"})

    # 1D with 1 block: ok
    g1 = MatrixSynthesisGroup(
        id="grp_0123456789abcdef",
        title=title,
        target_blocks=["blk_1"],
        view_type=PresetView.METRICS_1D,
    )
    assert len(g1.target_blocks) == 1

    # 1D with 2 blocks: raises
    with pytest.raises(ValueError, match="requires exactly 1 target block"):
        MatrixSynthesisGroup(
            id="grp_0123456789abcdef",
            title=title,
            target_blocks=["blk_1", "blk_2"],
            view_type=PresetView.METRICS_1D,
        )

    # 2D with 2 blocks: ok; with 1 block: raises
    g2 = MatrixSynthesisGroup(
        id="grp_0123456789abcdef",
        title=title,
        target_blocks=["blk_1", "blk_2"],
        view_type=PresetView.COMPARE_2D,
    )
    assert len(g2.target_blocks) == 2

    with pytest.raises(ValueError, match="requires exactly 2 target blocks"):
        MatrixSynthesisGroup(
            id="grp_0123456789abcdef",
            title=title,
            target_blocks=["blk_1"],
            view_type=PresetView.COMPARE_2D,
        )

    # 3D with 3 blocks: ok; with 2 blocks: raises
    g3 = MatrixSynthesisGroup(
        id="grp_0123456789abcdef",
        title=title,
        target_blocks=["blk_1", "blk_2", "blk_3"],
        view_type=PresetView.MATRIX_3D,
    )
    assert len(g3.target_blocks) == 3

    with pytest.raises(ValueError, match="requires exactly 3 target blocks"):
        MatrixSynthesisGroup(
            id="grp_0123456789abcdef",
            title=title,
            target_blocks=["blk_1"],
            view_type=PresetView.MATRIX_3D,
        )

    # TEXT_ONLY with >= 1 blocks: ok
    gt = MatrixSynthesisGroup(
        id="grp_0123456789abcdef",
        title=title,
        target_blocks=["blk_1"],
        view_type=PresetView.TEXT_ONLY,
    )
    assert len(gt.target_blocks) == 1


def test_distilled_evaluation_with_status_and_defaults() -> None:
    from backend_v2.models.domain.synthesis import DistilledEvaluation

    de = DistilledEvaluation(
        atom_id="atm_123",
        status="PASSED",
        exact_quotes=["quote verbatim"],
        semantic_reasoning="Strong evidence",
    )
    assert de.atom_id == "atm_123"
    assert de.status == "PASSED"
    assert de.exact_quotes == ["quote verbatim"]
    assert de.semantic_reasoning == "Strong evidence"
    assert de.extensions is None

    # Forbid extra fields
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        DistilledEvaluation.model_validate({"atom_id": "atm_1", "rogue_field": "disallowed"})


def test_distilled_matrix_payload_dto_valid_and_boundaries() -> None:
    from backend_v2.models.domain import DistilledMatrixPayloadDTO
    from backend_v2.models.domain.synthesis import DistilledEvaluation
    from backend_v2.models.dtos.lightweight_matrix import LevelStatsDTO

    de = DistilledEvaluation(atom_id="atm_1", status="PASSED", exact_quotes=["q1"])
    dto = DistilledMatrixPayloadDTO(
        results=[de],
        normalized_score=85.5,
        level_breakdown={"L1": LevelStatsDTO(hits=1, total=1, dlqs=0)},
    )
    assert len(dto.results) == 1
    assert dto.results[0].atom_id == "atm_1"
    assert dto.normalized_score == 85.5
    assert dto.level_breakdown is not None
    assert dto.level_breakdown["L1"].hits == 1

    # Negative boundary: empty results list triggers ValidationError (min_length=1)
    with pytest.raises(ValidationError, match="too_short"):
        DistilledMatrixPayloadDTO(results=[])

    # Negative boundary: extra fields forbidden
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        DistilledMatrixPayloadDTO.model_validate(
            {"results": [{"atom_id": "atm_1"}], "unauthorized_extra": "forbidden"}
        )

