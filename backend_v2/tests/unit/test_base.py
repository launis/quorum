from unittest.mock import MagicMock

import pytest

from backend_v2.services.orchestrator.strategies.base import NodeStrategy


class DummyStrategy(NodeStrategy):
    async def execute(self, step, projector, context, frozen_ctx, trace):
        return []


@pytest.mark.asyncio
async def test_node_strategy_instantiation():
    repo = MagicMock()
    compiler = MagicMock()
    strategy = DummyStrategy(repo, compiler)
    assert strategy.repository == repo
