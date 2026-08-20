from nicegui import ui

from frontend.layout.mobile import create_mobile_navigation


# ==========================================================
# HEADER
# ==========================================================

def create_header(active_page='dashboard'):
    """
    Create the persistent application header.
    """

    page_titles = {
        'dashboard': 'Dashboard',
        'expenses': 'Expenses',
        'income': 'Income',
        'budgets': 'Budgets',
        'predictions': 'Predictions',
        'analysis': 'Analysis',
        'reports': 'Reports',
        'days': 'Days',
        'events': 'Events',
        'health': 'Health',
        'sleep': 'Sleep',
        'settings': 'Settings',
    }

    title = page_titles.get(
        active_page,
        'Personal Finance AI',
    )

    mobile_navigation = create_mobile_navigation()

    with ui.header().classes(
        'bg-white '
        'text-gray-900 '
        'border-b border-gray-200 '
        'h-16 '
        'px-0 '
        'z-40'
    ):

        with ui.row().classes(
            'w-full '
            'h-full '
            'items-center '
            'justify-between '
            'px-4 md:px-6 '
            'gap-4'
        ):

            # ==================================================
            # LEFT SIDE
            # ==================================================

            with ui.row().classes(
                'items-center '
                'gap-3 '
                'min-w-0'
            ):

                ui.button(
                    icon='menu',
                    on_click=mobile_navigation.open,
                ).props(
                    'flat round'
                ).classes(
                    'lg:hidden '
                    'text-gray-600'
                )

                with ui.column().classes(
                    'gap-0 '
                    'min-w-0'
                ):

                    ui.label(
                        title
                    ).classes(
                        'text-base md:text-lg '
                        'font-semibold '
                        'text-primary-app '
                        'truncate'
                    )

                    ui.label(
                        'Personal Finance AI'
                    ).classes(
                        'hidden sm:block '
                        'text-xs '
                        'text-muted-app'
                    )

            # ==================================================
            # RIGHT SIDE
            # ==================================================

            with ui.row().classes(
                'items-center '
                'gap-1 '
                'shrink-0'
            ):

                _notification_button()

                _user_button()


# ==========================================================
# NOTIFICATIONS
# ==========================================================

def _notification_button():

    with ui.button(
        icon='notifications_none'
    ).props(
        'flat round'
    ).classes(
        'text-gray-600'
    ):
        pass


# ==========================================================
# USER
# ==========================================================

def _user_button():

    with ui.button().props(
        'flat no-caps'
    ).classes(
        'px-2 '
        'rounded-lg'
    ):

        with ui.row().classes(
            'items-center '
            'gap-2'
        ):

            with ui.element('div').classes(
                'w-9 h-9 '
                'rounded-full '
                'bg-[var(--primary-soft)] '
                'text-primary '
                'flex '
                'items-center '
                'justify-center '
                'font-semibold'
            ):
                ui.label('H')

            with ui.column().classes(
                'hidden md:flex '
                'gap-0 '
                'text-left'
            ):

                ui.label(
                    'User'
                ).classes(
                    'text-sm '
                    'font-medium '
                    'text-primary-app'
                )

                ui.label(
                    'Personal account'
                ).classes(
                    'text-[11px] '
                    'text-muted-app'
                )