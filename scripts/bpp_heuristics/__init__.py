"""Constructive heuristics for the one-dimensional bin packing problem.

Self-contained project that runs classic packing heuristics (Next/First/Best/
Worst/Almost-Worst Fit and their Decreasing variants) on the standardized
instances and records, per instance and heuristic, the number of bins, the
Falkenauer fitness, the average bin fill and the running time.

Modules:

- :mod:`bpp_heuristics.packing` -- the :class:`Packing` result type.
- :mod:`bpp_heuristics.heuristics` -- heuristic implementations and registry.
- :mod:`bpp_heuristics.metrics` -- fitness and other quality metrics.
- :mod:`bpp_heuristics.validation` -- feasibility checks.
- :mod:`bpp_heuristics.experiment` -- running heuristics on one instance.
- :mod:`bpp_heuristics.report` -- text table of the results of one instance.
- :mod:`bpp_heuristics.cli` -- command line (dataset sweep or single instance).
- :mod:`bpp_heuristics.analysis` -- loading and summarising result CSVs.
- :mod:`bpp_heuristics.plots` -- performance charts (requires matplotlib).
- :mod:`bpp_heuristics.plot_cli` -- command line for the charts.
"""
