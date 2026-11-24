"""Human-readable rendering of result rows."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

#: (column, header, format spec) of the per-heuristic table.
_TABLE_COLUMNS: tuple[tuple[str, str, str], ...] = (
    ("heuristic", "heuristic", ""),
    ("num_bins", "bins", "d"),
    ("gap_to_lower_bound", "gap_LB", "d"),
    ("gap_to_best_known", "gap_best", "d"),
    ("fitness", "fitness", ".6f"),
    ("avg_fill", "avg_fill", ".4f"),
    ("min_fill", "min_fill", ".4f"),
    ("time_s", "time_ms", ".3f"),
)


def _cell(row: Mapping[str, Any], column: str, spec: str) -> str:
    """Format one value; ``time_s`` is shown in milliseconds and ``None`` as ``-``."""
    value = row[column]
    if value is None:
        return "-"
    if column == "time_s":
        value *= 1000
    return format(value, spec)


def format_instance_report(rows: Sequence[Mapping[str, Any]]) -> str:
    """Render the rows of a single instance as a header line plus an aligned table.

    Args:
        rows: Rows produced by :func:`bpp_heuristics.experiment.run_instance`
            for one instance (one row per heuristic).
    """
    if not rows:
        return "(no results)"
    first = rows[0]
    best = first["best_known"]
    best_label = "unknown" if best is None else f"{best} ({'optimal' if first['is_optimal'] else 'best known'})"
    header = (
        f"{first['path']}  |  n={first['n_items']}  C={first['capacity']}  "
        f"L1={first['lower_bound']}  best={best_label}"
    )

    table = [[title for _, title, _ in _TABLE_COLUMNS]]
    table += [[_cell(row, column, spec) for column, _, spec in _TABLE_COLUMNS] for row in rows]
    widths = [max(len(line[i]) for line in table) for i in range(len(_TABLE_COLUMNS))]
    lines = [
        "  ".join(text.ljust(width) if i == 0 else text.rjust(width) for i, (text, width) in enumerate(zip(line, widths)))
        for line in table
    ]
    return "\n".join([header, "", lines[0], "-" * len(lines[0]), *lines[1:]])
