"""Worker functions to create reports."""

import os
import tempfile
import traceback
from pathlib import Path
from typing import Any, Optional
from celery import Celery
from pymetadata.log import get_logger

from fbc_curation.worker import frog_task

logger = get_logger(__name__)

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get(
    "CELERY_RESULT_BACKEND", "redis://localhost:6379"
)
# storage of data on server, only relevant for server
FROG_STORAGE = "/frog_data"
# FIXME: use environment variable from docker-compose


@celery.task(name="frog_task")
def frog_task_celery(
    source_path_str: str,
) -> dict[str, Any]:

    task_id = frog_task_celery.request.id
    omex_path_str = f"{FROG_STORAGE}/FROG_{task_id}.omex"

    try:
        result = frog_task(
            source_path_str=source_path_str,
            omex_path_str=omex_path_str,
        )
    finally:
        # cleanup temporary files for celery
        os.remove(source_path_str)

    return result


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
        task = frog_task_celery.delay(
            source_path_str = str(path),
        )
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
