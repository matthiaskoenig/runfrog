"""Worker functions to create reports."""

import os
import tempfile
import traceback
from typing import Any, Optional
from celery import Celery

from fbc_curation.worker import frog_task

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get(
    "CELERY_RESULT_BACKEND", "redis://localhost:6379"
)

# storage of data on server, only relevant for server
FROG_STORAGE = "/frog_data"

# celery example: https://github.com/generomuga/nicegui-celery/blob/main/app.py


@celery.task(name="frog_task")
def frog_task_celery(
    source_path_str: str,
    omex_path_str: Optional[str] = None,
    input_is_temporary: bool = False,
    frog_storage_path_str: str = FROG_STORAGE,
) -> dict[str, Any]:
    return frog_task(
        source_path_str=source_path_str,
        omex_path_str=omex_path_str,
        input_is_temporary=input_is_temporary,
        frog_storage_path_str=frog_storage_path_str,
    )


def frog_from_bytes(content: bytes) -> dict[str, Any]:
    """Start FROG task for given content.

    Necessary to serialize the content to a common location
    accessible for the task queue.

    :returns: `task_id`
    """
    try:
        # persistent temporary file cleaned up by task
        _, path = tempfile.mkstemp(dir="/frog_data")

        with open(path, "w+b") as f_tmp:
            f_tmp.write(content)
            f_tmp.close()
        task = frog_task_celery.delay(str(path))
        return {"task_id": task.id}

    except Exception as e:
        res = {
            "errors": [
                f"{e.__str__()}",
                f"{''.join(traceback.format_exception(None, e, e.__traceback__))}",
            ],
        }
        logger.error(res)

        return res
