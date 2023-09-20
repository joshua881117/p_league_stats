from pydantic import BaseModel
import importlib

import pandas as pd

class PLeagueYearStats(BaseModel):
    name: str
    number: str
    team: str
    games: int
    playing_seconds: int
    two_points_field_goals_made: int 
    two_points_field_goals_attempt: int
    three_points_field_goals_made: int
    three_points_field_goals_attempt: int
    free_throws_made: int
    free_throws_attempt: int
    points: int
    offense_rebounds: int
    defense_rebounds: int
    assists: int
    steals: int
    blocks: int
    turnovers: int
    personal_fouls: int

class PLeagueGameStats(BaseModel):
    points: int
    oncourt_plus_minus: int
    seconds: int
    starter: int
    turnover: int
    ast: int
    blk: int
    reb_d: int
    ft_m: int
    reb_o: int
    pfoul: int
    player_id: int
    number: str
    stl: int
    trey_m: int
    two_m: int
    two_a: int
    trey_a: int
    ft_a: int
    team_id: int
    game_id: int
    
def check_schema(df: pd.DataFrame, dataset: str) -> pd.DataFrame:
    """檢查資料型態, 確保每次要上傳資料庫前, 型態正確"""
    df_dict = df.to_dict("records")
    schema = getattr(importlib.import_module("stats.schema.dataset"), dataset)
    df_schema = [schema(**dd).__dict__ for dd in df_dict]
    df = pd.DataFrame(df_schema)
    return df