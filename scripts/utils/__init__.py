"""Reusable helpers shared by the scripts in ``scripts/``.

Submodules:

- :mod:`utils.instance` -- in-memory representation of a 1D BPP instance.
- :mod:`utils.instance_reader` -- parsing of standardized instance files.
- :mod:`utils.discovery` -- locating instance files in the dataset tree.
- :mod:`utils.paths` -- well-known repository paths and family inference.
- :mod:`utils.csv_io` -- streaming CSV writer.
- :mod:`utils.timing` -- wall-clock measurement of callables.

The most common names are re-exported here for convenience.
"""

from utils.csv_io import CsvRowWriter
from utils.discovery import iter_instance_paths
from utils.instance import BPPInstance
from utils.instance_reader import InstanceFormatError, is_instance_file, read_instance
from utils.paths import REPO_ROOT, STANDARDIZED_INSTANCES_DIR, family_of
from utils.timing import measure

__all__ = [
    "BPPInstance",
    "CsvRowWriter",
    "InstanceFormatError",
    "REPO_ROOT",
    "STANDARDIZED_INSTANCES_DIR",
    "family_of",
    "is_instance_file",
    "iter_instance_paths",
    "measure",
    "read_instance",
]
