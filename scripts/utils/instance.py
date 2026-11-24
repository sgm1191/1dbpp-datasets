"""In-memory representation of a one-dimensional bin packing instance."""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil


@dataclass(frozen=True, slots=True)
class BPPInstance:
    """Immutable 1D bin packing instance.

    Attributes:
        name: Instance identifier (usually the file name).
        capacity: Capacity shared by every bin.
        weights: Item weights, in the order they appear in the source file.
        best_known: Optimal or best-known number of bins, or ``None`` when the
            source does not provide one (``-1`` in the standardized files).
        is_optimal: ``True`` when ``best_known`` is a proven optimum
            (``//Optimal Solution`` header), ``False`` when it is only a
            best-known value or unknown.
        family: Benchmark family the instance belongs to (may be empty).
        path: Path of the source file relative to the instances root
            (may be empty when the instance was not read from disk).
    """

    name: str
    capacity: int
    weights: tuple[int, ...]
    best_known: int | None = None
    is_optimal: bool = False
    family: str = ""
    path: str = ""

    @property
    def n_items(self) -> int:
        """Number of items in the instance."""
        return len(self.weights)

    @property
    def total_weight(self) -> int:
        """Sum of all item weights."""
        return sum(self.weights)

    @property
    def lower_bound(self) -> int:
        """Continuous lower bound L1 = ceil(sum(w) / C) on the number of bins."""
        return ceil(self.total_weight / self.capacity)
