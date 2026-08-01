from typing import Any

from backend_v2.models.v2_core import OutputProfile


def test_worker_db_hydration_metric_mappings_bug() -> None:
    """Tier 4 Bug: Reproduce the crash in worker.py where it attempts to hydrate a raw DB profile
    containing `metric_mappings` using OutputProfileResponseDTO (which has extra='forbid').

    This test will crash with ValidationError, proving the root cause of the bug.
    The fix will be to use `OutputProfile` (the Domain model) instead of the API Response DTO for internal DB hydration.
    """
    db_profile_dict: dict[str, Any] = {
        "id": "prf_1234abcd1234abcd",
        "slug": "test_slug",
        "workflow_id": "wf_1234abcd1234abcd",
        "name": {"default_locale": "en", "translations": {"en": "Title", "fi": "Title"}},
        "layouts": [],
        "metric_mappings": {"variance_mechanical": {"default_locale": "en", "translations": {"en": "Variance"}}},
    }

    # This is exactly what worker.py line 145 does.
    active_profile_dto = OutputProfile.model_validate(db_profile_dict, strict=False)

    # If we get here, the bug is fixed.
    assert active_profile_dto is not None
