# `bpp_heuristics` — constructive heuristics for the 1D BPP

Self-contained project that runs classic bin packing heuristics on the
standardized instances (`standarized_instances/`) and records, for every
instance and heuristic, the running time, number of bins, fitness and bin fill.

The heuristics and the experiment runner use only the Python standard library
(Python ≥ 3.10); only the charts need matplotlib.
It reads instances through the shared `scripts/utils` package. The environment
is managed by the uv project in `scripts/` (see `scripts/README.md`); prefix
the commands below with `uv run --project scripts` to use it.

## Usage

From the repository root:

```bash
python3 scripts/run_heuristics.py                       # all instances, all heuristics
python3 scripts/run_heuristics.py -j 8                  # 8 worker processes
python3 scripts/run_heuristics.py --families Hard28 Scholl --heuristics FFD BFD
python3 scripts/run_heuristics.py --repeats 5 --output results/hard28.csv --families Hard28

# single instance: prints a table; add --output to also save a CSV
python3 scripts/run_heuristics.py --instance standarized_instances/BPP.5/BPP.5_100_1.txt
```

Example of the single-instance table:

```
BPP.5/BPP.5_100_1.txt  |  n=137  C=100  L1=30  best=30 (optimal)

heuristic  bins  gap_LB  gap_best   fitness  avg_fill  min_fill  time_ms
------------------------------------------------------------------------
NF           35       5         5  0.747834    0.8571    0.5700    0.027
FF           31       1         1  0.944652    0.9677    0.5000    0.273
FFD          30       0         0  1.000000    1.0000    1.0000    0.313
...
```

`--instance` cannot be combined with `--families`. Files outside
`--instances-dir` are accepted too (their family is reported as `root`).

or, from `scripts/`, `python3 -m bpp_heuristics [options]`. Run with `--help`
for every option. The default output is `results/heuristics_results.csv`.

The full dataset (~19.6k instances × 10 heuristics) takes about 1.5 min with
one process. `-j N` parallelises across instances; it is faster but processes
compete for CPU, so use `-j 1` (default) when the timings themselves matter.

Instances that cannot be parsed are skipped with a warning and the exit code
is `2`. (The 250 `Difficult_Instances/AI` files used to fail this way because of
a wrong header; `scripts/fix_difficult_headers.py` corrected it.)

## Charts

`scripts/plot_heuristics.py` turns any results CSV into PNG charts plus a
summary table, saved next to the CSV (or in `--output-dir`), with the CSV
name as prefix. It needs matplotlib, so run it through uv:

```bash
uv run --project scripts python scripts/plot_heuristics.py results/heuristics_metrics.csv
```

| File | Content |
|------|---------|
| `<name>_gap.png` | Extra bins over the best-known value per instance (over L1 when some instance has no best-known value) |
| `<name>_fitness.png` | Falkenauer fitness per instance |
| `<name>_avg_fill.png` | Average bin fill per instance |
| `<name>_time.png` | Running time per instance (log scale) |
| `<name>_win_rate.png` | Share of instances where each heuristic uses the fewest bins (ties count) |
| `<name>_tradeoff.png` | Median time vs. mean extra bins, one point per heuristic |
| `<name>_summary.csv` | Per-heuristic numbers behind the charts |

Distribution charts show one dot per instance and a median tick. Online
heuristics are blue and their Decreasing variants orange.

## Heuristics

| Name | Rule | Complexity |
|------|------|------------|
| `NF`  | Next Fit: only the last opened bin is considered | O(n) |
| `FF`  | First Fit: earliest opened bin that fits | O(n log n), max segment tree |
| `BF`  | Best Fit: fitting bin with the least residual room | O(n log n)\*, sorted list |
| `WF`  | Worst Fit: bin with the most residual room | O(n log n), heap |
| `AWF` | Almost Worst Fit: fitting bin with the 2nd most room | O(n log n)\*, sorted list |
| `NFD`, `FFD`, `BFD`, `WFD`, `AWFD` | Same rules after sorting items by decreasing weight | + O(n log n) sort |

\* binary search plus `list.insert`/`pop` (fast memmove in practice).

Ties are broken by the lowest bin index. The sort of the Decreasing variants is
part of the heuristic and is included in the timing. Note that most families
other than `BPP*` and `f0*` are already stored in decreasing order, so for them
each heuristic and its Decreasing variant give the same packing.

To add a heuristic, write a `(weights, capacity) -> Packing` function and add
it to `HEURISTICS` in `heuristics/registry.py`.

## Output columns

| Column | Meaning |
|--------|---------|
| `family`, `instance`, `path` | Top-level folder, file name and path relative to the instances root |
| `n_items`, `capacity` | Instance size and bin capacity |
| `best_known`, `is_optimal` | Optimal / best-known bins from the file (empty if `-1`) and whether it is a proven optimum |
| `lower_bound` | L1 = ⌈Σw / C⌉ |
| `heuristic` | Heuristic name |
| `num_bins` | Bins used |
| `fitness` | Falkenauer fitness (see below), in (0, 1], **higher is better** |
| `avg_fill` | Mean of `load / C` over the bins |
| `min_fill` | Fill of the emptiest bin |
| `gap_to_lower_bound` | `num_bins - lower_bound` |
| `gap_to_best_known` | `num_bins - best_known` (empty if unknown) |
| `time_s` | Seconds spent in the heuristic (min over `--repeats`), excluding I/O, validation and metrics |

### Fitness function

Falkenauer & Delchambre (1992), the usual choice for comparing BPP heuristics:

$$ f = \frac{1}{m}\sum_{b=1}^{m}\left(\frac{\text{load}_b}{C}\right)^{2} $$

Unlike the number of bins, it separates packings with the same bin count:
it rewards few very full bins plus one nearly empty bin (close to saving a bin)
over many half-full ones. It equals 1 only when every bin is completely full.

## Layout

```
bpp_heuristics/
├── packing.py          # Packing result (bin loads + item assignment)
├── heuristics/
│   ├── structures.py   # FirstFitTree (max segment tree)
│   ├── online.py       # NF, FF, BF, WF, AWF
│   ├── ordering.py     # decreasing() wrapper -> offline variants
│   └── registry.py     # name -> heuristic mapping
├── metrics.py          # fitness, fill, gaps
├── validation.py       # feasibility check of a packing
├── experiment.py       # run heuristics on one instance -> CSV rows
├── report.py           # text table for single-instance runs
├── analysis.py         # load result CSVs, win rates, per-heuristic summaries
├── plots.py            # matplotlib charts (one function per chart)
├── plot_cli.py         # command line for the charts
├── cli.py              # argument parsing, sweep / single-instance modes, CSV output
└── tests/              # unittest suite
```

## Tests

From `scripts/`:

```bash
python3 -m unittest discover -s bpp_heuristics/tests -t .
```

The optimized heuristics are checked against simple O(n·m) reference
implementations on random instances (identical assignments), and every
packing is checked for feasibility.
