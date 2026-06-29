from backend_v2.utils.scoring.pure_math_engine import PureMathScoringEngine

stats = {
    5.0: {"hits": 0, "total": 3, "dlqs": 0},
    4.0: {"hits": 1, "total": 1, "dlqs": 0},
    3.0: {"hits": 1, "total": 3, "dlqs": 0},
    2.0: {"hits": 2, "total": 3, "dlqs": 0},
    1.0: {"hits": 0, "total": 3, "dlqs": 0},
}
engine = PureMathScoringEngine()
score, xai, breakdown = engine.calculate(stats, math_min=0.0, math_max=100.0)
print(f"Score with 0-100: {score}")

score2, xai2, breakdown2 = engine.calculate(stats, math_min=1.0, math_max=5.0)
print(f"Score with 1-5: {score2}")
