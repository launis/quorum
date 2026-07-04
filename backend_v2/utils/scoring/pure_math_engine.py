"""Pure Math Scoring Engine for Phase 9 Cognitive Quorum.

Enables pure mathematically linear weighted average scoring without any strictness curves or outlier mitigation.
"""

from backend_v2.models.dtos.lightweight_matrix import XAILogDto
from backend_v2.models.enums import StrictnessAnchor
from backend_v2.utils.scoring.base_engine import ScoringEngineBase


class PureMathScoringEngine(ScoringEngineBase):
    """Pure Math Scoring implementation.

    Calculates the exact ratio of achieved weighted hits vs maximum possible weighted hits.
    Ignores strictness completely, returning a pure direct proportional score normalized to math bounds.
    """

    def calculate(
        self,
        stats: dict[float, dict[str, int]],
        math_min: float,
        math_max: float,
        strictness_level: int = StrictnessAnchor.STANDARD.value,
    ) -> tuple[float, XAILogDto, dict[str, dict[str, int]]]:
        """Calculate pure linear weighted ratio across score levels.

        Args:
            stats: Dictionary mapping scale levels to hits, total, and optional dlqs count.
            math_min: The minimum score threshold representing scale_min.
            math_max: The maximum score limit representing scale_max.
            strictness_level: The user strictness input mapped on 0-100 range. (Ignored in Pure Math).

        Returns:
            A tuple containing:
                - The computed float final score.
                - An XAILogDto filled with diagnostic trace timelines.
                - A dictionary breakdown of the scores per level stringified.
        """
        log_lines: list[str] = ["Puhdas Matematiikka Breakdown (No Strictness):"]
        sorted_levels = sorted(stats.keys())

        achieved_weights = 0.0
        max_weights = 0.0

        for s_level in sorted_levels:
            level_data = stats[s_level]
            t_hits = level_data["hits"]
            eff_total = level_data["total"] - level_data.setdefault("dlqs", 0)

            achieved_weights += t_hits * s_level
            max_weights += eff_total * s_level

            log_lines.append(f"Level {s_level} (Weight x{s_level}): {t_hits}/{eff_total} hits")

        ratio = (achieved_weights / max_weights) if max_weights > 0 else 0.0
        pct = int(ratio * 100)

        # Map to math bounds (direct proportional interpolation)
        pure_score = math_min + (ratio * (math_max - math_min))

        log_lines.append(f"Weighted Points Achieved: {achieved_weights:.1f} / {max_weights:.1f} ({pct}%)")
        log_lines.append(f"Final Pure Math Score: {pure_score:.2f} (Mapped directly to scale {math_min}-{math_max})")

        level_breakdown = {
            str(k): {"hits": int(v["hits"]), "total": int(v["total"]), "dlqs": int(v.setdefault("dlqs", 0))}
            for k, v in stats.items()
        }

        engine_debug_trace = {
            "engine": "pure_math",
            "stats": stats,
            "strictness_level": "IGNORED",
            "log_trace": log_lines,
        }

        xai_log = XAILogDto(
            pedagogical_key="xai_pure_math_engine_breakdown",
            engine_debug_trace=engine_debug_trace,
        )

        return float(pure_score), xai_log, level_breakdown
