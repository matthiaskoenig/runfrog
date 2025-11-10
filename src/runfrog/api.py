"""API for the runfrog web service.

This provides basic functionality of running the model
and returning the JSON representation based on fastAPI.
"""


import typing
from pathlib import Path
from typing import Any

import orjson
import requests
import uvicorn
from starlette.responses import FileResponse, JSONResponse
from celery.result import AsyncResult
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware


from pymetadata import log
from runfrog.worker import frog_from_bytes
from fbc_curation import __version__

logger = log.get_logger(__name__)


class ORJSONResponse(JSONResponse):
    """JSON response."""

    media_type = "application/json"

    def render(self, content: typing.Any) -> bytes:
        """Render function."""
        content_bytes: bytes = orjson.dumps(content)
        return content_bytes


description = """
## FROG webservice

This service provides an API for running FROG analysis.

After submission of a
model for frog analysis a `task_id` is returned which allows to query the status
of the FROG task and retrieve the FROG report after the task succeeded.
"""

api: FastAPI = FastAPI(
    default_response_class=ORJSONResponse,
    title="FROG REST API",
    description=description,
    version=__version__,
    terms_of_service="https://github.com/matthiaskoenig/fbc_curation/blob/develop/runfrog-site/privacy_notice.md",  # noqa: E501
    contact={
        "name": "Matthias König",
        "url": "https://livermetabolism.com",
        "email": "konigmatt@googlemail.com",
        "orcid": "0000-0003-1725-179X",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "core",
            "description": "API information.",
        },
        {
            "name": "frog",
            "description": "API endpoints to create FROG reports.",
        },
        {
            "name": "task",
            "description": "Task operations, such as querying status and "
            "retrieving results. When a FROG report is requested this is handled via a task scheduler. "
                           "The results can be retrieved via the `task_id`.",
        }
    ],
)


# API Permissions Data
origins = ["*"]

api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- FROG ---
@api.post("/api/frog/file", tags=["frog"])
async def create_frog_from_file(request: Request) -> dict[str, Any]:
    """Upload file and create FROG.

    Creates a task for the FROG report.

    :returns: `task_id`
    """
    file_data = await request.form()
    file_content = await file_data["source"].read()  # type: ignore
    return frog_from_bytes(file_content)


@api.post("/api/frog/content", tags=["frog"])
async def create_frog_from_content(request: Request) -> dict[str, Any]:
    """Create FROG from file contents.

    Creates a task for the FROG report.

    :returns: `task_id`
    """
    content: bytes = await request.body()
    return frog_from_bytes(content)


@api.get("/api/frog/url", tags=["frog"])
def create_frog_from_url(url: str) -> dict[str, Any]:
    """Create FROG via URL to SBML or COMBINE archive.

    Creates a task for the FROG report.

    :returns: `task_id`
    """
    response = requests.get(url)
    response.raise_for_status()
    return frog_from_bytes(response.content)

# --- CORE ---
@api.get("/api", tags=["core"])
def get_api_information(request: Request) -> dict[str, Any]:
    """Get API information."""

    return {
        "title": api.title,
        "description": api.description,
        "contact": api.contact,
        "root_path": request.scope.get("root_path"),
    }

# --- TASK ---
@api.get("/api/task/status/{task_id}", tags=["task"])
def get_status_for_task(task_id: str) -> JSONResponse:
    """Get status and results of FROG task with `task_id`."""
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result,
    }
    return JSONResponse(result)


@api.get("/api/task/omex/{task_id}", tags=["task"])
async def get_combine_archive_for_task(task_id: str) -> FileResponse:
    """Get COMBINE archive (omex) for FROG task with `task_id`."""

    omex_path = Path("/frog_data") / f"FROG_{task_id}.omex"

    if not omex_path:
        raise HTTPException(
            status_code=404,
            detail=f"No COMBINE archive for task with id '{task_id}'",
        )

    return FileResponse(
        path=omex_path, media_type="application/zip", filename=omex_path.name
    )



if __name__ == "__main__":
    # http://localhost:1555/
    # http://localhost:1555/docs

    uvicorn.run(
        "runfrog.api:api",
        host="localhost",
        port=1555,
        log_level="info",
        reload=True,
    )

