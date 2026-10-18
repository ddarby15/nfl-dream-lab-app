import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def create_opportunity_volume_figure(
    receiver_opportunity_df: pd.DataFrame,
    team: str,
    season: int,
) -> go.Figure:
    """
    Create a grouped horizontal bar chart comparing Targets/Game
    and Receptions/Game for a team's receivers.
    """
    required_columns = {
        "player_id",
        "display_name",
        "targets",
        "receptions",
        "games_observed",
        "targets_per_game",
        "receptions_per_game",
    }

    missing_columns = required_columns.difference(
        receiver_opportunity_df.columns
    )

    # -----------------------------
    # Quality & Validations
    # -----------------------------
    if missing_columns:
        raise ValueError(
            "Cannot create opportunity volume figure. "
            f"Missing columns: {sorted(missing_columns)}"
        )

    if receiver_opportunity_df.empty:
        raise ValueError(
            "Cannot create opportunity volume figure "
            "from an empty DataFrame."
        )

    plot_df = receiver_opportunity_df.rename(
        columns={
            "targets_per_game": "Targets/Game",
            "receptions_per_game": "Receptions/Game",
        }
    )

    # Ascending order places the largest value at the top of a
    # horizontal Plotly bar chart.
    plot_df = plot_df.sort_values(
        "Targets/Game",
        ascending=False,
    )

    player_order = plot_df["display_name"].tolist()

    figure = px.bar(
        plot_df,
        x=[
            "Receptions/Game",
            "Targets/Game",
        ],
        y="display_name",
        orientation="h",
        barmode="group",
        text_auto=".1f",
        category_orders={
            "display_name": player_order,
        },
        color_discrete_map={
            "Targets/Game": "#2563EB",
            "Receptions/Game": "#F59E0B",
        },
        labels={
            "display_name": "Receiver",
            "value": "Opportunities per Game",
            "variable": "",
            "targets": "Total Targets",
            "receptions": "Total Receptions",
            "games_observed": "Games Observed",
        },
        hover_data={
            "targets": True,
            "receptions": True,
            "games_observed": True,
            "player_id": False,
        },
        title=f"{team} WR Opportunity Volume — {season}",
    )

    figure.update_traces(
        textposition="outside",
        cliponaxis=False,
    )

    figure.update_layout(
        template="plotly_white",
        height=max(
            450,
            75 + 45 * len(plot_df),
        ),
        bargap=0.25,
        legend_title_text="",
        legend_orientation="h",
        legend_yanchor="bottom",
        legend_y=1.02,
        legend_xanchor="left",
        legend_x=0,
        margin={
            "l": 20,
            "r": 50,
            "t": 100,
            "b": 50,
        },
    )

    figure.update_xaxes(
        title="Opportunities per Game",
        rangemode="tozero",
        showgrid=True
    )

    figure.update_yaxes(
        title=None,
    )

    return figure


def create_receiver_role_figure(
    receiver_roles_df: pd.DataFrame,
    team: str,
    season: int,
) -> go.Figure:
    """
    Create a scatter plot comparing Target Share with Air-Yard Share.

    X-axis:
        Air-Yard Share

    Y-axis:
        Target Share

    The equality line identifies where both shares are the same.
    """
    required_columns = {
        "player_id",
        "display_name",
        "targets",
        "team_targets",
        "receiving_air_yards",
        "team_passing_air_yards",
        "games_observed",
        "target_share",
        "air_yards_share",
        "share_difference",
    }

    missing_columns = required_columns.difference(
        receiver_roles_df.columns
    )

    # -----------------------------
    # Quality and validations
    # -----------------------------
    if missing_columns:
        raise ValueError(
            "Cannot create receiver role figure. "
            f"Missing columns: {sorted(missing_columns)}"
        )

    if receiver_roles_df.empty:
        raise ValueError(
            "Cannot create receiver role figure "
            "from an empty DataFrame."
        )

    plot_df = receiver_roles_df.dropna(
        subset=[
            "target_share",
            "air_yards_share",
        ]
    ).copy()

    if plot_df.empty:
        raise ValueError(
            "Cannot create receiver role figure because "
            "all receiver share values are missing."
        )

    # --------------------------------------------------
    # Use the same numerical range for both axes
    # --------------------------------------------------
    # This ensures that the equality line represents a visually
    # honest one-to-one comparison.
    share_values = pd.concat(
        [
            plot_df["air_yards_share"],
            plot_df["target_share"],
        ],
        ignore_index=True,
    ).dropna()

    axis_min = min(
        0.0,
        float(share_values.min()),
    )

    axis_max = max(
        0.0,
        float(share_values.max()),
    )

    axis_span = axis_max - axis_min

    if axis_span == 0:
        axis_span = 0.10

    axis_padding = axis_span * 0.08

    # Keep zero as the lower boundary when all shares are positive.
    if axis_min < 0:
        axis_min -= axis_padding

    axis_max += axis_padding

    figure = px.scatter(
        plot_df,
        x="air_yards_share",
        y="target_share",
        text="display_name",
        labels={
            "air_yards_share": "Air-Yard Share",
            "target_share": "Target Share",
            "display_name": "Receiver",
        },
        custom_data=[
            "display_name",
            "share_difference",
            "targets",
            "team_targets",
            "receiving_air_yards",
            "team_passing_air_yards",
            "games_observed",
        ],
        title=(
            f"{team} WR Target Share vs. "
            f"Air-Yard Share — {season}"
        ),
    )

    figure.update_traces(
        textposition="top center",
        textfont={
            "size": 12,
            "color": "#9CA3AF",
        },
        cliponaxis=False,
        marker={
            "size": 10,
            "color": "#2563EB",
            "opacity": 0.85,
            "line": {
                "width": 1,
                "color": "white",
            },
        },
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Air-Yard Share: %{x:.1%}<br>"
            "Target Share: %{y:.1%}<br>"
            "Air-Yard Share minus Target Share: "
            "%{customdata[1]:.1%}<br>"
            "Targets: %{customdata[2]:,.0f}<br>"
            "Team Targets: %{customdata[3]:,.0f}<br>"
            "Receiving Air Yards: %{customdata[4]:,.0f}<br>"
            "Team Passing Air Yards: "
            "%{customdata[5]:,.0f}<br>"
            "Games Observed: %{customdata[6]:,.0f}"
            "<extra></extra>"
        ),
    )

    # --------------------------------------------------
    # Update plot
    # --------------------------------------------------
    figure.update_layout(
        template="plotly_white",
        height=525,
        showlegend=False,
        margin={
            "l": 60,
            "r": 40,
            "t": 100,
            "b": 60,
        },
    )

    figure.update_xaxes(
        title="Air-Yard Share",
        tickformat=".0%",
        range=[
            axis_min,
            axis_max,
        ],
        showgrid=True,
        # gridcolor="#E5E7EB",
        # gridwidth=1,
        zeroline=True,
        zerolinewidth=1,
        zerolinecolor="#9CA3AF",
        constrain="domain",
    )

    figure.update_yaxes(
        title="Target Share",
        tickformat=".0%",
        range=[
            axis_min,
            axis_max,
        ],
        showgrid=True,
        # gridcolor="#E5E7EB",
        # gridwidth=1,
        zeroline=True,
        zerolinewidth=1,
        zerolinecolor="#9CA3AF",
        scaleanchor="x",
        scaleratio=1,
        constrain="domain",
    )

    return figure


def create_target_depth_distribution_figure(
    receiver_target_depth_df: pd.DataFrame,
    team: str,
    season: int,
) -> go.Figure:
    """
    Create a horizontal box plot of game-level receiver aDOT values.

    Each point represents one qualifying player-week. Because the
    current Gold data has one observed game per player-week, each
    point currently represents one game.

    Gold diamonds show target-weighted season aDOT.
    """
    required_columns = {
        "player_id",
        "display_name",
        "week",
        "targets",
        "receiving_air_yards",
        "games_observed",
        "average_depth_of_target",
        "season_targets",
        "season_receiving_air_yards",
        "season_games_observed",
        "games_with_defined_adot",
        "season_average_depth_of_target",
        "team_wr_average_depth_of_target",
    }

    missing_columns = required_columns.difference(
        receiver_target_depth_df.columns
    )

    # -----------------------------
    # Quality and validations
    # -----------------------------
    if missing_columns:
        raise ValueError(
            "Cannot create target-depth distribution figure. "
            f"Missing columns: {sorted(missing_columns)}"
        )

    if receiver_target_depth_df.empty:
        raise ValueError(
            "Cannot create target-depth distribution figure "
            "from an empty DataFrame."
        )

    # Create reader-friendly names without modifying the
    # authoritative analytical DataFrame.
    plot_df = receiver_target_depth_df.rename(
        columns={
            "average_depth_of_target": "Game aDOT",
            "season_average_depth_of_target": "Season aDOT",
            "team_wr_average_depth_of_target": "Team WR aDOT",
        }
    )

    plot_df = plot_df.dropna(
        subset=[
            "Game aDOT",
            "Season aDOT",
        ]
    )

    if plot_df.empty:
        raise ValueError(
            "Cannot create target-depth distribution figure "
            "because all aDOT values are missing."
        )

    # One row per receiver for the weighted season-aDOT markers.
    receiver_summary_df = (
        plot_df[
            [
                "player_id",
                "display_name",
                "Season aDOT",
                "season_targets",
                "season_receiving_air_yards",
                "season_games_observed",
                "games_with_defined_adot",
            ]
        ]
        .drop_duplicates(
            subset=["player_id"]
        )
        .sort_values(
            ["Season aDOT", "display_name"],
            ascending=[False, True],
        )
        .reset_index(drop=True)
    )

    player_order = receiver_summary_df[
        "display_name"
    ].tolist()

    # The input remains in its natural player-week format.
    # No wide-to-long conversion is necessary.
    figure = px.box(
        plot_df,
        x="Game aDOT",
        y="display_name",
        orientation="h",
        points="all",
        category_orders={
            "display_name": player_order,
        },
        color_discrete_sequence=[
            "#93C5FD",
        ],
        labels={
            "display_name": "Receiver",
            "Game aDOT": "Average Depth of Target",
            "week": "Week",
            "targets": "Game Targets",
            "receiving_air_yards": "Game Air Yards",
            "games_observed": "Games Observed",
            "Season aDOT": "Season aDOT",
        },
        hover_data={
            "week": True,
            "targets": True,
            "receiving_air_yards": True,
            "games_observed": True,
            "Season aDOT": ":.1f",
            "player_id": False,
        },
        title=f"{team} WR Weekly aDOT Distribution — {season}",
    )

    figure.update_traces(
        name="Weekly aDOT distribution",
        showlegend=True,
        boxpoints="all",
        jitter=0.25,
        pointpos=0,
        fillcolor="rgba(147, 197, 253, 0.45)",
        line={
            "color": "#2563EB",
            "width": 2,
        },
        marker={
            "color": "#2563EB",
            "size": 6,
            "opacity": 0.70,
            "line": {
                "color": "white",
                "width": 0.5,
            },
        },
    )

    # Overlay each player's target-weighted season aDOT.
    figure.add_trace(
        go.Scatter(
            x=receiver_summary_df["Season aDOT"],
            y=receiver_summary_df["display_name"],
            mode="markers",
            name="Season aDOT",
            marker={
                "symbol": "diamond",
                "size": 12,
                "color": "#F59E0B",
                "line": {
                    "color": "white",
                    "width": 1,
                },
            },
            customdata=receiver_summary_df[
                [
                    "season_targets",
                    "season_receiving_air_yards",
                    "season_games_observed",
                    "games_with_defined_adot",
                ]
            ],
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Season aDOT: %{x:.1f} yards<br>"
                "Season Targets: %{customdata[0]:,.0f}<br>"
                "Season Air Yards: %{customdata[1]:,.0f}<br>"
                "Games Observed: %{customdata[2]:,.0f}<br>"
                "Games with Defined aDOT: %{customdata[3]:,.0f}"
                "<extra></extra>"
            ),
        )
    )

    # Add the target-weighted team WR reference line.
    team_average_values = (
        plot_df["Team WR aDOT"]
        .dropna()
        .unique()
    )

    if len(team_average_values) > 0:
        team_wr_average = team_average_values[0]

        figure.add_vline(
            x=team_wr_average,
            line_width=2,
            line_dash="dash",
            line_color="#6B7280",
            annotation_text=(
                f"Team WR aDOT: {team_wr_average:.1f}"
            ),
            annotation_position="top right",
            annotation_font_color="#4B5563",
        )

    figure.update_layout(
        template="plotly_white",
        height=max(
            450,
            75 + 50 * len(receiver_summary_df),
        ),
        legend_title_text="",
        legend_orientation="h",
        legend_yanchor="bottom",
        legend_y=1.02,
        legend_xanchor="left",
        legend_x=0,
        margin={
            "l": 20,
            "r": 50,
            "t": 100,
            "b": 50,
        },
    )

    figure.update_xaxes(
        title="Average Depth of Target (yards)",
        rangemode="tozero",
        showgrid=True
    )

    # Plotly categorical y-axis arrays run from bottom to top.
    # Reverse the order so the highest season aDOT appears on top.
    figure.update_yaxes(
        title=None,
        categoryorder="array",
        categoryarray=player_order[::-1],
    )

    return figure


def create_receiver_role_map_figure(
    receiver_role_map_df: pd.DataFrame,
    team: str,
    season: int,
) -> go.Figure:
    """
    Create a receiver role map using aDOT and Target Share.

    X-axis:
        Average Depth of Target

    Y-axis:
        Target Share

    Bubble size:
        Targets/Game

    Bubble color:
        Air-Yard Share
    """
    required_columns = {
        "player_id",
        "display_name",
        "targets",
        "team_targets",
        "receiving_air_yards",
        "team_passing_air_yards",
        "games_observed",
        "target_share",
        "air_yards_share",
        "average_depth_of_target",
        "targets_per_game",
        "team_wr_average_depth_of_target",
        "displayed_receiver_median_target_share",
    }

    missing_columns = required_columns.difference(
        receiver_role_map_df.columns
    )

    # -----------------------------
    # Quality and validations
    # -----------------------------
    if missing_columns:
        raise ValueError(
            "Cannot create receiver role map figure. "
            f"Missing columns: {sorted(missing_columns)}"
        )

    if receiver_role_map_df.empty:
        raise ValueError(
            "Cannot create receiver role map figure "
            "from an empty DataFrame."
        )

    plot_df = receiver_role_map_df.dropna(
        subset=[
            "target_share",
            "average_depth_of_target",
            "targets_per_game",
            "air_yards_share",
        ]
    ).copy()

    if plot_df.empty:
        raise ValueError(
            "Cannot create receiver role map figure because "
            "all role-map metrics are missing."
        )

    # -----------------------------
    # Plot
    # -----------------------------
    figure = px.scatter(
        plot_df,
        x="average_depth_of_target",
        y="target_share",
        size="targets_per_game",
        color="air_yards_share",
        text="display_name",
        size_max=34,
        color_continuous_scale=[
            "#DBEAFE",
            "#60A5FA",
            "#2563EB",
            "#1E3A8A",
        ],
        labels={
            "average_depth_of_target": (
                "Average Depth of Target"
            ),
            "target_share": "Target Share",
            "targets_per_game": "Targets/Game",
            "air_yards_share": "Air-Yard Share",
            "display_name": "Receiver",
        },
        custom_data=[
            "display_name",
            "targets_per_game",
            "air_yards_share",
            "targets",
            "team_targets",
            "receiving_air_yards",
            "team_passing_air_yards",
            "games_observed",
        ],
        title=f"{team} WR Role Map — {season}",
    )

    figure.update_traces(
        textposition="top center",
        textfont={
            "size": 12,
            "color": "#9CA3AF",
        },
        marker={
            "opacity": 0.85,
            "line": {
                "width": 1,
                "color": "white",
            },
        },
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "aDOT: %{x:.1f} yards<br>"
            "Target Share: %{y:.1%}<br>"
            "Targets/Game: %{customdata[1]:.1f}<br>"
            "Air-Yard Share: %{customdata[2]:.1%}<br>"
            "Targets: %{customdata[3]:,.0f}<br>"
            "Team Targets: %{customdata[4]:,.0f}<br>"
            "Receiving Air Yards: %{customdata[5]:,.0f}<br>"
            "Team Passing Air Yards: "
            "%{customdata[6]:,.0f}<br>"
            "Games Observed: %{customdata[7]:,.0f}"
            "<extra></extra>"
        ),
    )

    # aDOT is now on the x-axis, so the team WR aDOT
    # reference becomes a vertical line.
    # team_average_values = (
    #     plot_df["team_wr_average_depth_of_target"]
    #     .dropna()
    #     .unique()
    # )

    # if len(team_average_values) > 0:
    #     team_wr_average = team_average_values[0]

    #     figure.add_vline(
    #         x=team_wr_average,
    #         line_width=2,
    #         line_dash="dash",
    #         line_color="#F59E0B",
    #         annotation_text=(
    #             f"Team WR aDOT: {team_wr_average:.1f}"
    #         ),
    #         annotation_position="top right",
    #         annotation_font_color="#B45309",
    #     )

    # Target Share is now on the y-axis, so its median
    # reference becomes a horizontal line.
    # median_target_share_values = (
    #     plot_df["displayed_receiver_median_target_share"]
    #     .dropna()
    #     .unique()
    # )

    # if len(median_target_share_values) > 0:
    #     median_target_share = median_target_share_values[0]

    #     figure.add_hline(
    #         y=median_target_share,
    #         line_width=1.5,
    #         line_dash="dot",
    #         line_color="#6B7280",
    #         annotation_text=(
    #             "Displayed WR median: "
    #             f"{median_target_share:.1%}"
    #         ),
    #         annotation_position="top left",
    #         annotation_font_color="#4B5563",
    #     )

    figure.update_layout(
        template="plotly_white",
        height=525,
        showlegend=False,
        margin={
            "l": 60,
            "r": 40,
            "t": 100,
            "b": 60,
        },
        coloraxis_colorbar={
            "title": {
                "text": "Air-Yard<br>Share",
            },
            "tickformat": ".0%",
        },
    )

    figure.update_xaxes(
        title="Average Depth of Target (yards)",
        rangemode="tozero",
        showgrid=True,
        zeroline=True,
        zerolinewidth=1,
        zerolinecolor="#9CA3AF",
    )

    figure.update_yaxes(
        title="Target Share",
        tickformat=".0%",
        rangemode="tozero",
        showgrid=True,
        zeroline=True,
        zerolinewidth=1,
        zerolinecolor="#9CA3AF",
    )

    return figure