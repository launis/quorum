import base64
import io
import logging

import numpy as np  # type: ignore
from fastapi import status
from matplotlib.figure import Figure  # type: ignore

from backend.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)

class ChartService:
    """Service for generating static visualization assets."""

    @staticmethod
    def generate_radar_chart(scores: dict[str, float], max_val: int = 4) -> str:
        """Generates a radar (spider) chart from the provided scores.

        Args:
            scores: A dictionary mapping dimension names to float scores.
            max_val: The maximum value for the chart scale (outermost ring).

        Returns:
            A base64 encoded PNG string of the chart.
        """
        if not scores:
            return ""

        try:
            # Data preparation
            categories = list(scores.keys())
            values = list(scores.values())

            # Close the loop
            values += values[:1]
            angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
            angles += angles[:1]

            # Figure setup
            fig = Figure(figsize=(6, 6), dpi=100)
            ax = fig.add_subplot(111, polar=True)

            # Draw axes
            ax.set_theta_offset(np.pi / 2)
            ax.set_theta_direction(-1)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories)

            # --- POLYGON GRID (Spider Web Style) ---
            ax.yaxis.grid(False)

            # Dynamic Grid Calculation
            # Determine steps based on magnitude
            if max_val <= 5:
                grid_levels = list(range(1, max_val + 1)) # 1, 2, 3, 4, 5
            elif max_val <= 10:
                grid_levels = list(range(2, max_val + 1, 2)) # 2, 4, 6, 8, 10
            elif max_val == 50:
                # Special case for 10-50 scale: 10, 20, 30, 40, 50
                grid_levels = [10, 20, 30, 40, 50]
            elif max_val == 100:
                # Special case for 0-100 scale: 20, 40, 60, 80, 100
                grid_levels = [20, 40, 60, 80, 100]
            else:
                # Generic fallback: 4 quartiles
                step = max_val / 4
                # Use round numbers if possible
                grid_levels = [step, step*2, step*3, max_val]
                # Cast to int if whole numbers
                grid_levels = [int(l) if l.is_integer() else l for l in grid_levels]

            for level in grid_levels:
                ax.plot(angles, [level] * len(angles), color='grey', linewidth=0.5, linestyle=':')

            # Draw labels
            label_angle = 0
            if len(categories) > 0:
                label_angle = angles[0] + (angles[1] - angles[0])/2

            ax.set_rlabel_position(np.degrees(label_angle))
            ax.set_yticks(grid_levels)
            ax.set_yticklabels([str(l) for l in grid_levels], color="grey", size=7)

            # Ensure 0 is center
            ax.set_ylim(0, max_val)

            # Plot data
            ax.plot(angles, values, linewidth=1, linestyle='solid', color='#1A73E8', marker='o', markersize=4)
            ax.fill(angles, values, color='#1A73E8', alpha=0.25)

            # Annotate values
            for angle, val, label in zip(angles[:-1], values[:-1], categories):
                # Add text annotation
                # Adjust radial position slightly outward for visibility; use simple alignment
                ax.text(angle, val + 0.3, f"{val:.1f}", ha='center', va='center', size=8, color='#1A73E8', weight='bold')

            # Output to base64
            buf = io.BytesIO()
            fig.savefig(buf, format='png', transparent=True, bbox_inches='tight')
            buf.seek(0)
            img_str = base64.b64encode(buf.read()).decode('utf-8')

            return f"data:image/png;base64,{img_str}"

        except Exception as e:
            error_code = ErrorCodes.CHART_GENERATION_FAILED
            error_message = "Failed to generate radar chart."

            logger.error(
                f"{error_code}: {error_message}: {e}",
                exc_info=True
            )
            raise AppException(
                message=error_message,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": error_code, "original_error": str(e)}
            ) from e
