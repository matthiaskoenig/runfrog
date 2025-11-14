"""
NiceGUI graphical user interface
"""
from pathlib import Path
from urllib.parse import urlparse

import requests
from celery.result import AsyncResult
from nicegui import ui, events, app
from nicegui.events import GenericEventArguments
from pymetadata.console import console
from starlette.formparsers import MultiPartParser
from runfrog.worker import frog_from_bytes

MultiPartParser.spool_max_size = 1024 * 1024 * 20  # 20 MB


app.add_static_files('/static', Path(__file__).parent / 'static')


def is_valid_url(url: str) -> bool:
    """Check if a URL is valid."""
    result = urlparse(url)
    return all([result.scheme, result.netloc])

@ui.page('/', title='runfrog', favicon="/static/frog-100.png", dark=False)
def root_page():
    # color theme
    ui.colors(
        primary='#4F6EF7',
        secondary='#64748B',
        accent='#A5B4FC',
        dark='#1E293B',
        dark_page='#121212',
        positive='#10B981',
        negative='#EF4444',
        info='#38BDF8',
        warning='#FBBF24',
        brand='#FF0000'
    )

    # -----------------
    # navigation header
    # -----------------
    with ui.header().classes('items-center justify-between bg-dark'):

        with ui.row().classes('max-sm:hidden'):
            with ui.link(target="/"):
                ui.button('Home', icon='home').props('flat color=white')
            with ui.link(target="/api/docs"):
                ui.button('API', icon='api').props('flat color=white')
            with ui.link(target='http://localhost:5556/flower/'):
                ui.button('Dashboard', icon='analytics').props('flat color=white')
        with ui.row().classes('sm:hidden'):
            with ui.link(target="/"):
                ui.button(icon='home').props('flat color=white')
            with ui.link(target="/api/docs"):
                ui.button(icon='api').props('flat color=white')
            with ui.link(target='http://localhost:5556/flower/'):
                ui.button(icon='dashboard').props('flat color=white')

        # ui.button(icon='menu').props('flat color=white')
    # -----------------
    # navigation footer
    # -----------------
    with ui.footer().classes('bg-dark'):  # .style('background-color: #3874c8'):
        ui.markdown('''
        © 2025 [Matthias König](https://livermetabolism.com).
        By using any part of this service, you agree to the terms of the 
        [privacy notice](https://github.com/matthiaskoenig/runfrog/blob/main/docs/privacy_notice.md).
        ''')
    # -----------------

    ui.sub_pages({'/': upload_subpage, '/task/{task_id}': task_subpage}).classes('w-full')


def upload_subpage():
    """GUI for uploading SBML and omex."""

    with ui.row().classes('w-full'):
        ui.image('./static/frog-100.png').props('width=50px height=50px').classes('bg-transparent')
        with ui.row():
            with ui.tabs() as tabs:
                ui.tab('file', label='Upload File', icon='file_upload').tooltip('Upload an SBML file or COMBINE archive (OMEX).')
                ui.tab('url', label='Submit URL', icon='link').tooltip('Provide URL to an SBML file or COMBINE archive (OMEX).')

            with ui.tab_panels(tabs, value='file').classes('w-full'):
                with ui.tab_panel('file'):
                    ui.upload(
                        on_upload=handle_file_upload,
                        multiple=False,
                        max_files=1,
                        auto_upload=True,
                    ).classes('w-full')


                # https://raw.githubusercontent.com/matthiaskoenig/fbc_curation/refs/heads/develop/src/fbc_curation/resources/examples/models/e_coli_core.xml
                with ui.tab_panel('url'):
                    url_input = ui.input(
                        label='URL',
                        placeholder='start typing',
                        validation={
                                 'URL must be valid': lambda value: is_valid_url(value)
                             },
                    ).props('clearable').on('keydown.enter', lambda e: handle_url_upload(e, url_input))


def task_subpage(task_id: str):
    """GUI for managing task results."""
    with ui.row().classes('w-full'):
        ui.html("<h1>FROG Report</h1>", sanitize=False)
        ui.html(f"<h2>{task_id}</h1>", sanitize=False)

        status_url: str = f"/api/api/task/status/{task_id}"
        report_url: str = f"/task/{task_id}"
        omex_url: str = f"/api/task/omex/{task_id}"


        ui.label("This may take a few seconds. Please be patient.")
        ui.spinner(size='lg')
        status_label = ui.label("")
        ui.label(f"Please be patient. Running a complete FROG analysis for large models can take some time. "
                 f"You can check back later for your results using the url: '{report_url}'") # TODO: url

        #
        # # TODO: query results
        # def update_task_status(task_id: str):
        #     task_result = AsyncResult(task_id)
        #     status_label.text = task_result.status
        #
        #     # return {
        #     #     "task_id": task_id,
        #     #     "task_status": task_result.status,
        #     #     "task_result": task_result.result,
        #     # }
        #
        #
        # status = None
        # # while not status:
        # #     # poll every 0.5 s
        # #     ui.timer(0.5, update_task_status(task_id))
        #
        # ui.label("Download COMBINE archive with FROG Report")
        # # ui.download()
        # # /api/task/omex/{task_id}
        # # Check if the task has finished


async def handle_file_upload(e: events.UploadEventArguments):
    """Handle file upload."""
    file: ui.upload.FileUpload = e.file
    content: bytes = await file.read()
    console.print(f"Uploaded {e.file.name}")

    # some validation
    # FIXME

    # start task & load subpage
    results = frog_from_bytes(content=content)
    task_id = results["task_id"]
    ui.navigate.to(f"/task/{task_id}")

def handle_url_upload(e: events.KeyEventArguments, input_element: ui.input):
    """Handle URL upload."""
    url = input_element.value
    response = requests.get(url)
    response.raise_for_status()
    # FIXME: validation

    results = frog_from_bytes(response.content)
    task_id = results["task_id"]
    ui.navigate.to(f"/task/{task_id}")

# Mount FastAPI inside nicegui
from runfrog.api import api
app.mount("/api", api)  # or mount at "/ui" if preferred


ui.run(
    title="RunFrog",
    fastapi_docs=True,
    native=False,
    port=1555
)

