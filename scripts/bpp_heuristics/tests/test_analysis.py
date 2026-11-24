"""Tests for the result summaries behind the charts."""

from __future__ import annotations

import unittest

from bpp_heuristics.analysis import ResultRow, heuristic_order, summarize, win_rates


def _row(instance: str, heuristic: str, bins: int, best: int | None = None) -> ResultRow:
    return ResultRow(instance, "fam", heuristic, bins, lower_bound=10, best_known=best,
                     fitness=0.9, avg_fill=0.9, time_s=0.001)


class AnalysisTest(unittest.TestCase):
    """Win rates, ordering and gap reference."""

    def test_win_rates_count_ties(self):
        rows = [_row("a", "FF", 11), _row("a", "BF", 11), _row("a", "NF", 13),
                _row("b", "FF", 12), _row("b", "BF", 11), _row("b", "NF", 14)]
        self.assertEqual(win_rates(rows), {"NF": 0.0, "FF": 0.5, "BF": 1.0})

    def test_registry_order(self):
        rows = [_row("a", "FFD", 11), _row("a", "XYZ", 11), _row("a", "NF", 11)]
        self.assertEqual(heuristic_order(rows), ["NF", "FFD", "XYZ"])

    def test_gap_uses_best_known_when_available(self):
        summary = summarize([_row("a", "FF", 13, best=12), _row("b", "FF", 12)])[0]
        self.assertEqual(summary.mean_gap, 1.5)  # (13 - 12) and (12 - L1=10)


if __name__ == "__main__":
    unittest.main()
