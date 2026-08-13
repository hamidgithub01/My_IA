from nicegui import ui

NAVIGATION = [
{
'title': None,
'items': [
('Dashboard', '/', 'dashboard'),
],
},


{
    'title': 'FINANCE',
    'items': [
        ('Income', '/income', 'payments'),
        ('Expenses', '/expenses', 'shopping_cart'),
        ('Budgets', '/budgets', 'account_balance_wallet'),
        ('Recurring', '/recurring', 'autorenew'),
    ],
},

{
    'title': 'LIFE',
    'items': [
        ('Days', '/days', 'calendar_month'),
        ('Events', '/events', 'event'),
        ('Activities', '/activities', 'directions_run'),
        ('Social', '/social', 'groups'),
        ('Travel', '/travel', 'flight'),
    ],
},

{
    'title': 'HEALTH',
    'items': [
        ('Health', '/health', 'favorite'),
        ('Sleep', '/sleep', 'bedtime'),
    ],
},

{
    'title': 'PLANNING',
    'items': [
        ('Plans', '/plans', 'event_note'),
        ('Goals', '/goals', 'flag'),
    ],
},

{
    'title': 'AI',
    'items': [
        ('Predictions', '/predictions', 'psychology'),
        ('Analysis', '/analysis', 'analytics'),
    ],
},

{
    'title': 'REPORTS',
    'items': [
        ('Reports', '/reports', 'description'),
    ],
},

{
    'title': None,
    'items': [
        ('Settings', '/settings', 'settings'),
    ],
},


]

def create_sidebar(active_page=None):
        
    drawer = ui.left_drawer(
    value=True,
    bordered=True,
    ).classes('app-sidebar')


    with drawer:

        # -------------------------------------------------
        # SIDEBAR HEADER
        # -------------------------------------------------

        with ui.row().classes('sidebar-header'):

            ui.icon(
                'auto_awesome'
            ).classes('sidebar-brand-icon')

            with ui.column().classes('sidebar-brand-text'):

                ui.label(
                    'Personal Finance'
                ).classes('sidebar-brand-title')

                ui.label(
                    'AI Manager'
                ).classes('sidebar-brand-subtitle')

        ui.separator()

        # -------------------------------------------------
        # NAVIGATION
        # -------------------------------------------------

        for section in NAVIGATION:

            section_title = section['title']
            items = section['items']

            if section_title:

                ui.label(
                    section_title
                ).classes('sidebar-section-title')

            for label, path, icon in items:

                button = ui.button(
                    label,
                    icon=icon,
                    on_click=lambda path=path:
                        ui.navigate.to(path),
                ).props(
                    'flat no-caps'
                ).classes('sidebar-item')

                if active_page == label:
                    button.classes('sidebar-item-active')

    return drawer
