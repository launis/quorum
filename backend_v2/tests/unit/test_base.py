from typing import Any
from unittest.mock import MagicMock

import pytest

from backend_v2.services.orchestrator.strategies.base import NodeStrategy


class DummyStrategy(NodeStrategy):
    async def execute(self, step: Any, projector: Any, context: Any, frozen_ctx: Any, trace: Any) -> list[Any]:
        return []


@pytest.mark.asyncio
async def test_node_strategy_instantiation() -> None:
    repo = MagicMock()
    compiler = MagicMock()
    strategy = DummyStrategy(
        exec_repo=repo,
        workflow_repo=repo,
        comp_repo=repo,
        identity_repo=repo,
        audit_repo=repo,
        system_repo=repo,
        prompt_compiler=compiler,
    )  # noqa: E501
    assert strategy.exec_repo == repo
