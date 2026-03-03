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
            str: A base64 encoded PNG string of the chart.

        Raises:
            AppException: If generation fails or input is invalid.
        """
        # Fail Fast: Strict Input Validation
        if not scores:
            raise AppException(
                message="Radar chart requires at least one score.",
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.EMPTY_INPUT},
            )

        try:
            # Data preparation
            categories: list[str] = list(scores.keys())
            values: list[float] = list(scores.values())

            # Close the loop
            values += values[:1]
            angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
            angles += angles[:1]

            # Figure setup
            fig = Figure(figsize=(6, 6), dpi=100)
            ax = fig.add_subplot(111, polar=True)

            # Draw axes
            ax.set_theta_offset(np.pi / 2)  # type: ignore
            ax.set_theta_direction(-1)  # type: ignore
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories)

            # --- POLYGON GRID (Spider Web Style) ---
            ax.yaxis.grid(False)
            
            # Dynamic Grid Calculation - match Flutter (only 1 tick or very minimal)
            grid_levels: list[float] = [float(max_val)]

            for level in grid_levels:
                ax.plot(angles, [level] * len(angles), color="lightgrey", linewidth=0.5, linestyle="solid")

            # Draw labels
            label_angle = 0.0
            if len(categories) > 0:
                label_angle = angles[0] + (angles[1] - angles[0]) / 2

            ax.set_rlabel_position(np.degrees(label_angle))  # type: ignore
            ax.set_yticks(grid_levels)
            # Remove text labels for the grid to match Flutter UI
            ax.set_yticklabels([])

            # Ensure 0 is center
            ax.set_ylim(0, float(max_val))

            # Plot data - using Material 3 Purple to match the UI screenshot
            ax.plot(angles, values, linewidth=2, linestyle="solid", color="#6750A4", marker="o", markersize=3)
            ax.fill(angles, values, color="#6750A4", alpha=0.15)

            # Output to base64
            buf = io.BytesIO()
            fig.savefig(buf, format="png", transparent=True, bbox_inches="tight")
            buf.seek(0)
            img_str = base64.b64encode(buf.read()).decode("utf-8")

            return f"data:image/png;base64,{img_str}"

        except Exception as e:
            error_code = ErrorCodes.CHART_GENERATION_FAILED
            error_message = "Failed to generate radar chart."

            logger.error(f"{error_code}: {error_message}: {e}", exc_info=True)
            raise AppException(
                message=error_message,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": error_code, "original_error": str(e)},
            ) from e

    @staticmethod
    def generate_bubble_chart(
        x_val: float,
        y_val: float,
        size_val: float,
        x_label: str = "Cognitive Level (Bloom)",
        y_label: str = "Strategic Depth",
        title: str = "Logic Matrix Position",
    ) -> str:
        """Generates a 2D bubble chart representing the 3D Logic Matrix position.

        Args:
            x_val: Bloom Score (1-6)
            y_val: Strategic Score (1-4)
            size_val: Toulmin Score (determines bubble size)
            x_label: Label for X-axis
            y_label: Label for Y-axis
            title: Chart title

        Returns:
            str: Base64 encoded PNG

        Raises:
            AppException: If generation fails.
        """
        try:
            # Figure setup
            fig = Figure(figsize=(6, 4), dpi=100)
            ax = fig.add_subplot(111)

            # Define Limits (Fixed scales per domain model)
            # Bloom: 1-6, Strategy: 1-4
            ax.set_xlim(0.5, 6.5)
            ax.set_ylim(0.5, 4.5)

            # Grid and Labels
            ax.grid(True, linestyle="--", alpha=0.6)
            ax.set_xlabel(x_label)
            ax.set_ylabel(y_label)
            ax.set_title(title)

            # Display size calculation
            display_size = max(50.0, (size_val + 1.0) * 100.0)

            # Plot the single point
            ax.scatter([x_val], [y_val], s=[display_size], c=["#1976D2"], alpha=0.6, edgecolors="black", linewidth=1)

            # Annotation
            ax.text(
                x_val,
                y_val + 0.3,  # Offset slightly up
                f"Bloom: {x_val:.1f}\nStrat: {y_val:.1f}",
                ha="center",
                va="bottom",
                fontsize=8,
                bbox=dict(facecolor="white", alpha=0.7, edgecolor="none", boxstyle="round,pad=0.2"),
            )

            # Output to base64
            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight")
            buf.seek(0)
            img_str = base64.b64encode(buf.read()).decode("utf-8")

            return f"data:image/png;base64,{img_str}"

        except Exception as e:
            error_code = ErrorCodes.CHART_GENERATION_FAILED
            logger.error(f"{error_code}: Failed to generate bubble chart: {e}", exc_info=True)
            raise AppException(
                message="Failed to generate bubble chart.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": error_code, "original_error": str(e)},
            ) from e
