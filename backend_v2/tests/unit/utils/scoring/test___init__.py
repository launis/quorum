from unittest.mock import AsyncMock
import importlib
import sys

import pytest

import backend_v2.utils.scoring
from backend_v2.exceptions import AppException
from backend_v2.models.enums import ScoringStrategy

importlib.reload(backend_v2.utils.scoring)
sys.modules["backend_v2.utils.scoring.__init__"] = backend_v2.utils.scoring
from backend_v2.utils.scoring import get_scoring_engine
from backend_v2.utils.scoring.base_engine import ScoringEngineBase


def test_get_scoring_engine() -> None:
    engine = get_scoring_engine(ScoringStrategy.WATERFALL)
    assert isinstance(engine, ScoringEngineBase)


def test_get_scoring_engine_invalid() -> None:
    with pytest.raises(AppException):
        get_scoring_engine("invalid_strategy")
