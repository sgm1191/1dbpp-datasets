"""Running heuristics on a single instance and turning results into CSV rows."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from bpp_heuristics.heuristics import get_heuristics
from bpp_heuristics.metrics import evaluate_packing
from bpp_heuristics.validation import validate_packing
from utils import BPPInstance, measure, read_instance

#: Column order of the result rows.
RESULT_FIELDS: tuple[str, ...] = (
    "family",
    "instance",
    "path",
    "n_items",
    "capacity",
    "best_known",
    "is_optimal",
    "lower_bound",
    "heuristic",
    "num_bins",
    "fitness",
    "avg_fill",
    "min_fill",
    "gap_to_lower_bound",
    "gap_to_best_known",
    "time_s",
)


@dataclass(frozen=True, slots=True)
class ExperimentConfig:
    """Settings shared by every instance run.

    Attributes:
        heuristics: Names of the heuristics to run (``None`` = all).
        repeats: Times each heuristic is run per instance; the minimum time is kept.
        validate: Whether to check each packing for feasibility (not timed).
    """

    heuristics: tuple[str, ...] | None = None
    repeats: int = 1
    validate: bool = True


def run_instance(instance: BPPInstance, config: ExperimentConfig) -> list[dict[str, Any]]:
    """Run the configured heuristics on ``instance`` and return one row per heuristic.

    Only the heuristic call is timed; parsing, validation and metric
    computation are excluded.

    Raises:
        bpp_heuristics.validation.InfeasiblePackingError: If validation is
            enabled and a heuristic returns an infeasible packing.
    """
    weights, capacity = instance.weights, instance.capacity
    lower_bound = instance.lower_bound
    rows = []
    for name, heuristic in get_heuristics(config.heuristics).items():
        packing, seconds = measure(heuristic, weights, capacity, repeats=config.repeats)
        if config.validate:
            validate_packing(packing, weights, capacity)
        metrics = evaluate_packing(packing, capacity, lower_bound, instance.best_known)
        rows.append(
            {
                "family": instance.family,
                "instance": instance.name,
                "path": instance.path,
                "n_items": instance.n_items,
                "capacity": capacity,
                "best_known": instance.best_known,
                "is_optimal": instance.is_optimal,
                "lower_bound": lower_bound,
                "heuristic": name,
                "num_bins": metrics.num_bins,
                "fitness": metrics.fitness,
                "avg_fill": metrics.avg_fill,
                "min_fill": metrics.min_fill,
                "gap_to_lower_bound": metrics.gap_to_lower_bound,
                "gap_to_best_known": metrics.gap_to_best_known,
                "time_s": seconds,
            }
        )
    return rows


def run_instance_file(path: Path, root: Path, config: ExperimentConfig) -> list[dict[str, Any]]:
    """Read the instance at ``path`` (relative to ``root``) and run :func:`run_instance`.

    Top-level function so it can be dispatched to worker processes.
    """
    return run_instance(read_instance(path, root), config)
