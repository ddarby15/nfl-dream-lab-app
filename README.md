# NFL Dream Lab

NFL Dream Lab is an NFL analytics application for evaluating players, identifying draft value, discovering waiver opportunities, and understanding player trends through historical performance, usage, and opportunity data.

> Changes in opportunity can precede changes in fantasy production.

The project will emphasize interpretable metrics and transparent signals before introducing composite scores or machine learning.

## Current Status

NFL Dream Lab is currently in **Phase 1 — Notebook Data Pipeline Prototyping**. Application and production-pipeline implementation have not started.

The immediate focus is to understand nflverse data, validate metric definitions against real players, and produce reliable starter Bronze, Silver, and Gold datasets through Jupyter notebooks.

See [ROADMAP.md](ROADMAP.md) for the complete architecture, development sequence, deliverables, and exit criteria.

## Product Areas

- **Draft Analysis:** Evaluate historical player-season opportunity and production profiles.
- **Waiver Wire:** Identify meaningful recent changes in role and opportunity before production necessarily follows.
- **Player Explorer:** Understand a player's historical performance, current usage, and weekly trends.

## Data Architecture

NFL Dream Lab uses a shared medallion architecture:

```text
nflverse
    ↓
  Bronze     Source-oriented data with minimal transformation
    ↓
  Silver     Clean, normalized, trusted football facts
    ↓
   Gold      Features designed for fantasy decisions
    ↓
Streamlit    Draft Analysis, Waiver Wire, and Player Explorer
```

Bronze and Silver are reusable foundations across the application. Use cases primarily diverge at the Gold layer.

## Development Approach

The project is intentionally developed in stages:

```text
Research question
      ↓
Notebook prototype and validation
      ↓
Usable Gold dataset
      ↓
Streamlit product validation
      ↓
Reusable src modules and tests
      ↓
Executable pipelines
      ↓
Airflow automation
```

The future-state repository structure in the roadmap is directional, not a scaffold to create upfront. Infrastructure is added only when the current phase requires it.

## Initial Technology Direction

- **Language:** Python
- **Primary source:** nflverse through `nflreadpy`
- **DataFrames:** Polars where practical
- **Local storage:** Parquet
- **Research:** Jupyter notebooks
- **Application:** Streamlit
- **Future orchestration:** Apache Airflow

Installation and usage instructions will be added once the first runnable project environment exists.

## License

NFL Dream Lab is available under the [MIT License](LICENSE).
