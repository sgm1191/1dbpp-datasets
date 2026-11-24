# Dataset feature and annotation scripts

This directory contains utility scripts to derive standardized metadata from the raw 1D BPP benchmark files.

## Environment (uv)

`scripts/` is a [uv](https://docs.astral.sh/uv/) project (`pyproject.toml`, `uv.lock`,
`.python-version`) with a pinned interpreter (Python ≥ 3.10) and an isolated
virtual environment (`scripts/.venv`, git-ignored). The only third-party
dependency is `matplotlib`, used by `plot_heuristics.py`; everything else uses
only the standard library.

```bash
cd scripts
uv sync                                     # create / update the environment
uv run python run_heuristics.py --help      # run any script through it
uv run python -m unittest discover -s bpp_heuristics/tests -t .
```

From the repository root, add `--project scripts`:

```bash
uv run --project scripts python scripts/run_heuristics.py --families Hard28
```

When a script needs a new library, add it with `uv add <package>` (from
`scripts/`) so that `pyproject.toml` and `uv.lock` stay in sync. Scripts that
only use the standard library also work with plain `python3`.

## Scripts

### `generate_instance_features.py`

Scans the instance directories and extracts per-instance summary statistics from text files.

Usage:

```bash
python3 scripts/generate_instance_features.py --root . --output features/dataset_features.csv
```

This script extracts features such as:

- dataset family,
- instance name,
- file path,
- number of items,
- bin capacity,
- optimal or best-known solution,
- minimum, maximum, mean, and total item weight,
- fill ratio proxy.

### `generate_annotations.py`

Builds a repository-level annotation table that describes each benchmark instance and flags provenance or source information.

Usage:

```bash
python3 scripts/generate_annotations.py --root . --output annotations/dataset_annotations.csv
```

The generated annotation table includes fields such as:

- family,
- instance_id,
- file_path,
- source_collection,
- num_items,
- capacity,
- optimal_value,
- provenance_note,
- reference_status.

### `fix_difficult_headers.py`

Restores the true `//Number of items` and `//Bin Capacity` of
`standarized_instances/Difficult_Instances/{AI,ANI}` from the original BPPLIB
files. They had been taken from the file name, whose second field is the weight
range, not the capacity. The script checks that the weights match the source,
changes only those two values, and is idempotent.

```bash
python3 scripts/fix_difficult_headers.py --dry-run
python3 scripts/fix_difficult_headers.py
```

### `fill_known_solutions.py`

Fills the `-1` best-known value of the BPPLIB instances from `Solutions.xlsx`
(repository root), matching rows by file name. A `Solved` row becomes
`//Optimal Solution <value>`. An open row (best LB < best UB) becomes
`//Known Best Solution <best UB>`. Files that already hold a value are left
untouched. It needs `openpyxl`, which is not a project dependency:

```bash
uv run --project scripts --with openpyxl python scripts/fill_known_solutions.py --dry-run
uv run --project scripts --with openpyxl python scripts/fill_known_solutions.py
```

## Output folders

If the output directories do not exist, the scripts create them automatically.

- `features/`
- `annotations/`

## Notes

- These scripts are intentionally conservative: they parse structured metadata when available and skip malformed or unsupported files with a warning.
- Add or update source-attribution columns as more benchmark provenance becomes available.
- Keep script behavior deterministic and reproducible across the dataset tree.

## Shared package: `utils/`

Reusable helpers for any script in this directory (import with `from utils import ...`
when running from `scripts/` or from a script located in it):

- `BPPInstance` — immutable instance (capacity, weights, best-known value, family, path, L1 bound).
- `read_instance(path, root)` / `parse_instance_text(text)` — parse the standardized format; raise `InstanceFormatError` on malformed files.
- `is_instance_file(path)` — cheap check that skips index files such as `instances.txt`.
- `iter_instance_paths(root, families)` — sorted discovery of instance files, optionally filtered by family.
- `family_of(path, root)`, `REPO_ROOT`, `STANDARDIZED_INSTANCES_DIR` — path helpers.
- `CsvRowWriter` — streaming CSV writer.
- `measure(func, *args, repeats)` — best-of-N wall-clock timing.

## Heuristics project: `bpp_heuristics/`

Runs Next/First/Best/Worst/Almost-Worst Fit and their Decreasing variants on every
standardized instance and records time, bins, Falkenauer fitness and average fill:

```bash
python3 scripts/run_heuristics.py --help
python3 scripts/run_heuristics.py --instance standarized_instances/Hard28/Hard28_BPP13.txt
uv run --project scripts python scripts/plot_heuristics.py results/heuristics_metrics.csv   # charts
```

See [`bpp_heuristics/README.md`](bpp_heuristics/README.md) for details.
