"""Check the optimized heuristics against straightforward O(n*m) reference versions."""

from __future__ import annotations

import random
import unittest

from bpp_heuristics.heuristics import HEURISTICS
from bpp_heuristics.validation import validate_packing


def _reference(weights: list[int], capacity: int, choose) -> list[int]:
    """Generic O(n*m) packing: ``choose(residuals, w)`` returns a bin index or -1."""
    residuals: list[int] = []
    assignment = []
    for w in weights:
        target = choose(residuals, w)
        if target == -1:
            residuals.append(capacity)
            target = len(residuals) - 1
        residuals[target] -= w
        assignment.append(target)
    return assignment


def _ref_nf(res, w):
    return len(res) - 1 if res and res[-1] >= w else -1


def _ref_ff(res, w):
    return next((b for b, r in enumerate(res) if r >= w), -1)


def _ref_bf(res, w):
    fits = [(r, b) for b, r in enumerate(res) if r >= w]
    return min(fits)[1] if fits else -1


def _ref_wf(res, w):
    if not res:
        return -1
    best = max(range(len(res)), key=lambda b: (res[b], -b))
    return best if res[best] >= w else -1


def _ref_awf(res, w):
    ranked = sorted(range(len(res)), key=lambda b: (-res[b], b))
    if len(ranked) > 1 and res[ranked[1]] >= w:
        return ranked[1]
    if ranked and res[ranked[0]] >= w:
        return ranked[0]
    return -1


REFERENCES = {"NF": _ref_nf, "FF": _ref_ff, "BF": _ref_bf, "WF": _ref_wf, "AWF": _ref_awf}


class HeuristicsTest(unittest.TestCase):
    """Optimized heuristics must reproduce the reference assignments exactly."""

    def _random_instances(self):
        rng = random.Random(1234)
        for _ in range(200):
            capacity = rng.choice([10, 100, 1000])
            n = rng.randint(1, 120)
            yield [rng.randint(1, capacity) for _ in range(n)], capacity

    def test_online_match_reference(self):
        for weights, capacity in self._random_instances():
            for name, choose in REFERENCES.items():
                with self.subTest(heuristic=name, weights=weights, capacity=capacity):
                    packing = HEURISTICS[name](weights, capacity)
                    self.assertEqual(packing.assignment, _reference(weights, capacity, choose))

    def test_decreasing_match_reference(self):
        for weights, capacity in self._random_instances():
            order = sorted(range(len(weights)), key=weights.__getitem__, reverse=True)
            sorted_weights = [weights[i] for i in order]
            for name, choose in REFERENCES.items():
                with self.subTest(heuristic=f"{name}D"):
                    packing = HEURISTICS[f"{name}D"](weights, capacity)
                    expected = _reference(sorted_weights, capacity, choose)
                    got = [packing.assignment[i] for i in order]
                    self.assertEqual(got, expected)

    def test_all_packings_feasible(self):
        for weights, capacity in self._random_instances():
            for name, heuristic in HEURISTICS.items():
                with self.subTest(heuristic=name):
                    validate_packing(heuristic(weights, capacity), weights, capacity)

    def test_oversized_item_rejected(self):
        for name, heuristic in HEURISTICS.items():
            with self.subTest(heuristic=name), self.assertRaises(ValueError):
                heuristic([5, 11], 10)


if __name__ == "__main__":
    unittest.main()
