"""Unit tests for the backend_v2.utils package facade exports."""

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText, generate_opaque_id
from backend_v2.models.enums import EntityPrefix
from backend_v2.utils import (
    get_forensic_input_path,
    inflate,
    normalize_evaluation_input,
    ranked_round_robin_select,
)


def test_utils_facade_exports_positive_behavior() -> None:
    """Verify positive execution of utilities exported by backend_v2.utils."""
    exec_id = generate_opaque_id(EntityPrefix.EXECUTION)
    path = get_forensic_input_path(exec_id, "source_doc")
    assert path == f"executions/{exec_id}/inputs/input_source_doc.md"

    normalized = normalize_evaluation_input("  **Hello**   world  ")
    assert normalized == "Hello world"

    assert inflate(None, I18nText) is None

    selected = ranked_round_robin_select(
        items=["alpha", "apricot", "banana"],
        group_key=lambda item: item[:1],
        rank_key=len,
        max_items=2,
    )
    assert selected == ["apricot", "banana"]


def test_utils_facade_get_forensic_input_path_invalid() -> None:
    """Verify get_forensic_input_path raises AppException on path traversal input."""
    with pytest.raises(AppException) as exc_info:
        get_forensic_input_path("../invalid", "source_doc")
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


def test_utils_facade_normalize_evaluation_input_error() -> None:
    """Verify normalize_evaluation_input raises AppException on null byte boundary."""
    with pytest.raises(AppException) as exc_info:
        normalize_evaluation_input("invalid\x00text")
    assert exc_info.value.details["error_code"] == ErrorCodes.INTERNAL_SERVER_ERROR.value
