"""Static zero-math chart generation utility for PDF export.

Injects structural Server-Driven chart parity by generating Base64 PNG
strings mapped natively from the validated Pydantic DTOs.
"""

import base64
import io
import logging
from math import pi

import matplotlib
import matplotlib.pyplot as plt

from backend_v2.models.v2_core import MatrixScorecardRowDTO

logger = logging.getLogger(__name__)

# Enforce Non-Interactive Backend for Headless Thread-Safety
matplotlib.use("Agg")


def generate_scatter_chart(axes: list[MatrixScorecardRowDTO]) -> str:
    """Generate a Cartesian 2D scatter matrix plot from the provided axes.

    Strict parity with Flutter's LogicMatrixChart.

    Args:
        axes: The validated list of axes. Minimal required length is 2.

    Returns:
        A Base64 string literal of the generated PNG file.
    """
    if len(axes) < 2:
        return ""

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

    import math

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


def generate_radar_chart(axes: list[MatrixScorecardRowDTO]) -> str:
    """Generate a polar 3D Radar chart for N-dimensional datasets.

    Strict parity with Flutter's RadarChart layout block.

    Args:
        axes: The validated list of axes. Minimal required length is 3.

    Returns:
        A Base64 string literal of the generated PNG radar polygon.
    """
    if len(axes) < 3:
        return ""

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
