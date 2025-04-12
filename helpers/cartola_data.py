from services.mysql import get_data

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


def create_scoring_columns(row, teams_df):
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
    if row["Position"] == "DF":
        row["Clean_Sheet_Score"] = get_clean_sheet_info(teams_df, row["Team"]) * 5

    total_score = sum([row[col] for col in row.index if "Score" in col])
    row["Total_Score"] = total_score

    return row


def get_cartola_fc_teams_data(season):
    where_clause = get_season_where_clause(season)

    teams_columns = ["Keepers_CS as Clean_Sheets"]

    teams = get_data(
        "overall_teams", columns=columns + teams_columns, where_clause=where_clause
    )

    return teams


def get_cartola_fc_players_data(season, teams_df):
    where_clause = get_season_where_clause(season)

    players_columns = ["Name", "Position"]

    players = get_data(
        "overall_players", columns=players_columns + columns, where_clause=where_clause
    )

    players = players.apply(lambda x: create_scoring_columns(x, teams_df), axis=1)

    info_cols = ["Name", "Position", "Team"]
    remaining_cols = [col for col in players.columns if col not in info_cols]

    players = players[info_cols + remaining_cols]

    players.fillna(0, inplace=True)

    return players.sort_values(by="Total_Score", ascending=False)
