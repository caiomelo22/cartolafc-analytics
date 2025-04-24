import streamlit as st
import altair as alt
import pandas as pd

from helpers.cartola_data import (
    format_cartola_matches_api_response,
    get_cartola_fc_players_data,
    get_cartola_fc_teams_data,
)

season = 2025

st.set_page_config(layout="wide")

st.title("Cartola FC Analytics")

# Fetch and cache data only once using session state
if "teams" not in st.session_state:
    st.session_state.teams = get_cartola_fc_teams_data(season)

if "next_matches" not in st.session_state:
    st.session_state.next_matches = format_cartola_matches_api_response(
        st.session_state.teams
    )

if "players" not in st.session_state:
    st.session_state.players = get_cartola_fc_players_data(
        season,
        st.session_state.teams,
        st.session_state.next_matches,
    )

# Use session state variables
teams = st.session_state.teams
next_matches = st.session_state.next_matches
players = st.session_state.players

st.header("Teams")
st.dataframe(teams, use_container_width=True)

if isinstance(next_matches, pd.DataFrame):
    st.header("Next Matches Analysis")
    st.dataframe(next_matches, use_container_width=True)

    st.subheader("Player Analysis")

    position_options = ["DF", "MF", "FW"]

    selected_position = st.radio(
        "Select the position:", position_options, horizontal=True
    )

    if selected_position:
        players_filtered = players[
            players["Position"] == selected_position
        ].reset_index(drop=True)
    else:
        players_filtered = players.copy().reset_index(drop=True)

    chart = (
        alt.Chart(players_filtered)
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

    filtered_player_columns = [
        "Name",
        "Team",
        "Next_Opponent",
        "Matches_Played",
        "Next_Opponent_Score_Match",
        "Total_Score_Match",
        "Norm_Score_Match",
    ]

    st.markdown("Top Players by Position")
    st.dataframe(players_filtered[filtered_player_columns], use_container_width=True)
