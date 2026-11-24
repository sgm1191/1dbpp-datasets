"""Name -> callable registry of the available heuristics.

To add a heuristic, implement a ``(weights, capacity) -> Packing`` function
and add it to :data:`HEURISTICS` under a short, unique acronym.
"""

from __future__ import annotations

from collections.abc import Iterable

from bpp_heuristics.heuristics.online import (
    almost_worst_fit,
    best_fit,
    first_fit,
    next_fit,
    worst_fit,
)
from bpp_heuristics.heuristics.ordering import Heuristic, decreasing

#: All heuristics, keyed by their acronym, in reporting order.
HEURISTICS: dict[str, Heuristic] = {
    "NF": next_fit,
    "FF": first_fit,
    "BF": best_fit,
    "WF": worst_fit,
    "AWF": almost_worst_fit,
    "NFD": decreasing(next_fit),
    "FFD": decreasing(first_fit),
    "BFD": decreasing(best_fit),
    "WFD": decreasing(worst_fit),
    "AWFD": decreasing(almost_worst_fit),
}


def get_heuristics(names: Iterable[str] | None = None) -> dict[str, Heuristic]:
    """Return the requested heuristics (all of them when ``names`` is ``None``).

    Raises:
        KeyError: If an unknown heuristic name is requested.
    """
    if names is None:
        return dict(HEURISTICS)
    unknown = [name for name in names if name not in HEURISTICS]
    if unknown:
        raise KeyError(f"unknown heuristics {unknown}; available: {list(HEURISTICS)}")
    return {name: HEURISTICS[name] for name in names}
