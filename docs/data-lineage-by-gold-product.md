# NFL Dream Lab Data Lineage

Last updated: 2026-10-04

## Purpose

This is the canonical working data lineage for NFL Dream Lab. It presents the pipeline as four focused views, repeating relevant upstream layers so each Gold product can be followed without tracing a large web of crossing lines.

For a quick view of column counts entering and leaving each implemented step, see the companion [schema flow](schema-evolution.md).

The diagrams show the current 2023–2025 direction. Green nodes are implemented and persisted, gray dashed nodes are planned, and purple dashed nodes are optional. The notebooks import `nflreadpy as nfl`, so the source calls below use that exact alias. Implemented nodes list the current Parquet filenames; planned nodes explicitly say when a physical filename has not been established.

## 1. Shared data foundation

This graph shows the common source, Bronze, and Silver foundation reused by every Gold product. Gold-specific transformations are intentionally omitted.

```mermaid
flowchart TB
    SOURCE["nflverse source datasets"]

    B_FILES["Exact nflreadpy calls → Bronze files<br/><br/>nfl.load_players()<br/>→ data/bronze/players/players.parquet<br/><br/>nfl.load_schedules(seasons=[season])<br/>→ data/bronze/schedules/schedules_2023.parquet<br/>→ data/bronze/schedules/schedules_2024.parquet<br/>→ data/bronze/schedules/schedules_2025.parquet<br/><br/>nfl.load_player_stats(seasons=[season], summary_level='week')<br/>→ data/bronze/player_stats_weekly/player_stats_weekly_2023.parquet<br/>→ data/bronze/player_stats_weekly/player_stats_weekly_2024.parquet<br/>→ data/bronze/player_stats_weekly/player_stats_weekly_2025.parquet<br/><br/>nfl.load_rosters_weekly(seasons=[season])<br/>→ data/bronze/rosters_weekly/rosters_weekly_2023.parquet<br/>→ data/bronze/rosters_weekly/rosters_weekly_2024.parquet<br/>→ data/bronze/rosters_weekly/rosters_weekly_2025.parquet<br/><br/>nfl.load_snap_counts(seasons=[season])<br/>→ data/bronze/snap_counts/snap_counts_2023.parquet<br/>→ data/bronze/snap_counts/snap_counts_2024.parquet<br/>→ data/bronze/snap_counts/snap_counts_2025.parquet<br/><br/>nfl.load_pbp(seasons=[season])<br/>→ data/bronze/pbp/pbp_2023.parquet<br/>→ data/bronze/pbp/pbp_2024.parquet<br/>→ data/bronze/pbp/pbp_2025.parquet"]

    CONTRACTS["Validated Silver contracts<br/>GSIS identity · PFR bridge · participation<br/>weekly grain · contextual positions"]

    subgraph CurrentSilver["Shared Silver — implemented"]
        S_GAME["data/silver/player_game_participation/player_game_participation_2023.parquet<br/>data/silver/player_game_participation/player_game_participation_2024.parquet<br/>data/silver/player_game_participation/player_game_participation_2025.parquet<br/>grain: player_id + game_id"]
        S_WEEK["data/silver/player_week/player_week_2023.parquet<br/>data/silver/player_week/player_week_2024.parquet<br/>data/silver/player_week/player_week_2025.parquet<br/>grain: player_id + season + week + team"]
    end

    subgraph PositionSilver["Position Silver"]
        S_WR["data/silver/wr_week/wr_week_2023.parquet<br/>data/silver/wr_week/wr_week_2024.parquet<br/>data/silver/wr_week/wr_week_2025.parquet<br/>grain: player_id + season + week + team"]
        S_RB["data/silver/rb_week/rb_week_2023.parquet<br/>data/silver/rb_week/rb_week_2024.parquet<br/>data/silver/rb_week/rb_week_2025.parquet<br/>grain: player_id + season + week + team"]
        S_QB["data/silver/qb_week/qb_week_2023.parquet<br/>data/silver/qb_week/qb_week_2024.parquet<br/>data/silver/qb_week/qb_week_2025.parquet<br/>grain: player_id + season + week + team"]
    end

    subgraph NewSilver["Shared Silver — implemented play and opportunity facts"]
        S_PLAYS["data/silver/standardized_plays/standardized_plays_2023.parquet<br/>data/silver/standardized_plays/standardized_plays_2024.parquet<br/>data/silver/standardized_plays/standardized_plays_2025.parquet<br/>grain: game_id + play_id"]
        S_TEAM["data/silver/team_week_opportunity/team_week_opportunity_2023.parquet<br/>data/silver/team_week_opportunity/team_week_opportunity_2024.parquet<br/>data/silver/team_week_opportunity/team_week_opportunity_2025.parquet<br/>grain: team + season + week"]
    end

    SOURCE --> B_FILES --> CONTRACTS
    CONTRACTS --> S_GAME
    CONTRACTS --> S_WEEK
    B_FILES --> S_PLAYS
    S_PLAYS --> S_TEAM
    S_WEEK --> S_WR
    S_PLAYS --> S_WR
    S_TEAM --> S_WR
    B_FILES -->|team passing air yards| S_WR
    S_WEEK --> S_RB
    S_PLAYS --> S_RB
    S_TEAM --> S_RB
    S_WEEK --> S_QB
    S_PLAYS --> S_QB
    S_TEAM --> S_QB

    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a;
    classDef built fill:#d1fae5,stroke:#047857,color:#064e3b;
    classDef validation fill:#fef3c7,stroke:#b45309,color:#78350f;
    classDef planned fill:#f3f4f6,stroke:#6b7280,color:#374151,stroke-dasharray:5 5;

    class SOURCE source;
    class B_FILES,S_GAME,S_WEEK,S_PLAYS,S_TEAM,S_WR,S_RB,S_QB built;
    class CONTRACTS validation;
```

## 2. Draft Analysis Gold lineage

Draft Analysis answers what a player has historically demonstrated. Weekly football facts will be aggregated into position-specific player-season profiles for comparison, filtering, and percentile analysis.

```mermaid
flowchart TB
    SOURCE["nflverse source datasets"]
    B_FILES["Exact nflreadpy calls → Bronze files<br/><br/>nfl.load_players()<br/>→ data/bronze/players/players.parquet<br/><br/>nfl.load_schedules(seasons=[season])<br/>→ data/bronze/schedules/schedules_2023.parquet<br/>→ data/bronze/schedules/schedules_2024.parquet<br/>→ data/bronze/schedules/schedules_2025.parquet<br/><br/>nfl.load_player_stats(seasons=[season], summary_level='week')<br/>→ data/bronze/player_stats_weekly/player_stats_weekly_2023.parquet<br/>→ data/bronze/player_stats_weekly/player_stats_weekly_2024.parquet<br/>→ data/bronze/player_stats_weekly/player_stats_weekly_2025.parquet<br/><br/>nfl.load_rosters_weekly(seasons=[season])<br/>→ data/bronze/rosters_weekly/rosters_weekly_2023.parquet<br/>→ data/bronze/rosters_weekly/rosters_weekly_2024.parquet<br/>→ data/bronze/rosters_weekly/rosters_weekly_2025.parquet<br/><br/>nfl.load_snap_counts(seasons=[season])<br/>→ data/bronze/snap_counts/snap_counts_2023.parquet<br/>→ data/bronze/snap_counts/snap_counts_2024.parquet<br/>→ data/bronze/snap_counts/snap_counts_2025.parquet<br/><br/>nfl.load_pbp(seasons=[season])<br/>→ data/bronze/pbp/pbp_2023.parquet<br/>→ data/bronze/pbp/pbp_2024.parquet<br/>→ data/bronze/pbp/pbp_2025.parquet"]

    subgraph Silver["Relevant Silver foundation"]
        S_SHARED["Implemented shared facts<br/><br/>data/silver/player_game_participation/player_game_participation_2023.parquet<br/>data/silver/player_game_participation/player_game_participation_2024.parquet<br/>data/silver/player_game_participation/player_game_participation_2025.parquet<br/><br/>data/silver/player_week/player_week_2023.parquet<br/>data/silver/player_week/player_week_2024.parquet<br/>data/silver/player_week/player_week_2025.parquet"]
        S_OPPORTUNITY["Implemented play and team opportunity facts<br/><br/>data/silver/standardized_plays/standardized_plays_2023.parquet<br/>data/silver/standardized_plays/standardized_plays_2024.parquet<br/>data/silver/standardized_plays/standardized_plays_2025.parquet<br/><br/>data/silver/team_week_opportunity/team_week_opportunity_2023.parquet<br/>data/silver/team_week_opportunity/team_week_opportunity_2024.parquet<br/>data/silver/team_week_opportunity/team_week_opportunity_2025.parquet"]
        S_WR["Implemented WR weekly facts<br/>data/silver/wr_week/wr_week_2023.parquet<br/>data/silver/wr_week/wr_week_2024.parquet<br/>data/silver/wr_week/wr_week_2025.parquet<br/>grain: player_id + season + week + team"]
        S_RB["Implemented RB weekly facts<br/>data/silver/rb_week/rb_week_2023.parquet<br/>data/silver/rb_week/rb_week_2024.parquet<br/>data/silver/rb_week/rb_week_2025.parquet<br/>grain: player_id + season + week + team"]
        S_QB["Implemented QB weekly facts<br/>data/silver/qb_week/qb_week_2023.parquet<br/>data/silver/qb_week/qb_week_2024.parquet<br/>data/silver/qb_week/qb_week_2025.parquet<br/>grain: player_id + season + week + team"]
    end

    subgraph DraftGold["Draft Analysis Gold — player-season features"]
        G_WR["Implemented WR season features<br/>data/gold/draft/wr_season_features/wr_season_features_2023.parquet<br/>data/gold/draft/wr_season_features/wr_season_features_2024.parquet<br/>data/gold/draft/wr_season_features/wr_season_features_2025.parquet<br/>grain: player_id + season"]
        G_RB["Implemented RB/FB season features<br/>data/gold/draft/rb_season_features/rb_season_features_2023.parquet<br/>data/gold/draft/rb_season_features/rb_season_features_2024.parquet<br/>data/gold/draft/rb_season_features/rb_season_features_2025.parquet<br/>grain: player_id + season"]
        G_QB["Implemented QB season features<br/>data/gold/draft/qb_season_features/qb_season_features_2023.parquet<br/>data/gold/draft/qb_season_features/qb_season_features_2024.parquet<br/>data/gold/draft/qb_season_features/qb_season_features_2025.parquet<br/>grain: player_id + season"]
    end

    DRAFT["Draft Analysis<br/>historical profiles and comparisons"]

    SOURCE --> B_FILES --> S_SHARED
    B_FILES --> S_OPPORTUNITY
    S_SHARED --> S_WR
    S_OPPORTUNITY --> S_WR
    B_FILES -->|team passing air yards| S_WR
    S_SHARED --> S_RB
    S_OPPORTUNITY --> S_RB
    S_SHARED --> S_QB
    S_OPPORTUNITY --> S_QB
    S_WR --> G_WR
    S_RB --> G_RB
    S_QB --> G_QB
    G_WR -.-> DRAFT
    G_RB -.-> DRAFT
    G_QB -.-> DRAFT

    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a;
    classDef built fill:#d1fae5,stroke:#047857,color:#064e3b;
    classDef planned fill:#f3f4f6,stroke:#6b7280,color:#374151,stroke-dasharray:5 5;

    class SOURCE source;
    class B_FILES,S_SHARED,S_OPPORTUNITY,S_WR,S_RB,S_QB,G_WR,G_RB,G_QB built;
    class DRAFT planned;
```

The implemented WR, RB/FB, and QB datasets contain validated regular-season volume, opportunity share, production, efficiency, full-PPR scoring, participation, team-change context, and eligible-player percentiles. WR Gold retains same-games team pass-attempt context; RB Gold separates official and canonical opportunities and all-team versus backfield shares; QB Gold keeps official production separate from canonical complete dropbacks and meaningful rushing.

## 3. Waiver Wire Gold lineage

Waiver Wire answers whose role or opportunity is changing now. The current-week position foundations are implemented; rolling comparisons and signals remain planned so they can be reviewed separately for leakage and minimum-history behavior.

```mermaid
flowchart TB
    S_WR["Implemented WR Silver<br/>wr_week_{season}.parquet<br/>62 columns<br/>grain: player_id + season + week + team"]
    S_RB["Implemented RB/FB Silver<br/>rb_week_{season}.parquet<br/>68 columns<br/>grain: player_id + season + week + team"]
    S_QB["Implemented QB Silver<br/>qb_week_{season}.parquet<br/>71 columns<br/>grain: player_id + season + week + team"]

    X_WR["Build WR current-week Waiver features<br/>04_wr_waiver_weekly_trends.ipynb"]
    X_RB["Build RB/FB current-week Waiver features<br/>05_rb_waiver_weekly_trends.ipynb"]
    X_QB["Build QB current-week Waiver features<br/>06_qb_waiver_weekly_trends.ipynb"]

    G_WR["Implemented WR Waiver foundation<br/>data/gold/waiver/wr_weekly_trends/<br/>wr_weekly_trends_{season}.parquet<br/>80 columns · 8,475 rows<br/>grain: player_id + season + week"]
    G_RB["Implemented RB/FB Waiver foundation<br/>data/gold/waiver/rb_weekly_trends/<br/>rb_weekly_trends_{season}.parquet<br/>99 columns · 5,542 rows<br/>grain: player_id + season + week"]
    G_QB["Implemented QB Waiver foundation<br/>data/gold/waiver/qb_weekly_trends/<br/>qb_weekly_trends_{season}.parquet<br/>102 columns · 2,071 rows<br/>grain: player_id + season + week"]

    ROLLING["Planned time-safe extension<br/>prior 3 calendar weeks · season to date<br/>history counts · comparisons · transparent signals"]
    WAIVER["Planned Waiver Wire application<br/>role changes and transparent signals"]

    S_WR --> X_WR --> G_WR
    S_RB --> X_RB --> G_RB
    S_QB --> X_QB --> G_QB
    G_WR -.-> ROLLING
    G_RB -.-> ROLLING
    G_QB -.-> ROLLING
    ROLLING -.-> WAIVER

    classDef built fill:#d1fae5,stroke:#047857,color:#064e3b;
    classDef step fill:#fef3c7,stroke:#b45309,color:#78350f;
    classDef planned fill:#f3f4f6,stroke:#6b7280,color:#374151,stroke-dasharray:5 5;

    class S_WR,S_RB,S_QB,G_WR,G_RB,G_QB built;
    class X_WR,X_RB,X_QB step;
    class ROLLING,WAIVER planned;
```

The current Gold notebooks select only their position Silver facts, filter to regular-season rows, aggregate from player-team-week to player-week, recompute ratios from components, apply full-PPR scoring, and write season partitions. No current data needs same-week multi-team consolidation, but ordered game, team, and opponent fields preserve that future case without arbitrarily choosing a singular team.

The planned rolling extension will use the prior three NFL calendar weeks, retain every current-week row, expose contributing-history counts, and leave comparisons or signals null until sufficient history exists. It must use only current and earlier weeks at each row. Initial signals should remain transparent—for example, rising usage or high opportunity with low production—rather than becoming an unexplained composite score. See `docs/waiver-metric-contracts.md` for the detailed contract.

## 4. Player Explorer Gold lineage

Player Explorer combines the long-term Draft view with the recent Waiver view. Its preferred design is to reuse those Gold products rather than rebuild the same features in a third pipeline.

```mermaid
flowchart TB
    SOURCE["nflverse source datasets"]
    B_FILES["Exact nflreadpy calls → Bronze files<br/><br/>nfl.load_players()<br/>→ data/bronze/players/players.parquet<br/><br/>nfl.load_schedules(seasons=[season])<br/>→ data/bronze/schedules/schedules_2023.parquet<br/>→ data/bronze/schedules/schedules_2024.parquet<br/>→ data/bronze/schedules/schedules_2025.parquet<br/><br/>nfl.load_player_stats(seasons=[season], summary_level='week')<br/>→ data/bronze/player_stats_weekly/player_stats_weekly_2023.parquet<br/>→ data/bronze/player_stats_weekly/player_stats_weekly_2024.parquet<br/>→ data/bronze/player_stats_weekly/player_stats_weekly_2025.parquet<br/><br/>nfl.load_rosters_weekly(seasons=[season])<br/>→ data/bronze/rosters_weekly/rosters_weekly_2023.parquet<br/>→ data/bronze/rosters_weekly/rosters_weekly_2024.parquet<br/>→ data/bronze/rosters_weekly/rosters_weekly_2025.parquet<br/><br/>nfl.load_snap_counts(seasons=[season])<br/>→ data/bronze/snap_counts/snap_counts_2023.parquet<br/>→ data/bronze/snap_counts/snap_counts_2024.parquet<br/>→ data/bronze/snap_counts/snap_counts_2025.parquet<br/><br/>nfl.load_pbp(seasons=[season])<br/>→ data/bronze/pbp/pbp_2023.parquet<br/>→ data/bronze/pbp/pbp_2024.parquet<br/>→ data/bronze/pbp/pbp_2025.parquet"]
    S_CURRENT["Implemented shared Silver<br/><br/>data/silver/player_game_participation/player_game_participation_2023.parquet<br/>data/silver/player_game_participation/player_game_participation_2024.parquet<br/>data/silver/player_game_participation/player_game_participation_2025.parquet<br/><br/>data/silver/player_week/player_week_2023.parquet<br/>data/silver/player_week/player_week_2024.parquet<br/>data/silver/player_week/player_week_2025.parquet"]
    S_OPPORTUNITY["Implemented opportunity Silver<br/><br/>data/silver/standardized_plays/standardized_plays_2023.parquet<br/>data/silver/standardized_plays/standardized_plays_2024.parquet<br/>data/silver/standardized_plays/standardized_plays_2025.parquet<br/><br/>data/silver/team_week_opportunity/team_week_opportunity_2023.parquet<br/>data/silver/team_week_opportunity/team_week_opportunity_2024.parquet<br/>data/silver/team_week_opportunity/team_week_opportunity_2025.parquet"]
    S_WR["Implemented WR weekly facts<br/>data/silver/wr_week/wr_week_2023.parquet<br/>data/silver/wr_week/wr_week_2024.parquet<br/>data/silver/wr_week/wr_week_2025.parquet"]
    S_RB["Implemented RB weekly facts<br/>data/silver/rb_week/rb_week_2023.parquet<br/>data/silver/rb_week/rb_week_2024.parquet<br/>data/silver/rb_week/rb_week_2025.parquet"]
    S_QB["Implemented QB weekly facts<br/>data/silver/qb_week/qb_week_2023.parquet<br/>data/silver/qb_week/qb_week_2024.parquet<br/>data/silver/qb_week/qb_week_2025.parquet"]

    subgraph ExistingGoldShapes["Reusable Gold products"]
        G_WR_GOLD["Implemented WR Draft seasons<br/>data/gold/draft/wr_season_features/wr_season_features_2023.parquet<br/>data/gold/draft/wr_season_features/wr_season_features_2024.parquet<br/>data/gold/draft/wr_season_features/wr_season_features_2025.parquet<br/>grain: player_id + season"]
        G_RB_GOLD["Implemented RB/FB Draft seasons<br/>data/gold/draft/rb_season_features/rb_season_features_2023.parquet<br/>data/gold/draft/rb_season_features/rb_season_features_2024.parquet<br/>data/gold/draft/rb_season_features/rb_season_features_2025.parquet<br/>grain: player_id + season"]
        G_QB_GOLD["Implemented QB Draft seasons<br/>data/gold/draft/qb_season_features/qb_season_features_2023.parquet<br/>data/gold/draft/qb_season_features/qb_season_features_2024.parquet<br/>data/gold/draft/qb_season_features/qb_season_features_2025.parquet<br/>grain: player_id + season"]
        G_WAIVER["Implemented current-week Waiver Gold<br/>data/gold/waiver/wr_weekly_trends/wr_weekly_trends_{season}.parquet<br/>data/gold/waiver/rb_weekly_trends/rb_weekly_trends_{season}.parquet<br/>data/gold/waiver/qb_weekly_trends/qb_weekly_trends_{season}.parquet<br/>grain: player_id + season + week<br/>rolling extension planned"]
    end

    G_HISTORY["Optional gold/player/player_history<br/>grain: player_id + season + week<br/>physical filename not established"]
    EXPLORER["Player Explorer<br/>historical profile + recent weekly story"]

    SOURCE --> B_FILES --> S_CURRENT
    B_FILES --> S_OPPORTUNITY
    S_CURRENT --> G_WAIVER
    S_OPPORTUNITY --> G_WAIVER
    S_CURRENT --> S_WR
    S_OPPORTUNITY --> S_WR
    B_FILES -->|team passing air yards| S_WR
    S_CURRENT --> S_RB
    S_OPPORTUNITY --> S_RB
    S_CURRENT --> S_QB
    S_OPPORTUNITY --> S_QB
    S_WR --> G_WR_GOLD
    S_WR --> G_WAIVER
    S_RB --> G_RB_GOLD
    S_RB --> G_WAIVER
    S_QB --> G_QB_GOLD
    S_QB --> G_WAIVER
    G_WR_GOLD -.-> EXPLORER
    G_RB_GOLD -.-> EXPLORER
    G_QB_GOLD -.-> EXPLORER
    G_WAIVER -.-> EXPLORER
    G_WR_GOLD -.-> G_HISTORY
    G_RB_GOLD -.-> G_HISTORY
    G_QB_GOLD -.-> G_HISTORY
    G_WAIVER -.-> G_HISTORY
    G_HISTORY -.-> EXPLORER

    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a;
    classDef built fill:#d1fae5,stroke:#047857,color:#064e3b;
    classDef planned fill:#f3f4f6,stroke:#6b7280,color:#374151,stroke-dasharray:5 5;
    classDef optional fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,stroke-dasharray:5 5;

    class SOURCE source;
    class B_FILES,S_CURRENT,S_OPPORTUNITY,S_WR,S_RB,S_QB,G_WR_GOLD,G_RB_GOLD,G_QB_GOLD,G_WAIVER built;
    class EXPLORER planned;
    class G_HISTORY optional;
```

`gold/player/player_history` should be created only if it offers a useful access shape that cannot be served cleanly from the Draft and Waiver Gold datasets. The diagram therefore shows both direct reuse and the optional materialized history path.

## How to maintain these focused views

When a planned dataset is implemented, update the relevant graph without expanding unrelated graphs:

1. Change the node from planned to implemented styling.
2. Replace dashed provisional edges with solid validated edges.
3. Use the final persisted dataset name and grain.
4. Keep detailed field definitions and validation evidence in the producing notebook or metric documentation.
5. Keep all four views consistent when a shared upstream dependency changes.
