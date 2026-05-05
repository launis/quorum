from backend_v2.models.enums import CognitiveFlowStatus, CognitiveFlowThreshold
from backend_v2.utils.math_utils import calculate_progressive_dampening_score
from backend_v2.utils.scoring.base_engine import ScoringEngineBase


class DampeningScoringEngine(ScoringEngineBase):
    """Cognitive Diagnostic Model (CDM) / DINA score implementation.

    Instead of a hard threshold floor, each level acts as a modifier (amplifier/dampener)
    for the subsequent levels using a square root penalty curve.
    """

    def calculate(
        self, stats: dict[float, dict[str, int]], math_min: float, math_max: float, strictness_level: int = 50
    ) -> tuple[float, str, dict[str, dict[str, int]]]:
        dampening_score = calculate_progressive_dampening_score(stats, math_min, math_max)

        log_lines = ["### Cognitive Diagnostic Model (CDM) Breakdown:"]
        sorted_levels = sorted(stats.keys())

        modifier = 1.0

        for s_level in sorted_levels:
            level_data = stats[s_level]
            t_hits = level_data["hits"]
            t_total = level_data["total"]

            hit_rate = (t_hits / t_total) if t_total > 0 else 0.0
            pct = int(hit_rate * 100)

            if s_level == math_min:
                modifier = hit_rate
                log_lines.append(f"- **Level {s_level}:** {t_hits}/{t_total} ({pct}% - Cognitive Flow: {modifier:.2f})")
            else:
                if hit_rate >= CognitiveFlowThreshold.OPTIMAL.value:
                    status = CognitiveFlowStatus.OPTIMAL.value
                elif hit_rate >= CognitiveFlowThreshold.ACCEPTABLE.value:
                    status = f"{CognitiveFlowStatus.ACCEPTABLE.value} ({hit_rate:.2f})"
                else:
                    status = f"{CognitiveFlowStatus.WEAK.value} ({hit_rate:.2f})"

                log_lines.append(f"- **Level {s_level}:** {t_hits}/{t_total} ({pct}% - {status})")
                modifier = modifier * hit_rate

        log_lines.append("")
        log_lines.append(f"**Final CDM Score:** {dampening_score:.2f} (Progressively dampened)")

        level_breakdown = {str(k): {"hits": v["hits"], "total": v["total"]} for k, v in stats.items()}

        return float(dampening_score), "\n".join(log_lines), level_breakdown
