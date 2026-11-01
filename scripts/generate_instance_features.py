#!/usr/bin/env python3
"""Generate a compact CSV feature table for 1D BPP benchmark instances."""

from __future__ import annotations

import argparse
import csv
import os
import re
from pathlib import Path
from typing import Iterable


COMMENT_PREFIXES = ("//", "#", ";")


def iter_instance_files(root: Path) -> Iterable[Path]:
    for candidate in sorted(root.rglob("*")):
        if candidate.is_file() and candidate.suffix.lower() in {".txt", ".dat", ".bpp", ".inst"}:
            yield candidate


def parse_metadata(file_path: Path) -> dict:
    metadata: dict[str, object] = {
        "num_items": None,
        "capacity": None,
        "optimal_solution": None,
        "weights": [],
    }

    text = file_path.read_text(encoding="utf-8", errors="ignore")
    lines = [line.strip() for line in text.splitlines()]

    for idx, line in enumerate(lines):
        if not line:
            continue

        m = re.match(r"^(?://|#|;)?\s*(?:Number of items|n_items|items|num_items|n)\s*[:=]?\s*(\d+)", line, re.IGNORECASE)
        if m:
            metadata["num_items"] = int(m.group(1))
            continue

        m = re.match(r"^(?://|#|;)?\s*(?:Bin Capacity|capacity|c)\s*[:=]?\s*(\d+(?:\.\d+)?)", line, re.IGNORECASE)
        if m:
            metadata["capacity"] = float(m.group(1)) if "." in m.group(1) else int(m.group(1))
            continue

        m = re.match(r"^(?://|#|;)?\s*(?:Optimal Solution|opt|optimal)\s*[:=]?\s*(\d+(?:\.\d+)?)", line, re.IGNORECASE)
        if m:
            metadata["optimal_solution"] = float(m.group(1)) if "." in m.group(1) else int(m.group(1))
            continue

        # Accept numeric token lines that are item weights.
        if re.fullmatch(r"[-+]?\d+(?:\.\d+)?", line):
            try:
                metadata["weights"].append(float(line))
            except ValueError:
                pass

    if not metadata["weights"] and metadata["num_items"] is not None:
        # Fallback: extract numeric tokens from the file body.
        for token in re.findall(r"[-+]?\d+(?:\.\d+)?", text):
            if token.startswith("//"):
                continue
            try:
                metadata["weights"].append(float(token))
            except ValueError:
                continue

    return metadata


def summarize_instance(root: Path, file_path: Path) -> dict:
    rel = file_path.relative_to(root)
    metadata = parse_metadata(file_path)
    weights = metadata["weights"]

    if weights:
        min_weight = min(weights)
        max_weight = max(weights)
        total_weight = sum(weights)
        mean_weight = total_weight / len(weights)
    else:
        min_weight = max_weight = total_weight = mean_weight = None

    capacity = metadata.get("capacity")
    num_items = metadata.get("num_items")
    if num_items is not None and isinstance(num_items, int) and num_items > 0 and weights:
        if len(weights) >= num_items:
            weights = weights[:num_items]

    fill_ratio = None
    if capacity is not None and isinstance(capacity, (int, float)) and capacity > 0 and total_weight is not None:
        fill_ratio = total_weight / (capacity * (len(weights) if len(weights) else 1))

    family = rel.parts[0] if len(rel.parts) > 1 else "root"
    if len(rel.parts) > 1 and rel.parts[0] in {"source_instances", "standarized_instances"}:
        family = rel.parts[1] if len(rel.parts) > 1 else rel.parts[0]

    return {
        "family": family,
        "instance_name": file_path.name,
        "path": str(rel).replace(os.sep, "/"),
        "num_items": num_items,
        "capacity": capacity,
        "optimal_solution": metadata.get("optimal_solution"),
        "min_weight": min_weight,
        "max_weight": max_weight,
        "mean_weight": mean_weight,
        "total_weight": total_weight,
        "fill_ratio": fill_ratio,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a CSV feature table for BPP datasets.")
    parser.add_argument("--root", type=Path, default=Path("."), help="Repository root containing the dataset folders")
    parser.add_argument("--output", type=Path, default=Path("features/dataset_features.csv"), help="Output CSV path")
    args = parser.parse_args()

    root = args.root.resolve()
    output = args.output
    output.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for file_path in iter_instance_files(root):
        if "scripts" in file_path.parts:
            continue
        if any(part in {".git", "__pycache__"} for part in file_path.parts):
            continue
        try:
            rows.append(summarize_instance(root, file_path))
        except Exception as exc:  # pragma: no cover - nonfatal parser issue
            print(f"Warning: could not parse {file_path}: {exc}")

    fieldnames = [
        "family",
        "instance_name",
        "path",
        "num_items",
        "capacity",
        "optimal_solution",
        "min_weight",
        "max_weight",
        "mean_weight",
        "total_weight",
        "fill_ratio",
    ]

    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k) for k in fieldnames})

    print(f"Wrote {len(rows)} feature rows to {output}")


if __name__ == "__main__":
    main()
