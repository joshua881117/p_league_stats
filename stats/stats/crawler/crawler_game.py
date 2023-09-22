import datetime
import io
import sys
import time
import typing

import pandas as pd
import requests
from loguru import logger
from bs4 import BeautifulSoup
from stats.schema.dataset import check_schema
import stats.backend.db as db
import stats.backend.db.db_execute as db_execute
from sqlalchemy import engine

def pleague_header():
    """網頁瀏覽時, 所帶的 request header 參數, 模仿瀏覽器發送 request"""
    return {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.76",
        "content-type":"text/html; charset=UTF-8"
    }

def game_id_list(season: str) -> typing.List[int]:
    if season == '2020-21':
        return list(range(13, 13+48))
    elif season == '2021-22':
        return list(range(73, 73+90))

def convert_datatype(df: pd.DataFrame) -> pd.DataFrame:
    """留下必要欄位、轉換資料型態、欄位名稱"""
    df.drop(columns=['eff', 'efgp', 'profile_picture', 'name', 'position', 'tsp', 'ft_a', 'trey_a', 'two_a', 'ugp', 'mins',\
        'two_m_two', 'twop', 'trey_m_trey', 'treyp', 'ft_m_ft', 'ftp', 'reb'], inplace=True)
    df['starter'] = df['starter'].apply(lambda x: 1 if x == '〇' else 0)
    df.rename(columns={'name_alt':'name', 'positive':'oncourt_plus_minus', 'jersey':'number',\
        'two':'two_a', 'trey':'trey_a', 'ft':'ft_a'}, inplace=True)
    df[['points', 'oncourt_plus_minus', 'seconds', 'starter', 'turnover', 'ast', 'blk', 'reb_o', 'reb_d', 'ft_m', \
        'ft_a', 'pfoul', 'player_id', 'stl', 'trey_m', 'trey_a', 'two_m', 'two_a']] \
        = df[['points', 'oncourt_plus_minus', 'seconds', 'starter', 'turnover', 'ast', 'blk', 'reb_o', 'reb_d', 'ft_m', \
            'ft_a', 'pfoul', 'player_id', 'stl', 'trey_m', 'trey_a', 'two_m', 'two_a']].map(lambda x: 0 if x == '' else int(x))
    
    return df

def convert_raw_data_to_df(raw_data: typing.Dict, home_team_id: int, away_team_id: int) -> pd.DataFrame:
    """將 json 檔轉為 df"""
    df_home = pd.DataFrame(raw_data['home'])
    if len(df_home) == 0:
        return df_home
    df_home = convert_datatype(df_home.copy())
    df_home['team_id'] = home_team_id

    df_away = pd.DataFrame(raw_data['away'])
    df_away = convert_datatype(df_away.copy())
    df_away['team_id'] = away_team_id
    df = pd.concat([df_home, df_away])
    df = df.reset_index(drop=True)
    return df

def get_team_id(soup: BeautifulSoup, conn: engine.base.Connection):
    try:
        away_team = soup.find("div", "col-lg-7 col-12 text-right align-self-center").find("h6", "pb-0 mb-0 mt-2 fs14").\
            get_text().strip("\n ")
        home_team = soup.find("div", "col-lg-7 col-12 text-left align-self-center").find("h6", "pb-0 mb-0 mt-2 fs14").\
            get_text().strip("\n ")
        away_team_id = db_execute.search_data(f"team='{away_team}'", "id", "team_list", conn)
        home_team_id = db_execute.search_data(f"team='{home_team}'", "id", "team_list", conn)
        if len(away_team_id) == 0:
            data={'team':away_team_id}
            df = pd.DataFrame(data=data, index=[0])
            db_execute.upload_data(df, 'team_list', conn)
            away_team_id = db_execute.search_data(f"team='{away_team}'", "id", "team_list", conn)
        if len(home_team_id) == 0:
            data={'team':home_team_id}
            df = pd.DataFrame(data=data, index=[0])
            db_execute.upload_data(df, 'team_list', conn)
            home_team_id = db_execute.search_data(f"team='{home_team}'", "id", "team_list", conn)
        return home_team_id[0][0], away_team_id[0][0]
    except Exception as e:
        logger.info(e)
        return False
    
def get_game_id(season: str, game: int, home_team_id: int, away_team_id: int, conn: engine.base.Connection):
    game_id = db_execute.search_data(f"season='{season}' and game={game}", "id", "game_list", conn)
    if len(game_id) == 0:
        data={'season':season, 'game':game, 'home_team_id':home_team_id, 'away_team_id':away_team_id}
        df = pd.DataFrame(data=data, index=[0])
        db_execute.upload_data(df, 'game_list', conn)
        game_id = db_execute.search_data(f"season='{season}' and game={game}", "id", "game_list", conn)
    
    return game_id[0][0]

def insert_player_id(df: pd.DataFrame, conn: engine.base.Connection):
    df = df[['player_id', 'name']]
    df.rename(columns={'player_id':'id'}, inplace=True)
    db_execute.upload_data(df, 'player_list', conn)

def parameter_game(parameter: typing.List[str]):
    """回傳該賽季場次對應的 game index"""
    season = parameter[0]
    start_game = int(parameter[1])
    end_game = int(parameter[-1])
    parameter_list = []
    game_id = game_id_list(season)
    parameter_list = list(range(game_id[start_game-1], game_id[end_game-1]+1))
    return parameter_list

def game_and_season(id: int):
    if 13+48 >= id >= 13:
        game = id-12
        season = '2020-21'
    elif 73+90 >= id >= 73:
        game = id-72
        season = '2021-22'
    return game, season

def crawler(id: str) -> pd.DataFrame:
    """爬單場數據"""
    router = db.get_db_router()
    with router.mysql_conn as conn:
        # 該場主客場隊名
        team_url = f"https://pleagueofficial.com/game/{id}"
        team_r = requests.get(url=team_url, headers=pleague_header())
        if team_r == '':
            return pd.DataFrame()
        soup = BeautifulSoup(team_r.text, "html.parser")
        if get_team_id(soup, conn) == False:
            return pd.DataFrame()
        home_team_id, away_team_id = get_team_id(soup, conn)
        # 單場數據
        stats_url = f"https://pleagueofficial.com/api/boxscore.php?id={id}&away_tab=total&home_tab=total"
        stats_r = requests.get(url=stats_url, headers=pleague_header())
        if stats_r == '':
            return pd.DataFrame()
        raw_data = stats_r.json()['data']
        df = convert_raw_data_to_df(raw_data, home_team_id, away_team_id)

        if len(df) > 0:
            id = int(id)
            game, season = game_and_season(id)
            insert_player_id(df, conn)
            game_id = get_game_id(season, game, home_team_id, away_team_id, conn)
            df['game_id'] = game_id
            df = check_schema(df.copy(), dataset="PLeagueGameStats")

    return df