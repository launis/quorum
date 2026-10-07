"""Unit tests for BaseRepository and AppendOnlyRepositoryBase."""

from unittest.mock import AsyncMock

import pytest
from pydantic import ValidationError

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.base import (
    AppendOnlyRepositoryBase,
    BaseRepository,
    VersionIncrementDTO,
)


def test_base_repository_initialization() -> None:
    """Positive: verify BaseRepository initializes with injected StorageDriver."""
    mock_driver = AsyncMock(spec=StorageDriver)
    repo = BaseRepository(mock_driver)
    assert repo.driver is mock_driver


def test_append_only_repository_increment_version_unversioned() -> None:
    """Positive: verify _increment_version assigns version 2 to unversioned ID."""
    mock_driver = AsyncMock(spec=StorageDriver)
    repo = AppendOnlyRepositoryBase(mock_driver)

    result = repo._increment_version("wor_1122334455667788")
    assert result.base_id == "wor_1122334455667788"
    assert result.new_id == "wor_1122334455667788_v2"
    assert result.version == 2


def test_append_only_repository_increment_version_existing_numeric() -> None:
    """Positive: verify _increment_version increments existing numeric version."""
    mock_driver = AsyncMock(spec=StorageDriver)
    repo = AppendOnlyRepositoryBase(mock_driver)

    result = repo._increment_version("wor_1122334455667788_v2")
    assert result.base_id == "wor_1122334455667788"
    assert result.new_id == "wor_1122334455667788_v3"
    assert result.version == 3

    result_high = repo._increment_version("wor_1122334455667788_v99")
    assert result_high.base_id == "wor_1122334455667788"
    assert result_high.new_id == "wor_1122334455667788_v100"
    assert result_high.version == 100


def test_append_only_repository_increment_version_non_digit_suffix() -> None:
    """Negative/Edge: verify _increment_version handles non-digit version suffixes safely."""
    mock_driver = AsyncMock(spec=StorageDriver)
    repo = AppendOnlyRepositoryBase(mock_driver)

    result_alpha = repo._increment_version("wor_1122334455667788_v_draft")
    assert result_alpha.base_id == "wor_1122334455667788"
    assert result_alpha.new_id == "wor_1122334455667788_v2"
    assert result_alpha.version == 2

    result_trailing = repo._increment_version("wor_1122334455667788_v")
    assert result_trailing.base_id == "wor_1122334455667788"
    assert result_trailing.new_id == "wor_1122334455667788_v2"
    assert result_trailing.version == 2


def test_append_only_repository_increment_version_multiple_markers() -> None:
    """Edge: verify _increment_version splits on the rightmost version marker."""
    mock_driver = AsyncMock(spec=StorageDriver)
    repo = AppendOnlyRepositoryBase(mock_driver)

    result = repo._increment_version("wor_v1_snapshot_v4")
    assert result.base_id == "wor_v1_snapshot"
    assert result.new_id == "wor_v1_snapshot_v5"
    assert result.version == 5


def test_version_increment_dto_invariants() -> None:
    """Negative/Boundary: verify VersionIncrementDTO enforces strictness, immutability, and extra=forbid."""
    dto = VersionIncrementDTO(base_id="wor_123", new_id="wor_123_v2", version=2)
    assert dto.base_id == "wor_123"
    assert dto.new_id == "wor_123_v2"
    assert dto.version == 2

    # Immutability check (frozen=True)
    with pytest.raises(ValidationError):
        dto.version = 3

    # Extra fields forbidden check (extra="forbid")
    with pytest.raises(ValidationError):
        VersionIncrementDTO.model_validate(
            {
                "base_id": "wor_123",
                "new_id": "wor_123_v2",
                "version": 2,
                "extra_field": "invalid",
            }
        )

    # Strict type check (strict=True)
    with pytest.raises(ValidationError):
        VersionIncrementDTO.model_validate(
            {
                "base_id": "wor_123",
                "new_id": "wor_123_v2",
                "version": "not_an_int",
            }
        )
