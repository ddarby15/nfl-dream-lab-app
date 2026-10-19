# Waiver Gold Metric Contracts

Last updated: 2026-10-04

## Status

The position-specific current-week foundations are implemented and validated for the 2023–2025 regular seasons. Calendar-week rolling windows, history eligibility, comparisons, and transparent waiver signals remain planned until the current-week outputs are reviewed.

| Dataset | Persisted files | Grain | Rows | Columns | Rows without weekly-stat evidence |
|---|---|---|---:|---:|---:|
| `gold_wr_weekly_trends` | `data/gold/waiver/wr_weekly_trends/wr_weekly_trends_{season}.parquet` | `player_id + season + week` | 8,475 | 80 | 1,019 |
| `gold_rb_weekly_trends` | `data/gold/waiver/rb_weekly_trends/rb_weekly_trends_{season}.parquet` | `player_id + season + week` | 5,542 | 99 | 687 |
| `gold_qb_weekly_trends` | `data/gold/waiver/qb_weekly_trends/qb_weekly_trends_{season}.parquet` | `player_id + season + week` | 2,071 | 102 | 50 |

## Shared current-week contract

- Only regular-season rows enter Waiver Gold.
- Every contextual position row from the applicable Silver dataset is retained. Percentile or signal eligibility never removes a player-week.
- The source grain is `player_id + season + week + team`; the Gold grain is `player_id + season + week`.
- Current 2023–2025 data has no same-week multi-team player records. The Gold transformation still retains ordered `game_ids`, `teams_in_week`, and `opponents_in_week` values. Singular `team` and `opponent_team` are populated only when exactly one value exists; they will be null rather than arbitrary for any future multi-record week.
- `games_observed` counts distinct represented games. It is one for every current row, while the schema and rate calculations remain valid if a rescheduled week later contains more than one game.
- No roster-only, bye-week, or otherwise unobserved player-week rows are manufactured at this stage.
- Canonical PBP opportunity is zero when complete play evidence establishes zero. Official weekly statistics and fantasy points remain null when the player-week has no weekly-stat record.
- Shares and efficiencies are recomputed from aggregated components. Existing weekly percentages are never averaged.
- A zero denominator produces null. A zero numerator with a valid denominator produces zero.
- Per-game fields divide by `games_observed`.
- Full-PPR scoring uses the same transparent component rules as Draft Gold. QB passing touchdowns are worth four points; sacks have no fantasy-point penalty; no bonuses are applied.

## WR current-week metrics

The WR output contains identity and game context, participation, receiving and rushing opportunity, production, team denominators, shares, efficiencies, per-game fields, and scoring components.

Key opportunity and role definitions:

| Metric | Definition |
|---|---|
| `targets` | Canonical PBP targets |
| `targets_per_game` | `targets / games_observed` |
| `target_share` | `targets / team_targets` |
| `receptions_per_game` | `receptions / games_observed` |
| `average_depth_of_target` | `receiving_air_yards / targets` |
| `team_pass_attempts_per_game` | `team_pass_attempts / games_observed` |
| `air_yards_share` | `receiving_air_yards / team_passing_air_yards` |
| `target_air_yards_share` | `receiving_air_yards / team_target_air_yards` |
| `red_zone_target_share` | `red_zone_targets / team_red_zone_targets` |
| `goal_line_target_share` | `goal_line_targets / team_goal_line_targets` |
| `end_zone_target_share` | `end_zone_targets / team_end_zone_targets` |

## RB/FB current-week metrics

The RB/FB output preserves official and canonical workload separately and keeps all-team opportunity shares distinct from contextual RB/FB backfield-control shares.

Key opportunity and role definitions:

| Metric | Definition |
|---|---|
| `official_opportunities` | Official `rushing_attempts + targets` |
| `total_opportunities` | Canonical `non_kneel_rush_attempts + targets` |
| `total_opportunities_per_game` | `total_opportunities / games_observed` |
| `targets_per_game` | `targets / games_observed` |
| `receptions_per_game` | `receptions / games_observed` |
| `rush_attempt_share` | Canonical non-kneel rushes divided by all-team non-kneel rushes |
| `backfield_rush_share` | Official carries divided by contextual RB/FB official carries |
| `target_share` | `targets / team_targets` |
| `backfield_red_zone_rush_share` | RB/FB red-zone rushes divided by contextual RB/FB red-zone rushes |
| `backfield_goal_line_rush_share` | RB/FB goal-line rushes divided by contextual RB/FB goal-line rushes |
| `rushing_yards_per_game` | `rushing_yards / games_observed` |
| `receiving_yards_per_game` | `receiving_yards / games_observed` |
| `scrimmage_yards_per_game` | `(rushing_yards + receiving_yards) / games_observed` |

## QB current-week metrics

The QB output preserves official passing and rushing production separately from canonical PBP workload. Complete dropbacks include pass attempts, sacks, and scrambles; meaningful QB rushes include designed runs and scrambles while excluding kneels.

Key opportunity and role definitions:

| Metric | Definition |
|---|---|
| `passing_attempts_per_game` | Official passing attempts divided by `games_observed` |
| `complete_dropbacks_per_game` | Canonical complete dropbacks divided by `games_observed` |
| `passing_yards_per_attempt` | `passing_yards / passing_attempts` |
| `meaningful_qb_rush_attempts_per_game` | Meaningful QB rushes divided by `games_observed` |
| `red_zone_qb_rush_attempts_per_game` | Meaningful QB rushes at `yardline_100 <= 20` divided by `games_observed` |
| `goal_line_qb_rush_attempts_per_game` | Meaningful QB rushes at the configured goal-line threshold divided by `games_observed` |
| `ppr_fantasy_points_per_game` | Full-PPR component total divided by `games_observed` |
| `ppr_fantasy_points_per_complete_dropback` | Full-PPR component total divided by canonical complete dropbacks |
| `dropback_share` | Complete dropbacks divided by team dropbacks |

## Approved rolling-window contract

The next implementation checkpoint will extend these same position-specific datasets rather than create a unified sparse table.

- A three-week window means three NFL calendar weeks, not a player's last three active games.
- For a row at Week `W`, the prior-three baseline covers Weeks `W-3` through `W-1`; it excludes Week `W` and never crosses a season boundary.
- Season-to-date display metrics may include Week `W`. Comparison baselines must also expose a pre-current-week version so the current result is not compared partly with itself.
- Missing player-week rows are not silently converted to observed zero. Future rolling fields will expose the number of calendar weeks available and the number of observed games or player-weeks contributing to each calculation.
- Every current-week row remains in the output. Comparisons and signals remain null until their required history is available.
- Exact position-specific minimum workload thresholds for signals remain open for validation. Their eventual values must control only comparison or signal fields, never row retention.
- Rolling tests must prove that changing any future week cannot change an earlier row.

## Current limitations

- The datasets currently contain current-week facts only despite the `weekly_trends` names; rolling and signal columns are intentionally absent.
- Stat-correction and rescheduled-game refresh behavior still requires an explicit operational policy.
- The exact minimum prior workload for each position's trend signals remains unresolved pending inspection of the current-week distributions.
- nflverse licensing, attribution, freshness, availability, and redistribution constraints remain outside this metric contract and must be resolved before publication.
