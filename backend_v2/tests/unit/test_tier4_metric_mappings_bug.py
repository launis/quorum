from typing import Any

from backend_v2.models.v2_core import OutputProfile


def test_worker_db_hydration_metric_mappings_bug() -> None:
    """Verify that worker.py hydrates a raw DB profile containing matrix_synthesis_groups cleanly."""
    db_profile_dict: dict[str, Any] = {
        "id": "prf_1234abcd1234abcd",
        "slug": "test_slug",
        "workflow_id": "wf_1234abcd1234abcd",
        "name": {"translations": {"en": "Title", "fi": "Title"}},
        "matrix_synthesis_groups": [
            {
                "id": "grp_1",
                "title": {"translations": {"en": "Group 1"}},
                "target_blocks": ["blk_1"],
            }
        ],
    }

    active_profile_dto = OutputProfile.model_validate(db_profile_dict, strict=False)
    assert active_profile_dto is not None
    assert len(active_profile_dto.matrix_synthesis_groups) == 1
