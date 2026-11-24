"""Tests for the metrics and the shared instance reader."""

from __future__ import annotations

import unittest

from bpp_heuristics.metrics import average_fill, evaluate_packing, falkenauer_fitness
from bpp_heuristics.packing import Packing
from utils.instance_reader import InstanceFormatError, parse_instance_text

OPTIMAL_TEXT = """//Number of items
3
//Bin Capacity
10
//Optimal Solution
2
//Weight of Item
6
4
5
"""

UNKNOWN_TEXT = OPTIMAL_TEXT.replace("//Optimal Solution\n2", "//Known Best Solution\n-1")


class MetricsTest(unittest.TestCase):
    """Fitness and fill computations."""

    def test_full_bins_have_fitness_one(self):
        self.assertEqual(falkenauer_fitness([10, 10], 10), 1.0)

    def test_fitness_prefers_unbalanced_bins(self):
        self.assertGreater(falkenauer_fitness([10, 2], 10), falkenauer_fitness([6, 6], 10))

    def test_average_fill(self):
        self.assertAlmostEqual(average_fill([10, 5], 10), 0.75)

    def test_evaluate_packing(self):
        metrics = evaluate_packing(Packing([10, 5], [0, 0, 1]), 10, lower_bound=2, best_known=2)
        self.assertEqual(metrics.num_bins, 2)
        self.assertEqual(metrics.gap_to_lower_bound, 0)
        self.assertEqual(metrics.gap_to_best_known, 0)
        self.assertAlmostEqual(metrics.min_fill, 0.5)


class ReaderTest(unittest.TestCase):
    """Parsing of the standardized text format."""

    def test_parse_optimal(self):
        instance = parse_instance_text(OPTIMAL_TEXT, name="x")
        self.assertEqual(instance.capacity, 10)
        self.assertEqual(instance.weights, (6, 4, 5))
        self.assertEqual(instance.best_known, 2)
        self.assertTrue(instance.is_optimal)
        self.assertEqual(instance.lower_bound, 2)

    def test_unknown_best_is_none(self):
        instance = parse_instance_text(UNKNOWN_TEXT)
        self.assertIsNone(instance.best_known)
        self.assertFalse(instance.is_optimal)

    def test_item_count_mismatch(self):
        with self.assertRaises(InstanceFormatError):
            parse_instance_text(OPTIMAL_TEXT.replace("//Number of items\n3", "//Number of items\n4"))


if __name__ == "__main__":
    unittest.main()
