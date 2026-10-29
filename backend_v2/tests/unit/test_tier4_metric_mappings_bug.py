from pydantic import JsonValue

from backend_v2.models.domain.output_profile import OutputProfile


def test_worker_db_hydration_metric_mappings_bug() -> None:
    """Verify that worker.py hydrates a raw DB profile containing matrix_synthesis_groups cleanly."""
    db_profile_dict: dict[str, JsonValue] = {
        "id": "prf_0195f3a0000070018234abcd1234abcd",
        "slug": "test_slug",
        "workflow_id": "wf_0195f3a0000070018234abcd1234abcd",
        "name": {"translations": {"en": "Title", "fi": "Title"}},
        "matrix_synthesis_groups": [
            {
                "id": "grp_0195f3a0000070018111111111111111",
                "title": {"translations": {"en": "Group 1"}},
                "target_blocks": ["blk_1"],
            }
        ],
    }

    active_profile_dto = OutputProfile.model_validate(db_profile_dict, strict=False)
    assert active_profile_dto is not None
    assert len(active_profile_dto.matrix_synthesis_groups) == 1
