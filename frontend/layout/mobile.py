from nicegui import ui


# ==========================================================
# MOBILE NAVIGATION
# ==========================================================

def create_mobile_navigation():

    with ui.dialog() as dialog:

        with ui.card().classes(
            'w-full max-w-sm '
            'rounded-2xl '
            'p-0 '
            'overflow-hidden'
        ):

            # ==================================================
            # HEADER
            # ==================================================

            with ui.row().classes(
                'w-full '
                'items-center '
                'justify-between '
                'px-5 '
                'py-4 '
                'border-b '
                'border-gray-200'
            ):

                with ui.row().classes(
                    'items-center '
                    'gap-3'
                ):

                    with ui.element('div').classes(
                        'app-icon'
                    ):
                        ui.icon(
                            'account_balance_wallet'
                        ).classes(
                            'text-xl'
                        )

                    with ui.column().classes(
                        'gap-0'
                    ):

                        ui.label(
                            'Personal Finance'
                        ).classes(
                            'text-sm '
                            'font-bold '
                            'text-primary-app'
                        )

                        ui.label(
                            'AI'
                        ).classes(
                            'text-xs '
                            'text-muted-app'
                        )

                ui.button(
                    icon='close',
                    on_click=dialog.close,
                ).props(
                    'flat round'
                ).classes(
                    'text-gray-500'
                )

            # ==================================================
            # NAVIGATION
            # ==================================================

            with ui.column().classes(
                'w-full '
                'p-4 '
                'gap-1'
            ):

                _mobile_navigation_item(
                    'Dashboard',
                    'dashboard',
                    '/',
                    dialog,
                )

                _mobile_navigation_item(
                    'Expenses',
                    'payments',
                    '/expenses',
                    dialog,
                )

                _mobile_navigation_item(
                    'Income',
                    'account_balance',
                    '/income',
                    dialog,
                )

                _mobile_navigation_item(
                    'Budgets',
                    'account_balance_wallet',
                    '/budgets',
                    dialog,
                )

                _mobile_navigation_item(
                    'Predictions',
                    'auto_awesome',
                    '/predictions',
                    dialog,
                )

                _mobile_navigation_item(
                    'Analysis',
                    'analytics',
                    '/analysis',
                    dialog,
                )

                _mobile_navigation_item(
                    'Reports',
                    'description',
                    '/reports',
                    dialog,
                )

                _mobile_navigation_item(
                    'Days',
                    'calendar_today',
                    '/days',
                    dialog,
                )

                _mobile_navigation_item(
                    'Events',
                    'event',
                    '/events',
                    dialog,
                )

                _mobile_navigation_item(
                    'Health',
                    'favorite',
                    '/health',
                    dialog,
                )

                _mobile_navigation_item(
                    'Sleep',
                    'bedtime',
                    '/sleep',
                    dialog,
                )

                ui.separator().classes(
                    'my-2'
                )

                _mobile_navigation_item(
                    'Settings',
                    'settings',
                    '/settings',
                    dialog,
                )

    return dialog


# ==========================================================
# MOBILE NAVIGATION ITEM
# ==========================================================

def _mobile_navigation_item(
    label,
    icon,
    route,
    dialog,
):

    with ui.button(
        on_click=lambda: _navigate(
            route,
            dialog,
        ),
    ).props(
        'flat align=left no-caps'
    ).classes(
        'w-full '
        'justify-start '
        'px-3 '
        'py-3 '
        'rounded-[var(--radius-md)] '
        'text-gray-700 '
        'hover:bg-gray-50'
    ):

        with ui.row().classes(
            'items-center '
            'gap-3 '
            'w-full'
        ):

            ui.icon(
                icon
            ).classes(
                'text-xl '
                'shrink-0'
            )

            ui.label(
                label
            ).classes(
                'text-sm'
            )


# ==========================================================
# NAVIGATION
# ==========================================================

def _navigate(
    route,
    dialog,
):

    dialog.close()
    ui.navigate.to(route)