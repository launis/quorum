from unittest.mock import MagicMock

import pytest

from backend_v2.exceptions import AppException
from backend_v2.hooks.context_mapper import ContextMapper
from backend_v2.models.v2_core import PromptBlock


def test_context_mapper_empty_or_wildcard() -> None:
    """Test that empty target blocks or wildcard return empty string."""
    assert ContextMapper.build_ordinal_mapping([]) == ""
    assert ContextMapper.build_ordinal_mapping(["*"]) == ""


def test_context_mapper_fail_fast_on_dict() -> None:
    """Test that passing naked dictionaries triggers the Fail-Fast AppException."""
    with pytest.raises(AppException) as exc_info:
        ContextMapper.build_ordinal_mapping(
            target_blocks=["blk_1"], 
            all_blocks=[{"id": "blk_1"}]  # type: ignore
        )
    assert exc_info.value.status_code == 500
    assert "Internal compilation error" in str(exc_info.value.message)


def test_context_mapper_valid_blocks() -> None:
    """Test that valid PromptBlock instances map correctly with extrema."""
    b1 = MagicMock(spec=PromptBlock)
    b1.id = "blk_1"
    b1.computed_min = 1.0
    b1.computed_max = 5.0
    
    b2 = MagicMock(spec=PromptBlock)
    b2.id = "blk_2"
    b2.computed_min = 0.0
    b2.computed_max = 10.0

    b3 = MagicMock(spec=PromptBlock)
    b3.id = "blk_3"
    b3.computed_min = None
    b3.computed_max = None
    
    result = ContextMapper.build_ordinal_mapping(
        target_blocks=["blk_1", "blk_3"],
        all_blocks=[b1, b2, b3]
    )
    
    assert "=== TARGET DATA MAPPING" in result
    assert "1. Target Data Element -> ID: blk_1 (Absolute Scale Limits: 1.0 to 5.0)" in result
    assert "2. Target Data Element -> ID: blk_3" in result
    assert "(Absolute Scale Limits" not in result.split("blk_3")[1]


def test_context_mapper_global_mapping() -> None:
    """Test that global mapping returns empty string (MVP behavior)."""
    assert ContextMapper.build_global_mapping({}, []) == ""
