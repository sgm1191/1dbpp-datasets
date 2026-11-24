"""Streaming CSV output."""

from __future__ import annotations

import csv
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from types import TracebackType
from typing import Any


class CsvRowWriter:
    """Context manager that writes dict rows to a CSV file as they arrive.

    Rows are flushed to disk incrementally, so long experiments keep partial
    results if interrupted. Parent directories are created automatically.

    Example::

        with CsvRowWriter(Path("out.csv"), ["a", "b"]) as writer:
            writer.write({"a": 1, "b": 2})
    """

    def __init__(self, path: Path, fieldnames: Sequence[str]) -> None:
        """Prepare a writer for ``path`` with the given column order."""
        self.path = path
        self.fieldnames = list(fieldnames)
        self._handle = None
        self._writer: csv.DictWriter | None = None
        self.rows_written = 0

    def __enter__(self) -> CsvRowWriter:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._handle = self.path.open("w", newline="", encoding="utf-8")
        self._writer = csv.DictWriter(self._handle, fieldnames=self.fieldnames, extrasaction="ignore")
        self._writer.writeheader()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self._handle is not None:
            self._handle.close()

    def write(self, row: Mapping[str, Any]) -> None:
        """Write a single row; keys not in ``fieldnames`` are ignored."""
        if self._writer is None:
            raise RuntimeError("CsvRowWriter must be used as a context manager")
        self._writer.writerow(row)
        self.rows_written += 1

    def write_many(self, rows: Iterable[Mapping[str, Any]]) -> None:
        """Write several rows and flush them to disk."""
        for row in rows:
            self.write(row)
        if self._handle is not None:
            self._handle.flush()
