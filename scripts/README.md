# Dataset feature and annotation scripts

This directory contains utility scripts to derive standardized metadata from the raw 1D BPP benchmark files.

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

## Output folders

If the output directories do not exist, the scripts create them automatically.

- `features/`
- `annotations/`

## Notes

- These scripts are intentionally conservative: they parse structured metadata when available and skip malformed or unsupported files with a warning.
- Add or update source-attribution columns as more benchmark provenance becomes available.
- Keep script behavior deterministic and reproducible across the dataset tree.
