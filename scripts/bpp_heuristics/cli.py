"""Command-line entry point.

Two modes:

- **Sweep** (default): run the heuristics on every instance under
  ``--instances-dir`` (optionally filtered) and write a CSV.
- **Single instance** (``--instance PATH``): run the heuristics on one file and
  print a table; a CSV is written only if ``--output`` is given.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Iterator, Sequence
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from itertools import islice
from pathlib import Path
from typing import Any

from bpp_heuristics.experiment import RESULT_FIELDS, ExperimentConfig, run_instance_file
from bpp_heuristics.heuristics import HEURISTICS
from bpp_heuristics.report import format_instance_report
from utils import REPO_ROOT, STANDARDIZED_INSTANCES_DIR, CsvRowWriter, iter_instance_paths

DEFAULT_OUTPUT = REPO_ROOT / "results" / "heuristics_results.csv"

#: Outcome of one instance: (path, rows, error message or None).
Outcome = tuple[Path, list[dict[str, Any]], str | None]


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse the command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="bpp_heuristics",
        description="Run 1D bin packing heuristics on standardized instances and "
        "record bins, fitness, average fill and running time per heuristic.",
    )
    parser.add_argument(
        "--instances-dir", type=Path, default=STANDARDIZED_INSTANCES_DIR,
        help="Root folder of the instances (default: %(default)s)",
    )
    parser.add_argument(
        "--output", type=Path,
        help=f"Output CSV path (default: {DEFAULT_OUTPUT} in sweep mode; "
        "none with --instance, which only prints a table)",
    )
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument(
        "--instance", type=Path, metavar="PATH",
        help="Run a single instance file and print the results as a table",
    )
    selection.add_argument(
        "--families", nargs="+", metavar="FAMILY",
        help="Only run instances from these top-level folders (e.g. Hard28 Scholl)",
    )
    parser.add_argument(
        "--heuristics", nargs="+", choices=list(HEURISTICS), metavar="NAME",
        help=f"Heuristics to run (default: all of {', '.join(HEURISTICS)})",
    )
    parser.add_argument(
        "--repeats", type=int, default=1,
        help="Runs per heuristic and instance; the minimum time is reported (default: %(default)s)",
    )
    parser.add_argument(
        "-j", "--workers", type=int, default=1,
        help="Worker processes. >1 speeds up the sweep but adds timing noise (default: %(default)s)",
    )
    parser.add_argument("--limit", type=int, help="Process at most this many instances")
    parser.add_argument(
        "--no-validate", action="store_true",
        help="Skip the (untimed) feasibility check of every packing",
    )
    args = parser.parse_args(argv)
    if args.repeats < 1 or args.workers < 1:
        parser.error("--repeats and --workers must be >= 1")
    if args.instance is not None and not args.instance.is_file():
        parser.error(f"--instance: file not found: {args.instance}")
    if args.output is None and args.instance is None:
        args.output = DEFAULT_OUTPUT
    return args


def _config_from_args(args: argparse.Namespace) -> ExperimentConfig:
    """Build the :class:`ExperimentConfig` described by the parsed arguments."""
    return ExperimentConfig(
        heuristics=tuple(args.heuristics) if args.heuristics else None,
        repeats=args.repeats,
        validate=not args.no_validate,
    )


def _instance_root(path: Path, instances_dir: Path) -> Path:
    """Root used to infer family and relative path of a single instance file.

    ``instances_dir`` when the file lives inside it, otherwise the file's own folder.
    """
    return instances_dir if path.is_relative_to(instances_dir) else path.parent


def run_single(args: argparse.Namespace) -> int:
    """Run the heuristics on ``args.instance``, print a table and optionally write a CSV."""
    path = args.instance.resolve()
    root = _instance_root(path, args.instances_dir.resolve())
    _, rows, error = _safe_run(path, root, _config_from_args(args))
    if error is not None:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    print(format_instance_report(rows))
    if args.output is not None:
        with CsvRowWriter(args.output, RESULT_FIELDS) as writer:
            writer.write_many(rows)
        print(f"\nWrote {writer.rows_written} rows to {args.output}", file=sys.stderr)
    return 0


def _safe_run(path: Path, root: Path, config: ExperimentConfig) -> Outcome:
    """Run one instance, turning exceptions into an error message instead of aborting."""
    try:
        return path, run_instance_file(path, root, config), None
    except Exception as exc:  # noqa: BLE001 - one bad instance must not stop the sweep
        return path, [], f"{type(exc).__name__}: {exc}"


def _run_all(paths: list[Path], root: Path, config: ExperimentConfig, workers: int) -> Iterator[Outcome]:
    """Yield the outcome of every instance, in input order, sequentially or in parallel."""
    task = partial(_safe_run, root=root, config=config)
    if workers == 1:
        yield from map(task, paths)
        return
    chunksize = max(1, min(32, len(paths) // (workers * 8)))
    with ProcessPoolExecutor(max_workers=workers) as pool:
        yield from pool.map(task, paths, chunksize=chunksize)


def run_sweep(args: argparse.Namespace) -> int:
    """Run the heuristics on every selected instance and stream the rows to ``args.output``."""
    root = args.instances_dir.resolve()
    paths = list(islice(iter_instance_paths(root, args.families), args.limit))
    if not paths:
        print(f"No instances found under {root}", file=sys.stderr)
        return 1

    config = _config_from_args(args)
    total = len(paths)
    report_every = max(1, total // 100)
    failures = 0
    print(f"Running {total} instances with {args.workers} worker(s) -> {args.output}", file=sys.stderr)

    with CsvRowWriter(args.output, RESULT_FIELDS) as writer:
        for done, (path, rows, error) in enumerate(_run_all(paths, root, config, args.workers), 1):
            if error is not None:
                failures += 1
                print(f"\nWarning: skipped {path}: {error}", file=sys.stderr)
            writer.write_many(rows)
            if done % report_every == 0 or done == total:
                print(f"\r  {done}/{total} instances", end="", file=sys.stderr, flush=True)

    print(f"\nWrote {writer.rows_written} rows ({failures} instance(s) failed)", file=sys.stderr)
    return 0 if failures == 0 else 2


def main(argv: Sequence[str] | None = None) -> int:
    """Run the experiment described by ``argv``; return the process exit code."""
    args = parse_args(argv)
    return run_single(args) if args.instance is not None else run_sweep(args)
