#!/usr/bin/env python3
"""Run the 1D BPP heuristics over the standardized instances.

Thin launcher for :mod:`bpp_heuristics.cli` that works from any working
directory, e.g. ``python3 scripts/run_heuristics.py --help``.
"""

import sys

from bpp_heuristics.cli import main

if __name__ == "__main__":
    sys.exit(main())
