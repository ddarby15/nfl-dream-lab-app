# NFL Dream Lab Development Roadmap

## Purpose

NFL Dream Lab is an NFL analytics application for evaluating players, identifying draft value, discovering waiver opportunities, and understanding player trends through historical performance, usage, and opportunity data.

This roadmap is the source of truth for the intended architecture and development sequence. It describes a future state, not a scaffold to generate immediately. The repository should gain directories, modules, and infrastructure only as the phase that needs them begins.

## Current Status

**Current phase: Phase 1 — Notebook Data Pipeline Prototyping**

Application and production-pipeline implementation have not started. The immediate goal is to understand the source data and validate useful football and fantasy metrics in notebooks.

## Product and Development Philosophy

The project follows this promotion path:

```text
Research / Question
        ↓
Notebook Prototype
        ↓
Validate Data + Metric Definition
        ↓
Build Usable Gold Dataset
        ↓
Test Dataset Through Streamlit
        ↓
Promote Stable Logic to src/
        ↓
Build Executable Pipelines
        ↓
Automate with Airflow
```

The notebook is the laboratory. Feature engineering should not be productionized until its source data, grain, definitions, edge cases, and usefulness in the application have been validated.

A central product hypothesis is:

> Changes in opportunity can precede changes in fantasy production.

Initial features and signals should therefore be interpretable. Composite scores, machine learning, databases, authentication, and cloud infrastructure should wait until a demonstrated need justifies them.

## Architecture

### Data layers

| Layer | Responsibility | Examples | Exclusions |
|---|---|---|---|
| Bronze | Preserve source-oriented nflverse data with minimal transformation. | Play-by-play, weekly player stats, weekly rosters, snap counts, schedules, player metadata. | Fantasy feature engineering such as shares, rolling averages, opportunity scores, or breakout flags. |
| Silver | Produce clean, normalized, trusted football facts at explicit grains. | Player-week facts, game participation, team-week opportunity, standardized plays, position-specific weekly facts. | Page-specific datasets and opaque fantasy rankings. |
| Gold | Create decision-oriented fantasy features for application use cases. | Draft season profiles, waiver trends, player history, transparent derived signals. | Raw ingestion concerns and duplicated foundational cleaning. |

Bronze and Silver are shared foundations. They must not be duplicated for individual application pages. Use cases should primarily diverge in Gold:

```text
                  nflverse
                     ↓
                   Bronze
                     ↓
                   Silver
                     ↓
          ┌──────────┼──────────┐
          ↓          ↓          ↓
       Draft       Waiver     Player
        Gold         Gold       Gold
          └──────────┼──────────┘
                     ↓
                  Streamlit
```

### Component responsibilities

| Component | Responsibility |
|---|---|
| Notebooks | Explore source data, prototype transformations, validate definitions, investigate edge cases, and compare results with recognizable players. |
| `src/` | Hold stable, reusable, tested transformation logic after it has earned promotion from notebooks. |
| Pipelines | Define what runs and in what order by orchestrating `src/` functions; they should not duplicate business logic. |
| Streamlit | Consume Gold datasets to support fantasy decisions; it should not perform substantial feature engineering. |
| Airflow | Schedule and observe an already-working pipeline; DAGs should not become the transformation layer. |

### Initial technology direction

- Primary data source: nflverse through `nflreadpy`
- Language: Python
- DataFrames: `nflreadpy` loads Polars DataFrames; Phase 1 notebooks convert them deliberately to pandas for `eda_utils` profiling and transformations
- Development storage: local Parquet files
- Research: Jupyter notebooks
- Initial application: Streamlit
- Future orchestration: Apache Airflow
- Database: deferred until a concrete application requirement emerges

## Application Areas

### Draft Analysis

**Primary question:** What has this player historically demonstrated, and which players appear most valuable based on their opportunity and production profiles?

Draft Analysis will primarily use player-season Gold datasets by position, initially WR, RB, and QB. It should support filtering, sorting, player and season comparison, and percentile profiles. V1 does not require a proprietary draft score.

Candidate datasets:

- `gold/draft/wr_season_features`
- `gold/draft/rb_season_features`
- `gold/draft/qb_season_features`
- A TE dataset may be added later

### Waiver Wire

**Primary question:** Whose role or opportunity is changing right now?

Waiver analysis is a weekly and rolling-window problem. It should compare current-week, recent-window, and season-to-date opportunity and production rather than rank only the previous week's fantasy points.

Candidate dataset:

- `gold/waiver/player_weekly_trends` at `player_id + season + week`

Initial signals should be transparent and rule-based, such as rising usage or high opportunity with low production. Thresholds and underlying measures must remain visible to the user.

### Player Explorer

**Primary question:** What is the complete historical and recent story for this player?

Player Explorer should reuse the Draft and Waiver Gold products wherever possible. It should combine season-over-season profiles with current-season weekly and rolling trends so users can distinguish sustained role changes from one-week box-score noise.

Candidate supporting dataset:

- `gold/player/player_history` at `player_id + season + week`

This dataset should exist only if it provides a useful, non-duplicative access shape over shared Gold features.

## Roadmap Overview

| Phase | Status | Outcome |
|---|---|---|
| 1. Notebook Data Pipeline Prototyping | **Current** | Validated starter Bronze, Silver, and Gold Parquet datasets |
| 2. Streamlit Application Prototype | Planned | A useful local application consuming Gold datasets |
| 3. Promote Notebook Logic to `src/` | Planned | Reusable, tested transformation modules |
| 4. Pipeline Scripts | Planned | Repeatable one-command/manual data refresh |
| 5. Airflow Automation | Planned | Scheduled orchestration of the proven pipeline |

## Phase 1 — Notebook Data Pipeline Prototyping

### Objective

Understand nflverse data and prototype the Bronze → Silver → Gold flow in Jupyter notebooks before committing transformation logic to production modules.

### Dependencies

- The existing `sports_dev_env` Conda environment
- Access to the required nflverse datasets through `nflreadpy`
- The initial 2023–2025 season scope
- Full PPR as the default scoring format, with scoring-neutral components retained for future half-PPR support

### Notebook milestones

#### 1. Source and schema inventory

**Status: Completed 2026-09-07**

- Inspect available `nflreadpy` loaders and returned Polars schemas.
- Record source grains, identifiers, coverage, update behavior, and key nullability.
- Determine which sources are required for the first WR, RB, and QB metrics.
- Identify joins and known source limitations before persisting data.

The executed inventory is in `notebooks/bronze/01_nflverse_source_inventory.ipynb`. It loaded all seven candidate sources, identified the initial WR source set and candidate grains, and documented identifier, memory, and source-quality caveats before Bronze persistence.

#### 2. Bronze ingestion prototypes

**Status: Completed 2026-09-07**

- Extract the smallest useful set of seasons and source datasets.
- Persist source-oriented local Parquet datasets with minimal transformation.
- Validate row counts, partitions, schemas, uniqueness expectations, and reload behavior.
- Keep source metadata needed to reproduce or audit an extraction.

The core non-PBP sources are persisted by `notebooks/bronze/02_bronze_core_sources.ipynb`, and `notebooks/bronze/03_bronze_play_by_play.ipynb` persists play-by-play one season at a time. Together they provide the initial 2023–2025 Bronze inputs for the WR slice.

Candidate Bronze data:

- `data/bronze/pbp/`
- `data/bronze/player_weekly_stats/`
- `data/bronze/rosters_weekly/`
- `data/bronze/snap_counts/`
- `data/bronze/schedules/`
- `data/bronze/players/`

#### 3. Identity, participation, and grain validation

- Establish the canonical player identifier and inspect cross-source identifier coverage.
- Validate player/team/week relationships, including team changes and traded players.
- Define game and weekly participation rules.
- Document duplicate, inactive-player, missing-team, and multi-team edge cases.

#### 4. Shared Silver prototypes

- Prototype `silver_player_week` at `player_id + season + week + team`.
- Prototype `silver_player_game_participation` at `player_id + game_id`.
- Prototype `silver_team_week_opportunity` at `team + season + week`.
- Standardize the play classifications and denominators required by downstream shares.
- Add checks for unique grains, valid relationships, and plausible totals.

#### 5. Position-level Silver facts

- Prototype WR, RB, and QB weekly facts only where a shared table cannot express the facts clearly.
- Validate passing, rushing, receiving, red-zone, goal-line, and air-yard concepts.
- Explicitly define meaningful QB rush attempts and the treatment of kneel-downs.
- Confirm that position-specific facts reuse the shared Silver foundation.

#### 6. Historical Draft Gold features

- Aggregate validated weekly facts into player-season WR, RB, and QB profiles.
- Include volume, share, efficiency, scoring, and games-played context appropriate to each position.
- Validate calculations against recognizable player seasons and source totals.
- Document every metric's numerator, denominator, grain, and null-handling behavior.

#### 7. Weekly Waiver and Player Explorer features

- Build player-week features supporting current-week, rolling three-week, and season-to-date views.
- Compare recent opportunity with season-to-date baselines.
- Prevent future-week leakage in every rolling calculation.
- Prototype transparent, rule-based signals only after their component metrics validate.
- Determine whether Player Explorer needs a separate Gold table or can consume shared views directly.

#### 8. Cross-layer validation and starter publication

- Reconcile representative Gold metrics back through Silver to Bronze sources.
- Test missing weeks, byes, partial participation, team changes, and small samples.
- Record known limitations and metric definitions alongside the notebooks.
- Produce reliable starter Parquet datasets for the Streamlit prototype.

### Expected datasets and components

- Source-oriented Bronze Parquet datasets required for initial metrics
- Shared player, participation, and team-opportunity Silver datasets
- Validated WR, RB, and QB weekly facts
- Draft player-season Gold features
- Waiver rolling-trend Gold features
- Reusable Gold inputs for Player Explorer
- Notebook-level data-quality checks and metric documentation

### Deliverable

Reliable starter Bronze, Silver, and Gold Parquet datasets that the application can consume.

### Exit criteria

- Each published dataset has an explicit, tested grain.
- Source-to-Bronze ingestion can be rerun for the selected scope.
- Core cross-source player identity and team/week relationships are understood.
- Opportunity denominators and position-specific classifications are documented.
- WR, RB, and QB metrics reconcile to representative source data and real-player checks.
- Rolling features demonstrably avoid future-data leakage.
- Known limitations and edge cases are documented.
- The starter Gold datasets are stable enough to test through Streamlit.

## Phase 2 — Streamlit Application Prototype

### Objective

Build the first usable local application and validate whether the Phase 1 Gold datasets support real fantasy-football decisions.

### Dependencies

- Phase 1 starter Gold datasets meet their exit criteria.
- Initial scoring and supported-season decisions are documented.

### Major tasks

- Create a simple multi-page Streamlit application.
- Implement Draft Analysis filters, sorting, comparisons, and historical profiles.
- Implement Waiver Wire current/recent/season comparisons and transparent signals.
- Implement Player Explorer historical and weekly trend views.
- Keep substantial transformations out of the UI layer.
- Use application feedback to revise Gold schemas and metric definitions where needed.

### Expected datasets and components

- Draft, Waiver, and Player Explorer pages
- Gold dataset loading and lightweight presentation adapters
- Tables, filters, comparisons, and interpretable charts
- Clear display of scoring assumptions, data freshness, and metric definitions

### Deliverable

A working local Streamlit application demonstrating that the Gold datasets support useful fantasy-football decisions.

### Exit criteria

- All three application areas run locally against generated Gold data.
- Users can answer each area's primary question without notebook access.
- Major feature engineering remains outside Streamlit.
- Metrics and rule-based signals are explainable from the UI or linked definitions.
- Application testing has identified and resolved material Gold-model usability gaps.

## Phase 3 — Promote Notebook Logic to `src/`

### Objective

Move stable, repeated, and validated transformations into reusable, testable Python modules while retaining notebooks for research and validation.

### Dependencies

- Phase 2 confirms which datasets and features are useful.
- Transformation behavior and edge cases are sufficiently stable to encode as contracts.

### Major tasks

- Define package boundaries for Bronze, Silver, and Gold transformations.
- Extract stable logic from notebooks without duplicating implementations.
- Update notebooks to import production functions where appropriate.
- Add focused tests for grains, shares, participation, denominators, trades, kneel-down handling, and time-safe rolling windows.
- Define configuration and I/O boundaries without embedding orchestration in transformation modules.

### Expected datasets and components

- `src/bronze/` source-loading and normalization modules
- `src/silver/` shared football-fact transformations
- `src/gold/` position features and weekly-trend transformations
- `tests/` covering high-risk assumptions and transformation behavior

### Deliverable

Reusable, tested Python transformation modules representing stable Bronze → Silver → Gold logic.

### Exit criteria

- Stable transformations have one authoritative implementation in `src/`.
- Relevant notebooks call the production functions or clearly remain exploratory.
- Automated tests cover material grains, joins, denominators, edge cases, and leakage risks.
- Module APIs are clear enough for thin pipeline entry points.
- The application still receives equivalent, validated Gold outputs.

## Phase 4 — Pipeline Scripts

### Objective

Wrap the reusable modules in simple executable entry points for repeatable manual refreshes.

### Dependencies

- Phase 3 modules and tests are stable.
- Dataset inputs, outputs, ordering, and failure conditions are defined.

### Major tasks

- Add entry points for Bronze refresh, Silver build, Gold build, and full refresh.
- Keep orchestration in pipelines and business logic in `src/`.
- Support season/week configuration where appropriate.
- Make reruns idempotent where practical.
- Add clear logging, validation gates, and actionable failures.
- Document the manual operational workflow.

### Expected datasets and components

- `pipelines/refresh_bronze.py`
- `pipelines/build_silver.py`
- `pipelines/build_gold.py`
- `pipelines/refresh_all.py`
- Runtime configuration and pipeline-level validation

### Deliverable

A one-command/manual refresh of Bronze → Silver → Gold datasets for the Streamlit application.

### Exit criteria

- A developer can rebuild the supported scope through documented commands.
- Pipeline order and dependencies are explicit.
- Repeated runs do not create duplicate logical records.
- Invalid or incomplete data stops publication with a clear error.
- Logs identify the scope, progress, outputs, and failure point.
- Streamlit can consume the refreshed Gold outputs without manual notebook steps.

## Phase 5 — Airflow Automation

### Objective

Automate the already-working pipeline without moving transformation logic into Airflow.

### Dependencies

- Phase 4 runs reliably through its manual entry points.
- Scheduling, hosting, storage, credentials, and operational ownership requirements are known.

### Major tasks

- Define DAG tasks around the Phase 4 pipeline boundaries.
- Schedule appropriate in-season refreshes.
- Add retries, alerts, observability, and data-quality gates.
- Confirm atomic or otherwise safe publication of updated Gold data to Streamlit.
- Document backfill, recovery, and local testing procedures.

### Expected datasets and components

- Airflow DAG configuration
- Bronze → Silver → Gold task dependencies
- Data-quality and publication steps
- Scheduling, monitoring, alerting, and recovery documentation

### Deliverable

An automated, scheduled NFL Dream Lab data-refresh pipeline.

### Exit criteria

- Airflow invokes the existing pipeline or module interfaces without duplicating transformations.
- Scheduled runs publish validated data on the intended cadence.
- Failures are visible and recoverable without corrupting published outputs.
- Backfills and retries preserve the expected dataset grains.
- Streamlit receives refreshed Gold data through the chosen deployment/storage design.

## Future-State Repository Direction

This tree is illustrative. Paths should be created only when their phase begins and a real artifact needs them.

```text
nfl-dream-lab-app/
├── data/
│   ├── bronze/
│   ├── silver/
│   └── gold/
├── notebooks/
│   ├── bronze/
│   ├── silver/
│   └── gold/
├── src/
│   ├── bronze/
│   ├── silver/
│   └── gold/
├── pipelines/
│   ├── refresh_bronze.py
│   ├── build_silver.py
│   ├── build_gold.py
│   └── refresh_all.py
├── tests/
├── streamlit/
│   ├── app.py
│   └── pages/
├── airflow/
├── ROADMAP.md
└── README.md
```

The exact Streamlit application directory and Python package layout should be confirmed when those phases begin so they follow the selected tooling and packaging conventions.

## Cross-Cutting Rules

1. Prototype before productionizing.
2. Preserve source truth in Bronze.
3. Build trusted football facts in Silver.
4. Build fantasy decision features in Gold.
5. Share Bronze and Silver across application use cases.
6. Allow Gold to diverge by decision context.
7. Keep substantial feature engineering out of Streamlit.
8. Treat notebooks as research and validation artifacts, not the final production implementation.
9. Promote stable, repeated notebook logic to `src/`.
10. Keep orchestration in pipelines and transformations in `src/`.
11. Keep transformation logic out of Airflow DAGs.
12. Prefer transparent metrics before composite scores or machine learning.
13. Validate metrics against real NFL players and source totals.
14. Declare and test every dataset's grain.
15. Prevent future-data leakage in weekly and rolling features.
16. Build only the infrastructure required by the current phase.

## Open Questions During Phase 1

- Which non-reception scoring rules should complement the full-PPR default, including passing-touchdown, interception, yardage, turnover, conversion, and bonus values?
- Which source-specific licensing, attribution, freshness, and availability constraints must be reflected in storage or distribution?
- What is the canonical definition of a fantasy week for late corrections, rescheduled games, and multi-team player records?
- Which minimum participation and sample-size rules should govern rankings, percentiles, and trend signals?

These questions should be resolved when they first affect a notebook or dataset contract; they do not justify building infrastructure early.

## Progress Tracking

Update this roadmap when a phase starts, its scope materially changes, or its exit criteria are met. Keep detailed experimental results in the relevant notebook or metric documentation rather than turning this file into a sprint log or changelog.
