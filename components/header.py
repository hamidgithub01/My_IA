
from pathlib import Path

from nicegui import ui

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOGO = PROJECT_ROOT / 'assets' / 'budget.png'

def load_main_css():
    css_file = Path('styles/main.css')

    if css_file.exists():
        css_version = css_file.stat().st_mtime_ns

        ui.add_head_html(
            f'<link rel="stylesheet" '
            f'href="/styles/main.css?v={css_version}">'
        )


def create_header(title='Dashboard'):

    # Load shared application CSS
    load_main_css()

    navigation = {
        

        'Income': [
            ('Records', '/income', 'list'),
            ('Add Income', '/income/add', 'add'),
        ],

        'Expenses': [
            ('Records', '/expenses', 'list'),
            ('Add Expense', '/expenses/add', 'add'),
        ],

        'Budgets': [
            ('Overview', '/budgets', 'account_balance_wallet'),
            ('Add Budget', '/budgets/add', 'add'),
        ],

        'Days': [
            ('Daily Records', '/days', 'calendar_month'),
            ('Add Day', '/days/add', 'add'),
        ],

        'Events': [
            ('Records', '/events', 'event'),
            ('Add Event', '/events/add', 'add'),
        ],

        'Analysis': [
            ('Overview', '/analysis', 'analytics'),
        ],

        'Reports': [
            ('Reports', '/reports', 'description'),
        ],

        'Settings': [
            ('Settings', '/settings', 'settings'),
        ],
    }

    main_navigation = [
        ('Income', '/income', 'payments'),
        ('Expenses', '/expenses', 'shopping_cart'),
        ('Budgets', '/budgets', 'account_balance_wallet'),
        ('Days', '/days', 'calendar_month'),
        ('Events', '/events', 'event'),
        ('Analysis', '/analysis', 'analytics'),
        ('Reports', '/reports', 'description'),
        ('Settings', '/settings', 'settings'),
    ]

    with ui.header().classes('app-header'):

        # Application title
        with ui.row().classes('header-top'):

            with ui.link(target='/').classes('app-logo-link'):
                ui.image(str(LOGO)).classes('app-logo')
            ui.label(
                title
            ).classes('current-page')

        # Main navigation
        with ui.row().classes('main-navigation'):

            for label, path, icon in main_navigation:

                button = ui.button(
                    label,
                    icon=icon,
                    on_click=lambda path=path:
                        ui.navigate.to(path)
                ).props('flat')

                if label == title:
                    button.classes('navigation-active')

        # Section navigation
        section_items = navigation.get(title, [])

        if section_items:

            with ui.row().classes('section-navigation'):

                for label, path, icon in section_items:

                    ui.button(
                        label,
                        icon=icon,
                        on_click=lambda path=path:
                            ui.navigate.to(path)
                    ).props('flat dense')