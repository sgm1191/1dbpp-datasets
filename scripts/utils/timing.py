"""Wall-clock measurement of callables."""

from __future__ import annotations

from collections.abc import Callable
from time import perf_counter
from typing import Any, TypeVar

T = TypeVar("T")


def measure(func: Callable[..., T], *args: Any, repeats: int = 1, **kwargs: Any) -> tuple[T, float]:
    """Call ``func(*args, **kwargs)`` ``repeats`` times and time it.

    Following the ``timeit`` convention, the reported time is the *minimum*
    over the repetitions, which is the estimate least affected by noise from
    other processes.

    Returns:
        A tuple ``(result, seconds)`` with the result of the last call and the
        best elapsed time in seconds.

    Raises:
        ValueError: If ``repeats`` is smaller than 1.
    """
    if repeats < 1:
        raise ValueError(f"repeats must be >= 1, got {repeats}")
    best = float("inf")
    result: T
    for _ in range(repeats):
        start = perf_counter()
        result = func(*args, **kwargs)
        best = min(best, perf_counter() - start)
    return result, best
