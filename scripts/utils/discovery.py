"""Discovery of instance files inside the dataset tree."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from pathlib import Path

from utils.instance_reader import is_instance_file
from utils.paths import family_of


def iter_instance_paths(root: Path, families: Iterable[str] | None = None) -> Iterator[Path]:
    """Yield, in sorted order, every standardized instance file under ``root``.

    Files that are not instances (index files, hidden files, ...) are skipped
    using :func:`utils.instance_reader.is_instance_file`.

    Args:
        root: Directory to scan recursively.
        families: Optional names of top-level folders to restrict the scan to.
    """
    wanted = set(families) if families else None
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name.startswith("."):
            continue
        if wanted is not None and family_of(path, root) not in wanted:
            continue
        if is_instance_file(path):
            yield path
