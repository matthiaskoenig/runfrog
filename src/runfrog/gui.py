"""
NiceGUI graphical user interface
"""
from pathlib import Path
from urllib.parse import urlparse
from nicegui import ui, events, app
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
def root():
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
            with ui.link(target="/api/docs/"):
                ui.button('API', icon='api').props('flat color=white')
            with ui.link(target='http://localhost:5556/flower/'):
                ui.button('Dashboard', icon='analytics').props('flat color=white')
        with ui.row().classes('sm:hidden'):
            with ui.link(target="/"):
                ui.button(icon='home').props('flat color=white')
            with ui.link(target="/api/docs/"):
                ui.button(icon='api').props('flat color=white')
            with ui.link(target='http://localhost:5556/flower/'):
                ui.button(icon='dashboard').props('flat color=white')

        ui.button(icon='menu').props('flat color=white')
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

    ui.sub_pages({'/': upload, '/tasks': tasks}).classes('w-full')


def upload():
    """GUI for uploading SBML and omex."""

    with ui.row().classes('w-full'):
        ui.image('./static/frog-100.png').props('width=50px height=50px').classes('bg-transparent')
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

            with ui.tab_panel('url'):

                url_input = ui.input(label='URL', placeholder='start typing',
                         # on_change=lambda e: result.set_text('you typed: ' + e.value),
                         validation={
                             'URL must be valid': lambda value: is_valid_url(value)
                         },
                         ).props('clearable').on('keydown.enter', lambda value: console.print(value)).classes('w-full')


        # ui.button(
        #     text='FROG report',
        #     icon='article',
        #     on_click=lambda: ui.notify(f'Create report for {url_input.value}')
        # )
    with ui.row().classes('w-full'):
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

