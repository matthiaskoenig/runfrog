"""
NiceGUI graphical user intervface
"""

from urllib.parse import urlparse
from nicegui import ui, events, app
from pymetadata.console import console
from starlette.formparsers import MultiPartParser
from runfrog.worker import frog_from_bytes

MultiPartParser.spool_max_size = 1024 * 1024 * 20  # 20 MB



def is_valid_url(url: str) -> bool:
    """Check if a URL is valid."""
    result = urlparse(url)
    return all([result.scheme, result.netloc])

@ui.page('/', title='runfrog', favicon="./static/frog.png", dark=False)
def root():

    # -----------------
    # navigation header
    # -----------------
    with ui.header().classes('items-center justify-between'):
        # ui.avatar('favorite_border')
        with ui.row().classes('max-sm:hidden'):
            ui.button('Home', icon='home').props('flat color=white')
            ui.button('API', icon='api').props('flat color=white')
            ui.button('Dashboard', icon='analytics').props('flat color=white')
        with ui.row().classes('sm:hidden'):
            ui.button(icon='home').props('flat color=white')
            # ui.link(ui.button(icon='api').props('flat color=white'), "/docs")
            # ui.link(ui.button(icon='dashboard').props('flat color=white'), "/flower")

        ui.button(icon='menu').props('flat color=white')
    # -----------------
    # navigation footer
    # -----------------
    with ui.footer().style('background-color: #3874c8'):
        ui.label('FOOTER')
        # Report issue; source code, copyright, webpage
        # By using any part of this service, you agree to the terms of the privacy notice.
    # -----------------

    ui.sub_pages({'/': upload, '/tasks': tasks}).classes('w-full')


def upload():
    """GUI for uploading SBML and omex."""
    with ui.row().classes('w-full'):

        with ui.tabs().classes('w-full') as tabs:
            ui.tab('file', label='Upload File', icon='file_upload').tooltip('Upload an SBML file or COMBINE archive (OMEX).')
            ui.tab('url', label='Submit URL', icon='link').tooltip('Provide URL to an SBML file or COMBINE archive (OMEX).')

        with ui.tab_panels(tabs, value='url').classes('w-full'):
            with ui.tab_panel('file'):
                ui.upload(
                    on_upload=handle_file_upload,
                    multiple=False,
                    max_files=1,
                    auto_upload=True,
                ).classes('w-full')

            with ui.tab_panel('url'):
                url_input = ui.input(label='URL', placeholder='start typing',
                         # on_change=lambda e: result.set_text('you typed: ' + e.value),
                         validation={
                             'URL must be valid': lambda value: is_valid_url(value)
                         },
                         ).props('clearable').on('keydown.enter', lambda value: console.print(value)).classes('w-full')

                # ui.html('<h2>Examples</h2>', sanitize=False)
                # ui.button(icon='add_link',
                #           on_click=lambda: url_input.set_value(
                #               "https://github.com/matthiaskoenig/fbc_curation/raw/version-0.2.0/src/fbc_curation/resources/examples/models/e_coli_core.omex"))
                # ui.html('<code>https://github.com/matthiaskoenig/fbc_curation/raw/version-0.2.0/src/fbc_curation/resources/examples/models/e_coli_core.omex</code>',
                #         sanitize=False)
        ui.button(
            text='FROG report',
            icon='article',
            on_click=lambda: ui.notify(f'Create report for {url_input.value}')
        )
        ui.link('Go to tasks', '/tasks')


def tasks():
    """GUI for managing task results."""
    with ui.row().classes('w-full'):
        ui.label('Task dashboard')
        ui.link('Go to main page', '/')



async def handle_file_upload(e: events.UploadEventArguments):
    ui.notify(f'Uploaded {e.file.name}')
    # markdown.content = e.file.name

    file: ui.upload.FileUpload = e.file
    content: bytes = await file.read()

    # start task
    results = frog_from_bytes(content=content)
    console.print(f"Uploaded {e.file.name}")
    console.print(f"Results: {results}")



# Mount FastAPI inside nicegui
from runfrog.api import api
app.mount("/api", api)  # or mount at "/ui" if preferred


ui.run(
    title="RunFrog",
    fastapi_docs=True,
    native=False,
    port=1555
)

