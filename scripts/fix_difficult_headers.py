"""Restore the true item count and capacity of the Difficult_Instances (AI / ANI).

The standardized AI and ANI files were written with ``//Number of items`` and
``//Bin Capacity`` taken from the file name (``<n>_<range>_<type>_<i>.txt``)
instead of the original BPPLIB file, whose format is::

    <number of items>
    <bin capacity>
    <weight>
    ...

The name's second field is the weight range, not the capacity (e.g.
``1002_80000_NR_0`` has C = 65088), and AI files hold one item more than the
name says. The weights themselves were copied correctly. This script checks
that the weights match the source and rewrites only those two header values.

Usage::

    python3 scripts/fix_difficult_headers.py --dry-run
    python3 scripts/fix_difficult_headers.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from utils.paths import REPO_ROOT, STANDARDIZED_INSTANCES_DIR

SOURCE_DIR = REPO_ROOT / "source_instances" / "bpplib" / "Difficult_Instances"
TARGET_DIR = STANDARDIZED_INSTANCES_DIR / "Difficult_Instances"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true", help="report only, write nothing")
    args = parser.parse_args(argv)

    changed = unchanged = 0
    for target in sorted(TARGET_DIR.rglob("*.txt")):
        source = SOURCE_DIR / target.relative_to(TARGET_DIR)
        tokens = source.read_text(encoding="utf-8").split()
        n, cap, weights = int(tokens[0]), int(tokens[1]), tokens[2:]
        if len(weights) != n:
            raise ValueError(f"{source}: declares {n} items but has {len(weights)}")

        lines = target.read_text(encoding="utf-8").split("\n")
        if lines[0].strip() != "//Number of items" or lines[2].strip() != "//Bin Capacity":
            raise ValueError(f"{target}: unexpected header layout")
        start = next(i for i, l in enumerate(lines) if l.strip() == "//Weight of Item") + 1
        if [l.strip() for l in lines[start:] if l.strip()] != weights:
            raise ValueError(f"{target}: weights differ from {source}")

        if int(lines[1]) == n and int(lines[3]) == cap:
            unchanged += 1
            continue
        lines[1], lines[3] = str(n), str(cap)
        changed += 1
        if not args.dry_run:
            target.write_text("\n".join(lines), encoding="utf-8", newline="")

    print(f"fixed {changed}, already correct {unchanged}" + (" (dry run)" if args.dry_run else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
