"""Fill the optimum / best-known value of BPPLIB instances from Solutions.xlsx.

The BPPLIB files in ``standarized_instances/`` carry ``//Known Best Solution``
``-1``. ``Solutions.xlsx`` (BPPLIB) lists, per instance, the best lower bound,
the best upper bound and a status. For each instance file still at ``-1``:

* status ``Solved`` (LB == UB)  -> header becomes ``//Optimal Solution`` = UB,
* otherwise (open instance)     -> ``//Known Best Solution`` = UB (best known).

Only those two header lines change; files that already hold a value are left
untouched. Instances are matched by file name (with or without ``.txt``).

Usage (openpyxl is not a project dependency, so add it on the fly)::

    uv run --project scripts --with openpyxl python scripts/fill_known_solutions.py --dry-run
    uv run --project scripts --with openpyxl python scripts/fill_known_solutions.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from openpyxl import load_workbook

from utils.paths import REPO_ROOT, STANDARDIZED_INSTANCES_DIR

KNOWN_HEADER = "//Known Best Solution"
OPTIMAL_HEADER = "//Optimal Solution"


def _key(name: str) -> str:
    name = name.strip()
    return name[:-4] if name.endswith(".txt") else name


def load_solutions(xlsx: Path) -> dict[str, tuple[int, int, str, str]]:
    """Return ``{instance key: (best_lb, best_ub, status, sheet)}``."""
    out: dict[str, tuple[int, int, str, str]] = {}
    wb = load_workbook(xlsx, read_only=True, data_only=True)
    for ws in wb.worksheets:
        rows = ws.iter_rows(values_only=True)
        header = [str(c).strip().lower() if c is not None else "" for c in next(rows)]
        i_name, i_lb, i_ub, i_st = (header.index(h) for h in ("name", "best lb", "best ub", "status"))
        for row in rows:
            if row[i_name] is None:
                continue
            key = _key(str(row[i_name]))
            if key in out:
                raise ValueError(f"instance {key!r} listed twice ({out[key][3]!r}, {ws.title!r})")
            out[key] = (int(row[i_lb]), int(row[i_ub]), str(row[i_st]).strip(), ws.title)
    return out


def updated_text(text: str, value: int, optimal: bool) -> str | None:
    """Return ``text`` with the ``-1`` best-known header filled, or None if not applicable."""
    lines = text.split("\n")
    for i, line in enumerate(lines[:-1]):
        if line.strip() == KNOWN_HEADER and lines[i + 1].strip() == "-1":
            eol = "\r" if lines[i + 1].endswith("\r") else ""
            lines[i] = (OPTIMAL_HEADER if optimal else KNOWN_HEADER) + eol
            lines[i + 1] = f"{value}{eol}"
            return "\n".join(lines)
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--xlsx", type=Path, default=REPO_ROOT / "Solutions.xlsx")
    parser.add_argument("--instances-dir", type=Path, default=STANDARDIZED_INSTANCES_DIR)
    parser.add_argument("--dry-run", action="store_true", help="report only, write nothing")
    args = parser.parse_args(argv)

    solutions = load_solutions(args.xlsx)
    used: set[str] = set()
    stats = {"optimal": 0, "best_known": 0, "already_set": 0, "no_solution": 0}
    missing: list[str] = []
    for path in sorted(p for p in args.instances_dir.rglob("*") if p.is_file()):
        text = path.read_text(encoding="utf-8")
        if not text.startswith("//Number of items"):
            continue
        key = _key(path.name)
        if key not in solutions:
            if "\n-1" in text.split("//Weight of Item")[0]:
                stats["no_solution"] += 1
                missing.append(str(path.relative_to(args.instances_dir)))
            continue
        lb, ub, status, _ = solutions[key]
        optimal = status.lower() == "solved" and lb == ub
        new = updated_text(text, ub, optimal)
        if new is None:
            stats["already_set"] += 1
            continue
        used.add(key)
        stats["optimal" if optimal else "best_known"] += 1
        if not args.dry_run:
            path.write_text(new, encoding="utf-8", newline="")

    for k, v in stats.items():
        print(f"{k:12s} {v}")
    unused = sorted(set(solutions) - used)
    print(f"workbook rows not matched to a -1 file: {len(unused)}")
    for k in unused[:20]:
        print("  ", k, solutions[k])
    for m in missing[:20]:
        print("  no workbook row:", m)
    if args.dry_run:
        print("(dry run: nothing written)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
