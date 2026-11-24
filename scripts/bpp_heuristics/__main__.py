"""Allow ``python -m bpp_heuristics`` (run from the ``scripts/`` directory)."""

import sys

from bpp_heuristics.cli import main

sys.exit(main())
