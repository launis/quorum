import pytest
from pydantic import ValidationError

from backend_v2.models.enums import ScoringStrategy
from backend_v2.models.v2_core import ExecutionCreate, ExecutionRecord, ReportDataDTO

# Import existing tests so they are included in the coverage run for v2_core.py
from backend_v2.tests.unit.test_v2_core_models import *  # noqa: F403, F401
from backend_v2.tests.unit.test_v2_core_strictness import *  # noqa: F403, F401


def test_execution_create_strictness_level_validation() -> None:
    # Fail if missing
    with pytest.raises(ValidationError) as exc_info:
        ExecutionCreate.model_validate(
            {
                "workflow_id": "wf_123",
                "target_locale": "fi",
                "matrix_sampling_strategy": 10,
                "raw_inputs": {},
                "scoring_strategy": ScoringStrategy.WATERFALL_FLOOR,
            }
        )
    assert "strictness_level" in str(exc_info.value)

    # Fail if < 0
    with pytest.raises(ValidationError) as exc_info_low:
        ExecutionCreate.model_validate(
            {
                "workflow_id": "wf_123",
                "target_locale": "fi",
                "strictness_level": -1,
                "scoring_strategy": ScoringStrategy.WATERFALL_FLOOR,
                "matrix_sampling_strategy": 10,
                "raw_inputs": {},
            }
        )
    assert "greater than or equal to 0" in str(exc_info_low.value)

    # Fail if > 100
    with pytest.raises(ValidationError) as exc_info_high:
        ExecutionCreate.model_validate(
            {
                "workflow_id": "wf_123",
                "target_locale": "fi",
                "strictness_level": 101,
                "scoring_strategy": ScoringStrategy.WATERFALL_FLOOR,
                "matrix_sampling_strategy": 10,
                "raw_inputs": {},
            }
        )
    assert "less than or equal to 100" in str(exc_info_high.value)

    # Success
    valid = ExecutionCreate.model_validate(
        {
            "workflow_id": "wf_123",
            "target_locale": "fi",
            "strictness_level": 50,
            "scoring_strategy": ScoringStrategy.WATERFALL_FLOOR,
            "matrix_sampling_strategy": 10,
            "raw_inputs": {},
        }
    )
    assert valid.strictness_level == 50


def test_execution_record_strictness_level_validation() -> None:
    with pytest.raises(ValidationError) as exc_info:
        ExecutionRecord.model_validate(
            {
                "id": "exe_aaaaaaaaaaaaaaaa",
                "workflow_id": "wf_1",
                "status": "pending",
                "raw_inputs": {},
                "scoring_strategy": ScoringStrategy.WATERFALL_FLOOR,
            }
        )
    assert "strictness_level" in str(exc_info.value)


def test_report_data_dto_strictness_level_validation() -> None:
    with pytest.raises(ValidationError) as exc_info:
        ReportDataDTO.model_validate(
            {
                "workflow_id": "wf_1",
                "profile_id": "prof_1",
                "scoring_strategy": ScoringStrategy.WATERFALL_FLOOR,
            }
        )
    assert "strictness_level" in str(exc_info.value)
