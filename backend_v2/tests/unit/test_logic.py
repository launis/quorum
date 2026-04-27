from unittest.mock import MagicMock

import pytest

from backend_v2.exceptions import AppException
from backend_v2.services.orchestrator.strategies.logic import LogicNodeStrategy


@pytest.mark.asyncio
async def test_logic_strategy_missing_blueprint() -> None:
    repo = MagicMock()
    compiler = MagicMock()
    strategy = LogicNodeStrategy(repo, compiler)

    step = MagicMock()
    step.task_blueprint = None
    step.id = "step_123"

    projector = MagicMock()
    projector.snapshot = {}

    context = MagicMock()

    with pytest.raises(AppException) as excinfo:
        await strategy.execute(step, projector, context, None, [])

    assert "has no task_blueprint configured" in str(excinfo.value.message)
