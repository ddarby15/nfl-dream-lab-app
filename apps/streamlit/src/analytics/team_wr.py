import pandas as pd


def prepare_receiver_opportunity_volume(
    team_week_df: pd.DataFrame,
    minimum_targets: int = 1,
) -> pd.DataFrame:
    """
    Aggregate WR player-week rows into team-specific receiver profiles.

    Input grain:
        player_id + season + week

    Output grain:
        player_id

    Per-game metrics use the sum of component values divided by the
    sum of games observed. Weekly per-game rates are not averaged.
    """
    required_columns = {
        "player_id",
        "display_name",
        "targets",
        "receptions",
        "games_observed",
    }

    missing_columns = required_columns.difference(
        team_week_df.columns
    )

    # -----------------------------
    # Quality & Validations
    # -----------------------------
    if missing_columns:
        raise ValueError(
            "Cannot prepare receiver opportunity volume. "
            f"Missing columns: {sorted(missing_columns)}"
        )

    if team_week_df.empty:
        raise ValueError(
            "Cannot prepare receiver opportunity volume "
            "from an empty DataFrame."
        )

    if minimum_targets < 0:
        raise ValueError(
            "minimum_targets must be greater than or equal to zero."
        )


    # --------------------------------------------------
    # Aggregate weekly rows into receiver-season profiles
    # Grain: player_id + display_name
    # --------------------------------------------------
    receiver_opportunity_df = (
        team_week_df
        .groupby(
            ["player_id", "display_name"],
            as_index=False,
        )
        .agg(
            targets=(
                "targets",
                lambda values: values.sum(min_count=1),
            ),
            receptions=(
                "receptions",
                lambda values: values.sum(min_count=1),
            ),
            games_observed=(
                "games_observed",
                "sum",
            ),
        )
    )

    receiver_opportunity_df["targets_per_game"] = (
        receiver_opportunity_df["targets"]
        / receiver_opportunity_df["games_observed"]
    )

    receiver_opportunity_df["receptions_per_game"] = (
        receiver_opportunity_df["receptions"]
        / receiver_opportunity_df["games_observed"]
    )

    # Keep the threshold explicit so zero-target contextual receivers
    # can be included by passing minimum_targets=0.
    receiver_opportunity_df = receiver_opportunity_df.loc[
        receiver_opportunity_df["targets"].fillna(0)
        >= minimum_targets
    ]

    # Descending order is convenient when displaying the prepared
    # DataFrame as a table.
    receiver_opportunity_df = (
        receiver_opportunity_df
        .sort_values(
            ["targets_per_game", "display_name"],
            ascending=[False, True],
        )
        .reset_index(drop=True)
    )

    return receiver_opportunity_df


def prepare_receiver_role_shares(
    team_week_df: pd.DataFrame,
    minimum_targets: int = 1,
) -> pd.DataFrame:
    """
    Aggregate WR player-week rows into receiver opportunity-share profiles.

    Input grain:
        player_id + season + week

    Output grain:
        player_id

    Target Share and Air-Yard Share are recalculated from aggregated
    components. Weekly share percentages are not averaged.

    A positive share difference means Air-Yard Share exceeds Target
    Share, which generally indicates relatively deeper usage.
    """
    required_columns = {
        "player_id",
        "display_name",
        "targets",
        "team_targets",
        "receiving_air_yards",
        "team_passing_air_yards",
        "games_observed",
    }

    missing_columns = required_columns.difference(
        team_week_df.columns
    )

    # -----------------------------
    # Quality and validations
    # -----------------------------
    if missing_columns:
        raise ValueError(
            "Cannot prepare receiver role shares. "
            f"Missing columns: {sorted(missing_columns)}"
        )

    if team_week_df.empty:
        raise ValueError(
            "Cannot prepare receiver role shares "
            "from an empty DataFrame."
        )

    if minimum_targets < 0:
        raise ValueError(
            "minimum_targets must be greater than or equal to zero."
        )

    # --------------------------------------------------
    # Aggregate weekly rows into receiver-season profiles
    # Grain: player_id + display_name
    # --------------------------------------------------
    receiver_roles_df = (
        team_week_df
        .groupby(
            ["player_id", "display_name"],
            as_index=False,
        )
        .agg(
            targets=(
                "targets",
                lambda values: values.sum(min_count=1),
            ),
            team_targets=(
                "team_targets",
                lambda values: values.sum(min_count=1),
            ),
            receiving_air_yards=(
                "receiving_air_yards",
                lambda values: values.sum(min_count=1),
            ),
            team_passing_air_yards=(
                "team_passing_air_yards",
                lambda values: values.sum(min_count=1),
            ),
            games_observed=(
                "games_observed",
                "sum",
            ),
        )
    )

    # Recalculate both shares from their aggregated components.
    receiver_roles_df["target_share"] = (
        receiver_roles_df["targets"]
        / receiver_roles_df["team_targets"]
    ).where(
        receiver_roles_df["team_targets"] != 0
    )

    receiver_roles_df["air_yards_share"] = (
        receiver_roles_df["receiving_air_yards"]
        / receiver_roles_df["team_passing_air_yards"]
    ).where(
        receiver_roles_df["team_passing_air_yards"] != 0
    )

    # Positive values mean Air-Yard Share exceeds Target Share.
    receiver_roles_df["share_difference"] = (
        receiver_roles_df["air_yards_share"]
        - receiver_roles_df["target_share"]
    )

    receiver_roles_df = receiver_roles_df.loc[
        receiver_roles_df["targets"].fillna(0)
        >= minimum_targets
    ].copy()

    # Both values are required to position a receiver on the chart.
    receiver_roles_df = receiver_roles_df.dropna(
        subset=[
            "target_share",
            "air_yards_share",
        ]
    )

    if receiver_roles_df.empty:
        raise ValueError(
            "Cannot prepare receiver role shares because "
            "no receivers have complete share metrics."
        )

    receiver_roles_df = (
        receiver_roles_df
        .sort_values(
            ["target_share", "display_name"],
            ascending=[False, True],
        )
        .reset_index(drop=True)
    )

    return receiver_roles_df


def prepare_receiver_target_depth_distribution(
    team_week_df: pd.DataFrame,
    minimum_season_targets: int = 1,
) -> pd.DataFrame:
    """
    Prepare game-level aDOT observations for a team's receivers.

    Input grain:
        player_id + season + week

    Output grain:
        player_id + season + week

    The current Gold data has one observed game per player-week, so
    each weekly aDOT is currently equivalent to a game-level aDOT.

    The box-plot observations use the existing weekly aDOT values.
    Season aDOT is recalculated from aggregated components:

        total receiving air yards / total targets

    Weekly aDOT values are not averaged to calculate season aDOT.
    """
    required_columns = {
        "player_id",
        "display_name",
        "week",
        "targets",
        "receiving_air_yards",
        "games_observed",
        "average_depth_of_target",
    }

    missing_columns = required_columns.difference(
        team_week_df.columns
    )

    # -----------------------------
    # Quality and validations
    # -----------------------------
    if missing_columns:
        raise ValueError(
            "Cannot prepare receiver target-depth distribution. "
            f"Missing columns: {sorted(missing_columns)}"
        )

    if team_week_df.empty:
        raise ValueError(
            "Cannot prepare receiver target-depth distribution "
            "from an empty DataFrame."
        )

    if minimum_season_targets < 1:
        raise ValueError(
            "minimum_season_targets must be at least one."
        )

    # A box-plot observation is only defined when the receiver
    # recorded at least one target and has a calculated weekly aDOT.
    valid_game_mask = (
        team_week_df["targets"].fillna(0).gt(0)
        & team_week_df["average_depth_of_target"].notna()
    )

    valid_game_df = team_week_df.loc[
        valid_game_mask,
        [
            "player_id",
            "display_name",
            "week",
            "targets",
            "receiving_air_yards",
            "games_observed",
            "average_depth_of_target",
        ],
    ].copy()

    if valid_game_df.empty:
        raise ValueError(
            "Cannot prepare receiver target-depth distribution "
            "because no rows have both targets and a defined aDOT."
        )

    # The current Gold data contains one game per player-week.
    # Raise an error if that contract changes rather than silently
    # presenting a multi-game weekly value as a game-level value.
    if not valid_game_df["games_observed"].eq(1).all():
        raise ValueError(
            "The target-depth distribution requires one observed "
            "game per player-week. At least one qualifying row "
            "contains a different games_observed value."
        )

    # --------------------------------------------------
    # Calculate target-weighted receiver summaries
    # Grain: player_id + display_name
    # --------------------------------------------------
    receiver_summary_df = (
        team_week_df
        .groupby(
            ["player_id", "display_name"],
            as_index=False,
        )
        .agg(
            season_targets=(
                "targets",
                lambda values: values.sum(min_count=1),
            ),
            season_receiving_air_yards=(
                "receiving_air_yards",
                lambda values: values.sum(min_count=1),
            ),
            season_games_observed=(
                "games_observed",
                "sum",
            ),
        )
    )

    receiver_summary_df["season_average_depth_of_target"] = (
        receiver_summary_df["season_receiving_air_yards"]
        / receiver_summary_df["season_targets"]
    ).where(
        receiver_summary_df["season_targets"] != 0
    )

    # Count the actual observations that will appear in each box.
    games_with_defined_adot_df = (
        valid_game_df
        .groupby(
            ["player_id", "display_name"],
            as_index=False,
        )
        .size()
        .rename(
            columns={
                "size": "games_with_defined_adot",
            }
        )
    )

    receiver_summary_df = receiver_summary_df.merge(
        games_with_defined_adot_df,
        on=["player_id", "display_name"],
        how="left",
        validate="one_to_one",
    )

    # Calculate the target-weighted team WR aDOT before applying
    # the receiver display threshold.
    team_wr_targets = receiver_summary_df[
        "season_targets"
    ].sum(
        min_count=1
    )

    team_wr_receiving_air_yards = receiver_summary_df[
        "season_receiving_air_yards"
    ].sum(
        min_count=1
    )

    if pd.notna(team_wr_targets) and team_wr_targets != 0:
        team_wr_average_depth_of_target = (
            team_wr_receiving_air_yards
            / team_wr_targets
        )
    else:
        team_wr_average_depth_of_target = pd.NA

    # Apply the season-level display threshold.
    receiver_summary_df = receiver_summary_df.loc[
        receiver_summary_df["season_targets"].fillna(0)
        >= minimum_season_targets
    ]

    # Add the season summaries to each game observation.
    receiver_target_depth_df = valid_game_df.merge(
        receiver_summary_df,
        on=["player_id", "display_name"],
        how="inner",
        validate="many_to_one",
    )

    receiver_target_depth_df[
        "team_wr_average_depth_of_target"
    ] = team_wr_average_depth_of_target

    receiver_target_depth_df = (
        receiver_target_depth_df
        .sort_values(
            [
                "season_average_depth_of_target",
                "display_name",
                "week",
            ],
            ascending=[False, True, True],
        )
        .reset_index(drop=True)
    )

    return receiver_target_depth_df


def prepare_receiver_role_map(
    team_week_df: pd.DataFrame,
    minimum_targets: int = 1,
) -> pd.DataFrame:
    """
    Aggregate WR player-week rows into receiver-season role profiles.

    Input grain:
        player_id + season + week

    Output grain:
        player_id

    Target Share, Air-Yard Share, aDOT, and Targets/Game are
    recalculated from aggregated components. Weekly rates and shares
    are not averaged.

    Team denominators cover the games observed for each receiver.
    """
    required_columns = {
        "player_id",
        "display_name",
        "targets",
        "team_targets",
        "receiving_air_yards",
        "team_passing_air_yards",
        "games_observed",
    }

    missing_columns = required_columns.difference(
        team_week_df.columns
    )

    # -----------------------------
    # Quality and validations
    # -----------------------------
    if missing_columns:
        raise ValueError(
            "Cannot prepare receiver role map. "
            f"Missing columns: {sorted(missing_columns)}"
        )

    if team_week_df.empty:
        raise ValueError(
            "Cannot prepare receiver role map "
            "from an empty DataFrame."
        )

    if minimum_targets < 1:
        raise ValueError(
            "minimum_targets must be at least one."
        )

    # --------------------------------------------------
    # Aggregate weekly rows into receiver-season profiles
    # Grain: player_id + display_name
    # --------------------------------------------------
    receiver_role_map_df = (
        team_week_df
        .groupby(
            ["player_id", "display_name"],
            as_index=False,
        )
        .agg(
            targets=(
                "targets",
                lambda values: values.sum(min_count=1),
            ),
            team_targets=(
                "team_targets",
                lambda values: values.sum(min_count=1),
            ),
            receiving_air_yards=(
                "receiving_air_yards",
                lambda values: values.sum(min_count=1),
            ),
            team_passing_air_yards=(
                "team_passing_air_yards",
                lambda values: values.sum(min_count=1),
            ),
            games_observed=(
                "games_observed",
                "sum",
            ),
        )
    )

    # Recalculate all ratios from their aggregated components.
    receiver_role_map_df["target_share"] = (
        receiver_role_map_df["targets"]
        / receiver_role_map_df["team_targets"]
    ).where(
        receiver_role_map_df["team_targets"] != 0
    )

    receiver_role_map_df["air_yards_share"] = (
        receiver_role_map_df["receiving_air_yards"]
        / receiver_role_map_df["team_passing_air_yards"]
    ).where(
        receiver_role_map_df["team_passing_air_yards"] != 0
    )

    receiver_role_map_df["average_depth_of_target"] = (
        receiver_role_map_df["receiving_air_yards"]
        / receiver_role_map_df["targets"]
    ).where(
        receiver_role_map_df["targets"] != 0
    )

    receiver_role_map_df["targets_per_game"] = (
        receiver_role_map_df["targets"]
        / receiver_role_map_df["games_observed"]
    ).where(
        receiver_role_map_df["games_observed"] != 0
    )

    # Calculate the target-weighted team WR aDOT before applying
    # the receiver display threshold.
    team_wr_targets = receiver_role_map_df[
        "targets"
    ].sum(
        min_count=1
    )

    team_wr_receiving_air_yards = receiver_role_map_df[
        "receiving_air_yards"
    ].sum(
        min_count=1
    )

    if pd.notna(team_wr_targets) and team_wr_targets != 0:
        team_wr_average_depth_of_target = (
            team_wr_receiving_air_yards
            / team_wr_targets
        )
    else:
        team_wr_average_depth_of_target = pd.NA

    receiver_role_map_df[
        "team_wr_average_depth_of_target"
    ] = team_wr_average_depth_of_target

    # Apply the receiver display threshold.
    receiver_role_map_df = receiver_role_map_df.loc[
        receiver_role_map_df["targets"].fillna(0)
        >= minimum_targets
    ].copy()

    # Remove players who cannot be positioned on both axes.
    receiver_role_map_df = receiver_role_map_df.dropna(
        subset=[
            "target_share",
            "average_depth_of_target",
            "targets_per_game",
            "air_yards_share",
        ]
    )

    if receiver_role_map_df.empty:
        raise ValueError(
            "Cannot prepare receiver role map because "
            "no receivers have complete role-map metrics."
        )

    # This reference divides the displayed receivers into relatively
    # higher- and lower-share groups. It is a descriptive reference,
    # not a league-wide performance threshold.
    displayed_receiver_median_target_share = (
        receiver_role_map_df["target_share"].median()
    )

    receiver_role_map_df[
        "displayed_receiver_median_target_share"
    ] = displayed_receiver_median_target_share

    receiver_role_map_df = (
        receiver_role_map_df
        .sort_values(
            ["target_share", "display_name"],
            ascending=[False, True],
        )
        .reset_index(drop=True)
    )

    return receiver_role_map_df