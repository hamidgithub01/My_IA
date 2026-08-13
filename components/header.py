
from pathlib import Path

from nicegui import ui

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOGO = PROJECT_ROOT / 'assets' / 'budget.png'

def load_main_css():
    css_file = PROJECT_ROOT / 'styles' / 'main.css'


    if css_file.exists():

        css_version = css_file.stat().st_mtime_ns

        ui.add_head_html(
            f'<link rel="stylesheet" '
            f'href="/styles/main.css?v={css_version}">'
        )


def create_header(title='Dashboard', drawer=None):


    load_main_css()

    with ui.header().classes('app-header'):

        # -------------------------------------------------
        # LEFT
        # -------------------------------------------------

        with ui.row().classes('header-left'):

            if drawer is not None:

                ui.button(
                    icon='menu',
                    on_click=drawer.toggle,
                ).props(
                    'flat round'
                ).classes('menu-button')

            with ui.link(
                target='/'
            ).classes('app-logo-link'):

                ui.image(
                    str(LOGO)
                ).classes('app-logo')

            with ui.column().classes(
                'header-title-group'
            ):

                ui.label(
                    'Personal Finance AI'
                ).classes('app-title')

                ui.label(
                    title
                ).classes('current-page')

        # -------------------------------------------------
        # RIGHT
        # -------------------------------------------------

        with ui.row().classes('header-actions'):

            ui.button(
                icon='search',
                on_click=lambda: ui.notify(
                    'Search will be available soon.'
                ),
            ).props(
                'flat round'
            ).classes('header-action')

            ui.button(
                icon='notifications_none',
                on_click=lambda: ui.notify(
                    'Notifications will be available soon.'
                ),
            ).props(
                'flat round'
            ).classes('header-action')

            ui.button(
                icon='settings',
                on_click=lambda: ui.navigate.to(
                    '/settings'
                ),
            ).props(
                'flat round'
            ).classes('header-action')
