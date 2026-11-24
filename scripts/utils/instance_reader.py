"""Parsing of standardized 1D BPP instance files.

Standardized files consist of ``//``-prefixed section headers, each followed
by its value(s)::

    //Number of items
    126
    //Bin Capacity
    100
    //Optimal Solution          (or //Known Best Solution, -1 if unknown)
    15
    //Weight of Item
    4
    1
    ...

Some folders also contain index files (e.g. ``instances.txt``) that only list
file names; :func:`is_instance_file` tells them apart cheaply.
"""

from __future__ import annotations

from pathlib import Path

from utils.instance import BPPInstance
from utils.paths import family_of

_HEADER_PREFIX = "//"
_FIRST_HEADER = "//Number of items"

_N_ITEMS = "number of items"
_CAPACITY = "bin capacity"
_OPTIMAL = "optimal solution"
_BEST_KNOWN = "known best solution"
_WEIGHTS = "weight of item"


class InstanceFormatError(ValueError):
    """Raised when a file does not follow the standardized instance format."""


def is_instance_file(path: Path) -> bool:
    """Return whether ``path`` looks like a standardized instance file.

    Only the first line is read, so this is cheap enough to call on every
    file of the dataset tree.
    """
    try:
        with path.open("r", encoding="utf-8") as handle:
            return handle.readline().strip() == _FIRST_HEADER
    except (OSError, UnicodeDecodeError):
        return False


def _to_number(token: str) -> int:
    """Convert a numeric token to ``int``, accepting integral floats like ``"3.0"``."""
    try:
        return int(token)
    except ValueError:
        value = float(token)
        if not value.is_integer():
            raise InstanceFormatError(f"non-integer value {token!r}") from None
        return int(value)


def _split_sections(text: str) -> dict[str, list[str]]:
    """Group the non-empty lines of ``text`` under their lower-cased ``//`` header."""
    sections: dict[str, list[str]] = {}
    current: list[str] | None = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith(_HEADER_PREFIX):
            current = sections.setdefault(line[len(_HEADER_PREFIX):].strip().lower(), [])
        elif current is None:
            raise InstanceFormatError(f"value {line!r} found before any header")
        else:
            current.append(line)
    return sections


def _single_value(sections: dict[str, list[str]], key: str) -> int:
    """Return the only value stored under section ``key``."""
    values = sections.get(key)
    if not values or len(values) != 1:
        raise InstanceFormatError(f"section {key!r} must contain exactly one value")
    return _to_number(values[0])


def parse_instance_text(text: str, name: str = "", family: str = "", path: str = "") -> BPPInstance:
    """Build a :class:`BPPInstance` from the contents of a standardized file.

    Args:
        text: Full file contents.
        name: Instance name to store in the result.
        family: Benchmark family to store in the result.
        path: Relative source path to store in the result.

    Raises:
        InstanceFormatError: If a mandatory section is missing or malformed,
            or if the number of weights does not match the declared count.
    """
    sections = _split_sections(text)
    n_items = _single_value(sections, _N_ITEMS)
    capacity = _single_value(sections, _CAPACITY)
    weights = tuple(_to_number(token) for token in sections.get(_WEIGHTS, ()))

    if len(weights) != n_items:
        raise InstanceFormatError(f"declared {n_items} items but found {len(weights)} weights")
    if capacity <= 0:
        raise InstanceFormatError(f"capacity must be positive, got {capacity}")

    is_optimal = _OPTIMAL in sections
    best_key = _OPTIMAL if is_optimal else _BEST_KNOWN
    best_known: int | None = _single_value(sections, best_key) if best_key in sections else None
    if best_known is not None and best_known <= 0:
        best_known, is_optimal = None, False

    return BPPInstance(
        name=name,
        capacity=capacity,
        weights=weights,
        best_known=best_known,
        is_optimal=is_optimal,
        family=family,
        path=path,
    )


def read_instance(path: Path, root: Path | None = None) -> BPPInstance:
    """Read and parse the instance stored at ``path``.

    Args:
        path: File to read.
        root: Instances root. When given, the instance ``family`` and relative
            ``path`` are inferred from the location of the file under it.

    Raises:
        InstanceFormatError: If the file is not a valid standardized instance.
    """
    family, rel_path = "", str(path)
    if root is not None:
        family = family_of(path, root)
        rel_path = path.relative_to(root).as_posix()
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise InstanceFormatError(f"{path}: not a UTF-8 text file") from exc
    try:
        return parse_instance_text(text, name=path.name, family=family, path=rel_path)
    except InstanceFormatError as exc:
        raise InstanceFormatError(f"{path}: {exc}") from exc
