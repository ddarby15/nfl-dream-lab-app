import streamlit as st

from src.data.load_data import load_gold_data


# -----------------------------
# Header
# -----------------------------
st.title("NFL Dream Lab 🏈")
st.caption("NFL Player Performance Analytics")
    
    
# -----------------------------
# Load & validate Data
# -----------------------------
wr_week_df = load_gold_data()


# -----------------------------
# Sidebar
# -----------------------------

# start with a copy of the full dataset. This will be drilled down to our final player data depending on filter selections
available_players_df = wr_week_df.copy()

with st.sidebar:
    # Get filter options & Implement Cascading Filters feature
    st.title("Filters")

    # Build season options from initial dataframe
    season_options = [*sorted(available_players_df["season"].dropna().unique(), reverse=True)]
    selected_season = st.selectbox("Season", options=season_options)
    
    # update available players dataframe from selected season
    available_players_df = available_players_df.loc[available_players_df["season"] == selected_season]
    debug_season_df = available_players_df.copy() # debug temp df
    
    # Build team options from remaining rows
    team_options = ["All", *sorted(available_players_df["team"].dropna().unique())]
    selected_team = st.selectbox("Team", options=team_options)
    
    # update available players dataframe from selected team
    if selected_team != "All":
        available_players_df = available_players_df.loc[available_players_df["team"] == selected_team]
    debug_team_df = available_players_df.copy() # debug temp df
    
    # Build position options from remaining rows
    position_options = ["All", *sorted(available_players_df["position"].dropna().unique())]
    selected_position = st.selectbox("Position", options=position_options)
    
    # update available players dataframe from selected position
    if selected_position != "All":
        available_players_df = available_players_df.loc[available_players_df["position"] == selected_position]
    debug_position_df = available_players_df.copy() # debug temp df
    
    # Build player options from remaining rows
    player_options = sorted(available_players_df["display_name"].unique())
    selected_player = st.selectbox("Player Name", options=player_options)


# -----------------------------
# Select Data
# -----------------------------
player_df = wr_week_df.loc[(wr_week_df["display_name"] == selected_player) & (wr_week_df["season"] == selected_season)] \
                        .sort_values(by="week") \
                        .reset_index(drop=True).copy()

# -----------------------------
# Body
# -----------------------------

st.subheader("Current Role")
st.container(border=True).write("Latest-week metric cards")

st.subheader("Receiving Volume")
st.container(border=True).write("Targets and receptions by week")

st.subheader("Opportunity Share")
st.container(border=True).write("Target share and air-yard share by week")

st.subheader("Target Depth")
st.container(border=True).write("aDOT by week")

# detail table
st.markdown(f"Rows: {player_df.shape[0]}")
st.dataframe(player_df)

st.dataframe(wr_week_df)


# -----------------------------
# Debug Tables
# -----------------------------
# st.markdown(f"### Debug: Selected Season: {selected_season}, Team: {selected_team}, Position: {selected_position}, Player: {selected_player}")
# st.markdown(f"Rows: {debug_season_df.shape[0]}")
# st.dataframe(debug_season_df)

# st.markdown(f"### Debug: Selected Season: {selected_season}, Team: {selected_team}, Position: {selected_position}, Player: {selected_player}")
# st.markdown(f"Rows: {debug_team_df.shape[0]}")
# st.dataframe(debug_team_df)

# st.markdown(f"### Debug: Selected Season: {selected_season}, Team: {selected_team}, Position: {selected_position}, Player: {selected_player}")
# st.markdown(f"Rows: {debug_position_df.shape[0]}")
# st.dataframe(debug_position_df)
