import logging
from typing import Any

from fastapi import status

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.dtos.lightweight_matrix import LevelStatsDTO, XAILogDto
from backend_v2.models.enums import StrictnessAnchor, WaterfallThreshold
from backend_v2.utils.math_utils import calculate_soft_waterfall_score, get_strictness_config
from backend_v2.utils.scoring.base_engine import ScoringEngineBase

logger = logging.getLogger(__name__)


class WaterfallScoringEngine(ScoringEngineBase):
    """Guttman scale (Waterfall Floor) implementation with Soft Scaling.

    Also known as: 'Koearvostelu'.
    Finds the highest floor where all criteria pass the threshold.
    If a failure occurs, applies a sliding penalty multiplier to higher levels
    based on the shortfall distance and strictness level.

    Attributes:
        None.
    """

    def calculate(
        self,
        stats: dict[float, LevelStatsDTO],
        math_min: float,
        math_max: float,
        strictness_level: int = StrictnessAnchor.STRICT.value,
    ) -> tuple[float, XAILogDto, dict[str, dict[str, int]]]:
        """Executes Guttman Waterfall algorithmic scoring calibration.

        Args:
            stats: Hierarchical execution dictionary containing level stats (hits, total, dlqs).
            math_min: Minimum computational scoring boundary.
            math_max: Maximum computational scoring boundary.
            strictness_level: Forgiveness rating coefficient.

        Returns:
            Tuple holding final computed score, pedagogical XAI metadata DTO, and level breakdowns.

        Raises:
            AppException: If scoring computation or calibration fails.
        """
        try:
            if strictness_level < StrictnessAnchor.RELAXED.value:
                target_threshold: float = float(WaterfallThreshold.LENIENT.value)
            elif strictness_level > StrictnessAnchor.BALANCED.value:
                target_threshold = float(WaterfallThreshold.STRICT.value)
            else:
                target_threshold = float(WaterfallThreshold.STANDARD.value)

            config = get_strictness_config(strictness_level)
            base_forgiveness = float(config.base_forgiveness)

            floor_score = float(
                calculate_soft_waterfall_score(stats, math_min, math_max, target_threshold, base_forgiveness)
            )

            sorted_levels = sorted(stats.keys())
            trace_details: list[dict[str, Any]] = []
            current_multiplier: float = 1.0

            for s_level in sorted_levels:
                level_data = stats[s_level]
                t_hits = level_data.hits
                t_total = level_data.total - (level_data.dlqs or 0)

                hit_rate = (t_hits / t_total) if t_total > 0 else 0.0
                pct = int(hit_rate * 100)
                passed = hit_rate >= target_threshold

                shortfall = 0.0
                sliding_penalty = 1.0
                next_multiplier = current_multiplier

                if passed:
                    trace_details.append(
                        {
                            "level": s_level,
                            "hits": t_hits,
                            "total": t_total,
                            "pct": pct,
                            "passed": True,
                            "multiplier_applied": current_multiplier,
                        }
                    )
                else:
                    if target_threshold > 0.0:
                        shortfall = (target_threshold - hit_rate) / target_threshold

                    sliding_penalty = 1.0 - (shortfall * (1.0 - base_forgiveness))
                    next_multiplier = current_multiplier * sliding_penalty

                    trace_details.append(
                        {
                            "level": s_level,
                            "hits": t_hits,
                            "total": t_total,
                            "pct": pct,
                            "passed": False,
                            "shortfall": shortfall,
                            "penalty_multiplier": sliding_penalty,
                            "subsequent_multiplier": next_multiplier,
                        }
                    )
                    current_multiplier = next_multiplier

            level_breakdown: dict[str, dict[str, int]] = {
                str(k): {"hits": int(v.hits), "total": int(v.total), "dlqs": int(v.dlqs or 0)} for k, v in stats.items()
            }

            engine_debug_trace: dict[str, Any] = {
                "engine": "waterfall",
                "stats": {k: v.model_dump() for k, v in stats.items()},
                "strictness_level": strictness_level,
                "target_threshold": target_threshold,
                "base_forgiveness": base_forgiveness,
                "trace_details": trace_details,
                "final_score": floor_score,
            }

            xai_log = XAILogDto(
                pedagogical_key="xai_waterfall_engine_breakdown",
                engine_debug_trace=engine_debug_trace,
            )

            return floor_score, xai_log, level_breakdown

        except Exception as e:
            logger.error("Waterfall scoring calculation failed dramatically", exc_info=True)
            raise AppException(
                message=f"Scoring calculation failed inside Waterfall Engine: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.CALCULATION_FAILED.value},
            ) from e
