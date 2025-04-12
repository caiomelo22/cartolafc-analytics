from services.mysql import get_data

columns = [
    "Team", "Stats_MP as Matches_Played",
    "Stats_Min as Minutes", "Stats_Gls as Goals", "Stats_Ast as Assists",
    "Stats_PK as Penalties_Scored", "Stats_PKatt as Penalties_Attempted",
    "Stats_CrdY as Yellow_Cards", "Stats_CrdR as Red_Cards", "Stats_xG as xG",
    "Shooting_Sh as Shots", "Shooting_SoT as Shots_On_Target",
    "Passing_types_Att as Passes_Attempted", "Passing_types_Cmp as Passes_Completed",
    "Defense_Tkl as Tackles", "Defense_TklW as Tackles_Won",
    "Misc_Fls as Fouls", "Misc_Fld as Fouls_Drawn", "Misc_Off as Offsides",
    "Misc_PKwon as PK_Won", "Misc_PKcon as PK_Conceded", "Misc_OG as Own_Goals",
]

def get_season_where_clause(season):
    return f"season = {season}"

def get_cartola_fc_teams_data(season):
    where_clause = get_season_where_clause(season)

    teams = get_data('overall_teams', columns=columns, where_clause=where_clause)

    return teams

def get_cartola_fc_players_data(season):
    where_clause = get_season_where_clause(season)

    players_columns = ["Name", "Position"]

    players = get_data('overall_players', columns=players_columns+columns, where_clause=where_clause)

    return players
