import pandas as pd
from thefuzz import process

from services.mysql import get_data
from services.cartola_api import CartolaFCAPI

columns = [
    "Team",
    "Stats_MP as Matches_Played",
    "Stats_Min as Minutes",
    "Stats_Gls as Goals",
    "Stats_Ast as Assists",
    "Stats_PK as Penalties_Scored",
    "Stats_PKatt as Penalties_Attempted",
    "Stats_CrdY as Yellow_Cards",
    "Stats_CrdR as Red_Cards",
    "Stats_xG as xG",
    "Shooting_Sh as Shots",
    "Shooting_SoT as Shots_On_Target",
    "Passing_types_Att as Passes_Attempted",
    "Passing_types_Cmp as Passes_Completed",
    "Defense_Tkl as Tackles",
    "Defense_TklW as Tackles_Won",
    "Misc_Fls as Fouls",
    "Misc_Fld as Fouls_Drawn",
    "Misc_Off as Offsides",
    "Misc_PKwon as PK_Won",
    "Misc_PKcon as PK_Conceded",
    "Misc_OG as Own_Goals",
]


def get_season_where_clause(season):
    return f"season = {season}"


def get_clean_sheet_info(teams_df, team):
    team_filtered = teams_df[teams_df["Team"] == team].iloc[0]
    return team_filtered["Clean_Sheets"]


def create_base_scoring_columns(row):
    # Attack Scoring
    row["Goals_Score"] = row["Goals"] * 8
    row["Assists_Score"] = row["Assists"] * 5
    row["Shots_On_Target_Score"] = (row["Shots_On_Target"] - row["Goals"]) * 1.2
    row["Shots_Off_Target_Score"] = (row["Shots"] - row["Shots_On_Target"]) * 0.8
    row["Fouls_Drawn_Score"] = row["Fouls_Drawn"] * 0.5
    row["PK_Won_Score"] = row["PK_Won"]
    row["PK_Missed_Score"] = -(row["Penalties_Attempted"] - row["Penalties_Scored"]) * 4
    row["Offsides_Score"] = -row["Offsides"] * 0.1

    # Defense Scoring
    row["Tackles_Score"] = (row["Tackles_Won"] - row["Tackles"]) * 1.5
    row["Own_Goals_Score"] = -row["Own_Goals"] * 3
    row["Red_Cards_Score"] = -row["Red_Cards"] * 3
    row["Yellow_Cards_Score"] = -row["Yellow_Cards"] * 3
    row["Fouls_Score"] = -row["Fouls"] * 0.3
    row["PK_Conceded_Score"] = -row["PK_Conceded"]

    return row


def create_team_scoring_columns(row):
    row = create_base_scoring_columns(row)

    row["Clean_Sheet_Score"] = row["Clean_Sheets"] * 5

    total_score = sum([row[col] for col in row.index if "Score" in col])
    row["Total_Score"] = total_score
    row["Total_Score_Match"] = total_score / row["Matches_Played"]

    return row


def get_next_opponent_score_match(team, next_matches: pd.DataFrame):
    for _, match in next_matches.iterrows():
        if team == match["Home_Team"]:
            return match["Away_Team"], match["Away_Team_Score_Match"]
        elif team == match["Away_Team"]:
            return match["Home_Team"], match["Home_Team_Score_Match"]

    return None, None


def create_player_scoring_columns(row, teams_df, next_matches_df):
    row = create_base_scoring_columns(row)

    if row["Position"] == "DF":
        row["Clean_Sheet_Score"] = (
            min((get_clean_sheet_info(teams_df, row["Team"]), row["Matches_Played"]))
            * 5
        )

    total_score = sum([row[col] for col in row.index if "Score" in col])
    row["Total_Score"] = total_score
    row["Total_Score_Match"] = total_score / row["Matches_Played"]

    if next_matches_df:
        row["Next_Opponent"], row["Next_Opponent_Score_Match"] = (
            get_next_opponent_score_match(row["Team"], next_matches_df)
        )

    return row


def get_cartola_fc_teams_data(season):
    where_clause = get_season_where_clause(season)

    teams_columns = ["Keepers_CS as Clean_Sheets"]

    teams = get_data(
        "overall_teams", columns=columns + teams_columns, where_clause=where_clause
    )

    teams = teams.apply(create_team_scoring_columns, axis=1)

    return teams.sort_values(by="Total_Score_Match", ascending=False)


def get_cartola_fc_players_data(season, teams_df, next_matches_df):
    where_clause = get_season_where_clause(season)

    players_columns = ["Name", "Position"]

    players = get_data(
        "overall_players", columns=players_columns + columns, where_clause=where_clause
    )

    players = players.apply(
        lambda x: create_player_scoring_columns(x, teams_df, next_matches_df), axis=1
    )

    info_cols = ["Name", "Position", "Team"]
    remaining_cols = [col for col in players.columns if col not in info_cols]

    players = players[info_cols + remaining_cols]

    players.fillna(0, inplace=True)

    return players.sort_values(by="Total_Score_Match", ascending=False)


def find_best_match(teams_df, search_team, score_cutoff=70):
    choices = teams_df["Team"].dropna().astype(str).tolist()
    match, _ = process.extractOne(search_team, choices, score_cutoff=score_cutoff)

    if match:
        return teams_df[teams_df["Team"] == match].iloc[0]
    else:
        return None


def format_cartola_matches_api_response(teams_df):
    cartola_api = CartolaFCAPI()

    matches_response = cartola_api.get_matches()

    print("Matches response", matches_response)

    if matches_response.get("code") == "1":
        return None

    teams = matches_response["clubes"]
    matches = matches_response["partidas"]

    matches_formatted = []
    for m in matches:
        home_team = find_best_match(
            teams_df, teams[str(m["clube_casa_id"])]["nome_fantasia"]
        )
        away_team = find_best_match(
            teams_df, teams[str(m["clube_visitante_id"])]["nome_fantasia"]
        )

        match_formatted = {
            "Home_Team": home_team["Team"],
            "Away_Team": away_team["Team"],
            "Home_Team_Score_Match": home_team["Total_Score_Match"],
            "Away_Team_Score_Match": away_team["Total_Score_Match"],
        }

        matches_formatted.append(match_formatted)

    return pd.DataFrame(matches_formatted)
