from celery import Celery
from stats.config import (
    WORKER_ACCOUNT,
    WORKER_PASSWORD,
    MESSAGE_QUEUE_HOST,
    MESSAGE_QUEUE_PORT,
)

broker = (
    f"pyamqp://{WORKER_ACCOUNT}:{WORKER_PASSWORD}@"
    f"{MESSAGE_QUEUE_HOST}:{MESSAGE_QUEUE_PORT}/"
)
app = Celery("task", include=["stats.tasks.task"], broker=broker)
app.conf.broker_connection_retry_on_startup = True