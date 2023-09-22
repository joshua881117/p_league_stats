import pandas as pd

from stats.crawler.crawler_game import (
    game_id_list,
    convert_datatype,
    convert_raw_data_to_df,
    get_team_id,
    get_game_id,
    parameter_game,
    game_and_season,
    crawler
)
import stats.backend.db as db
from stats.schema.dataset import check_schema
import requests
from bs4 import BeautifulSoup

router = db.get_db_router()
def test_game_id_list_2020():
    result = game_id_list("2020-21")
    expected = list(range(13, 13+48))
    assert(result == expected)

def test_game_id_list_2021():
    result = game_id_list("2021-22")
    expected = list(range(73, 73+90))
    assert(result == expected)

def test_convert_datatype():
    df = pd.DataFrame(
        [
            {
                'eff':'', 
                'efgp':'', 
                'profile_picture':'', 
                'name':'', 
                'position':'', 
                'tsp':'', 
                'ft_a':'', 
                'trey_a':'', 
                'two_a':'', 
                'ugp':'', 
                'mins':'',
                'two_m_two':'', 
                'twop':'', 
                'trey_m_trey':'', 
                'treyp':'', 
                'ft_m_ft':'', 
                'ftp':'', 
                'reb':'', 
                'name_alt':'', 
                'positive':'', 
                'jersey':'', 
                'two':'', 
                'trey':'', 
                'ft':'', 
                'points':'', 
                'seconds':'', 
                'starter':'', 
                'turnover':'', 
                'ast':'', 
                'blk':'', 
                'reb_o':'', 
                'reb_d':'', 
                'ft_m':'', 
                'pfoul':'', 
                'player_id':'', 
                'stl':'', 
                'trey_m':'', 
                'two_m':''
            },
            {
                'eff':'1', 
                'efgp':'2', 
                'profile_picture':'3', 
                'name':'4', 
                'position':'5', 
                'tsp':'6', 
                'ft_a':'7', 
                'trey_a':'8', 
                'two_a':'9', 
                'ugp':'10', 
                'mins':'11',
                'two_m_two':'12', 
                'twop':'13', 
                'trey_m_trey':'14', 
                'treyp':'15', 
                'ft_m_ft':'16', 
                'ftp':'17', 
                'reb':'18', 
                'name_alt':'19', 
                'positive':'20', 
                'jersey':'21', 
                'two':'22', 
                'trey':'23', 
                'ft':'24', 
                'points':'25', 
                'seconds':'26', 
                'starter':'〇', 
                'turnover':'28', 
                'ast':'29', 
                'blk':'30', 
                'reb_o':'31', 
                'reb_d':'32', 
                'ft_m':'33', 
                'pfoul':'34', 
                'player_id':'35', 
                'stl':'36', 
                'trey_m':'37', 
                'two_m':'38'
            }
        ]
    )
    result = convert_datatype(df)
    expected = pd.DataFrame(
        [
            {
                'name':'', 
                'oncourt_plus_minus':0, 
                'number':'', 
                'two_a':0, 
                'trey_a':0, 
                'ft_a':0, 
                'points':0, 
                'seconds':0, 
                'starter':0, 
                'turnover':0, 
                'ast':0, 
                'blk':0, 
                'reb_o':0, 
                'reb_d':0, 
                'ft_m':0, 
                'pfoul':0, 
                'player_id':0, 
                'stl':0, 
                'trey_m':0, 
                'two_m':0
            },
            { 
                'name':'19', 
                'oncourt_plus_minus':20, 
                'number':'21', 
                'two_a':22, 
                'trey_a':23, 
                'ft_a':24, 
                'points':25, 
                'seconds':26, 
                'starter':1, 
                'turnover':28, 
                'ast':29, 
                'blk':30, 
                'reb_o':31, 
                'reb_d':32, 
                'ft_m':33, 
                'pfoul':34, 
                'player_id':35, 
                'stl':36, 
                'trey_m':37, 
                'two_m':38
            }
        ]
    )
    assert(pd.testing.assert_frame_equal(result, expected) is None)

def test_convert_raw_data_to_df():
    raw_data = {
        'home':[
            {
                'eff':'', 
                'efgp':'', 
                'profile_picture':'', 
                'name':'', 
                'position':'', 
                'tsp':'', 
                'ft_a':'', 
                'trey_a':'', 
                'two_a':'', 
                'ugp':'', 
                'mins':'',
                'two_m_two':'', 
                'twop':'', 
                'trey_m_trey':'', 
                'treyp':'', 
                'ft_m_ft':'', 
                'ftp':'', 
                'reb':'', 
                'name_alt':'', 
                'positive':'', 
                'jersey':'', 
                'two':'', 
                'trey':'', 
                'ft':'', 
                'points':'', 
                'seconds':'', 
                'starter':'', 
                'turnover':'', 
                'ast':'', 
                'blk':'', 
                'reb_o':'', 
                'reb_d':'', 
                'ft_m':'', 
                'pfoul':'', 
                'player_id':'', 
                'stl':'', 
                'trey_m':'', 
                'two_m':''
            }
        ],
        'away':[
            {
                'eff':'1', 
                'efgp':'2', 
                'profile_picture':'3', 
                'name':'4', 
                'position':'5', 
                'tsp':'6', 
                'ft_a':'7', 
                'trey_a':'8', 
                'two_a':'9', 
                'ugp':'10', 
                'mins':'11',
                'two_m_two':'12', 
                'twop':'13', 
                'trey_m_trey':'14', 
                'treyp':'15', 
                'ft_m_ft':'16', 
                'ftp':'17', 
                'reb':'18', 
                'name_alt':'19', 
                'positive':'20', 
                'jersey':'21', 
                'two':'22', 
                'trey':'23', 
                'ft':'24', 
                'points':'25', 
                'seconds':'26', 
                'starter':'〇', 
                'turnover':'28', 
                'ast':'29', 
                'blk':'30', 
                'reb_o':'31', 
                'reb_d':'32', 
                'ft_m':'33', 
                'pfoul':'34', 
                'player_id':'35', 
                'stl':'36', 
                'trey_m':'37', 
                'two_m':'38'
            }
        ]
    }
    result = convert_raw_data_to_df(raw_data, 1, 2)
    expected = pd.DataFrame(
        [
            {
                'name':'', 
                'oncourt_plus_minus':0, 
                'number':'', 
                'two_a':0, 
                'trey_a':0, 
                'ft_a':0, 
                'points':0, 
                'seconds':0, 
                'starter':0, 
                'turnover':0, 
                'ast':0, 
                'blk':0, 
                'reb_o':0, 
                'reb_d':0, 
                'ft_m':0, 
                'pfoul':0, 
                'player_id':0, 
                'stl':0, 
                'trey_m':0, 
                'two_m':0,
                'team_id': 1
            },
            { 
                'name':'19', 
                'oncourt_plus_minus':20, 
                'number':'21', 
                'two_a':22, 
                'trey_a':23, 
                'ft_a':24, 
                'points':25, 
                'seconds':26, 
                'starter':1, 
                'turnover':28, 
                'ast':29, 
                'blk':30, 
                'reb_o':31, 
                'reb_d':32, 
                'ft_m':33, 
                'pfoul':34, 
                'player_id':35, 
                'stl':36, 
                'trey_m':37, 
                'two_m':38,
                'team_id': 2
            }
        ]
    )
    assert(pd.testing.assert_frame_equal(result, expected) is None)

def test_get_team_id():
    r = requests.get("https://pleagueofficial.com/game/74")
    soup = BeautifulSoup(r.text, 'html.parser')
    with router.mysql_conn as conn:
        result = get_team_id(soup, conn)
    
    expected = (1, 2)
    assert(result == expected)

def test_get_game_id():
    with router.mysql_conn as conn:
        result = get_game_id("2020-21", 1, 3, 1, conn)
    expected = 10
    assert(result == expected)

def test_parameter_game():
    result = parameter_game(["2020-21", 1, 5])
    expected = list(range(13, 13+5))
    assert(result == expected)

def test_game_and_season():
    result = game_and_season(74)
    expected = (2, "2021-22")
    assert(result == expected)

def test_crawler_no_data():
    """測試錯誤的 game index 爬蟲是否正常"""
    result = crawler(-1)
    assert(len(result) == 0)
    assert isinstance(result, pd.DataFrame)

def test_crawler_error(mocker):
    """
    測試對方網站回傳例外狀況時, 或是被 ban IP 時, 爬蟲是否會失敗

    這邊使用特別的技巧, mocker,
    因為在測試階段, 無法保證對方一定會給錯誤的結果
    因此使用 mocker, 對 requests 做"替換", 換成我們設定的結果
    如下
    """
    # 將特定路徑下的 requests 替換掉
    mock_requests = mocker.patch(
        "stats.crawler.crawler_game.requests"
    )
    # 將 requests.get 的回傳值 response, 替換掉成 ""
    # 如此一來, 當我們在測試爬蟲時,
    # 發送 requests 得到的 response, 就會是 ""
    mock_requests.get.return_value = ""
    result = crawler(id=-1)
    assert (len(result) == 0)  # 沒 data, 回傳 0
    # 沒 data, 一樣要回傳 pd.DataFrame 型態
    assert isinstance(result, pd.DataFrame)

def test_crawler_success():
    result = crawler(13)
    result = check_schema(result, 'PLeagueGameStats')
    assert(len(result) == 24)
    assert(isinstance(result, pd.DataFrame))