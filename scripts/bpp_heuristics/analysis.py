"""Loading and summarising result CSVs produced by :mod:`bpp_heuristics.cli`.

Pure standard library, so it can be reused without the plotting dependencies.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, median

from bpp_heuristics.heuristics import HEURISTICS


@dataclass(frozen=True, slots=True)
class ResultRow:
    """One (instance, heuristic) result, with the columns used for analysis."""

    instance: str
    family: str
    heuristic: str
    num_bins: int
    lower_bound: int
    best_known: int | None
    fitness: float
    avg_fill: float
    time_s: float

    @property
    def reference_bins(self) -> int:
        """Best known value when available, otherwise the L1 lower bound."""
        return self.lower_bound if self.best_known is None else self.best_known

    @property
    def gap(self) -> int:
        """Extra bins with respect to :attr:`reference_bins`."""
        return self.num_bins - self.reference_bins


def load_results(path: Path) -> list[ResultRow]:
    """Read a results CSV into :class:`ResultRow` objects."""
    with path.open(newline="", encoding="utf-8") as handle:
        return [
            ResultRow(
                instance=row["path"] or row["instance"],
                family=row["family"],
                heuristic=row["heuristic"],
                num_bins=int(row["num_bins"]),
                lower_bound=int(row["lower_bound"]),
                best_known=int(row["best_known"]) if row["best_known"] else None,
                fitness=float(row["fitness"]),
                avg_fill=float(row["avg_fill"]),
                time_s=float(row["time_s"]),
            )
            for row in csv.DictReader(handle)
        ]


def heuristic_order(rows: list[ResultRow]) -> list[str]:
    """Heuristics present in ``rows``: registry order first, unknown names after."""
    present = {row.heuristic for row in rows}
    known = [name for name in HEURISTICS if name in present]
    return known + sorted(present - set(known))


def group_by_heuristic(rows: list[ResultRow]) -> dict[str, list[ResultRow]]:
    """Group rows per heuristic, keyed in :func:`heuristic_order`."""
    groups: dict[str, list[ResultRow]] = defaultdict(list)
    for row in rows:
        groups[row.heuristic].append(row)
    return {name: groups[name] for name in heuristic_order(rows)}


def uses_best_known(rows: list[ResultRow]) -> bool:
    """Whether every row has a best-known value (otherwise gaps refer to L1)."""
    return all(row.best_known is not None for row in rows)


def win_rates(rows: list[ResultRow]) -> dict[str, float]:
    """Fraction of instances where each heuristic uses the fewest bins among all heuristics.

    Ties count as a win for every tied heuristic, so rates can add up to more than 1.
    """
    best: dict[str, int] = {}
    for row in rows:
        best[row.instance] = min(best.get(row.instance, row.num_bins), row.num_bins)
    groups = group_by_heuristic(rows)
    return {
        name: sum(row.num_bins == best[row.instance] for row in group) / len(group)
        for name, group in groups.items()
    }


@dataclass(frozen=True, slots=True)
class HeuristicSummary:
    """Aggregated performance of one heuristic over all instances."""

    heuristic: str
    instances: int
    mean_gap: float
    max_gap: int
    win_rate: float
    mean_fitness: float
    mean_avg_fill: float
    median_time_ms: float
    max_time_ms: float


def summarize(rows: list[ResultRow]) -> list[HeuristicSummary]:
    """Return one :class:`HeuristicSummary` per heuristic, in :func:`heuristic_order`."""
    wins = win_rates(rows)
    return [
        HeuristicSummary(
            heuristic=name,
            instances=len(group),
            mean_gap=mean(row.gap for row in group),
            max_gap=max(row.gap for row in group),
            win_rate=wins[name],
            mean_fitness=mean(row.fitness for row in group),
            mean_avg_fill=mean(row.avg_fill for row in group),
            median_time_ms=median(row.time_s for row in group) * 1000,
            max_time_ms=max(row.time_s for row in group) * 1000,
        )
        for name, group in group_by_heuristic(rows).items()
    ]
