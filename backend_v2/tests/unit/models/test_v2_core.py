from backend_v2.models.v2_core import ReportDataDTO

# Import existing tests so they are included in the coverage run for v2_core.py
from backend_v2.tests.unit.test_v2_core_models import *  # noqa: F403, F401
from backend_v2.tests.unit.test_v2_core_strictness import *  # noqa: F403, F401


def test_report_data_dto_strictness_level_validation() -> None:
    dto = ReportDataDTO.model_validate(
        {
            "workflow_id": "wf_1",
            "profile_id": "prof_1",
        }
    )
    assert dto.strictness_level is None
