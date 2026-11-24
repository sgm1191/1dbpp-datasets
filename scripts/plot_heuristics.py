#!/usr/bin/env python3
"""Plot per-heuristic performance from a results CSV.

Thin launcher for :mod:`bpp_heuristics.plot_cli`; needs matplotlib, so run it
through the uv environment, e.g.
``uv run --project scripts python scripts/plot_heuristics.py results/heuristics_metrics.csv``.
"""

import sys

from bpp_heuristics.plot_cli import main

if __name__ == "__main__":
    sys.exit(main())
