from api.main import (
    get_mysql_conn,
    app
)

from fastapi.testclient import TestClient
from sqlalchemy import engine

client = TestClient(app)
# 使用 fastapi 官方教學
# https://fastapi.tiangolo.com/tutorial/testing/
# 測試框架

def test_get_mysql_conn():
    conn = get_mysql_conn()
    assert isinstance(conn, engine.Connection)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "Hello": "World"
    }

def test_player_season_stats():
    response = client.get(
        "/player_season_stats", 
        params={
            "season": "2021-22",
            "player_name": "周桂羽",
            "total_or_avg": "avg",
            "more_stats": 0,
            "advanced_stats": 1
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        "data": [
            {
                "name": "周桂羽",
                "season": "2021-22",
                "games": 22,
                "mins": 13.36,
                "points": 3.57,
                "rebounds": 1.52,
                "assists": 1.43,
                "steals": 0.70,
                "blocks": 0.13,
                "personal_fouls": 1.65,
                "turnovers": 1.04,
                "field_goal_percentage": 0.3537,
                "3point_percentage": 0.3182,
                "free_throw_percentage": 0.7692,
                "effective_field_goal_percentage": 0.4390,
                "true_shooting_percentage": 0.4674
            }
        ]
    }
    
def test_team_season_stats():
    response = client.get(
        "/team_season_stats", 
        params={
            "season": "2021-22",
            "team_name": "新北國王"
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        "data": [
            {
                "team": "新北國王",
                "avg_scores": 98.40,
                "avg_loss_points": 97.80,
                "home_wins": 7,
                "home_loss": 8,
                "away_wins": 9,
                "away_loss": 6
            }
        ]
    }
    


 