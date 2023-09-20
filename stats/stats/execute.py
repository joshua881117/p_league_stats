import importlib
import sys
import typing

from loguru import logger

from stats.tasks.task import crawler


def Update(dataset: str, parameter: typing.List[str]):
    # 拿取每個爬蟲任務的參數列表
    parameter_list = getattr(importlib.import_module(f"stats.crawler.crawler_{dataset}"), f"parameter_{dataset}")(parameter)
    # 用 for loop 發送任務
    for p in parameter_list:
        logger.info(f"{dataset}, {p}")
        task = crawler.s(dataset, p) #.s 讓 function 變為異步執行
        # queue 參數，可以指定要發送到特定 queue 列隊中
        task.apply_async(queue=dataset)



if __name__ == "__main__":
    dataset = sys.argv[1]
    parameter = sys.argv[2:]
    Update(dataset, parameter)
