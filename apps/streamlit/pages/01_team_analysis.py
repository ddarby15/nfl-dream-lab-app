import streamlit as st

from src.data.load_data import load_gold_data
from src.analytics.team_wr import (
    prepare_receiver_opportunity_volume,
    prepare_receiver_role_shares,
    prepare_receiver_target_depth_distribution,
    prepare_receiver_role_map,
)
from src.charts.team_wr import (
    create_opportunity_volume_figure,
    create_receiver_role_figure,
    create_target_depth_distribution_figure,
    create_receiver_role_map_figure,
)

# -----------------------------
# Header
# -----------------------------
st.title("Team Analysis")
st.caption("Analyze an individual team")

# -----------------------------
# Load & validate Data
# -----------------------------
team_metrics_df = load_gold_data("team_week_metrics")             # team week-to-week stats
receiving_games_df = load_gold_data("receiving_player_game")      # receiver week-to-week stats
receiving_std_df = load_gold_data("receiving_player_team_season") # receiver season-to-date stats


# -----------------------------
# Sidebar Filters
# -----------------------------
# start with a copy of the full dataset. This will be drilled down to our final team data depending on filter selections
selected_team_receiving_std_df = receiving_std_df.copy()

with st.sidebar:
    # Get filter options & Implement Cascading Filters feature
    st.title("Filters")

    # Build season options from initial dataframe
    season_options = [*sorted(selected_team_receiving_std_df["season"].dropna().unique(), reverse=True)]
    selected_season = st.selectbox("Season", options=season_options)
    
    # update available teams dataframe from selected season
    selected_team_receiving_std_df = selected_team_receiving_std_df.loc[selected_team_receiving_std_df["season"] == selected_season]
    debug_season_df = selected_team_receiving_std_df.copy() # debug temp df
    
    # Build team options from remaining rows
    team_options = [*sorted(selected_team_receiving_std_df["team"].dropna().unique())]
    selected_team = st.selectbox("Team", options=team_options)
    
    # update available teams dataframe from selected team
    selected_team_receiving_std_df = selected_team_receiving_std_df.loc[selected_team_receiving_std_df["team"] == selected_team]
    debug_team_df = selected_team_receiving_std_df.copy() # debug temp df


# -----------------------------
# Body
# -----------------------------

# METRICS SECTION
metrics_section = st.container(horizontal=True, border=False)

# get metrics data
season_metrics_df = team_metrics_df.loc[team_metrics_df["season"].eq(selected_season) & team_metrics_df["season_type"].eq("REG")] # for league average calculations
selected_team_metrics_df = season_metrics_df.loc[season_metrics_df["team"].eq(selected_team)]

if selected_team_metrics_df.empty:
    st.warning("No completed games found for this team and season.")
    st.stop()

# compute primary metrics
offensive_plays = selected_team_metrics_df["offensive_plays"].sum()
defensive_plays = selected_team_metrics_df["defensive_plays_faced"].sum()

offensive_epa_per_play = (selected_team_metrics_df["offensive_epa_sum"].sum() / offensive_plays)
defensive_epa_per_play_allowed = (selected_team_metrics_df["defensive_epa_allowed_sum"].sum() / defensive_plays)
offensive_success_rate = (selected_team_metrics_df["offensive_successful_plays"].sum() / offensive_plays)
offensive_explosive_play_rate = (selected_team_metrics_df["offensive_explosive_plays"].sum() / offensive_plays)

# compute delta vs league averages
league_offensive_plays = season_metrics_df["offensive_plays"].sum()
league_defensive_plays = season_metrics_df["defensive_plays_faced"].sum()

league_offensive_epa_per_play = (season_metrics_df["offensive_epa_sum"].sum() / league_offensive_plays)
league_defensive_epa_per_play_allowed = (season_metrics_df["defensive_epa_allowed_sum"].sum() / league_defensive_plays)
league_success_rate = (season_metrics_df["offensive_successful_plays"].sum() / league_offensive_plays)
league_explosive_play_rate = (season_metrics_df["offensive_explosive_plays"].sum() / league_offensive_plays)

with metrics_section:
    st.metric("Offense EPA Per Play", help="Measures the total scoring value an offense creates on average per snap. Higher (or positive) numbers mean a stronger offense.", 
              value=f"{offensive_epa_per_play:+.3f}", 
              delta=f"{offensive_epa_per_play - league_offensive_epa_per_play:+.3f} vs league", 
              border=True)
    st.metric("Defense EPA Per Play", help="Measures how many expected points a defense allows per play. Lower (or negative) numbers mean a stronger defense.", 
              value=f"{defensive_epa_per_play_allowed:+.3f}", 
              delta=f"{defensive_epa_per_play_allowed - league_defensive_epa_per_play_allowed:+.3f} vs league", 
              delta_color="inverse", 
              border=True)
    st.metric("Success Rate", help="The percentage of plays that generate a positive EPA (EPA > 0). While EPA per play captures big-play magnitude, Success Rate measures down-to-down consistency.",
              value=f"{offensive_success_rate:.1%}", 
              delta=f"{(offensive_success_rate - league_success_rate) * 100:+.1f} pp vs league", 
              border=True)
    st.metric("Explosive-Play Rate", help="The frequency of high-impact gains (runs of 12+ yards or passes of 16+ yards) that heavily spike EPA and scoring probability", 
              value=f"{offensive_explosive_play_rate:.1%}", 
              delta=f"{(offensive_explosive_play_rate - league_explosive_play_rate) * 100:+.1f} pp vs league", 
              border=True)

# VISUALIZATION SECTION
tab1, tab2, tab3, tab4 = st.tabs(["Receiving", "Rushing", "Passing", "Overview"])

with tab1:
    st.caption("Compare receiving players within a selected team")
    viz_section = st.container(horizontal=False, border=True)
    with viz_section:
        # position selection - receiving
        position_options = [*sorted(selected_team_receiving_std_df["position"].dropna().unique())]
        selected_positions = st.pills("Select Positions", options=position_options, default=position_options, selection_mode="multi", key="receiving_positions")
        
        # update available teams dataframe from selected position
        if not selected_positions:
            st.info("Select at least one position to display.")
            st.stop()
        selected_team_receiving_std_df = selected_team_receiving_std_df.loc[selected_team_receiving_std_df["position"].isin(selected_positions)]
        
        # This is where we can finally update the selected team dataframe
        first_row_left, first_row_right = st.columns(2, border=True)
        with first_row_left:
            # Receiver role map plot
            receiver_role_map_df = prepare_receiver_role_map(selected_team_receiving_std_df, minimum_targets=5)
            receiver_role_map_figure = create_receiver_role_map_figure(
                receiver_role_map_df,
                team=selected_team,
                season=selected_season,
            )
            st.plotly_chart(receiver_role_map_figure, width="stretch", key="receiver_role_map_chart")
            st.caption(
                "Bubble size represents Targets/Game. Bubble color represents "
                "Air-Yard Share. Reference lines show the team WR aDOT and "
                "the median Target Share among displayed receivers."
            )
        
        with first_row_right:
            # opportunity volume plot
            receiver_opportunity_df = prepare_receiver_opportunity_volume(selected_team_receiving_std_df, minimum_targets=5)
            opportunity_volume_figure = create_opportunity_volume_figure(
                receiver_opportunity_df,
                team=selected_team,
                season=selected_season,
            )
            st.plotly_chart(opportunity_volume_figure, width="stretch", key="opportunity_chart")
            
        second_row_left, second_row_right = st.columns(2, border=True)
        with second_row_left:
            # weekly aDot distribution
            receiver_target_depth_df = prepare_receiver_target_depth_distribution(receiving_games_df, selected_team_receiving_std_df, minimum_season_targets=5)
            target_depth_figure = create_target_depth_distribution_figure(
                receiver_target_depth_df,
                team=selected_team,
                season=selected_season,
            )
            st.plotly_chart(target_depth_figure, width="stretch", key="target_depth_chart")
            st.caption(
                "Each blue point is one player-week with at least 5 targets. "
                "Gold diamonds show target-weighted season aDOT."
            )

        with second_row_right:
            # Receiver role-share plot
            receiver_roles_df = prepare_receiver_role_shares(selected_team_receiving_std_df, minimum_targets=5)
            receiver_role_figure = create_receiver_role_figure(
                receiver_roles_df,
                team=selected_team,
                season=selected_season,
            )
            st.plotly_chart(receiver_role_figure, width="stretch", key="role_chart")

with tab2:
    st.caption("Compare rushing players within a selected team")
    with st.expander("Advanced settings"):
        st.slider("Threshold", 0.0, 1.0, 0.5)
        
with tab3:
    st.caption("Compare passing players within a selected team")
    col1, col2 = st.columns(2)
    col1.metric("Users", "1,204")
    col2.metric("Revenue", "$12K")

with tab3:
    st.caption("High level team overview")
    col1, col2 = st.columns(2)
    col1.metric("Users", "1,204")
    col2.metric("Revenue", "$12K")

# -----------------------------
# Debug Tables
# -----------------------------
st.markdown(
    """
    ## **Notes:**  
    - Team Metric cards: Team WR efficiency (Receptions/Targets), Team Season aDot, Offensive EPA/Play, Defensive EPA/Play, Net EPA, Success Rate, Explosive-Play Rate   
    - Add Top 10 most team targets per game (to identify high volume passing teams)
    - Opportunity Volume plot: Add league average horizontal line.
    - Offensive Roles plot: Don't really like this visual. Explore WOPR instead.    
    Analysts combine a player's target share and air yards share into a single metric called WOPR.   
    Calculated as 1.5 × Target Share + 0.7 × Air Yards Share,  to quantify elite, sustainable usage.
    - Weekly aDot Distribution: Clean up hover data. Too many metrics in there makes it feel cluttered. Narrow down to most important.
    - Role Map: Clean up hover data. 
    - Role Map: For hover data, verify team target counts 
    - Role Map: Add "WR1 Target Share" horizontal level. Remove "Displayed WR median" level
    - Role Map: Add short, medium, deep aDot vertical ranges/levels. Remove "Team WR aDot" level
    
    """
            
)

# st.dataframe(team_metrics_df)
# st.dataframe(receiving_seasons_df)
# st.dataframe(receiving_games_df)


# st.markdown(f"### Debug: Selected Season: {selected_season}, Team: {selected_team}, Position: {selected_position}")
# st.markdown(f"Rows: {debug_season_df.shape[0]}")

# st.markdown(f"### Debug: Selected Season: {selected_season}, Team: {selected_team}, Position: {selected_position}")
# st.markdown(f"Rows: {debug_team_df.shape[0]}")
# st.dataframe(debug_team_df)

# st.markdown(f"### Debug: Selected Season: {selected_season}, Team: {selected_team}, Position: {selected_position}")
# st.markdown(f"Rows: {debug_position_df.shape[0]}")
# st.dataframe(debug_position_df)