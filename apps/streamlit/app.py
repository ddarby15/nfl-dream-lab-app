import streamlit as st


st.set_page_config(
    page_title="NFL Dream Lab",
    page_icon="🏈",
    layout="wide",
)

# define pages
team_page = st.Page("pages/01_team_analysis.py", title="Team Analysis", icon="🏟️", default=True)
player_page = st.Page("pages/02_player_analysis.py", title="Player Trends", icon="📈")


navigation = st.navigation(pages={"Navigation": [team_page, player_page]}, position="sidebar")

navigation.run()