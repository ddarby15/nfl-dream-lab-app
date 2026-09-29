# NFL Dream Lab Schema Flow

Last updated: 2026-09-28

## How to read the diagrams

- Dataset nodes show the total number of columns available in the persisted dataset.
- Solid-arrow labels show how many columns the next step selects from that dataset.
- Dotted arrows are validation-only inputs and do not create the output schema.
- Selected input counts do not need to add up to the output count. Joins share keys, some inputs are omitted after use, and transformations add derived columns.
- Counts in the change-summary tables describe that specific type of change and can overlap. A column can, for example, be both renamed and type-standardized.

## 1. nflreadpy source to Bronze

Bronze preserves the schema returned by `nflreadpy`, so the source and Bronze column counts are equal.

```mermaid
flowchart LR
    S_PLAYERS["nfl.load_players()<br/><b>39 columns</b>"]
    X_PLAYERS["Persist players<br/>02_bronze_core_sources.ipynb"]
    B_PLAYERS["Bronze players<br/><b>39 columns</b><br/>players/players.parquet"]

    S_SCHEDULES["nfl.load_schedules()<br/><b>46 columns</b>"]
    X_SCHEDULES["Persist schedules<br/>02_bronze_core_sources.ipynb"]
    B_SCHEDULES["Bronze schedules<br/><b>46 columns</b><br/>schedules/schedules_{season}.parquet"]

    S_STATS["nfl.load_player_stats(summary_level='week')<br/><b>150 columns</b>"]
    X_STATS["Persist weekly stats<br/>02_bronze_core_sources.ipynb"]
    B_STATS["Bronze player_stats_weekly<br/><b>150 columns</b><br/>player_stats_weekly/player_stats_weekly_{season}.parquet"]

    S_ROSTERS["nfl.load_rosters_weekly()<br/><b>36 columns</b>"]
    X_ROSTERS["Persist weekly rosters<br/>02_bronze_core_sources.ipynb"]
    B_ROSTERS["Bronze rosters_weekly<br/><b>36 columns</b><br/>rosters_weekly/rosters_weekly_{season}.parquet"]

    S_SNAPS["nfl.load_snap_counts()<br/><b>16 columns</b>"]
    X_SNAPS["Persist snap counts<br/>02_bronze_core_sources.ipynb"]
    B_SNAPS["Bronze snap_counts<br/><b>16 columns</b><br/>snap_counts/snap_counts_{season}.parquet"]

    S_PBP["nfl.load_pbp()<br/><b>372 columns</b>"]
    X_PBP["Persist play-by-play<br/>03_bronze_play_by_play.ipynb"]
    B_PBP["Bronze pbp<br/><b>372 columns</b><br/>pbp/pbp_{season}.parquet"]

    S_PLAYERS -->|39 columns| X_PLAYERS -->|39 columns| B_PLAYERS
    S_SCHEDULES -->|46 columns| X_SCHEDULES -->|46 columns| B_SCHEDULES
    S_STATS -->|150 columns| X_STATS -->|150 columns| B_STATS
    S_ROSTERS -->|36 columns| X_ROSTERS -->|36 columns| B_ROSTERS
    S_SNAPS -->|16 columns| X_SNAPS -->|16 columns| B_SNAPS
    S_PBP -->|372 columns| X_PBP -->|372 columns| B_PBP

    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a;
    classDef step fill:#fef3c7,stroke:#b45309,color:#78350f;
    classDef bronze fill:#fed7aa,stroke:#c2410c,color:#7c2d12;

    class S_PLAYERS,S_SCHEDULES,S_STATS,S_ROSTERS,S_SNAPS,S_PBP source;
    class X_PLAYERS,X_SCHEDULES,X_STATS,X_ROSTERS,X_SNAPS,X_PBP step;
    class B_PLAYERS,B_SCHEDULES,B_STATS,B_ROSTERS,B_SNAPS,B_PBP bronze;
```

### Output Data Details

| Step | Joins and shared keys | Renamed or standardized | Derived or transformed | Not carried forward |
|---|---|---|---|---|
| `nflreadpy → Bronze` | No joins. | **0 intentional column renames.** | **0 feature-engineered columns.** DataFrames are converted from Polars to pandas and written to Parquet. | **0 columns intentionally removed.** Source column counts are preserved in Bronze. |

## 2. Bronze to player participation and weekly Silver

```mermaid
flowchart LR
    B_PLAYERS["Bronze players<br/><b>39 columns available</b>"]
    B_SCHEDULES["Bronze schedules<br/><b>46 columns available</b>"]
    B_STATS["Bronze player_stats_weekly<br/><b>150 columns available</b>"]
    B_ROSTERS["Bronze rosters_weekly<br/><b>36 columns available</b>"]
    B_SNAPS["Bronze snap_counts<br/><b>16 columns available</b>"]

    X_PLAYER["Build player identity, participation,<br/>and weekly football facts<br/><b>02_shared_player_participation_and_week.ipynb</b>"]

    S_GAME["Silver player_game_participation<br/><b>30 output columns</b><br/>player_game_participation_{season}.parquet"]
    S_WEEK["Silver player_week<br/><b>54 output columns</b><br/>player_week_{season}.parquet"]

    B_PLAYERS -->|5 columns selected| X_PLAYER
    B_SCHEDULES -->|6 columns selected| X_PLAYER
    B_STATS -->|30 columns selected| X_PLAYER
    B_ROSTERS -->|8 columns selected| X_PLAYER
    B_SNAPS -->|11 columns selected| X_PLAYER
    X_PLAYER --> S_GAME
    X_PLAYER --> S_WEEK

    classDef bronze fill:#fed7aa,stroke:#c2410c,color:#7c2d12;
    classDef step fill:#fef3c7,stroke:#b45309,color:#78350f;
    classDef silver fill:#d1fae5,stroke:#047857,color:#064e3b;

    class B_PLAYERS,B_SCHEDULES,B_STATS,B_ROSTERS,B_SNAPS bronze;
    class X_PLAYER step;
    class S_GAME,S_WEEK silver;
```

### Output Data Details

| Output | Joins and shared keys | Renamed or standardized | Derived or transformed | Not carried forward |
|---|---|---|---|---|
| `player_game_participation` — 30 columns | Stats and snaps combine on `player_id + game_id + team`. Schedule, roster, and player-master enrichment use their respective shared keys. | **14 columns renamed or disambiguated** — includes `gsis_id → player_id`, source-specific position prefixes, `st_snaps → special_teams_snaps`, and snap-percentage renames. **6 snap fields type-standardized.** | **9 columns derived** — `season_type`, seven source or participation flags, and one consolidated `display_name`. | **24 selected stat columns excluded** from this participation-only output. Join helpers and source-specific fallback names are also removed. |
| `player_week` — 54 columns | Uses the same joined observations at `player_id + season + week + team`; `game_id` remains an attribute. | **24 columns renamed or disambiguated** — 14 contextual fields plus 10 weekly-stat names such as `attempts → passing_attempts` and `targets → receiving_targets`. **30 numeric fields type-standardized** across stats and snaps. | **9 columns derived** — the same context, source-presence, participation, WR, and display-name fields used by the participation output. | **227 Bronze columns not selected** across the five input datasets. Source fantasy points, precomputed shares, and join-only helper fields are omitted. |

## 3. Bronze to standardized plays and team-week opportunity

```mermaid
flowchart LR
    B_PBP["Bronze pbp<br/><b>372 columns available</b>"]
    B_SCHEDULES["Bronze schedules<br/><b>46 columns available</b>"]
    V_PLAYERS["Bronze players<br/><b>1 of 39 columns used</b>"]
    V_STATS["Bronze player_stats_weekly<br/><b>9 of 150 columns used</b>"]
    V_WEEK["Silver player_week<br/><b>5 of 54 columns used</b>"]

    X_PLAYS["Standardize play classifications<br/><b>03_standardized_plays_and_team_week_opportunity.ipynb</b>"]
    S_PLAYS["Silver standardized_plays<br/><b>56 output columns</b><br/>standardized_plays_{season}.parquet"]

    X_TEAM["Aggregate team-week opportunity<br/><b>03_standardized_plays_and_team_week_opportunity.ipynb</b>"]
    S_TEAM["Silver team_week_opportunity<br/><b>24 output columns</b><br/>team_week_opportunity_{season}.parquet"]

    B_PBP -->|33 columns selected| X_PLAYS
    B_SCHEDULES -->|6 columns selected| X_PLAYS
    V_PLAYERS -.->|validation only| X_PLAYS
    V_STATS -.->|validation only| X_PLAYS
    V_WEEK -.->|validation only| X_PLAYS
    X_PLAYS --> S_PLAYS

    S_PLAYS -->|19 of 56 columns selected| X_TEAM
    B_SCHEDULES -->|6 columns selected| X_TEAM
    X_TEAM --> S_TEAM

    classDef bronze fill:#fed7aa,stroke:#c2410c,color:#7c2d12;
    classDef validation fill:#f3f4f6,stroke:#6b7280,color:#374151,stroke-dasharray:5 5;
    classDef step fill:#fef3c7,stroke:#b45309,color:#78350f;
    classDef silver fill:#d1fae5,stroke:#047857,color:#064e3b;

    class B_PBP,B_SCHEDULES bronze;
    class V_PLAYERS,V_STATS,V_WEEK validation;
    class X_PLAYS,X_TEAM step;
    class S_PLAYS,S_TEAM silver;
```

### Output Data Details

| Output | Joins and shared keys | Renamed or standardized | Derived or transformed | Not carried forward |
|---|---|---|---|---|
| `standardized_plays` — 56 columns | PBP joins to schedules on `game_id`; the `game_id + play_id` grain remains unchanged. | **20 columns renamed or standardized** — four canonical context names, 15 Boolean `source_*` flags, and integer `play_id`. | **22 columns derived** — 21 canonical `is_*` classifications plus `target_air_yards`. | **379 source columns not selected** — 339 from PBP and 40 from schedules. All PBP rows remain despite the column reduction. |
| `team_week_opportunity` — 24 columns | Plays group on `game_id + team`, then join to schedule team-game rows. Final grain is `team + season + week`. | **16 aggregated fields renamed** with the `team_` prefix, such as `is_target → team_targets`. | **17 opportunity metrics aggregated** — 16 Boolean counts and one air-yard total. **16 count fields** are standardized to integer zero when missing. | **77 input columns not selected** — 37 from standardized plays and 40 from schedules. Play descriptions, player IDs, and individual-play details disappear during aggregation. |

## 4. Shared Silver to WR weekly facts

```mermaid
flowchart LR
    S_WEEK["Silver player_week<br/><b>54 columns available</b>"]
    S_PLAYS["Silver standardized_plays<br/><b>56 columns available</b>"]
    S_TEAM["Silver team_week_opportunity<br/><b>24 columns available</b>"]
    V_STATS["Bronze player_stats_weekly<br/><b>9 of 150 columns used</b>"]

    X_WR["Build WR weekly facts<br/><b>04_wr_weekly_facts.ipynb</b>"]
    S_WR["Silver wr_week<br/><b>59 output columns</b><br/>wr_week/wr_week_{season}.parquet"]

    S_WEEK -->|33 columns selected| X_WR
    S_PLAYS -->|14 columns selected| X_WR
    S_TEAM -->|12 columns selected| X_WR
    V_STATS -.->|validation only| X_WR
    X_WR --> S_WR

    classDef bronze fill:#fed7aa,stroke:#c2410c,color:#7c2d12;
    classDef validation fill:#f3f4f6,stroke:#6b7280,color:#374151,stroke-dasharray:5 5;
    classDef step fill:#fef3c7,stroke:#b45309,color:#78350f;
    classDef silver fill:#d1fae5,stroke:#047857,color:#064e3b;

    class S_WEEK,S_PLAYS,S_TEAM,S_WR silver;
    class V_STATS validation;
    class X_WR step;
```

### Output Data Details

| Output dataset | Joins and shared keys | Renamed or standardized | Derived or transformed | Columns not carried forward | Grain changes or aggregation |
|---|---|---|---|---|---|
| `wr_week` — **59 verified columns** | Receiver and rusher aggregates join to WR rows on `player_id + game_id + team`. Team denominators join on `team + season + week`, with `game_id` agreement required. Bronze weekly stats are validation-only. | **18 generated numeric columns standardized** — nine PBP counts use nullable integers, PBP target air yards and eight shares use nullable floats. **10 PBP fields are renamed as player opportunity aggregates.** | **18 columns derived** — ten player-game opportunity aggregates and eight same-week shares. | **75 schema-producing input columns not selected** — 21 from `player_week`, 42 from standardized plays, and 12 from team-week opportunity. The nine selected Bronze validation fields are not persisted. | The WR subset retains `player_id + season + week + team`; no aggregation changes the base output grain. PBP is aggregated from play to player-game-team before the one-to-one join. |

## 5. Shared Silver to RB weekly facts

```mermaid
flowchart LR
    S_WEEK["Silver player_week<br/><b>54 columns available</b>"]
    S_PLAYS["Silver standardized_plays<br/><b>56 columns available</b>"]
    S_TEAM["Silver team_week_opportunity<br/><b>24 columns available</b>"]
    V_STATS["Bronze player_stats_weekly<br/><b>9 of 150 columns used</b>"]

    X_RB["Build RB weekly facts<br/><b>05_rb_weekly_facts.ipynb</b>"]
    S_RB["Silver rb_week<br/><b>62 output columns</b><br/>rb_week/rb_week_{season}.parquet"]

    S_WEEK -->|33 columns selected| X_RB
    S_PLAYS -->|18 columns selected| X_RB
    S_TEAM -->|14 columns selected| X_RB
    V_STATS -.->|validation only| X_RB
    X_RB --> S_RB

    classDef validation fill:#f3f4f6,stroke:#6b7280,color:#374151,stroke-dasharray:5 5;
    classDef step fill:#fef3c7,stroke:#b45309,color:#78350f;
    classDef silver fill:#d1fae5,stroke:#047857,color:#064e3b;

    class S_WEEK,S_PLAYS,S_TEAM,S_RB silver;
    class V_STATS validation;
    class X_RB step;
```

### Output Data Details

| Output dataset | Joins and shared keys | Renamed or standardized | Derived or transformed | Columns not carried forward | Grain changes or aggregation |
|---|---|---|---|---|---|
| `rb_week` — **62 verified columns** | Rusher and receiver aggregates join to contextual RB/FB rows on `player_id + game_id + team`. Team denominators join on `team + season + week`, with `game_id` agreement required. Bronze weekly stats are validation-only. | **19 generated numeric columns standardized** — nine PBP counts use nullable integers, PBP target air yards and nine shares use nullable floats. **10 PBP fields are renamed as player opportunity aggregates.** | **19 columns derived** — ten player-game opportunity aggregates and nine same-week shares. | **69 schema-producing input columns not selected** — 21 from `player_week`, 38 from standardized plays, and 10 from team-week opportunity. The nine selected Bronze validation fields are not persisted. | The RB/FB subset retains `player_id + season + week + team`; no aggregation changes the base output grain. PBP is aggregated from play to player-game-team before the one-to-one join. |

## 6. Shared Silver to QB weekly facts

```mermaid
flowchart LR
    S_WEEK["Silver player_week<br/><b>54 columns available</b>"]
    S_PLAYS["Silver standardized_plays<br/><b>56 columns available</b>"]
    S_TEAM["Silver team_week_opportunity<br/><b>24 columns available</b>"]

    X_QB["Build QB weekly facts<br/><b>06_qb_weekly_facts.ipynb</b>"]
    S_QB["Silver qb_week<br/><b>71 output columns</b><br/>qb_week/qb_week_{season}.parquet"]

    S_WEEK -->|41 columns selected| X_QB
    S_PLAYS -->|16 columns selected| X_QB
    S_TEAM -->|15 columns selected| X_QB
    X_QB --> S_QB

    classDef step fill:#fef3c7,stroke:#b45309,color:#78350f;
    classDef silver fill:#d1fae5,stroke:#047857,color:#064e3b;

    class S_WEEK,S_PLAYS,S_TEAM,S_QB silver;
    class X_QB step;
```

### Output Data Details

| Output dataset | Joins and shared keys | Renamed or standardized | Derived or transformed | Columns not carried forward | Grain changes or aggregation |
|---|---|---|---|---|---|
| `qb_week` — **71 verified columns** | Passer, rusher, and complete-dropback aggregates join to contextual QB rows on `player_id + game_id + team`. Team denominators join on `team + season + week`, with `game_id` agreement required. | **19 generated numeric columns standardized** — 12 PBP opportunity fields use nullable integers and seven shares use nullable floats. **12 PBP fields are named as QB passing, dropback, and rushing facts.** | **19 columns derived** — 12 player-game opportunity fields and seven same-week shares. Dropback identity combines passer IDs for attempts and sacks with rusher IDs for scrambles. | **62 schema-producing input columns not selected** — 13 from `player_week`, 40 from standardized plays, and nine from team-week opportunity. | The QB subset retains `player_id + season + week + team`; no aggregation changes the base output grain. PBP is aggregated from play to player-game-team before the one-to-one joins. |

Planned Gold datasets are intentionally omitted until their notebooks establish actual input selections and output column counts.
