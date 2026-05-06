from backend_v2.models.dtos.lightweight_matrix import XAILogDto
from backend_v2.models.enums import WaterfallThreshold
from backend_v2.utils.math_utils import calculate_soft_waterfall_score, get_strictness_config
from backend_v2.utils.scoring.base_engine import ScoringEngineBase


class WaterfallScoringEngine(ScoringEngineBase):
    """Guttman scale (Waterfall Floor) implementation with Soft Scaling.

    Now called: 'Koearvostelu'
    Finds the highest floor where all criteria pass the threshold.
    If a failure occurs, applies a sliding penalty multiplier to higher levels
    based on the shortfall distance and strictness level.
    """

    def calculate(
        self, stats: dict[float, dict[str, int]], math_min: float, math_max: float, strictness_level: int = 85
    ) -> tuple[float, XAILogDto, dict[str, dict[str, int]]]:
        if strictness_level < 30:
            target_threshold = WaterfallThreshold.LENIENT.value
        elif strictness_level > 70:
            target_threshold = WaterfallThreshold.STRICT.value
        else:
            target_threshold = WaterfallThreshold.STANDARD.value

        config = get_strictness_config(strictness_level)
        base_forgiveness = config.base_forgiveness

        floor_score = calculate_soft_waterfall_score(stats, math_min, math_max, target_threshold, base_forgiveness)

        log_lines = ["### Koearvostelu Evaluation (Soft Benefit of the Doubt) Breakdown:"]
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
                if target_threshold == 0.0:
                    shortfall = 0.0
                else:
                    shortfall = (target_threshold - hit_rate) / target_threshold

                sliding_penalty = 1.0 - (shortfall * (1.0 - base_forgiveness))
                next_multiplier = current_multiplier * sliding_penalty

                log_lines.append(
                    f"- **Level {s_level}:** {t_hits}/{t_total} ({pct}% - FAILED) "
                    f"[Shortfall: {shortfall:.2f}, Penalty multiplier: {sliding_penalty:.2f}. "
                    f"Subsequent multiplier reduced to {next_multiplier:.2f}]"
                )
                current_multiplier = next_multiplier

        log_lines.append("")
        log_lines.append(f"**Final Koearvostelu Score:** {floor_score:.2f} (Sliding penalty applied)")

        level_breakdown = {str(k): {"hits": v["hits"], "total": v["total"]} for k, v in stats.items()}

        engine_debug_trace = {
            "engine": "waterfall",
            "stats": stats,
            "strictness_level": strictness_level,
            "target_threshold": target_threshold,
            "base_forgiveness": base_forgiveness,
            "log_trace": log_lines,
        }

        xai_log = XAILogDto(
            pedagogical_key="xai_waterfall_engine_breakdown",
            engine_debug_trace=engine_debug_trace,
        )

        return float(floor_score), xai_log, level_breakdown
