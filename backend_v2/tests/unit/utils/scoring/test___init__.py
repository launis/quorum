from backend_v2.utils.scoring import ScoringEngineProtocol, ScoringResultDTO, UnifiedScoringEngine, get_scoring_engine


def test_get_scoring_engine() -> None:
    engine = get_scoring_engine()
    assert isinstance(engine, ScoringEngineProtocol)
    assert isinstance(engine, UnifiedScoringEngine)


def test_get_scoring_engine_legacy_arg() -> None:
    engine = get_scoring_engine("WATERFALL")
    assert isinstance(engine, ScoringEngineProtocol)
    assert isinstance(engine, UnifiedScoringEngine)

