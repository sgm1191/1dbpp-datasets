"""Offline variants obtained by pre-sorting the items before an online heuristic."""

from __future__ import annotations

from collections.abc import Callable, Sequence

from bpp_heuristics.packing import Packing

Heuristic = Callable[[Sequence[int], int], Packing]


def decreasing(heuristic: Heuristic) -> Heuristic:
    """Return the "Decreasing" variant of ``heuristic`` (e.g. First Fit -> FFD).

    The wrapped heuristic receives the items sorted by non-increasing weight
    (stable, so equal items keep their original relative order). The returned
    packing is mapped back so that ``assignment`` stays aligned with the
    original item order. The sort is part of the heuristic and is therefore
    included in any timing of the returned callable.
    """

    def sorted_heuristic(weights: Sequence[int], capacity: int) -> Packing:
        order = sorted(range(len(weights)), key=weights.__getitem__, reverse=True)
        packing = heuristic([weights[i] for i in order], capacity)
        assignment = [0] * len(weights)
        for sorted_pos, original in enumerate(order):
            assignment[original] = packing.assignment[sorted_pos]
        return Packing(packing.loads, assignment)

    sorted_heuristic.__name__ = f"{heuristic.__name__}_decreasing"
    sorted_heuristic.__doc__ = f"{heuristic.__name__} applied to items sorted by decreasing weight."
    return sorted_heuristic
