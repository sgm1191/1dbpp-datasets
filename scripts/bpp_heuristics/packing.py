"""Result of applying a packing heuristic to an instance."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Packing:
    """Assignment of items to bins produced by a heuristic.

    Attributes:
        loads: Total weight packed in each bin; ``loads[b]`` is the load of bin ``b``.
        assignment: Bin index of every item, aligned with the instance weights
            (``assignment[i]`` is the bin holding item ``i``).
    """

    loads: list[int]
    assignment: list[int]

    @property
    def num_bins(self) -> int:
        """Number of bins used."""
        return len(self.loads)
