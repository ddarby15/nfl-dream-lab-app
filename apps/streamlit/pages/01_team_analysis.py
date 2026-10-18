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
wr_week_df = load_gold_data()


# -----------------------------
# Sidebar Filters
# -----------------------------
# start with a copy of the full dataset. This will be drilled down to our final team data depending on filter selections
available_teams_df = wr_week_df.copy()

with st.sidebar:
    # Get filter options & Implement Cascading Filters feature
    st.title("Filters")

    # Build season options from initial dataframe
    season_options = [*sorted(available_teams_df["season"].dropna().unique(), reverse=True)]
    selected_season = st.selectbox("Season", options=season_options)
    
    # update available teams dataframe from selected season
    available_teams_df = available_teams_df.loc[available_teams_df["season"] == selected_season]
    debug_season_df = available_teams_df.copy() # debug temp df
    
    # Build team options from remaining rows
    team_options = [*sorted(available_teams_df["team"].dropna().unique())]
    selected_team = st.selectbox("Team", options=team_options)
    
    # update available teams dataframe from selected team
    available_teams_df = available_teams_df.loc[available_teams_df["team"] == selected_team]
    debug_team_df = available_teams_df.copy() # debug temp df
    
    # Build position options from remaining rows
    position_options = ["All", *sorted(available_teams_df["position"].dropna().unique())]
    selected_position = st.selectbox("Position", options=position_options)
    
    # update available teams dataframe from selected position
    if selected_position != "All":
        available_teams_df = available_teams_df.loc[available_teams_df["position"] == selected_position]
    debug_position_df = available_teams_df.copy() # debug temp df


# -----------------------------
# Prepare Data
# -----------------------------

# opportunity volume plot
receiver_opportunity_df = prepare_receiver_opportunity_volume(available_teams_df, minimum_targets=5)
opportunity_volume_figure = create_opportunity_volume_figure(
    receiver_opportunity_df,
    team=selected_team,
    season=selected_season,
)

# Receiver role map plot
receiver_role_map_df = prepare_receiver_role_map(available_teams_df, minimum_targets=5)
receiver_role_map_figure = create_receiver_role_map_figure(
    receiver_role_map_df,
    team=selected_team,
    season=selected_season,
)

# weekly aDot distribution
receiver_target_depth_df = (prepare_receiver_target_depth_distribution(available_teams_df, minimum_season_targets=5))
target_depth_figure = (
    create_target_depth_distribution_figure(
        receiver_target_depth_df,
        team=selected_team,
        season=selected_season,
    )
)

# Receiver role-share plot
receiver_roles_df = prepare_receiver_role_shares(available_teams_df, minimum_targets=5)
receiver_role_figure = create_receiver_role_figure(
    receiver_roles_df,
    team=selected_team,
    season=selected_season,
)

# -----------------------------
# Body
# -----------------------------

# metrics section
metrics_section = st.container(horizontal=True, border=False)
with metrics_section:
    st.metric("Offense EPA Per Play", help="Measures the total scoring value an offense creates on average per snap. Higher (or positive) numbers mean a stronger offense.", 
              value=10, delta="-1.2 from League Average", border=True)
    st.metric("Defense EPA Per Play", help="Measures how many expected points a defense allows per play. Lower (or negative) numbers mean a stronger defense.", 
              value=10, delta="1.2 from League Average", border=True)
    st.metric("Success Rate", help="The percentage of plays that generate a positive EPA (EPA > 0). While EPA per play captures big-play magnitude, Success Rate measures down-to-down consistency.",
              value=10, delta="1.2 from League Average", border=True)
    st.metric("Explosive-Play Rate", help="The frequency of high-impact gains (runs of 12+ yards or passes of 16+ yards) that heavily spike EPA and scoring probability", 
              value=10, delta="1.2 from League Average", border=True)

# visualizations section
tab1, tab2, tab3, tab4 = st.tabs(["Wide Receivers", "Running Backs", "Quarterbacks", "Overview"])

with tab1:
    st.caption("Compare wide receiver roles within a selected team.")
    viz_section = st.container(horizontal=False, border=True)
    with viz_section:
        first_row_left, first_row_right = st.columns(2, border=True)
        with first_row_left:
            st.plotly_chart(opportunity_volume_figure, width="stretch", key="opportunity_chart")

        with first_row_right:
            st.plotly_chart(receiver_role_map_figure, width="stretch", key="receiver_role_map_chart")
            st.caption(
                "Bubble size represents Targets/Game. Bubble color represents "
                "Air-Yard Share. Reference lines show the team WR aDOT and "
                "the median Target Share among displayed receivers."
            )
            
        second_row_left, second_row_right = st.columns(2, border=True)
        with second_row_left:
            st.plotly_chart(target_depth_figure, width="stretch", key="target_depth_chart")
            st.caption(
                "Each blue point is one player-week with at least 5 targets. "
                "Gold diamonds show target-weighted season aDOT."
            )

        with second_row_right:
            st.plotly_chart(receiver_role_figure, width="stretch", key="role_chart")

with tab2:
    with st.expander("Advanced settings"):
        st.slider("Threshold", 0.0, 1.0, 0.5)
        
with tab3:
    col1, col2 = st.columns(2)
    col1.metric("Users", "1,204")
    col2.metric("Revenue", "$12K")

with tab3:
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
# st.markdown(f"### Debug: Selected Season: {selected_season}, Team: {selected_team}, Position: {selected_position}")
# st.markdown(f"Rows: {debug_season_df.shape[0]}")
# st.dataframe(debug_season_df)

# st.markdown(f"### Debug: Selected Season: {selected_season}, Team: {selected_team}, Position: {selected_position}")
# st.markdown(f"Rows: {debug_team_df.shape[0]}")
# st.dataframe(debug_team_df)

# st.markdown(f"### Debug: Selected Season: {selected_season}, Team: {selected_team}, Position: {selected_position}")
# st.markdown(f"Rows: {debug_position_df.shape[0]}")
# st.dataframe(debug_position_df)