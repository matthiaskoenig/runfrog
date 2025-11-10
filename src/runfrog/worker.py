"""Worker functions to create reports."""

import tempfile
import traceback
from typing import Any


from fbc_curation.worker import frog_task


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
        task = frog_task.delay(str(path))
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