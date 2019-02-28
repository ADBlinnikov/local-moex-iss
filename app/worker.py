import os
from celery import Celery

app = Celery("app")
app.conf.update(
    {
        "broker_url": os.environ["CELERY_BROKER_URL"],
        "result_backend": os.environ["CELERY_RESULT_BACKEND"],
        "imports": ("tasks",),
        "task_serializer": "json",
        "result_serializer": "json",
        "accept_content": ["json"],
        "result_compression": "gzip",
        "timezone": "UTC",
    }
)
