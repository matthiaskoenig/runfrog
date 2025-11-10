"""
NiceGUI Documentation:

navigation bar:
https://github.com/zauberzeug/nicegui/discussions/1715

icons:
https://fonts.google.com/icons

"""
# Some fixes for native mode: github.com/zauberzeug/nicegui/issues/1841
import multiprocessing
multiprocessing.set_start_method("spawn", force=True)

from nicegui import ui, events
from pymetadata.console import console
from starlette.formparsers import MultiPartParser

MultiPartParser.spool_max_size = 1024 * 1024 * 20  # 20 MB

from urllib.parse import urlparse

def is_valid_url(url):
    result = urlparse(url)
    return all([result.scheme, result.netloc])


@ui.page('/', title='runfrog', favicon="./static/frog.png", dark=False)
def homepage():
    # navigation header
    with ui.header().classes('items-center justify-between'):
        # ui.avatar('favorite_border')
        with ui.row().classes('max-sm:hidden'):
            ui.button('Home', icon='home').props('flat color=white')
            ui.button('API', icon='api').props('flat color=white')
            ui.button('Dashboard', icon='analytics').props('flat color=white')
        with ui.row().classes('sm:hidden'):
            ui.button(icon='home').props('flat color=white')
            ui.button(icon='api').props('flat color=white')
            ui.button(icon='dashboard').props('flat color=white')

        ui.button(icon='menu').props('flat color=white')

    with ui.row().classes('w-full'):
        ui.html(
            'Upload an <strong>SBML file</strong> or <strong>COMBINE archive</strong> (OMEX), or enter a URL.',
            sanitize=False
        )

        with ui.tabs().classes('w-full') as tabs:
            ui.tab('file', label='Upload File', icon='file_upload')
            ui.tab('url', label='Submit URL', icon='link')

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

    with ui.footer().style('background-color: #3874c8'):
        ui.label('FOOTER')
        # Report issue; source code, copyright, webpage
        # By using any part of this service, you agree to the terms of the privacy notice.
        ui.link('Visit other page', other_page)
        ui.link('Visit dark page', dark_page)


@ui.page('/page_layout')
def page_layout():
    ui.label('CONTENT')
    [ui.label(f'Line {i}') for i in range(100)]
    with ui.header(elevated=True).style('background-color: #3874c8').classes('items-center justify-between'):
        ui.label('HEADER')
        ui.button(on_click=lambda: right_drawer.toggle(), icon='menu').props('flat color=white')
    with ui.left_drawer(top_corner=True, bottom_corner=True).style('background-color: #d7e3f4'):
        ui.label('LEFT DRAWER')
    with ui.right_drawer(fixed=False).style('background-color: #ebf1fa').props('bordered') as right_drawer:
        ui.label('RIGHT DRAWER')
    with ui.footer().style('background-color: #3874c8'):
        ui.label('FOOTER')

@ui.page('/other_page')
def other_page():
    ui.label('Welcome to the other side')

@ui.page('/dark_page', dark=True)
def dark_page():
    ui.label('Welcome to the dark side')


async def handle_file_upload(e: events.UploadEventArguments):
    ui.notify(f'Uploaded {e.file.name}')
    # markdown.content = e.file.name

    file: ui.upload.FileUpload = e.file
    await file.read()



    console.print("Uploaded " + e.file.name)

    # with ui.header().classes('bg-blue-500 row items-center') as header:
    #     ui.image('images/mylogo.svg').classes('h-8 mr-4')
    #     ui.link('Home', '/').classes('text-white mr-4')
    #     ui.link('Features', '/features').classes('text-white mr-4')
    #     ui.link('Contact', '/contact').classes('text-white')

    # with ui.card():
    #     ui.label('Card content')
    #     ui.button('Add label', on_click=lambda: ui.label('Click!'))
    #     ui.timer(1.0, lambda: ui.label('Tick!'), once=True)


    # with ui.row():
    #     ui.label('label 1')
    #     ui.label('label 2')
    #     ui.label('label 3')

# ui.run_with(
#     title="RunFrog",
#     app=api,
# )

ui.run(
    title="RunFrog",
    fastapi_docs=True,
    native=False,
)

# native mode:
# see: https://github.com/zauberzeug/nicegui/issues/1841
# sudo apt install gobject-introspection libgirepository-1.0-dev



