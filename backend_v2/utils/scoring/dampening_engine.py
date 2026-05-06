from backend_v2.models.enums import CognitiveFlowStatus, CognitiveFlowThreshold
from backend_v2.utils.math_utils import calculate_progressive_dampening_score, clamp_score, get_strictness_config
from backend_v2.utils.scoring.base_engine import ScoringEngineBase


class DampeningScoringEngine(ScoringEngineBase):
    """Cognitive Diagnostic Model (CDM) / DINA score implementation.

    Instead of a hard threshold floor, each level acts as a modifier (amplifier/dampener)
    for the subsequent levels using a square root penalty curve.
    """

    def calculate(
        self, stats: dict[float, dict[str, int]], math_min: float, math_max: float, strictness_level: int = 50
    ) -> tuple[float, str, dict[str, dict[str, int]]]:
        config = get_strictness_config(strictness_level)
        dampening_score = calculate_progressive_dampening_score(stats, math_min, math_max, config)

        log_lines = ["### Cognitive Diagnostic Model (CDM) Breakdown:"]
        sorted_levels = sorted(stats.keys())

        modifier = 1.0

        safe_exponent = max(0.2, min(3.0, config.dynamic_exponent))

        for s_level in sorted_levels:
            level_data = stats[s_level]
            t_hits = level_data["hits"]
            t_total = level_data["total"]

            hit_rate = (t_hits / t_total) if t_total > 0 else 0.0
            pct = int(hit_rate * 100)

            effective_hit_rate = config.base_forgiveness + (hit_rate * (1.0 - config.base_forgiveness))
            if effective_hit_rate <= 0.0:
                effective_hit_rate = 0.0

            try:
                modifier_factor = effective_hit_rate**safe_exponent
            except (ValueError, OverflowError, ZeroDivisionError) as e:
                import logging

                logging.getLogger(__name__).error("Math error in DampeningScoringEngine: %s", e)
                modifier_factor = 0.0

            if s_level == math_min:
                modifier = modifier_factor
                if hit_rate == 0.0:
                    log_lines.append(
                        f"- **Level {s_level}:** {t_hits}/{t_total} ({pct}% - Tasolta {s_level} saatiin 0 osumaa. "
                        f"Käytetään Strictness {strictness_level}:n mukaista joustokerrointa "
                        f"({config.base_forgiveness:.2f}), joten pisteitä vaimennettiin pehmeästi.)"
                    )
                else:
                    log_lines.append(
                        f"- **Level {s_level}:** {t_hits}/{t_total} ({pct}% - Cognitive Flow: {modifier:.2f})"
                    )
            else:
                if hit_rate >= CognitiveFlowThreshold.OPTIMAL.value:
                    status = CognitiveFlowStatus.OPTIMAL.value
                elif hit_rate >= CognitiveFlowThreshold.ACCEPTABLE.value:
                    status = f"{CognitiveFlowStatus.ACCEPTABLE.value} ({hit_rate:.2f})"
                else:
                    if hit_rate == 0.0:
                        status = (
                            f"Tasolta {s_level} saatiin 0 osumaa. Käytetään Strictness {strictness_level}:n "
                            f"mukaista joustokerrointa ({config.base_forgiveness:.2f}), "
                            "joten pisteitä vaimennettiin pehmeästi."
                        )
                    else:
                        status = f"{CognitiveFlowStatus.WEAK.value} ({hit_rate:.2f})"

                log_lines.append(f"- **Level {s_level}:** {t_hits}/{t_total} ({pct}% - {status})")
                modifier = modifier * modifier_factor

        log_lines.append("")
        log_lines.append(f"**Final CDM Score:** {dampening_score:.2f} (Progressively dampened)")

        level_breakdown = {str(k): {"hits": v["hits"], "total": v["total"]} for k, v in stats.items()}

        final_score = clamp_score(dampening_score, math_min, math_max)
        return float(final_score), "\n".join(log_lines), level_breakdown
