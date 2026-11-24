"""Well-known paths of the dataset repository."""

from __future__ import annotations

from pathlib import Path

#: Root of the repository (parent of ``scripts/``).
REPO_ROOT: Path = Path(__file__).resolve().parents[2]

#: Directory holding the standardized benchmark instances.
STANDARDIZED_INSTANCES_DIR: Path = REPO_ROOT / "standarized_instances"


def family_of(path: Path, root: Path) -> str:
    """Return the benchmark family of ``path``: its top-level folder under ``root``.

    Files stored directly under ``root`` get the family ``"root"``.
    """
    parts = path.relative_to(root).parts
    return parts[0] if len(parts) > 1 else "root"
