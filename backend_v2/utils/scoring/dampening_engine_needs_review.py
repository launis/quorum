import logging

from backend_v2.models.dtos.lightweight_matrix import XAILogDto
from backend_v2.models.enums import CognitiveFlowStatus, CognitiveFlowThreshold
from backend_v2.utils.math_utils import calculate_progressive_dampening_score, clamp_score, get_strictness_config
from backend_v2.utils.scoring.base_engine import ScoringEngineBase

logger = logging.getLogger(__name__)


class DampeningScoringEngine(ScoringEngineBase):
    """Cognitive Diagnostic Model (CDM) / DINA score implementation.

    Instead of a hard threshold floor, each level acts as a modifier (amplifier/dampener)
    for the subsequent levels using a square root penalty curve.
    """

    def calculate(
        self, stats: dict[float, dict[str, int]], math_min: float, math_max: float, strictness_level: int = 50
    ) -> tuple[float, XAILogDto, dict[str, dict[str, int]]]:
        """Calculates progressive dampening scores based on cognitive diagnostic model concepts.

        Args:
            stats: Dictionary mapping level floats to hits and total counts.
            math_min: Minimum mathematical threshold boundaries.
            math_max: Maximum mathematical threshold boundaries.
            strictness_level: Strictness level configuration from 0 to 100.

        Returns:
            A tuple containing the final calculated score, XAILogDto, and a serializable level breakdown.
        """
        config = get_strictness_config(strictness_level)
        dampening_score = calculate_progressive_dampening_score(stats, math_min, math_max, config)

        log_lines = ["COGNITIVE_BREAKDOWN_TITLE"]
        sorted_levels = sorted(stats.keys())

        modifier = 1.0
        safe_exponent = max(0.2, min(3.0, config.dynamic_exponent))

        for s_level in sorted_levels:
            level_data = stats[s_level]
            t_hits = level_data["hits"]
            t_total = level_data["total"] - level_data.get("dlqs", 0)

            hit_rate = (t_hits / t_total) if t_total > 0 else 0.0
            pct = int(hit_rate * 100)

            effective_hit_rate = config.base_forgiveness + (hit_rate * (1.0 - config.base_forgiveness))
            if effective_hit_rate <= 0.0:
                effective_hit_rate = 0.0

            try:
                modifier_factor = effective_hit_rate**safe_exponent
            except (ValueError, OverflowError, ZeroDivisionError) as e:
                logger.error("Math error in DampeningScoringEngine: %s", e, exc_info=True)
                modifier_factor = 0.0

            if s_level == math_min:
                modifier = modifier_factor
                if hit_rate == 0.0:
                    log_lines.append(
                        f"LEVEL_{s_level}_HITS_{t_hits}_TOTAL_{t_total}_PCT_{pct}_ZERO_HITS_BASE_FORGIVENESS_{config.base_forgiveness:.2f}"
                    )
                else:
                    log_lines.append(f"LEVEL_{s_level}_HITS_{t_hits}_TOTAL_{t_total}_PCT_{pct}_FLOW_{modifier:.2f}")
            else:
                if hit_rate >= CognitiveFlowThreshold.OPTIMAL.value:
                    status_str = CognitiveFlowStatus.OPTIMAL.value
                elif hit_rate >= CognitiveFlowThreshold.ACCEPTABLE.value:
                    status_str = f"{CognitiveFlowStatus.ACCEPTABLE.value}_{hit_rate:.2f}"
                else:
                    if hit_rate == 0.0:
                        status_str = f"LEVEL_{s_level}_ZERO_HITS_BASE_FORGIVENESS_{config.base_forgiveness:.2f}"
                    else:
                        status_str = f"{CognitiveFlowStatus.WEAK.value}_{hit_rate:.2f}"

                log_lines.append(f"LEVEL_{s_level}_HITS_{t_hits}_TOTAL_{t_total}_PCT_{pct}_STATUS_{status_str}")
                modifier = modifier * modifier_factor

        log_lines.append(f"FINAL_CDM_SCORE_{dampening_score:.2f}")

        level_breakdown = {
            str(k): {"hits": v["hits"], "total": v["total"], "dlqs": v.get("dlqs", 0)} for k, v in stats.items()
        }

        final_score = clamp_score(dampening_score, math_min, math_max)

        engine_debug_trace = {
            "engine": "dampening",
            "stats": stats,
            "strictness_level": strictness_level,
            "config": config.model_dump() if hasattr(config, "model_dump") else getattr(config, "dict", lambda: {})(),
            "log_trace": log_lines,
        }

        xai_log = XAILogDto(
            pedagogical_key="xai_dampening_engine_breakdown",
            engine_debug_trace=engine_debug_trace,
        )

        return float(final_score), xai_log, level_breakdown
