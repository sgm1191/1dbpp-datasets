"""Classic online (single-pass) bin packing heuristics.

Every heuristic places the items in the given order and has the signature
``heuristic(weights, capacity) -> Packing``. Bins are indexed in opening
order. Implementations avoid linear scans over the open bins so they scale
to the largest benchmark instances:

==================  =====================================  ===============
Heuristic           Rule                                   Complexity
==================  =====================================  ===============
Next Fit            only the most recently opened bin      O(n)
First Fit           left-most open bin that fits           O(n log n)
Best Fit            fitting bin with the least room left   O(n log n)*
Worst Fit           fitting bin with the most room left    O(n log n)
Almost Worst Fit    fitting bin with the 2nd most room     O(n log n)*
==================  =====================================  ===============

\\* Binary search plus ``list.insert``/``list.pop``, which are O(m) memmoves
but very fast in practice for the instance sizes in this repository.
"""

from __future__ import annotations

import heapq
from bisect import bisect_left, insort
from collections.abc import Sequence

from bpp_heuristics.heuristics.structures import FirstFitTree
from bpp_heuristics.packing import Packing


def _check_fits(weight: int, capacity: int) -> None:
    """Raise ``ValueError`` if ``weight`` cannot fit in an empty bin."""
    if weight > capacity or weight <= 0:
        raise ValueError(f"item weight {weight} is not in (0, {capacity}]")


def next_fit(weights: Sequence[int], capacity: int) -> Packing:
    """Next Fit: keep a single open bin; open a new one when the item does not fit."""
    loads: list[int] = []
    assignment: list[int] = []
    current = -1
    room = 0
    for weight in weights:
        if weight > room:
            _check_fits(weight, capacity)
            loads.append(0)
            current += 1
            room = capacity
        loads[current] += weight
        room -= weight
        assignment.append(current)
    return Packing(loads, assignment)


def first_fit(weights: Sequence[int], capacity: int) -> Packing:
    """First Fit: place each item in the earliest-opened bin where it fits."""
    tree = FirstFitTree(max(len(weights), 1), capacity)
    loads: list[int] = []
    assignment: list[int] = []
    for weight in weights:
        _check_fits(weight, capacity)
        target = tree.first_fit(weight)
        if target == len(loads):
            loads.append(0)
        tree.consume(target, weight)
        loads[target] += weight
        assignment.append(target)
    return Packing(loads, assignment)


def best_fit(weights: Sequence[int], capacity: int) -> Packing:
    """Best Fit: place each item in the bin it fills the most (least residual room).

    Ties are broken by the lowest bin index.
    """
    # Sorted (residual, bin) pairs of open bins that still have room.
    open_bins: list[tuple[int, int]] = []
    loads: list[int] = []
    assignment: list[int] = []
    for weight in weights:
        _check_fits(weight, capacity)
        pos = bisect_left(open_bins, (weight, -1))
        if pos < len(open_bins):
            residual, target = open_bins.pop(pos)
        else:
            residual, target = capacity, len(loads)
            loads.append(0)
        residual -= weight
        if residual:
            insort(open_bins, (residual, target))
        loads[target] += weight
        assignment.append(target)
    return Packing(loads, assignment)


def worst_fit(weights: Sequence[int], capacity: int) -> Packing:
    """Worst Fit: place each item in the open bin with the most residual room.

    A new bin is opened only when the item does not fit in the emptiest one.
    Ties are broken by the lowest bin index.
    """
    # Max-heap of (-residual, bin).
    heap: list[tuple[int, int]] = []
    loads: list[int] = []
    assignment: list[int] = []
    for weight in weights:
        _check_fits(weight, capacity)
        if heap and -heap[0][0] >= weight:
            neg_residual, target = heap[0]
            heapq.heapreplace(heap, (neg_residual + weight, target))
        else:
            target = len(loads)
            loads.append(0)
            heapq.heappush(heap, (weight - capacity, target))
        loads[target] += weight
        assignment.append(target)
    return Packing(loads, assignment)


def almost_worst_fit(weights: Sequence[int], capacity: int) -> Packing:
    """Almost Worst Fit: like Worst Fit, but prefer the bin with the 2nd largest room.

    Falls back to the bin with the largest room when the item only fits there,
    and opens a new bin when it fits in none. Ties are broken by bin index.
    """
    # Sorted (-residual, bin) pairs: index 0 is the emptiest bin, index 1 the second.
    open_bins: list[tuple[int, int]] = []
    loads: list[int] = []
    assignment: list[int] = []
    for weight in weights:
        _check_fits(weight, capacity)
        if len(open_bins) > 1 and -open_bins[1][0] >= weight:
            neg_residual, target = open_bins.pop(1)
        elif open_bins and -open_bins[0][0] >= weight:
            neg_residual, target = open_bins.pop(0)
        else:
            neg_residual, target = -capacity, len(loads)
            loads.append(0)
        insort(open_bins, (neg_residual + weight, target))
        loads[target] += weight
        assignment.append(target)
    return Packing(loads, assignment)
