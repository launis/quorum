from backend_v2.models.enums import WaterfallThreshold
from backend_v2.utils.math_utils import calculate_soft_waterfall_score, convert_strictness_to_forgiveness
from backend_v2.utils.scoring.base_engine import ScoringEngineBase


class WaterfallScoringEngine(ScoringEngineBase):
    """Guttman scale (Waterfall Floor) implementation with Soft Scaling.

    Finds the highest floor where all criteria pass the threshold.
    If a failure occurs, applies a progressive penalty to higher levels
    based on the strictness level instead of stopping entirely.
    """

    def calculate(
        self, stats: dict[float, dict[str, int]], math_min: float, math_max: float, strictness_level: int = 50
    ) -> tuple[float, str, dict[str, dict[str, int]]]:
        if strictness_level < 30:
            target_threshold = WaterfallThreshold.LENIENT.value
        elif strictness_level > 70:
            target_threshold = WaterfallThreshold.STRICT.value
        else:
            target_threshold = WaterfallThreshold.STANDARD.value

        base_forgiveness = convert_strictness_to_forgiveness(strictness_level)
        floor_score = calculate_soft_waterfall_score(stats, math_min, math_max, target_threshold, base_forgiveness)

        log_lines = ["### Waterfall Evaluation (Soft Benefit of the Doubt) Breakdown:"]
        sorted_levels = sorted(stats.keys())

        current_multiplier = 1.0

        for s_level in sorted_levels:
            level_data = stats[s_level]
            t_hits = level_data["hits"]
            t_total = level_data["total"]

            hit_rate = (t_hits / t_total) if t_total > 0 else 0.0
            pct = int(hit_rate * 100)

            if hit_rate >= target_threshold:
                log_lines.append(
                    f"- **Level {s_level}:** {t_hits}/{t_total} ({pct}% - PASSED) "
                    f"[Multiplier applied: {current_multiplier:.2f}]"
                )
            else:
                next_multiplier = current_multiplier * base_forgiveness
                log_lines.append(
                    f"- **Level {s_level}:** {t_hits}/{t_total} ({pct}% - FAILED) "
                    f"[Partial points: {hit_rate:.2f}. "
                    f"Subsequent multiplier reduced to {next_multiplier:.2f} due to strictness {strictness_level}]"
                )
                current_multiplier = next_multiplier

        log_lines.append("")
        log_lines.append(f"**Final Soft Waterfall Score:** {floor_score:.2f} (Penalty applied deterministically)")

        level_breakdown = {str(k): {"hits": v["hits"], "total": v["total"]} for k, v in stats.items()}

        return float(floor_score), "\n".join(log_lines), level_breakdown
