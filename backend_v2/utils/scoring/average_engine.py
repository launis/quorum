from backend_v2.utils.math_utils import calculate_weighted_score, convert_strictness_to_forgiveness
from backend_v2.utils.scoring.base_engine import ScoringEngineBase


class PureAverageScoringEngine(ScoringEngineBase):
    """Pure Average implementation (Linear, unweighted).

    Transforms the matrix statistics so that all scale levels have the same weight (1.0).
    Calculates the exact ratio of hits vs total criteria across the entire matrix.
    """

    def calculate(
        self, stats: dict[float, dict[str, int]], math_min: float, math_max: float, strictness_level: int = 50
    ) -> tuple[float, str, dict[str, dict[str, int]]]:
        # Flattens the weights to 1.0 for all levels
        flattened_stats = {
            1.0: {"hits": sum(v["hits"] for v in stats.values()), "total": sum(v["total"] for v in stats.values())}
        }

        # Calculate unweighted score. Since weight is 1.0, math_min and math_max are implicitly scaled
        # We want the output to be scaled mathematically identically to the others.
        # calculate_weighted_score natively maps the percentage of achieved points to the scale.
        base_forgiveness = convert_strictness_to_forgiveness(strictness_level)
        exponent = 1.0 + (1.0 - base_forgiveness)
        pure_score = calculate_weighted_score(flattened_stats, math_min, math_max, exponent)

        log_lines = ["### Pure Average Breakdown (Linear Ratio):"]

        total_hits = flattened_stats[1.0]["hits"]
        total_criteria = flattened_stats[1.0]["total"]

        hit_rate = (total_hits / total_criteria) if total_criteria > 0 else 0.0
        pct = int(hit_rate * 100)

        log_lines.append(f"- **Total Hit Ratio:** {total_hits}/{total_criteria} ({pct}%)")
        log_lines.append("")
        log_lines.append(
            f"**Final Pure Average Score:** {pure_score:.2f} (Mapped to scale {math_min}-{math_max} "
            f"with exponent {exponent:.2f} based on strictness {strictness_level})"
        )

        level_breakdown = {str(k): {"hits": v["hits"], "total": v["total"]} for k, v in stats.items()}

        return float(pure_score), "\n".join(log_lines), level_breakdown


class WeightedAverageScoringEngine(ScoringEngineBase):
    """Weighted Average implementation.

    Calculates the global weighted average of all matrix atoms,
    using the matrix scale levels natively as the mathematical weights.
    """

    def calculate(
        self, stats: dict[float, dict[str, int]], math_min: float, math_max: float, strictness_level: int = 50
    ) -> tuple[float, str, dict[str, dict[str, int]]]:
        base_forgiveness = convert_strictness_to_forgiveness(strictness_level)
        exponent = 1.0 + (1.0 - base_forgiveness)
        weighted_score = calculate_weighted_score(stats, math_min, math_max, exponent)

        log_lines = ["### Weighted Average Breakdown:"]
        sorted_levels = sorted(stats.keys())

        achieved_weights = 0.0
        max_weights = 0.0

        for s_level in sorted_levels:
            level_data = stats[s_level]
            t_hits = level_data["hits"]
            t_total = level_data["total"]

            achieved_weights += t_hits * s_level
            max_weights += t_total * s_level

            log_lines.append(f"- **Level {s_level} (Weight x{s_level}):** {t_hits}/{t_total} hits")

        ratio = (achieved_weights / max_weights) if max_weights > 0 else 0.0
        pct = int(ratio * 100)

        log_lines.append("")
        log_lines.append(f"- **Weighted Points Achieved:** {achieved_weights:.1f} / {max_weights:.1f} ({pct}%)")
        log_lines.append(
            f"**Final Weighted Score:** {weighted_score:.2f} (Proportionally mapped to scale "
            f"{math_min}-{math_max} with exponent {exponent:.2f})"
        )

        level_breakdown = {str(k): {"hits": v["hits"], "total": v["total"]} for k, v in stats.items()}

        return float(weighted_score), "\n".join(log_lines), level_breakdown
