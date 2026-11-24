"""Quality metrics of a packing.

Fitness
-------
The number of bins alone is a coarse measure: many packings share the same
bin count but differ in how close they are to freeing one more bin. We use
the fitness function of Falkenauer & Delchambre (1992), standard in the
bin packing heuristic / hyper-heuristic literature::

    fitness = (1 / m) * sum_b (load_b / C) ** k,    k = 2

where ``m`` is the number of bins and ``C`` the capacity. It lies in
``(0, 1]``, is **maximized**, equals 1 only when every bin is completely full,
and rewards packings with a few very full bins over evenly half-full ones.
"""

from __future__ import annotations

from dataclasses import dataclass

from bpp_heuristics.packing import Packing

#: Exponent of the Falkenauer fitness function.
FALKENAUER_K = 2


def falkenauer_fitness(loads: list[int], capacity: int, k: int = FALKENAUER_K) -> float:
    """Return the Falkenauer fitness ``mean((load / capacity) ** k)`` of the bins."""
    if not loads:
        return 0.0
    return sum((load / capacity) ** k for load in loads) / len(loads)


def average_fill(loads: list[int], capacity: int) -> float:
    """Return the mean fill ratio ``load / capacity`` over the bins, in ``(0, 1]``."""
    if not loads:
        return 0.0
    return sum(loads) / (capacity * len(loads))


@dataclass(frozen=True, slots=True)
class PackingMetrics:
    """Summary of the quality of a packing.

    Attributes:
        num_bins: Number of bins used.
        fitness: Falkenauer fitness (see module docstring), higher is better.
        avg_fill: Mean fill ratio of the bins.
        min_fill: Fill ratio of the emptiest bin.
        gap_to_lower_bound: ``num_bins - L1`` where L1 = ceil(sum(w) / C).
        gap_to_best_known: ``num_bins - best_known``, or ``None`` if unknown.
    """

    num_bins: int
    fitness: float
    avg_fill: float
    min_fill: float
    gap_to_lower_bound: int
    gap_to_best_known: int | None


def evaluate_packing(
    packing: Packing,
    capacity: int,
    lower_bound: int,
    best_known: int | None = None,
) -> PackingMetrics:
    """Compute the :class:`PackingMetrics` of ``packing``.

    Args:
        packing: Packing to evaluate.
        capacity: Bin capacity of the instance.
        lower_bound: A valid lower bound on the number of bins (e.g. L1).
        best_known: Optimal / best-known number of bins, if available.
    """
    loads = packing.loads
    num_bins = len(loads)
    return PackingMetrics(
        num_bins=num_bins,
        fitness=falkenauer_fitness(loads, capacity),
        avg_fill=average_fill(loads, capacity),
        min_fill=min(loads) / capacity if loads else 0.0,
        gap_to_lower_bound=num_bins - lower_bound,
        gap_to_best_known=None if best_known is None else num_bins - best_known,
    )
