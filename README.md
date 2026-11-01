# 1D Bin Packing Problem (BPP) Datasets

This repository collects benchmark instances for the one-dimensional bin packing problem (1D BPP), also known as the cutting-stock / bin packing optimization problem. The collection includes both raw benchmark families from the literature and standardized subsets prepared for experimentation.

The goal is to provide a single, versioned, self-contained dataset catalog for reproducible benchmarking and feature extraction in machine learning and optimization studies.

## Repository structure

- `source_instances/` — original or minimally processed benchmark families.
- `standarized_instances/` — curated subsets standardized for experimental use.
- `scripts/` — utilities to extract metadata, compute dataset features, and create annotation tables.
- `annotations/` — generated dataset annotation files (created by scripts).
- `features/` — generated feature tables (created by scripts).

## Problem definition

The 1D BPP is defined as follows:

- A set of items with positive weights is given.
- A set of bins with identical capacity is available.
- Each item must be assigned to one bin.
- The sum of item weights in each bin cannot exceed the bin capacity.
- The objective is to minimize the number of used bins.

Typical metadata in each instance includes:

- number of items,
- bin capacity,
- optional optimal or best-known solution value,
- item weights.

## Data format conventions

Files are plain-text benchmarks. Most files include comments, such as:

```text
//Number of items
126
//Bin Capacity
100
//Optimal Solution
15
//Weight of Item
4
1
17
9
...
```

Some benchmark families follow the same core pattern; others are raw benchmark files with different naming conventions. The scripts in `scripts/` normalize these differences and extract a consistent feature representation.

## Dataset families

### 1. `source_instances/bpplib/`

This is the main benchmark source from the BPPLIB collection and related bin-packing benchmark families.

- `Difficult_Instances/` — difficult benchmark instances used in challenging optimization settings.
- `Falkenauer/` — benchmark family associated with Falkenauer-style bin packing instances.
- `Hard28/` — smaller but difficult benchmark sets often used for hard instances.
- `Irnich_BPP/` — instances associated with Irnich and related bin-packing studies.
- `Randomly_Generated/` — synthetic random benchmark sets.
- `SSTriples-BPP/` — benchmark family with structured triple-based generation patterns.
- `Scholl/` — benchmark family associated with Scholl and related BPP literature.
- `Schwerin/` — benchmark family from the Schwerin benchmark suite.
- `Wäscher/` — benchmark family tied to Wäscher-style BPP instances.

#### References

- BPPLIB / bin packing benchmark library: likely associated with benchmark collections used in BPP research (see Scholl, Klein, and related benchmark suites).  
- Falkenauer: likely from Falkenauer's grouping genetic algorithm work on bin packing.  
- Scholl / Schwerin / Wäscher: commonly used benchmark families in the bin-packing literature.  
- `Hard28`, `Irnich_BPP`, `Randomly_Generated`, `SSTriples-BPP`: provenance should be confirmed for each subfamily. Leave a placeholder if not yet assigned.

### 2. `source_instances/cga-cct-instances/`

This directory contains the synthetic BPP instances generated under the CGA-CCT benchmark family structure.

- `bpp_instances/` — generated bin-packing instances organized by family and size.
- Naming conventions include `BPP_*` and pattern-based instance identifiers such as `N...` and `bpp1` groups.

#### Reference

- Unknown or not yet formally attributed in this repository. Add publication or benchmark origin here when identified.

### 3. `standarized_instances/`

This directory contains curated benchmark subsets standardized for experimental evaluation. These are often arranged by family and scale.

- `BPP.5/` — reduced benchmark family with bin capacity scaling factor approximately 5.
- `BPP.25/` — capacity-setting benchmark family with scale factor 25.
- `BPP.75/` — capacity-setting benchmark family with scale factor 75.
- `BPP1/` — benchmark family at unit capacity scale.
- `Difficult_Instances/` — difficult benchmark sets selected for harder optimization regimes.
- `f0/` through `f0.4/` — frequency or fill-ratio style benchmark partitions, typically designed for structured scaling analyses.
- `Falkenauer/` — standardized Falkenauer-derived instances.
- `Hard28/` — standardized difficult set.
- `Irnich_BPP/` — standardized Irnich family.
- `Randomly_Generated/` — random benchmark subsets.
- `Scholl/` — standardized Scholl subsets.
- `Schwerin/` — standardized Schwerin subsets.
- `SSTriples-BPP/` — structured triple-based synthetics.
- `Wäscher/` — standardized Wäscher benchmarks.

#### Reference

- Standardized families are derived from published benchmark sources and/or internal preprocessing steps. Fill in exact paper/source attributions when available.

## Known references and provenance notes

The following list is intentionally conservative. Some references are well established in the bin-packing literature; others are left as placeholders because the exact original source was not yet confirmed at repository setup time.

- Falkenauer, E. — Grouping Genetic Algorithm for Bin Packing and Related Problems  
- Scholl, A.; Klein, R. — Bin packing benchmark generation and algorithmic evaluations  
- Schwerin, S.; Wäscher, G. — Benchmark instances for cutting and packing  
- Wäscher, G.; Gau, T. — Bin packing benchmark suites and one-dimensional cutting stock literature  
- BPPLIB benchmark collection — benchmark repository used for BPP experimentation  
- Hard28 — source to be added  
- Irnich_BPP — source to be added  
- SSTriples-BPP — source to be added  
- Randomly_Generated — source to be added  
- CGA-CCT generated synthetic instances — source to be added  
- BPP.5, BPP.25, BPP.75, BPP1 — source to be added  

## Suggested usage

This repository is designed for:

- benchmarking optimization methods,
- comparing heuristic and exact approaches,
- extracting statistical dataset features,
- training machine learning models on BPP instance structure,
- annotating instance difficulty and structure.

## Data processing and feature generation

The scripts in `scripts/` create structured feature tables and annotation metadata from the benchmark files.

### Available scripts

- `scripts/generate_instance_features.py` — builds a CSV feature table from the instance files.
- `scripts/generate_annotations.py` — creates a dataset annotation manifest for each benchmark instance.
- `scripts/README.md` — usage instructions and expected outputs.

### Typical generated outputs

- `features/dataset_features.csv`
- `annotations/dataset_annotations.csv`

These outputs include fields such as:

- dataset family,
- instance name,
- file path,
- number of items,
- bin capacity,
- optimal or best-known value,
- total item weight,
- minimum/maximum item weight,
- mean item weight,
- notes and provenance tags.

## Notes for maintainers

- This repository is intentionally documented for future expansion.
- Missing references should be filled in as soon as provenance is confirmed.
- The raw benchmark files should not be renamed without updating the annotation manifest.
- Generated feature and annotation files are meant to be reproducible from the source data.

## License

The repository metadata and scripts are provided for dataset organization and research use. Please check the original benchmark sources and their licenses before redistribution or reuse of the raw data files.

---

This document is a working catalog and should be updated as references, provenance, and benchmark metadata become more precise.
