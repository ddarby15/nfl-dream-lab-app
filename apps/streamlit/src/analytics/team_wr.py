import pandas as pd


def prepare_receiver_opportunity_volume(
    team_season_df: pd.DataFrame,
    minimum_targets: int = 1,
) -> pd.DataFrame:
    """
    Prepare receivers for the opportunity-volume chart.

    Input: player-team-season Gold, filtered to one season,
           season type, and team.
    Output: one row per player on that team.
    """
    required_columns = {
        "player_id",
        "season",
        "season_type",
        "team",
        "display_name",
        "targets",
        "receptions",
        "games_observed",
        "targets_per_game",
        "receptions_per_game",
    }

    missing_columns = required_columns - set(team_season_df.columns)
    if missing_columns:
        raise ValueError(f"Missing columns: {sorted(missing_columns)}")

    if minimum_targets < 0:
        raise ValueError("minimum_targets must be at least zero.")

    if team_season_df.empty:
        raise ValueError("No receiving data for this selection.")

    selection_count = (
        team_season_df[["season", "season_type", "team"]]
        .drop_duplicates()
        .shape[0]
    )
    if selection_count != 1:
        raise ValueError(
            "Filter to one season, season type, and team before "
            "preparing the opportunity chart."
        )

    receiver_opportunity_df = team_season_df.loc[
        team_season_df["targets"] >= minimum_targets,
        [
            "player_id",
            "display_name",
            "targets",
            "receptions",
            "games_observed",
            "targets_per_game",
            "receptions_per_game",
        ],
    ].copy()

    if receiver_opportunity_df.empty:
        raise ValueError("No players meet the minimum-target threshold.")

    return (
        receiver_opportunity_df
        .sort_values(
            ["targets_per_game", "display_name"],
            ascending=[False, True],
        )
        .reset_index(drop=True)
    )


def prepare_receiver_role_map(
    team_season_df: pd.DataFrame,
    minimum_targets: int = 1,
) -> pd.DataFrame:
    """Prepare the aDOT-versus-target-share chart from season Gold."""
    required_columns = {
        "player_id",
        "season",
        "season_type",
        "team",
        "display_name",
        "targets",
        "games_observed",
        "air_yards",
        "team_targets_observed",
        "team_passing_air_yards_observed",
        "target_share_observed",
        "air_yard_share_observed",
        "adot",
        "targets_per_game",
    }

    missing_columns = required_columns - set(team_season_df.columns)
    if missing_columns:
        raise ValueError(
            f"Cannot prepare receiver role map. "
            f"Missing columns: {sorted(missing_columns)}"
        )

    if team_season_df.empty:
        raise ValueError("No receiving data for this selection.")

    if minimum_targets < 1:
        raise ValueError("minimum_targets must be at least one.")

    selection_count = (
        team_season_df[["season", "season_type", "team"]]
        .drop_duplicates()
        .shape[0]
    )
    if selection_count != 1:
        raise ValueError(
            "Filter to one season, season type, and team first."
        )

    # Reference aDOT for the selected group, before the display threshold.
    group_targets = team_season_df["targets"].sum()
    group_air_yards = team_season_df["air_yards"].sum()
    group_adot = (
        group_air_yards / group_targets
        if group_targets > 0
        else pd.NA
    )

    receiver_role_map_df = (
        team_season_df.loc[
            team_season_df["targets"] >= minimum_targets,
            [
                "player_id",
                "display_name",
                "targets",
                "games_observed",
                "air_yards",
                "team_targets_observed",
                "team_passing_air_yards_observed",
                "target_share_observed",
                "air_yard_share_observed",
                "adot",
                "targets_per_game",
            ],
        ]
        .rename(
            columns={
                "air_yards": "receiving_air_yards",
                "team_targets_observed": "team_targets",
                "team_passing_air_yards_observed": "team_passing_air_yards",
                "target_share_observed": "target_share",
                "air_yard_share_observed": "air_yards_share",
                "adot": "average_depth_of_target",
            }
        )
        .dropna(
            subset=[
                "target_share",
                "air_yards_share",
                "average_depth_of_target",
                "targets_per_game",
            ]
        )
        .copy()
    )

    if receiver_role_map_df.empty:
        raise ValueError("No players have complete role-map metrics.")

    # Retain these names for compatibility with the existing chart.
    receiver_role_map_df["team_wr_average_depth_of_target"] = group_adot
    receiver_role_map_df[
        "displayed_receiver_median_target_share"
    ] = receiver_role_map_df["target_share"].median()

    return (
        receiver_role_map_df
        .sort_values(
            ["target_share", "display_name"],
            ascending=[False, True],
        )
        .reset_index(drop=True)
    )


def prepare_receiver_target_depth_distribution(
    team_game_df: pd.DataFrame,
    team_season_df: pd.DataFrame,
    minimum_season_targets: int = 1,
) -> pd.DataFrame:
    """Prepare game aDOT observations and season summaries for one team."""
    season_keys = ["player_id", "season", "season_type", "team"]

    required_game_columns = set(season_keys) | {
        "game_id", "week", "targets", "air_yards", "adot"
    }
    required_season_columns = set(season_keys) | {
        "display_name", "targets", "air_yards",
        "games_observed", "adot"
    }

    missing_game = required_game_columns - set(team_game_df.columns)
    missing_season = required_season_columns - set(team_season_df.columns)

    if missing_game or missing_season:
        raise ValueError(
            f"Missing game columns: {sorted(missing_game)}; "
            f"missing season columns: {sorted(missing_season)}"
        )

    if team_season_df.empty:
        raise ValueError("No receiving season data for this selection.")

    if minimum_season_targets < 1:
        raise ValueError("minimum_season_targets must be at least one.")

    if (
        team_season_df[["season", "season_type", "team"]]
        .drop_duplicates()
        .shape[0] != 1
    ):
        raise ValueError(
            "Filter to one season, season type, and team first."
        )

    # Calculate the selected group's reference aDOT before applying
    # the player display threshold.
    group_targets = team_season_df["targets"].sum()
    group_adot = (
        team_season_df["air_yards"].sum() / group_targets
        if group_targets > 0
        else pd.NA
    )

    season_summary_df = (
        team_season_df.loc[
            team_season_df["targets"] >= minimum_season_targets,
            season_keys + [
                "display_name", "targets", "air_yards",
                "games_observed", "adot",
            ],
        ]
        .rename(
            columns={
                "targets": "season_targets",
                "air_yards": "season_receiving_air_yards",
                "games_observed": "season_games_observed",
                "adot": "season_average_depth_of_target",
            }
        )
        .copy()
    )

    if season_summary_df.empty:
        raise ValueError("No players meet the season-target threshold.")

    # One row per targeted game becomes one box-plot observation.
    valid_games_df = (
        team_game_df.loc[
            team_game_df["targets"].gt(0)
            & team_game_df["adot"].notna(),
            season_keys + ["game_id", "week", "targets", "air_yards", "adot"],
        ]
        .rename(
            columns={
                "air_yards": "receiving_air_yards",
                "adot": "average_depth_of_target",
            }
        )
        .copy()
    )

    receiver_target_depth_df = valid_games_df.merge(
        season_summary_df,
        on=season_keys,
        how="inner",
        validate="many_to_one",
    )

    if receiver_target_depth_df.empty:
        raise ValueError("No targeted games have a defined aDOT.")

    # These columns retain compatibility with the existing Plotly function.
    receiver_target_depth_df["games_observed"] = 1
    receiver_target_depth_df["games_with_defined_adot"] = (
        receiver_target_depth_df
        .groupby(season_keys)["game_id"]
        .transform("size")
    )
    receiver_target_depth_df[
        "team_wr_average_depth_of_target"
    ] = group_adot

    return (
        receiver_target_depth_df
        .sort_values(
            ["season_average_depth_of_target", "display_name", "week"],
            ascending=[False, True, True],
        )
        .reset_index(drop=True)
    )


def prepare_receiver_role_shares(
    team_season_df: pd.DataFrame,
    minimum_targets: int = 1,
) -> pd.DataFrame:
    """
    Prepare observed-game receiving shares for one team and season.

    Input: player-team-season Gold filtered to one season,
           season type, and team.
    Output: one row per player, using the column names expected
            by create_receiver_role_figure().
    """
    required_columns = {
        "player_id",
        "season",
        "season_type",
        "team",
        "display_name",
        "targets",
        "games_observed",
        "air_yards",
        "team_targets_observed",
        "team_passing_air_yards_observed",
        "target_share_observed",
        "air_yard_share_observed",
    }

    missing_columns = required_columns - set(team_season_df.columns)
    if missing_columns:
        raise ValueError(f"Missing columns: {sorted(missing_columns)}")

    if team_season_df.empty:
        raise ValueError("No receiving data for this selection.")

    if minimum_targets < 0:
        raise ValueError("minimum_targets must be at least zero.")

    selection_count = (
        team_season_df[["season", "season_type", "team"]]
        .drop_duplicates()
        .shape[0]
    )
    if selection_count != 1:
        raise ValueError(
            "Filter to one season, season type, and team first."
        )

    receiver_roles_df = (
        team_season_df.loc[
            team_season_df["targets"] >= minimum_targets,
            [
                "player_id",
                "display_name",
                "targets",
                "games_observed",
                "air_yards",
                "team_targets_observed",
                "team_passing_air_yards_observed",
                "target_share_observed",
                "air_yard_share_observed",
            ],
        ]
        .rename(
            columns={
                "air_yards": "receiving_air_yards",
                "team_targets_observed": "team_targets",
                "team_passing_air_yards_observed": "team_passing_air_yards",
                "target_share_observed": "target_share",
                "air_yard_share_observed": "air_yards_share",
            }
        )
        .dropna(subset=["target_share", "air_yards_share"])
        .copy()
    )

    if receiver_roles_df.empty:
        raise ValueError(
            "No players meet the target threshold with both "
            "shares defined."
        )

    receiver_roles_df["share_difference"] = (
        receiver_roles_df["air_yards_share"]
        - receiver_roles_df["target_share"]
    )

    return (
        receiver_roles_df
        .sort_values(
            ["target_share", "display_name"],
            ascending=[False, True],
        )
        .reset_index(drop=True)
    )