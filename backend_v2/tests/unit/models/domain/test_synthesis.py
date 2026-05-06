import pytest
from pydantic import ValidationError

from backend_v2.models.domain.synthesis import SynthesisMetadataDTO, SynthesisStepDataDTO


def test_synthesis_metadata_dto_valid() -> None:
    data = {
        "target_locale": "fi",
        "token_usage": {"prompt_tokens": 10},
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


def test_synthesis_step_data_dto_ignores_extra_fields() -> None:
    data = {
        "reasoning_trace": {"thought_process": "thinking", "conclusion": "acting", "confidence_score": 0.9},
        "invalid_extra_field": 1337,
        "another_field": "value",
    }
    # As a polymorphic extraction schema, it MUST ignore extra fields safely.
    model = SynthesisStepDataDTO.model_validate(data)
    assert model.reasoning_trace is not None
    assert not hasattr(model, "invalid_extra_field")
