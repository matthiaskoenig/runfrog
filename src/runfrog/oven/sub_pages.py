from nicegui import ui
from uuid import uuid4

def root():
    ui.label(f'This ID {str(uuid4())[:6]} changes only on reload.')
    ui.separator()
    ui.sub_pages({'/': main, '/other': other})

def main():
    ui.label('Main page content')
    ui.link('Go to other page', '/other')

def other():
    ui.label('Another page content')
    ui.link('Go to main page', '/')

ui.run(root)
