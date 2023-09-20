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

def futures_header():
    """網頁瀏覽時, 所帶的 request header 參數, 模仿瀏覽器發送 request"""
    return {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.76",
        "content-type":"text/html; charset=UTF-8"
    }

def year_stats_columes(soup: BeautifulSoup) -> typing.List[str]:
    """抓取數據的欄位"""
    col_list = soup.find("body", class_="toolbar-enabled bg-light").find("section", class_="bg-dark text-light py-md-5 py-0").\
        find("div", class_='container-fluid').find("div", id="lock-table-scroll").find("table", id="main-table").\
        find("thead", class_="bg-deepgray").find("tr").select("th")
    columes = [col.get_text() for col in col_list]
    return columes

def year_stats_data(soup: BeautifulSoup) -> typing.List[typing.List[str]]:
    """抓取數據"""
    stats_list = soup.find("body", class_="toolbar-enabled bg-light").find("section", class_="bg-dark text-light py-md-5 py-0").\
        find("div", class_='container-fluid').find("div", id="lock-table-scroll").find("table", id="main-table").\
        find("tbody").find_all("tr")
    player_total_stats = []
    for stats in stats_list:
        name = stats.find("th").get_text()
        all_stats = stats.find_all("td", {'data-total': True})
        total_stats = [data['data-total'] for data in all_stats]

        total_stats.insert(0, name)
        player_total_stats.append(total_stats)
    return player_total_stats

def convert_mins_to_seconds(df: pd.DataFrame) -> pd.DataFrame:
    """上場時間轉為秒數"""
    df['playing_seconds'] = df['時間 (分)'].apply(lambda x: int(x.split(":")[0])*60+int(x.split(":")[1]))
    df.drop(columns=['時間 (分)'], inplace=True)
    return df

def convert_datatype(df: pd.DataFrame) -> pd.DataFrame:
    """留下必要欄位、轉換資料型態、欄位名稱"""
    df.drop(columns=['兩分%', '三分%', '罰球%', '籃板'], inplace=True)
    df.columns = ['name', 'number', 'team', 'games', 'two_points_field_goals_made', 'two_points_field_goals_attempt',\
        'three_points_field_goals_made', 'three_points_field_goals_attempt', 'free_throws_made', 'free_throws_attempt', 'points',\
        'offense_rebounds', 'defense_rebounds', 'assists', 'steals', 'blocks', 'turnovers', 'personal_fouls', 'playing_seconds']
    df[['games', 'playing_seconds', 'two_points_field_goals_made', 'two_points_field_goals_attempt',\
        'three_points_field_goals_made', 'three_points_field_goals_attempt', 'free_throws_made', 'free_throws_attempt', 'points',\
        'offense_rebounds', 'defense_rebounds', 'assists', 'steals', 'blocks', 'turnovers', 'personal_fouls']] \
    = df[['games', 'playing_seconds', 'two_points_field_goals_made', 'two_points_field_goals_attempt',\
        'three_points_field_goals_made', 'three_points_field_goals_attempt', 'free_throws_made', 'free_throws_attempt', 'points',\
        'offense_rebounds', 'defense_rebounds', 'assists', 'steals', 'blocks', 'turnovers', 'personal_fouls']].apply(pd.to_numeric)
    
    return df

def parameter_year(parameter: typing.List[str]):
    return parameter

def crawler(season: str) -> pd.DataFrame:
    """爬年度數據"""
    index = 2
    if season == '2021-22':
        index = 6 # 2021-22 賽季的 index 為 6，其他為 2
    url = f"https://pleagueofficial.com/stat-player/{season}/{index}#record"
    r = requests.get(url=url, headers=futures_header())
    soup = BeautifulSoup(r.text, "html.parser")
    columes = year_stats_columes(soup)
    stats = year_stats_data(soup)
    
    df = pd.DataFrame(stats, columns=columes)
    df = convert_mins_to_seconds(df.copy())
    df = convert_datatype(df.copy())
    df = check_schema(df.copy(), dataset="PLeagueYearStats")
    df['season'] = season

    return df