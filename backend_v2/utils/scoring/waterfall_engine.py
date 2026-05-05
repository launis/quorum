from backend_v2.models.enums import WaterfallThreshold
from backend_v2.utils.math_utils import calculate_waterfall_floor
from backend_v2.utils.scoring.base_engine import ScoringEngineBase


class WaterfallScoringEngine(ScoringEngineBase):
    """Guttman scale (Waterfall Floor) implementation.

    Finds the highest floor where all criteria pass the threshold.
    Stops immediately upon the first failure.
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

        floor_score = calculate_waterfall_floor(stats, math_min, threshold=target_threshold)

        log_lines = ["### Waterfall Evaluation (Guttman Scale) Breakdown:"]
        sorted_levels = sorted(stats.keys())

        failed_at = None

        for s_level in sorted_levels:
            level_data = stats[s_level]
            t_hits = level_data["hits"]
            t_total = level_data["total"]

            hit_rate = (t_hits / t_total) if t_total > 0 else 0.0
            pct = int(hit_rate * 100)

            status = "PASSED" if hit_rate >= target_threshold else "FAILED"

            if failed_at is not None:
                log_lines.append(
                    f"- **Level {s_level}:** {t_hits}/{t_total} (SKIPPED - Blocked by failure at Level {failed_at})"
                )
            else:
                log_lines.append(f"- **Level {s_level}:** {t_hits}/{t_total} ({pct}% - {status})")
                if status == "FAILED":
                    failed_at = s_level

        log_lines.append("")
        log_lines.append(f"**Final Waterfall Score:** {floor_score:.2f} (Absolute floor)")

        level_breakdown = {str(k): {"hits": v["hits"], "total": v["total"]} for k, v in stats.items()}

        return float(floor_score), "\n".join(log_lines), level_breakdown
