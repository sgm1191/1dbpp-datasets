#!/usr/bin/env python3
"""Create a dataset annotation CSV for all 1D BPP benchmark files."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


DEFAULT_REFERENCE = "To be filled in"


def iter_files(root: Path):
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() in {".txt", ".dat", ".bpp", ".inst"}:
            if any(part in {".git", "__pycache__"} for part in path.parts):
                continue
            if "scripts" in path.parts:
                continue
            yield path


def infer_family(path: Path, root: Path) -> str:
    rel = path.relative_to(root)
    parts = rel.parts
    if len(parts) >= 2 and parts[0] in {"source_instances", "standarized_instances"}:
        return parts[1]
    if len(parts) >= 2:
        return parts[0]
    return "root"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate dataset annotations for BPP instance files.")
    parser.add_argument("--root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument("--output", type=Path, default=Path("annotations/dataset_annotations.csv"), help="Output CSV path")
    args = parser.parse_args()

    root = args.root.resolve()
    output = args.output
    output.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for file_path in iter_files(root):
        rel = file_path.relative_to(root)
        family = infer_family(file_path, root)
        rows.append(
            {
                "family": family,
                "instance_name": file_path.name,
                "path": str(rel).replace("\\", "/"),
                "source_collection": family,
                "n_items": "unknown",
                "capacity": "unknown",
                "optimal_value": "unknown",
                "provenance_note": "Dataset provenance to be confirmed",
                "reference": DEFAULT_REFERENCE,
                "reference_status": "pending",
            }
        )

    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "family",
                "instance_name",
                "path",
                "source_collection",
                "n_items",
                "capacity",
                "optimal_value",
                "provenance_note",
                "reference",
                "reference_status",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} annotation rows to {output}")


if __name__ == "__main__":
    main()
