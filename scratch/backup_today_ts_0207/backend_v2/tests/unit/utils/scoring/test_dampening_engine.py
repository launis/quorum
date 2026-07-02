from backend_v2.models.enums import CognitiveFlowStatus
from backend_v2.utils.scoring.dampening_engine import DampeningScoringEngine


def test_dampening_engine_calculate() -> None:
    engine = DampeningScoringEngine()
    stats = {
        1.0: {"hits": 1, "total": 1},
        2.0: {"hits": 0, "total": 1},
    }
    score, log, breakdown = engine.calculate(
        stats,
        math_min=1.0,
        math_max=3.0,
    )

    # Mathematical bounds test
    assert score >= 1.0 and score <= 3.0

    log_str = "\n".join(log.engine_debug_trace["log_trace"])

    # String breakdown test for UI
    assert (
        "Tasolta 2.0 saatiin 0 osumaa. Käytetään Strictness 85:n mukaista "
        "joustokerrointa (0.10), joten pisteitä vaimennettiin pehmeästi."
    ) in log_str

    # Standard log checks
    assert "Progressively dampened" in log_str
    assert breakdown["1.0"]["hits"] == 1


def test_dampening_engine_optimal_flow() -> None:
    engine = DampeningScoringEngine()
    stats = {
        1.0: {"hits": 1, "total": 1},
        2.0: {"hits": 1, "total": 1},
    }
    score, log, breakdown = engine.calculate(
        stats,
        math_min=1.0,
        math_max=3.0,
    )
    log_str = "\n".join(log.engine_debug_trace["log_trace"])
    assert CognitiveFlowStatus.OPTIMAL.value in log_str
