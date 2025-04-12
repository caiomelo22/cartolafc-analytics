import streamlit as st

from helpers.cartola_data import get_cartola_fc_players_data, get_cartola_fc_teams_data

season = 2025

st.set_page_config(layout="wide")

st.title("Cartola FC Analytics")

teams = get_cartola_fc_teams_data(season)
players = get_cartola_fc_players_data(season)

col1, col2 = st.columns(2)

with col1:
    st.header("Teams")
    st.dataframe(teams, use_container_width=True)

with col2:
    st.header("Players")
    st.dataframe(players, use_container_width=True)
