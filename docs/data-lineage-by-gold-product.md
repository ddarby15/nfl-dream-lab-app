# NFL Dream Lab Data Lineage

Last updated: 2026-09-14

## Purpose

This is the canonical working data lineage for NFL Dream Lab. It presents the pipeline as four focused views, repeating relevant upstream layers so each Gold product can be followed without tracing a large web of crossing lines.

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

    subgraph PlannedSilver["Shared Silver — planned"]
        S_POSITION["WR, RB, and QB weekly facts<br/>physical filenames not established"]
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
    S_WEEK -.-> S_POSITION
    S_GAME -.-> S_POSITION
    S_PLAYS -.-> S_POSITION
    S_TEAM -.-> S_POSITION

    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a;
    classDef built fill:#d1fae5,stroke:#047857,color:#064e3b;
    classDef validation fill:#fef3c7,stroke:#b45309,color:#78350f;
    classDef planned fill:#f3f4f6,stroke:#6b7280,color:#374151,stroke-dasharray:5 5;

    class SOURCE source;
    class B_FILES,S_GAME,S_WEEK,S_PLAYS,S_TEAM built;
    class CONTRACTS validation;
    class S_POSITION planned;
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
        S_POSITION["Planned position-week facts<br/>WR · RB · QB<br/>physical filenames not established"]
    end

    subgraph DraftGold["Draft Analysis Gold — planned player-season features"]
        G_WR["gold/draft/wr_season_features<br/>grain: player_id + season<br/>physical filename not established"]
        G_RB["gold/draft/rb_season_features<br/>grain: player_id + season<br/>physical filename not established"]
        G_QB["gold/draft/qb_season_features<br/>grain: player_id + season<br/>physical filename not established"]
    end

    DRAFT["Draft Analysis<br/>historical profiles and comparisons"]

    SOURCE --> B_FILES --> S_SHARED
    B_FILES --> S_OPPORTUNITY
    S_SHARED -.-> S_POSITION
    S_OPPORTUNITY -.-> S_POSITION
    S_POSITION -.-> G_WR
    S_POSITION -.-> G_RB
    S_POSITION -.-> G_QB
    G_WR -.-> DRAFT
    G_RB -.-> DRAFT
    G_QB -.-> DRAFT

    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a;
    classDef built fill:#d1fae5,stroke:#047857,color:#064e3b;
    classDef planned fill:#f3f4f6,stroke:#6b7280,color:#374151,stroke-dasharray:5 5;

    class SOURCE source;
    class B_FILES,S_SHARED,S_OPPORTUNITY built;
    class S_POSITION,G_WR,G_RB,G_QB,DRAFT planned;
```

Expected Draft features include validated volume, opportunity share, production, efficiency, scoring, and games-played context appropriate to each position. Exact feature definitions and dependencies will be established in future notebooks.

## 3. Waiver Wire Gold lineage

Waiver Wire answers whose role or opportunity is changing now. Its lineage remains weekly and time-ordered so recent trends can be calculated without using future games.

```mermaid
flowchart TB
    SOURCE["nflverse source datasets"]
    B_FILES["Exact nflreadpy calls → Bronze files<br/><br/>nfl.load_players()<br/>→ data/bronze/players/players.parquet<br/><br/>nfl.load_schedules(seasons=[season])<br/>→ data/bronze/schedules/schedules_2023.parquet<br/>→ data/bronze/schedules/schedules_2024.parquet<br/>→ data/bronze/schedules/schedules_2025.parquet<br/><br/>nfl.load_player_stats(seasons=[season], summary_level='week')<br/>→ data/bronze/player_stats_weekly/player_stats_weekly_2023.parquet<br/>→ data/bronze/player_stats_weekly/player_stats_weekly_2024.parquet<br/>→ data/bronze/player_stats_weekly/player_stats_weekly_2025.parquet<br/><br/>nfl.load_rosters_weekly(seasons=[season])<br/>→ data/bronze/rosters_weekly/rosters_weekly_2023.parquet<br/>→ data/bronze/rosters_weekly/rosters_weekly_2024.parquet<br/>→ data/bronze/rosters_weekly/rosters_weekly_2025.parquet<br/><br/>nfl.load_snap_counts(seasons=[season])<br/>→ data/bronze/snap_counts/snap_counts_2023.parquet<br/>→ data/bronze/snap_counts/snap_counts_2024.parquet<br/>→ data/bronze/snap_counts/snap_counts_2025.parquet<br/><br/>nfl.load_pbp(seasons=[season])<br/>→ data/bronze/pbp/pbp_2023.parquet<br/>→ data/bronze/pbp/pbp_2024.parquet<br/>→ data/bronze/pbp/pbp_2025.parquet"]

    subgraph Silver["Relevant Silver foundation"]
        S_WEEK["data/silver/player_week/player_week_2023.parquet<br/>data/silver/player_week/player_week_2024.parquet<br/>data/silver/player_week/player_week_2025.parquet<br/>statistics, participation, and context"]
        S_GAME["data/silver/player_game_participation/player_game_participation_2023.parquet<br/>data/silver/player_game_participation/player_game_participation_2024.parquet<br/>data/silver/player_game_participation/player_game_participation_2025.parquet"]
        S_PLAYS["data/silver/standardized_plays/standardized_plays_2023.parquet<br/>data/silver/standardized_plays/standardized_plays_2024.parquet<br/>data/silver/standardized_plays/standardized_plays_2025.parquet"]
        S_TEAM["data/silver/team_week_opportunity/team_week_opportunity_2023.parquet<br/>data/silver/team_week_opportunity/team_week_opportunity_2024.parquet<br/>data/silver/team_week_opportunity/team_week_opportunity_2025.parquet"]
        S_POSITION["Planned position-week facts<br/>physical filenames not established"]
    end

    TRENDS["Time-safe feature calculations<br/>current week · prior 3 weeks · season to date"]
    G_WAIVER["gold/waiver/player_weekly_trends<br/>grain: player_id + season + week<br/>physical filename not established"]
    WAIVER["Waiver Wire<br/>role changes and transparent signals"]

    SOURCE --> B_FILES
    B_FILES --> S_WEEK
    B_FILES --> S_GAME
    B_FILES --> S_PLAYS --> S_TEAM
    S_WEEK -.-> S_POSITION
    S_TEAM -.-> S_POSITION
    S_WEEK -.-> TRENDS
    S_GAME -.-> TRENDS
    S_TEAM -.-> TRENDS
    S_POSITION -.-> TRENDS
    TRENDS -.-> G_WAIVER -.-> WAIVER

    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a;
    classDef built fill:#d1fae5,stroke:#047857,color:#064e3b;
    classDef planned fill:#f3f4f6,stroke:#6b7280,color:#374151,stroke-dasharray:5 5;

    class SOURCE source;
    class B_FILES,S_WEEK,S_GAME,S_PLAYS,S_TEAM built;
    class S_POSITION,TRENDS,G_WAIVER,WAIVER planned;
```

The rolling feature step must use only the current and earlier weeks available at each row. Initial signals should remain transparent—for example, rising usage or high opportunity with low production—rather than becoming an unexplained composite score.

## 4. Player Explorer Gold lineage

Player Explorer combines the long-term Draft view with the recent Waiver view. Its preferred design is to reuse those Gold products rather than rebuild the same features in a third pipeline.

```mermaid
flowchart TB
    SOURCE["nflverse source datasets"]
    B_FILES["Exact nflreadpy calls → Bronze files<br/><br/>nfl.load_players()<br/>→ data/bronze/players/players.parquet<br/><br/>nfl.load_schedules(seasons=[season])<br/>→ data/bronze/schedules/schedules_2023.parquet<br/>→ data/bronze/schedules/schedules_2024.parquet<br/>→ data/bronze/schedules/schedules_2025.parquet<br/><br/>nfl.load_player_stats(seasons=[season], summary_level='week')<br/>→ data/bronze/player_stats_weekly/player_stats_weekly_2023.parquet<br/>→ data/bronze/player_stats_weekly/player_stats_weekly_2024.parquet<br/>→ data/bronze/player_stats_weekly/player_stats_weekly_2025.parquet<br/><br/>nfl.load_rosters_weekly(seasons=[season])<br/>→ data/bronze/rosters_weekly/rosters_weekly_2023.parquet<br/>→ data/bronze/rosters_weekly/rosters_weekly_2024.parquet<br/>→ data/bronze/rosters_weekly/rosters_weekly_2025.parquet<br/><br/>nfl.load_snap_counts(seasons=[season])<br/>→ data/bronze/snap_counts/snap_counts_2023.parquet<br/>→ data/bronze/snap_counts/snap_counts_2024.parquet<br/>→ data/bronze/snap_counts/snap_counts_2025.parquet<br/><br/>nfl.load_pbp(seasons=[season])<br/>→ data/bronze/pbp/pbp_2023.parquet<br/>→ data/bronze/pbp/pbp_2024.parquet<br/>→ data/bronze/pbp/pbp_2025.parquet"]
    S_CURRENT["Implemented shared Silver<br/><br/>data/silver/player_game_participation/player_game_participation_2023.parquet<br/>data/silver/player_game_participation/player_game_participation_2024.parquet<br/>data/silver/player_game_participation/player_game_participation_2025.parquet<br/><br/>data/silver/player_week/player_week_2023.parquet<br/>data/silver/player_week/player_week_2024.parquet<br/>data/silver/player_week/player_week_2025.parquet"]
    S_OPPORTUNITY["Implemented opportunity Silver<br/><br/>data/silver/standardized_plays/standardized_plays_2023.parquet<br/>data/silver/standardized_plays/standardized_plays_2024.parquet<br/>data/silver/standardized_plays/standardized_plays_2025.parquet<br/><br/>data/silver/team_week_opportunity/team_week_opportunity_2023.parquet<br/>data/silver/team_week_opportunity/team_week_opportunity_2024.parquet<br/>data/silver/team_week_opportunity/team_week_opportunity_2025.parquet"]
    S_POSITION["Planned WR, RB, and QB weekly facts<br/>physical filenames not established"]

    subgraph ExistingGoldShapes["Planned reusable Gold products"]
        G_DRAFT["gold/draft/wr_season_features<br/>gold/draft/rb_season_features<br/>gold/draft/qb_season_features<br/>grain: player_id + season<br/>physical filenames not established"]
        G_WAIVER["gold/waiver/player_weekly_trends<br/>grain: player_id + season + week<br/>physical filename not established"]
    end

    G_HISTORY["Optional gold/player/player_history<br/>grain: player_id + season + week<br/>physical filename not established"]
    EXPLORER["Player Explorer<br/>historical profile + recent weekly story"]

    SOURCE --> B_FILES --> S_CURRENT
    B_FILES --> S_OPPORTUNITY
    S_CURRENT -.-> G_DRAFT
    S_CURRENT -.-> G_WAIVER
    S_OPPORTUNITY -.-> G_DRAFT
    S_OPPORTUNITY -.-> G_WAIVER
    S_CURRENT -.-> S_POSITION
    S_OPPORTUNITY -.-> S_POSITION
    S_POSITION -.-> G_DRAFT
    S_POSITION -.-> G_WAIVER
    G_DRAFT -.-> EXPLORER
    G_WAIVER -.-> EXPLORER
    G_DRAFT -.-> G_HISTORY
    G_WAIVER -.-> G_HISTORY
    G_HISTORY -.-> EXPLORER

    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a;
    classDef built fill:#d1fae5,stroke:#047857,color:#064e3b;
    classDef planned fill:#f3f4f6,stroke:#6b7280,color:#374151,stroke-dasharray:5 5;
    classDef optional fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,stroke-dasharray:5 5;

    class SOURCE source;
    class B_FILES,S_CURRENT,S_OPPORTUNITY built;
    class S_POSITION,G_DRAFT,G_WAIVER,EXPLORER planned;
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
