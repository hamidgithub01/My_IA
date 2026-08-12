
from nicegui import ui

from components.header import create_header
from services.data.budgets import get_budgets


@ui.page('/budgets')
def budget_overview_page():

    create_header('Budgets')

    with ui.column().classes('w-full p-6 gap-6'):

        # --------------------------------------------------
        # Page header
        # --------------------------------------------------

        with ui.row().classes(
            'w-full items-center justify-between'
        ):

            with ui.column().classes('gap-1'):

                ui.label(
                    'Budgets'
                ).classes(
                    'text-3xl font-bold'
                )

                ui.label(
                    'Manage your monthly spending limits.'
                ).classes(
                    'text-gray-600'
                )

            ui.button(
                'Add Budget',
                icon='add',
                on_click=lambda: ui.navigate.to('/budgets/add')
            ).props('color=primary')

        # --------------------------------------------------
        # Load budgets
        # --------------------------------------------------

        budgets = get_budgets()

        # --------------------------------------------------
        # Empty state
        # --------------------------------------------------

        if not budgets:

            with ui.card().classes(
                'w-full p-8 items-center'
            ):

                ui.icon(
                    'account_balance_wallet',
                    size='48px'
                )

                ui.label(
                    'No budgets found.'
                ).classes(
                    'text-xl font-semibold'
                )

                ui.label(
                    'Create your first budget to start tracking your spending limits.'
                ).classes(
                    'text-gray-600'
                )

                ui.button(
                    'Create Budget',
                    icon='add',
                    on_click=lambda: ui.navigate.to('/budgets/add')
                ).props('color=primary')

            return

        # --------------------------------------------------
        # Summary
        # --------------------------------------------------

        total_limit = sum(
            float(budget['Limit'])
            for budget in budgets
        )

        with ui.row().classes('w-full gap-4'):

            with ui.card().classes('flex-1'):

                ui.label(
                    'Total Budgets'
                ).classes(
                    'text-gray-500'
                )

                ui.label(
                    str(len(budgets))
                ).classes(
                    'text-3xl font-bold'
                )

            with ui.card().classes('flex-1'):

                ui.label(
                    'Total Monthly Limits'
                ).classes(
                    'text-gray-500'
                )

                ui.label(
                    f'{total_limit:,.2f}'
                ).classes(
                    'text-3xl font-bold'
                )

        # --------------------------------------------------
        # Budget table
        # --------------------------------------------------

        with ui.card().classes('w-full'):

            for budget in budgets:

                month = str(budget['Month'])
                category = budget['Category']

                with ui.row().classes(
                    'w-full items-center px-4 py-3 border-b'
                ):

                    # Month
                    with ui.column().classes('flex-1'):

                        ui.label(
                            'Month'
                        ).classes(
                            'text-xs text-gray-500'
                        )

                        ui.label(
                            month
                        ).classes(
                            'font-semibold'
                        )

                    # Category
                    with ui.column().classes('flex-1'):

                        ui.label(
                            'Category'
                        ).classes(
                            'text-xs text-gray-500'
                        )

                        ui.label(
                            category
                        ).classes(
                            'font-semibold'
                        )

                    # Limit
                    with ui.column().classes(
                        'flex-1 items-end'
                    ):

                        ui.label(
                            'Limit'
                        ).classes(
                            'text-xs text-gray-500'
                        )

                        ui.label(
                            f"{float(budget['Limit']):,.2f}"
                        ).classes(
                            'font-semibold'
                        )

                    # Notes
                    with ui.column().classes('flex-1'):

                        ui.label(
                            'Notes'
                        ).classes(
                            'text-xs text-gray-500'
                        )

                        ui.label(
                            budget['Notes'] or ''
                        ).classes(
                            'text-gray-600'
                        )

                    # View button
                    ui.button(
                        icon='visibility',
                        on_click=lambda
                        month=month,
                        category=category:
                        ui.navigate.to(
                            f'/budgets/details?'
                            f'month={month}&category={category}'
                        )
                    ).props(
                        'flat round'
                    ).tooltip(
                        'View budget'
                    )
