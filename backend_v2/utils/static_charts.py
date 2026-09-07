"""Static zero-math chart generation utility for PDF export.

Injects structural Server-Driven chart parity by generating Base64 PNG
strings mapped natively from the validated Pydantic DTOs.
"""

import base64
import io
import logging
import math
from math import pi

from fastapi import status

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.v2_core import MatrixScorecardRowDTO
from backend_v2.services.localization import LocalizationService

logger = logging.getLogger(__name__)


def generate_scatter_chart(axes: list[MatrixScorecardRowDTO]) -> str:
    """Generate a Cartesian 2D scatter matrix plot from the provided axes.

    Strict parity with Flutter's LogicMatrixChart.

    Args:
        axes: The validated list of axes. Minimal required length is 2.

    Returns:
        A Base64 string literal of the generated PNG file.

    Raises:
        AppException: If chart generation fails or if insufficient axes are provided.
    """
    if len(axes) < 2:
        raise AppException(
            message="Scatter chart requires at least 2 axes.",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA.value},
        )

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    try:
        x_axis = axes[0]
        y_axis = axes[1]
        z_axis = axes[2] if len(axes) > 2 else None

        x_val = x_axis.score if x_axis.score is not None else 0.0
        y_val = y_axis.score if y_axis.score is not None else 0.0

        x_min = x_axis.scale_min if x_axis.scale_min is not None else 0.0
        x_max = x_axis.scale_max if x_axis.scale_max is not None else 6.0
        if x_max <= x_min:
            x_max = x_min + 6.0

        y_min = y_axis.scale_min if y_axis.scale_min is not None else 0.0
        y_max = y_axis.scale_max if y_axis.scale_max is not None else 6.0
        if y_max <= y_min:
            y_max = y_min + 6.0

        area = 300
        if z_axis and z_axis.score is not None:
            # Use SDUI pre-calculated plot ratio if available, otherwise fallback
            pct = z_axis.ui_plot_ratio if z_axis.ui_plot_ratio is not None else 0.5
            # Mapped to 6x visual diameter contrast (sqrt(1800/50) = 6) to match Flutter UI
            area = int(50 + (pct * 1750))

        fig, ax = plt.subplots(figsize=(6, 4))

        ax.scatter([x_val], [y_val], s=area, c="#2196F3", alpha=0.7, edgecolors="#0D47A1", linewidths=2)

        x_range = x_max - x_min
        x_margin = math.pow(10, math.floor(math.log10(max(1.0, x_range - 0.001))))

        y_range = y_max - y_min
        y_margin = math.pow(10, math.floor(math.log10(max(1.0, y_range - 0.001))))

        ax.set_xlim(x_min - x_margin, x_max + x_margin)
        ax.set_ylim(y_min - y_margin, y_max + y_margin)

        x_mid = (x_min + x_max) / 2
        y_mid = (y_min + y_max) / 2

        ax.axhline(y=y_mid, color="gray", linestyle="--", alpha=0.5)
        ax.axvline(x=x_mid, color="gray", linestyle="--", alpha=0.5)

        ax.set_xlabel(f"{x_axis.name} ({x_val} / {x_max})", fontsize=10)
        ax.set_ylabel(f"{y_axis.name} ({y_val} / {y_max})", fontsize=10)
        ax.grid(True, linestyle=":", alpha=0.6)

        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", transparent=True)
        plt.close(fig)

        return base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception as e:
        logger.error("Scatter chart generation failed", exc_info=True)
        raise AppException(
            message=f"Scatter chart generation failed: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.CHART_GENERATION_FAILED.value},
        ) from e


def generate_quadrant_matrix_chart(
    axes: list[MatrixScorecardRowDTO],
    locale: str = "fi",
) -> str:
    """Generate a 2D Quadrant Matrix plot with 4 diagnostic quadrants for Variance Validation.

    Strict parity with Flutter's QuadrantMatrixChart.

    Args:
        axes: The validated list of axes. Minimal required length is 2.
        locale: Target locale for quadrant titles and labels (default: "fi").

    Returns:
        A Base64 string literal of the generated PNG file.

    Raises:
        AppException: If chart generation fails or if insufficient axes are provided.
    """
    if len(axes) < 2:
        raise AppException(
            message="Quadrant matrix chart requires at least 2 axes.",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA.value},
        )

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    try:
        x_axis = axes[0]
        y_axis = axes[1]
        z_axis = axes[2] if len(axes) > 2 else None

        x_val = x_axis.score if x_axis.score is not None else 0.0
        y_val = y_axis.score if y_axis.score is not None else 0.0

        x_min = x_axis.scale_min if x_axis.scale_min is not None else 0.0
        x_max = x_axis.scale_max if x_axis.scale_max is not None else 6.0
        if x_max <= x_min:
            x_max = x_min + 6.0

        y_min = y_axis.scale_min if y_axis.scale_min is not None else 0.0
        y_max = y_axis.scale_max if y_axis.scale_max is not None else 6.0
        if y_max <= y_min:
            y_max = y_min + 6.0

        area = 300
        if z_axis and z_axis.score is not None:
            # Use SDUI pre-calculated plot ratio if available, otherwise fallback
            pct = z_axis.ui_plot_ratio if z_axis.ui_plot_ratio is not None else 0.5
            # Mapped to 6x visual diameter contrast (sqrt(1800/50) = 6) to match Flutter UI
            area = int(50 + (pct * 1750))

        fig, ax = plt.subplots(figsize=(6, 4))

        x_range = x_max - x_min
        if x_range <= 5.0:
            x_margin = 0.05 * x_range
        else:
            x_margin = math.pow(10, math.floor(math.log10(max(1.0, x_range - 0.001))))

        y_range = y_max - y_min
        if y_range <= 5.0:
            y_margin = 0.05 * y_range
        else:
            y_margin = math.pow(10, math.floor(math.log10(max(1.0, y_range - 0.001))))

        x_plot_min = x_min - x_margin
        x_plot_max = x_max + x_margin
        y_plot_min = y_min - y_margin
        y_plot_max = y_max + y_margin

        ax.set_xlim(x_plot_min, x_plot_max)
        ax.set_ylim(y_plot_min, y_plot_max)

        x_mid = (x_min + x_max) / 2
        y_mid = (y_min + y_max) / 2

        # 4 Diagnostic Quadrants shading
        # Top-Left (Q2): Soft warm amber
        ax.fill_between([x_plot_min, x_mid], y_mid, y_plot_max, color="#FFF3E0", alpha=0.6, zorder=0)
        # Top-Right (Q1): Soft sage teal
        ax.fill_between([x_mid, x_plot_max], y_mid, y_plot_max, color="#E0F2F1", alpha=0.6, zorder=0)
        # Bottom-Left (Q3): Neutral light gray
        ax.fill_between([x_plot_min, x_mid], y_plot_min, y_mid, color="#F5F5F5", alpha=0.6, zorder=0)
        # Bottom-Right (Q4): Soft light green
        ax.fill_between([x_mid, x_plot_max], y_plot_min, y_mid, color="#E8F5E9", alpha=0.6, zorder=0)

        # Quadrant divider crosshairs
        ax.axhline(y=y_mid, color="#9E9E9E", linestyle="--", alpha=0.6, zorder=1)
        ax.axvline(x=x_mid, color="#9E9E9E", linestyle="--", alpha=0.6, zorder=1)

        # Localized corner annotations for the 4 quadrants
        q_tl = LocalizationService.translate("quadrant_top_left_title", locale)
        q_tr = LocalizationService.translate("quadrant_top_right_title", locale)
        q_bl = LocalizationService.translate("quadrant_bottom_left_title", locale)
        q_br = LocalizationService.translate("quadrant_bottom_right_title", locale)

        ax.text(
            0.03,
            0.96,
            q_tl,
            transform=ax.transAxes,
            fontsize=8,
            color="#555555",
            ha="left",
            va="top",
            style="italic",
            weight="bold",
            zorder=2,
        )
        ax.text(
            0.97,
            0.96,
            q_tr,
            transform=ax.transAxes,
            fontsize=8,
            color="#555555",
            ha="right",
            va="top",
            style="italic",
            weight="bold",
            zorder=2,
        )
        ax.text(
            0.03,
            0.04,
            q_bl,
            transform=ax.transAxes,
            fontsize=8,
            color="#555555",
            ha="left",
            va="bottom",
            style="italic",
            weight="bold",
            zorder=2,
        )
        ax.text(
            0.97,
            0.04,
            q_br,
            transform=ax.transAxes,
            fontsize=8,
            color="#555555",
            ha="right",
            va="bottom",
            style="italic",
            weight="bold",
            zorder=2,
        )

        # Plot data point with high-contrast edge and circular callout
        ax.scatter([x_val], [y_val], s=area, c="#2196F3", alpha=0.85, edgecolors="#0D47A1", linewidths=2, zorder=5)
        ax.annotate(
            f"({x_val:.2f}, {y_val:.2f})",
            (x_val, y_val),
            textcoords="offset points",
            xytext=(8, 8),
            ha="left",
            fontsize=9,
            fontweight="bold",
            color="#0D47A1",
            bbox=dict(boxstyle="round,pad=0.2", fc="#FFFFFF", ec="#2196F3", alpha=0.9),
            zorder=6,
        )

        ax.set_xlabel(f"{x_axis.name} ({x_val:.2f} / {x_max})", fontsize=10)
        ax.set_ylabel(f"{y_axis.name} ({y_val:.2f} / {y_max})", fontsize=10)
        ax.grid(True, linestyle=":", alpha=0.4, zorder=1)

        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", transparent=True)
        plt.close(fig)

        return base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception as e:
        logger.error("Quadrant matrix chart generation failed", exc_info=True)
        raise AppException(
            message=f"Quadrant matrix chart generation failed: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.CHART_GENERATION_FAILED.value},
        ) from e


def generate_radar_chart(axes: list[MatrixScorecardRowDTO]) -> str:
    """Generate a polar 3D Radar chart for N-dimensional datasets.

    Strict parity with Flutter's RadarChart layout block.

    Args:
        axes: The validated list of axes. Minimal required length is 3.

    Returns:
        A Base64 string literal of the generated PNG radar polygon.

    Raises:
        AppException: If chart generation fails or if insufficient axes are provided.
    """
    if len(axes) < 3:
        raise AppException(
            message="Radar chart requires at least 3 axes.",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA.value},
        )

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    try:
        num_vars = len(axes)
        angles = [n / float(num_vars) * 2 * pi for n in range(num_vars)]
        angles += angles[:1]

        values = []
        names = []

        for axis in axes:
            score = axis.score if axis.score is not None else 0.0
            values.append(score)
            names.append(axis.name)

        values += values[:1]

        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={"polar": True})

        max_scale = max((a.scale_max for a in axes if a.scale_max is not None), default=6.0)
        min_scale = min((a.scale_min for a in axes if a.scale_min is not None), default=0.0)

        ax.set_theta_offset(pi / 2)  # type: ignore[attr-defined]
        ax.set_theta_direction(-1)  # type: ignore[attr-defined]

        ax.set_xticks(angles[:-1])
        wrapped_names = [n.replace(" ", "\n") for n in names]
        ax.set_xticklabels(wrapped_names, size=8)

        ax.set_ylim(min_scale, max_scale)

        ax.plot(angles, values, linewidth=2, linestyle="solid", label="Score")
        ax.fill(angles, values, "b", alpha=0.25)

        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", transparent=True)
        plt.close(fig)

        return base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception as e:
        logger.error("Radar chart generation failed", exc_info=True)
        raise AppException(
            message=f"Radar chart generation failed: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.CHART_GENERATION_FAILED.value},
        ) from e
