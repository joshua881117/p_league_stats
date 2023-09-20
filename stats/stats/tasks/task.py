import importlib
import typing

from stats.backend import db
from stats.backend.db import db_execute
from stats.tasks.worker import app


# 註冊 task, 有註冊的 task 才可以變成任務發送給 rabbitmq
@app.task()
def crawler(dataset: str, parameter: str):
    # 使用 getattr, importlib,
    # 根據不同 dataset, 使用相對應的 crawler 收集資料
    # 爬蟲
    df = getattr(importlib.import_module(f"stats.crawler.crawler_{dataset}"), "crawler")(parameter)
    # 上傳資料庫
    db_dataset = dict(
        year = "year_stats",
        game = "game_stats"
    )
    table = db_dataset[dataset]
    r = db.get_db_router()
    with r.mysql_conn as conn:
        db_execute.upload_data(df, table, conn)
