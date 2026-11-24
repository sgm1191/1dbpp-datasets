"""Data structures that keep the heuristics sub-quadratic on large instances."""

from __future__ import annotations


class FirstFitTree:
    """Max segment tree over bin residual capacities, for First Fit in O(log m).

    Leaves hold the residual capacity of each bin. Bins not opened yet keep the
    full capacity, so the left-most leaf able to hold an item is either the
    first open bin where it fits or, if none, the next bin to open. This turns
    First Fit from O(n*m) into O(n log n).
    """

    __slots__ = ("_size", "_tree")

    def __init__(self, max_bins: int, capacity: int) -> None:
        """Create a tree for at most ``max_bins`` bins of the given capacity."""
        size = 1
        while size < max_bins:
            size <<= 1
        self._size = size
        self._tree = [capacity] * (2 * size)

    def first_fit(self, weight: int) -> int:
        """Return the index of the left-most bin with residual capacity >= ``weight``.

        The caller must ensure ``weight`` fits in an empty bin.
        """
        tree, size = self._tree, self._size
        node = 1
        while node < size:
            node <<= 1
            if tree[node] < weight:
                node += 1
        return node - size

    def consume(self, bin_index: int, weight: int) -> None:
        """Subtract ``weight`` from bin ``bin_index`` and update the ancestors' maxima."""
        tree = self._tree
        node = bin_index + self._size
        tree[node] -= weight
        node >>= 1
        while node:
            left, right = tree[2 * node], tree[2 * node + 1]
            best = left if left > right else right
            if tree[node] == best:
                break
            tree[node] = best
            node >>= 1
