import pandas as pd
from fastapi import FastAPI
from sqlalchemy import create_engine, engine, text
from api import config


def get_mysql_conn() -> engine.base.Connection:
    address = (
        f"mysql+pymysql://{config.MYSQL_DATA_USER}:{config.MYSQL_DATA_PASSWORD}"
        f"@{config.MYSQL_DATA_HOST}:{config.MYSQL_DATA_PORT}/{config.MYSQL_DATA_DATABASE}"
    )

    engine = create_engine(address)
    connect = engine.connect()
    return connect


app = FastAPI()

@app.get("/player_game_stats")
def player_game_stats(
    season: str = "",
    player_name: str = "",
    game: int = 0
):
    sql = f"""
    SELECT season, game, name, starter, team, number, 
    ROUND(seconds/60, 2) as mins, 
    points, reb_d as defensive_rebounds, reb_o as offensive_rebounds,  
    ast as assists, blk as blocks, stl as steals, turnover as turnovers, 
    pfoul as personal_fouls, 
    trey_m as 3points_made, trey_a as 3points_attempted, 
    two_m as 2points_made, two_a as 2points_attempted,
    ft_m as free_throw_made, ft_a as free_throw_attempted, 
    oncourt_plus_minus
    FROM game_stats s 
    LEFT JOIN game_list g on s.game_id = g.id
    LEFT JOIN player_list p on s.player_id = p.id
    LEFT JOIN team_list t on s.team_id = t.id
    WHERE season = "{season}" and game = {game} and name = "{player_name}"
    """

@app.get("/player_season_stats")
def player_season_stats(
    season: str = "",
    player_name: str = "",
    total_or_avg: str = "",
    more_stats: int = 0,
    advanced_stats: int = 0
):
    if total_or_avg == "total":
        aggregate_func = "SUM"
    else:
        aggregate_func = total_or_avg
    
    if more_stats == 1:
        more_stats_sql = f"""
            ,
            ROUND({aggregate_func}(reb_o), 2) as offensive_rebounds,
            ROUND({aggregate_func}(reb_d), 2) as defensive_rebounds,
            ROUND({aggregate_func}(two_m), 2) as 2points_made,
            ROUND({aggregate_func}(two_a), 2) as 2points_attempted,
            ROUND({aggregate_func}(trey_m), 2) as 3points_made,
            ROUND({aggregate_func}(trey_a), 2) as 3points_attempted,
            ROUND({aggregate_func}(ft_m), 2) as free_throw_made,
            ROUND({aggregate_func}(ft_a), 2) as free_throw_attempted,
            ROUND({aggregate_func}(oncourt_plus_minus), 2) as oncourt_plus_minus
        """
    else:
        more_stats_sql = ""

    if advanced_stats == 1:
        advanced_stats_sql = f"""
        ,
        ROUND(sum(two_m+1.5*trey_m)/sum(two_a+trey_a), 4) as effective_field_goal_percentage,
        ROUND(sum(points)/sum(2*(two_a+trey_a+ft_a*0.44)), 4) as true_shooting_percentage
        """
    else:
        advanced_stats_sql = ""

    sql = f"""
    SELECT name, season, 
    count(distinct CASE WHEN seconds > 0 THEN game_id END) as games,
    ROUND({aggregate_func}(seconds)/60, 2) as mins,
    ROUND({aggregate_func}(points), 2) as points, 
    ROUND({aggregate_func}(reb_o+reb_d), 2) as rebounds,
    ROUND({aggregate_func}(ast), 2) as assists,
    ROUND({aggregate_func}(stl), 2) as steals,
    ROUND({aggregate_func}(blk), 2) as blocks,
    ROUND({aggregate_func}(pfoul), 2) as personal_fouls,
    ROUND({aggregate_func}(turnover), 2) as turnovers,
    sum(two_m+trey_m)/sum(two_a+trey_a) as field_goal_percentage,
    sum(trey_m)/sum(trey_a) as 3point_percentage,
    sum(ft_m)/sum(ft_a) as free_throw_percentage
    {more_stats_sql}
    {advanced_stats_sql}
    FROM game_stats s 
    LEFT JOIN player_list p ON s.player_id = p.id 
    LEFT JOIN game_list g ON s.game_id = g.id 
    WHERE name = "{player_name}" AND season = "{season}"
    GROUP BY name, season
    """
    with get_mysql_conn() as conn:
        sql_query = text(sql)
        data_df = pd.read_sql(sql_query, con=conn)
        conn.commit()
        data_dict = data_df.to_dict("records") # records: 轉換為 list 形式
    return {"data": data_dict}

@app.get("/team_season_stats")
def team_season_stats(
    season: str = "",
    team_name: str = ""
):
    sql = f"""
    WITH result as (
        SELECT team_id, game_id,
        SUM(points) as points
        FROM game_stats s 
        LEFT JOIN game_list g ON s.game_id = g.id 
        WHERE season = "{season}"
        GROUP BY team_id, game_id  
    )
    SELECT team, ROUND(AVG(scores), 2) as avg_scores, ROUND(AVG(loss), 2) as avg_loss_points, 
    COUNT(DISTINCT CASE WHEN is_home=1 and scores>loss THEN game END) as home_wins,
    COUNT(DISTINCT CASE WHEN is_home=1 and scores<loss THEN game END) as home_loss,
    COUNT(DISTINCT CASE WHEN is_home=0 and scores>loss THEN game END) as away_wins,
    COUNT(DISTINCT CASE WHEN is_home=0 and scores<loss THEN game END) as away_loss
    FROM(
        SELECT team, g.game, g.home_scores as scores, g.away_scores as loss, 1 as is_home
        FROM team_list t 
        LEFT JOIN(
            SELECT game, r1.points as home_scores, r2.points as away_scores, home_team_id
            FROM game_list g
            LEFT JOIN result r1 ON g.id = r1.game_id and g.home_team_id = r1.team_id 
            LEFT JOIN result r2 ON g.id = r2.game_id and g.away_team_id = r2.team_id 
            WHERE season = "{season}"
        )g on t.id = g.home_team_id
        WHERE g.home_team_id is not null and team = "{team_name}"

        UNION ALL
        SELECT team, g.game, g.away_scores as scores, g.home_scores as loss, 0 as is_home
        FROM team_list t 
        LEFT JOIN(
            SELECT game, r1.points as home_scores, r2.points as away_scores, away_team_id
            FROM game_list g
            LEFT JOIN result r1 ON g.id = r1.game_id and g.home_team_id = r1.team_id 
            LEFT JOIN result r2 ON g.id = r2.game_id and g.away_team_id = r2.team_id 
            WHERE season = "{season}"
        )g on t.id = g.away_team_id
        WHERE g.away_team_id is not null and team = "{team_name}"
    )r
    GROUP BY team
    """
    with get_mysql_conn() as conn:
        sql_query = text(sql)
        data_df = pd.read_sql(sql_query, con=conn)
        conn.commit()
        data_dict = data_df.to_dict("records") # records: 轉換為 list 形式
    return {"data": data_dict}


