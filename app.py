import streamlit as st
import altair as alt

from helpers.cartola_data import (
    format_cartola_matches_api_response,
    get_cartola_fc_players_data,
    get_cartola_fc_teams_data,
)

season = 2025

st.set_page_config(layout="wide")

st.title("Cartola FC Analytics")

teams = get_cartola_fc_teams_data(season)

next_matches = format_cartola_matches_api_response(teams)

players = get_cartola_fc_players_data(season, teams, next_matches)

col1, col2 = st.columns(2)

with col1:
    st.header("Teams")
    st.dataframe(teams, use_container_width=True)

with col2:
    st.header("Players")
    st.dataframe(players, use_container_width=True)

st.header("Next Matches Analysis")
st.dataframe(next_matches, use_container_width=True)

st.subheader("Player Analysis")
# st.scatter_chart(players[["Total_Score_Match", "Next_Opponent_Score_Match"]])
chart = (
    alt.Chart(players)
    .mark_circle(size=60)
    .encode(
        x=alt.X("Total_Score_Match", axis=alt.Axis(title="Score/Match")),
        y=alt.Y(
            "Next_Opponent_Score_Match", axis=alt.Axis(title="Opponent Score/Match")
        ),
        tooltip=[
            "Name",
            "Team",
            "Next_Opponent",
            "Total_Score_Match",
            "Next_Opponent_Score_Match",
        ],
    )
    .interactive()
)

st.altair_chart(chart, use_container_width=True)
