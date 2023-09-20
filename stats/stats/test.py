import stats.backend.db as db
import stats.backend.db.db_execute as db_execute
import stats.crawler.crawler_game as game

if __name__ == "__main__":
    # router = db.get_db_router()
    # with router.mysql_conn as conn:
    #     result = db_execute.search_data("team = '富邦勇士'", "id", "team_list", conn)
    #     print(result)
    id = game.crawler(id=75)
    print(id.head())