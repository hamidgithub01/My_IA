from nicegui import ui

from components.header import create_header
from components.sidebar import create_sidebar

def create_layout(
    title='Dashboard',
    active_page=None,
    ):

    
    # Create the sidebar first
    drawer = create_sidebar(
        active_page=active_page or title
    )

    # Pass the sidebar to the header
    # so the menu button can control it
    create_header(
        title=title,
        drawer=drawer,
    )

    return drawer


def create_page_layout(
    title='Dashboard',
    active_page=None,
    ):


    create_layout(
        title=title,
        active_page=active_page,
    )

    return ui.column().classes('page-content')
