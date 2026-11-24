"""Command line: build performance charts and a summary table from a results CSV."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from dataclasses import asdict, fields
from pathlib import Path

from bpp_heuristics.analysis import HeuristicSummary, load_results, summarize, uses_best_known
from bpp_heuristics.plots import (
    plot_avg_fill,
    plot_fitness,
    plot_gap,
    plot_time,
    plot_tradeoff,
    plot_win_rate,
)
from utils import CsvRowWriter


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse the command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="plot_heuristics",
        description="Plot per-heuristic performance from a CSV written by run_heuristics.py.",
    )
    parser.add_argument("results", type=Path, help="Results CSV to plot")
    parser.add_argument(
        "--output-dir", type=Path,
        help="Folder for the PNGs and summary CSV (default: the folder of the results CSV)",
    )
    parser.add_argument(
        "--prefix", default="",
        help="Prefix for the output file names (default: the results file name, e.g. 'heuristics_metrics_')",
    )
    args = parser.parse_args(argv)
    if not args.results.is_file():
        parser.error(f"results file not found: {args.results}")
    args.output_dir = args.output_dir or args.results.parent
    args.prefix = args.prefix or f"{args.results.stem}_"
    return args


def write_summary(summaries: list[HeuristicSummary], path: Path) -> Path:
    """Write the per-heuristic summary table (the data behind the charts) as CSV."""
    with CsvRowWriter(path, [field.name for field in fields(HeuristicSummary)]) as writer:
        writer.write_many(asdict(summary) for summary in summaries)
    return path


def main(argv: Sequence[str] | None = None) -> int:
    """Generate every chart and the summary CSV; return the process exit code."""
    args = parse_args(argv)
    rows = load_results(args.results)
    if not rows:
        print(f"No rows in {args.results}", file=sys.stderr)
        return 1
    summaries = summarize(rows)
    out = args.output_dir / args.prefix
    gap_label = "best known" if uses_best_known(rows) else "L1"

    written = [
        plot_gap(rows, Path(f"{out}gap.png")),
        plot_fitness(rows, Path(f"{out}fitness.png")),
        plot_avg_fill(rows, Path(f"{out}avg_fill.png")),
        plot_time(rows, Path(f"{out}time.png")),
        plot_win_rate(summaries, Path(f"{out}win_rate.png")),
        plot_tradeoff(summaries, gap_label, Path(f"{out}tradeoff.png")),
        write_summary(summaries, Path(f"{out}summary.csv")),
    ]
    instances = len({row.instance for row in rows})
    print(f"{len(rows)} rows, {instances} instances, {len(summaries)} heuristics", file=sys.stderr)
    for path in written:
        print(f"  {path}", file=sys.stderr)
    return 0
