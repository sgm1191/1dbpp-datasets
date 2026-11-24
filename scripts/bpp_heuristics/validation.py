"""Feasibility checks for packings."""

from __future__ import annotations

from collections.abc import Sequence

from bpp_heuristics.packing import Packing


class InfeasiblePackingError(ValueError):
    """Raised when a packing violates the bin packing constraints."""


def validate_packing(packing: Packing, weights: Sequence[int], capacity: int) -> None:
    """Check that ``packing`` is a feasible solution for the given items.

    Verifies that every item is assigned to an existing bin, that the
    reported loads match the assigned weights, that no bin exceeds the
    capacity and that no bin is empty. Runs in O(n + m).

    Raises:
        InfeasiblePackingError: Describing the first violated constraint.
    """
    if len(packing.assignment) != len(weights):
        raise InfeasiblePackingError(
            f"{len(packing.assignment)} assignments for {len(weights)} items"
        )
    num_bins = packing.num_bins
    recomputed = [0] * num_bins
    for item, (weight, target) in enumerate(zip(weights, packing.assignment)):
        if not 0 <= target < num_bins:
            raise InfeasiblePackingError(f"item {item} assigned to missing bin {target}")
        recomputed[target] += weight
    for target, (load, expected) in enumerate(zip(packing.loads, recomputed)):
        if load != expected:
            raise InfeasiblePackingError(f"bin {target} reports load {load}, actual {expected}")
        if load > capacity:
            raise InfeasiblePackingError(f"bin {target} load {load} exceeds capacity {capacity}")
        if load == 0:
            raise InfeasiblePackingError(f"bin {target} is empty")
