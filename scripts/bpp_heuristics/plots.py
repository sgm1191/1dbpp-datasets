"""Static (PNG) charts comparing heuristic performance.

Each ``plot_*`` function draws one figure from the loaded results and saves it
to the given path. Requires ``matplotlib`` (declared in ``scripts/pyproject.toml``).

Visual conventions: heuristics are on the x axis in registry order; online
heuristics use one color and their Decreasing variants another, with a legend.
Distributions are drawn as one dot per instance plus a median tick, so every
instance stays visible (the benchmark sets are small enough).
"""

from __future__ import annotations

import random
from collections.abc import Callable
from pathlib import Path
from statistics import median

import matplotlib

matplotlib.use("Agg")  # file output only, no display needed

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.axes import Axes  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.axis import Axis  # noqa: E402
from matplotlib.ticker import FuncFormatter, LogLocator, PercentFormatter  # noqa: E402

from bpp_heuristics.analysis import (  # noqa: E402
    HeuristicSummary,
    ResultRow,
    group_by_heuristic,
    uses_best_known,
)

SURFACE = "#fcfcfb"
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
GRID = "#e4e3df"
ONLINE_COLOR = "#2a78d6"  # categorical slot 1 (blue)
DECREASING_COLOR = "#eb6834"  # categorical slot 2 (orange)

DPI = 150
FIGSIZE = (9, 4.8)


def _color(heuristic: str) -> str:
    """Color of a heuristic: Decreasing variants (name ending in ``D``) vs online ones."""
    return DECREASING_COLOR if heuristic.endswith("D") else ONLINE_COLOR


def _new_axes(title: str, ylabel: str) -> tuple[plt.Figure, Axes]:
    """Create a figure with the shared styling: recessive grid, no top/right spines."""
    fig, ax = plt.subplots(figsize=FIGSIZE, facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    ax.set_title(title, loc="left", fontsize=13, color=TEXT_PRIMARY, pad=12)
    ax.set_ylabel(ylabel, color=TEXT_SECONDARY)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=TEXT_SECONDARY, length=0)
    return fig, ax


def _plain_log_axis(axis: Axis) -> None:
    """Show a log-scaled axis with plain numbers (0.05, 0.1, 0.2) instead of 10^x."""
    plain = FuncFormatter(lambda value, _: f"{value:g}")
    axis.set_major_locator(LogLocator(base=10, subs=(1.0, 2.0, 5.0)))
    axis.set_major_formatter(plain)
    axis.set_minor_formatter(FuncFormatter(lambda value, _: ""))


def _place_labels(ax: Axes, points: list[tuple[float, float, str]]) -> None:
    """Annotate points with their text, choosing for each label the first of four
    offsets (right-up, right-down, left-up, left-down) whose box does not overlap
    the labels already placed or any point marker."""
    fig = ax.figure
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    to_display = ax.transData.transform
    marker_boxes = []
    for x, y, _ in points:
        px, py = to_display((x, y))
        marker_boxes.append((px - 5, py - 5, px + 5, py + 5))
    placed: list[tuple[float, float, float, float]] = []
    offsets = ((7, 4, "left"), (7, -12, "left"), (-7, 4, "right"), (-7, -12, "right"))
    for x, y, text in points:
        for dx, dy, align in offsets:
            label = ax.annotate(text, (x, y), xytext=(dx, dy), textcoords="offset points",
                                fontsize=9, color=TEXT_PRIMARY, ha=align)
            box = label.get_window_extent(renderer)
            bounds = (box.x0, box.y0, box.x1, box.y1)
            if not any(_overlaps(bounds, other) for other in placed + marker_boxes):
                break
            label.remove()
        else:  # every option collides: keep the default position
            label = ax.annotate(text, (x, y), xytext=offsets[0][:2], textcoords="offset points",
                                fontsize=9, color=TEXT_PRIMARY)
            box = label.get_window_extent(renderer)
            bounds = (box.x0, box.y0, box.x1, box.y1)
        placed.append(bounds)


def _overlaps(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
    """Whether two (x0, y0, x1, y1) boxes intersect."""
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def _legend(ax: Axes, extra: list[Line2D] | None = None) -> None:
    """Legend identifying the online / Decreasing color encoding."""
    handles = [
        Line2D([], [], marker="o", linestyle="", color=ONLINE_COLOR, label="Online order"),
        Line2D([], [], marker="o", linestyle="", color=DECREASING_COLOR, label="Decreasing order"),
        *(extra or []),
    ]
    ax.legend(handles=handles, frameon=False, labelcolor=TEXT_SECONDARY, loc="best")


def _save(fig: plt.Figure, path: Path) -> Path:
    """Save ``fig`` to ``path`` and release it."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=DPI, facecolor=SURFACE)
    plt.close(fig)
    return path


def plot_distribution(
    rows: list[ResultRow],
    value: Callable[[ResultRow], float],
    title: str,
    ylabel: str,
    path: Path,
    log_scale: bool = False,
    percent: bool = False,
) -> Path:
    """Dot-per-instance distribution of ``value`` per heuristic, with a median tick.

    Args:
        rows: Results to plot.
        value: Extracts the plotted value from a row.
        title: Figure title.
        ylabel: Y-axis label.
        path: Output PNG path.
        log_scale: Use a logarithmic y axis (for running times).
        percent: Format the y axis as a percentage of 1.0.
    """
    fig, ax = _new_axes(title, ylabel)
    jitter = random.Random(0)  # deterministic horizontal spread
    groups = group_by_heuristic(rows)
    for x, (name, group) in enumerate(groups.items()):
        values = [value(row) for row in group]
        xs = [x + jitter.uniform(-0.18, 0.18) for _ in values]
        ax.scatter(xs, values, s=22, color=_color(name), alpha=0.55, edgecolors=SURFACE, linewidths=0.6, zorder=2)
        ax.hlines(median(values), x - 0.3, x + 0.3, color=TEXT_PRIMARY, linewidth=2, zorder=3)
    ax.set_xticks(range(len(groups)), list(groups))
    if log_scale:
        ax.set_yscale("log")
        _plain_log_axis(ax.yaxis)
    if percent:
        ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    _legend(ax, [Line2D([], [], color=TEXT_PRIMARY, linewidth=2, label="Median")])
    return _save(fig, path)


def plot_gap(rows: list[ResultRow], path: Path) -> Path:
    """Extra bins over the best-known value (or over L1 when it is unknown)."""
    reference = "best known" if uses_best_known(rows) else "lower bound L1"
    return plot_distribution(
        rows, lambda row: row.gap,
        f"Extra bins over the {reference}, per instance (lower is better)",
        f"bins − {reference}", path,
    )


def plot_fitness(rows: list[ResultRow], path: Path) -> Path:
    """Falkenauer fitness per instance."""
    return plot_distribution(
        rows, lambda row: row.fitness,
        "Falkenauer fitness, per instance (higher is better)", "fitness", path,
    )


def plot_avg_fill(rows: list[ResultRow], path: Path) -> Path:
    """Average bin fill per instance."""
    return plot_distribution(
        rows, lambda row: row.avg_fill,
        "Average bin fill, per instance (higher is better)", "average fill", path, percent=True,
    )


def plot_time(rows: list[ResultRow], path: Path) -> Path:
    """Running time per instance, on a log scale."""
    return plot_distribution(
        rows, lambda row: row.time_s * 1000,
        "Running time, per instance (log scale)", "time (ms)", path, log_scale=True,
    )


def plot_win_rate(summaries: list[HeuristicSummary], path: Path) -> Path:
    """Share of instances where each heuristic attains the fewest bins (ties included)."""
    fig, ax = _new_axes("Instances where the heuristic uses the fewest bins (ties count)", "share of instances")
    names = [summary.heuristic for summary in summaries]
    rates = [summary.win_rate for summary in summaries]
    bars = ax.bar(range(len(names)), rates, width=0.6, color=[_color(name) for name in names], zorder=2)
    ax.bar_label(bars, labels=[f"{rate:.0%}" for rate in rates], padding=3, color=TEXT_SECONDARY, fontsize=9)
    ax.set_xticks(range(len(names)), names)
    ax.set_ylim(0, 1.08)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    _legend(ax)
    return _save(fig, path)


def plot_tradeoff(summaries: list[HeuristicSummary], gap_label: str, path: Path) -> Path:
    """Quality vs speed: median time against mean extra bins, one labeled dot per heuristic.

    The y axis is symmetric-log (linear below 1 bin, logarithmic above) so that a
    very poor heuristic such as NF does not squash the differences among the
    good ones, while a gap of 0 can still be shown.
    """
    fig, ax = _new_axes(
        "Quality vs. speed (closer to the bottom-left is better)",
        f"mean extra bins over {gap_label} (symlog scale)",
    )
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    for summary in summaries:
        ax.scatter(summary.median_time_ms, summary.mean_gap, s=64, color=_color(summary.heuristic),
                   edgecolors=SURFACE, linewidths=2, zorder=3)
    ax.set_xscale("log")
    _plain_log_axis(ax.xaxis)
    ax.set_yscale("symlog", linthresh=1)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:g}"))
    ax.set_ylim(0, max(1.0, max(summary.mean_gap for summary in summaries)) * 1.8)  # room for labels
    ax.set_xlabel("median time per instance (ms, log scale)", color=TEXT_SECONDARY)
    _legend(ax)
    fig.tight_layout()
    _place_labels(ax, [(s.median_time_ms, s.mean_gap, s.heuristic) for s in summaries])
    return _save(fig, path)
