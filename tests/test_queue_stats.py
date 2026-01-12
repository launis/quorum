"""Tests for Queue Stats Endpoint."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI, Request
from starlette.datastructures import State

from backend.api.admin_router import get_queue_stats
from backend.schemas.admin import QueueStats


@pytest.mark.asyncio
async def test_get_queue_stats_root_success():
    """Test standard success path for ROOT user."""
    # Mock Request and App State
    mock_request = MagicMock(spec=Request)
    mock_app = MagicMock(spec=FastAPI)
    mock_state = MagicMock(spec=State)

    # Mock ArQ Pool
    mock_pool = AsyncMock()
    # Mock return of queued_jobs()
    mock_pool.queued_jobs.return_value = ["job1", "job2"]  # length 2

    mock_state.arq_pool = mock_pool
    mock_app.state = mock_state
    mock_request.app = mock_app

    # Execute
    stats = await get_queue_stats(mock_request)

    # Verify
    assert isinstance(stats, QueueStats)
    assert stats.queued_jobs == 2
    assert stats.active_jobs == 0
    assert stats.dead_jobs == 0


@pytest.mark.asyncio
async def test_get_queue_stats_no_pool():
    """Test behavior when ArQ pool is missing (e.g. Mock DB mode)."""
    mock_request = MagicMock(spec=Request)

    # Alternative: Use a real class or simple object for state
    class SimpleState:
        pass

    mock_request.app.state = SimpleState()  # No arq_pool attr

    # Execute
    stats = await get_queue_stats(mock_request)

    # Verify
    assert stats.queued_jobs == 0


@pytest.mark.asyncio
async def test_get_queue_stats_exception_handling():
    """Test that introspection errors are handled gracefully."""
    mock_request = MagicMock(spec=Request)
    mock_pool = AsyncMock()
    mock_pool.queued_jobs.side_effect = Exception("Redis Down")

    mock_request.app.state.arq_pool = mock_pool

    # Execute
    stats = await get_queue_stats(mock_request)

    # Verify fail-safe (zeros)
    assert stats.queued_jobs == 0
