from nicegui import ui


# ==========================================================
# NAVIGATION
# ==========================================================

NAVIGATION_SECTIONS = [
    {
        'title': 'MAIN',
        'items': [
            {
                'label': 'Dashboard',
                'icon': 'dashboard',
                'route': '/',
                'key': 'dashboard',
            },
            {
                'label': 'Expenses',
                'icon': 'payments',
                'route': '/expenses',
                'key': 'expenses',
            },
            {
                'label': 'Income',
                'icon': 'account_balance',
                'route': '/income',
                'key': 'income',
            },
            {
                'label': 'Budgets',
                'icon': 'account_balance_wallet',
                'route': '/budgets',
                'key': 'budgets',
            },
        ],
    },
    {
        'title': 'AI & PREDICTIONS',
        'items': [
            {
                'label': 'Predictions',
                'icon': 'auto_awesome',
                'route': '/predictions',
                'key': 'predictions',
            },
            {
                'label': 'Analysis',
                'icon': 'analytics',
                'route': '/analysis',
                'key': 'analysis',
            },
            {
                'label': 'Reports',
                'icon': 'description',
                'route': '/reports',
                'key': 'reports',
            },
        ],
    },
    {
        'title': 'MACHINE LEARNING',
        'items': [
            {
                'label': 'Data',
                'icon': 'database',
                'route': '/data',
                'key': 'data',
            },
            {
                'label': 'Features',
                'icon': 'tune',
                'route': '/features',
                'key': 'features',
            },
            {
                'label': 'Targets',
                'icon': 'track_changes',
                'route': '/targets',
                'key': 'targets',
            },
            {
                'label': 'Training',
                'icon': 'model_training',
                'route': '/training',
                'key': 'training',
            },
            {
                'label': 'Models',
                'icon': 'psychology',
                'route': '/models',
                'key': 'models',
            },
            {
                'label': 'Evaluation',
                'icon': 'fact_check',
                'route': '/evaluation',
                'key': 'evaluation',
            },
        ],
    },
    {
        'title': 'MONITORING',
        'items': [
            {
                'label': 'Monitoring',
                'icon': 'monitor_heart',
                'route': '/monitoring',
                'key': 'monitoring',
            },
            {
                'label': 'Patterns',
                'icon': 'pattern',
                'route': '/patterns',
                'key': 'patterns',
            },
            {
                'label': 'Alerts',
                'icon': 'notifications',
                'route': '/alerts',
                'key': 'alerts',
            },
            {
                'label': 'Recommendations',
                'icon': 'lightbulb',
                'route': '/recommendations',
                'key': 'recommendations',
            },
        ],
    },
    {
        'title': 'LIFE & CONTEXT',
        'items': [
            {
                'label': 'Days',
                'icon': 'calendar_today',
                'route': '/days',
                'key': 'days',
            },
            {
                'label': 'Events',
                'icon': 'event',
                'route': '/events',
                'key': 'events',
            },
            {
                'label': 'Health',
                'icon': 'favorite',
                'route': '/health',
                'key': 'health',
            },
            {
                'label': 'Sleep',
                'icon': 'bedtime',
                'route': '/sleep',
                'key': 'sleep',
            },
        ],
    },
]


# ==========================================================
# SIDEBAR
# ==========================================================

def create_sidebar(active_page='dashboard'):
    """
    Create the persistent application sidebar.
    """

    with ui.left_drawer(
        value=True,
        bordered=True,
    ).classes(
        'bg-white '
        'border-r border-gray-200 '
        'w-64 '
        'z-30'
    ):

        with ui.column().classes(
            'w-full '
            'h-full '
            'p-4 '
            'gap-1'
        ):

            # ==================================================
            # BRAND
            # ==================================================

            with ui.row().classes(
                'w-full '
                'items-center '
                'gap-3 '
                'px-2 '
                'py-3 '
                'mb-5'
            ):

                with ui.element('div').classes(
                    'app-icon '
                    'shrink-0'
                ):
                    ui.icon(
                        'account_balance_wallet'
                    ).classes(
                        'text-xl'
                    )

                with ui.column().classes(
                    'gap-0 '
                    'min-w-0'
                ):

                    ui.label(
                        'Personal Finance'
                    ).classes(
                        'text-sm '
                        'font-bold '
                        'text-primary-app '
                        'truncate'
                    )

                    ui.label(
                        'AI'
                    ).classes(
                        'text-xs '
                        'text-muted-app'
                    )

            # ==================================================
            # NAVIGATION SECTIONS
            # ==================================================

            for section in NAVIGATION_SECTIONS:

                ui.label(
                    section['title']
                ).classes(
                    'px-3 '
                    'mb-2 '
                    'mt-2 '
                    'text-[10px] '
                    'font-semibold '
                    'tracking-wider '
                    'text-gray-400'
                )

                for item in section['items']:

                    _navigation_item(
                        item=item,
                        active_page=active_page,
                    )

            ui.space()

            # ==================================================
            # SETTINGS
            # ==================================================

            ui.separator().classes(
                'my-3'
            )

            _settings_item()


# ==========================================================
# NAVIGATION ITEM
# ==========================================================

def _navigation_item(
    item,
    active_page,
):

    is_active = item['key'] == active_page

    if is_active:

        classes = (
            'w-full '
            'justify-start '
            'px-3 '
            'py-2.5 '
            'rounded-[var(--radius-md)] '
            'bg-[var(--primary-soft)] '
            'text-primary '
            'font-semibold'
        )

    else:

        classes = (
            'w-full '
            'justify-start '
            'px-3 '
            'py-2.5 '
            'rounded-[var(--radius-md)] '
            'text-gray-600 '
            'hover:bg-gray-50 '
            'hover:text-gray-900'
        )

    with ui.button(
        on_click=lambda route=item['route']: (
            ui.navigate.to(route)
        ),
    ).props(
        'flat align=left no-caps'
    ).classes(
        classes
    ):

        with ui.row().classes(
            'items-center '
            'gap-3 '
            'w-full'
        ):

            ui.icon(
                item['icon']
            ).classes(
                'text-xl '
                'shrink-0'
            )

            ui.label(
                item['label']
            ).classes(
                'text-sm'
            )


# ==========================================================
# SETTINGS
# ==========================================================

def _settings_item():

    with ui.button(
        on_click=lambda: ui.navigate.to('/settings'),
    ).props(
        'flat align=left no-caps'
    ).classes(
        'w-full '
        'justify-start '
        'px-3 '
        'py-2.5 '
        'rounded-[var(--radius-md)] '
        'text-gray-600 '
        'hover:bg-gray-50 '
        'hover:text-gray-900'
    ):

        with ui.row().classes(
            'items-center '
            'gap-3 '
            'w-full'
        ):

            ui.icon(
                'settings'
            ).classes(
                'text-xl '
                'shrink-0'
            )

            ui.label(
                'Settings'
            ).classes(
                'text-sm'
            )