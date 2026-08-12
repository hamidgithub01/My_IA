
from datetime import datetime

from nicegui import ui

from components.header import create_header
from services.data.budgets import (
    get_budget,
    delete_budget,
)


@ui.page('/budgets/details')
def budget_details_page():

    # --------------------------------------------------
    # Get parameters from URL
    # --------------------------------------------------

    month = ui.context.client.request.query_params.get('month')
    category = ui.context.client.request.query_params.get('category')

    create_header('Budgets')

    # --------------------------------------------------
    # Validate parameters
    # --------------------------------------------------

    if not month or not category:

        with ui.column().classes('w-full p-6 gap-4'):

            ui.label(
                'Budget not found'
            ).classes(
                'text-2xl font-bold'
            )

            ui.label(
                'The required budget information is missing.'
            ).classes(
                'text-gray-600'
            )

            ui.button(
                'Back to Budgets',
                icon='arrow_back',
                on_click=lambda: ui.navigate.to('/budgets')
            )

        return

    # --------------------------------------------------
    # Convert month
    # --------------------------------------------------

    try:

        month_date = datetime.strptime(
            month,
            '%Y-%m-%d'
        ).date()

    except ValueError:

        with ui.column().classes('w-full p-6 gap-4'):

            ui.label(
                'Invalid month'
            ).classes(
                'text-2xl font-bold'
            )

            ui.button(
                'Back to Budgets',
                icon='arrow_back',
                on_click=lambda: ui.navigate.to('/budgets')
            )

        return

    # --------------------------------------------------
    # Load budget
    # --------------------------------------------------

    budget = get_budget(
        month_date,
        category
    )

    # --------------------------------------------------
    # Budget not found
    # --------------------------------------------------

    if not budget:

        with ui.column().classes('w-full p-6 gap-4'):

            ui.label(
                'Budget not found'
            ).classes(
                'text-2xl font-bold'
            )

            ui.label(
                f'No budget was found for {month} / {category}.'
            ).classes(
                'text-gray-600'
            )

            ui.button(
                'Back to Budgets',
                icon='arrow_back',
                on_click=lambda: ui.navigate.to('/budgets')
            )

        return

    # --------------------------------------------------
    # Delete confirmation dialog
    # --------------------------------------------------

    with ui.dialog() as delete_dialog:

        with ui.card().classes(
            'w-full max-w-md p-6'
        ):

            ui.icon(
                'warning',
                size='48px'
            )

            ui.label(
                'Delete Budget?'
            ).classes(
                'text-2xl font-bold'
            )

            ui.label(
                'Are you sure you want to delete this budget?'
            ).classes(
                'text-gray-700'
            )

            ui.label(
                f'{budget["Month"]} — {budget["Category"]}'
            ).classes(
                'font-semibold'
            )

            ui.label(
                'This action cannot be undone.'
            ).classes(
                'text-red-600 text-sm'
            )

            with ui.row().classes(
                'w-full justify-end gap-2 mt-4'
            ):

                ui.button(
                    'Cancel',
                    on_click=delete_dialog.close
                ).props(
                    'flat'
                )

                def confirm_delete():

                    delete_budget(
                        month_date,
                        category
                    )

                    delete_dialog.close()

                    ui.notify(
                        'Budget deleted successfully.',
                        type='positive'
                    )

                    ui.navigate.to('/budgets')

                ui.button(
                    'Delete',
                    icon='delete',
                    on_click=confirm_delete
                ).props(
                    'color=negative'
                )

    # --------------------------------------------------
    # Page content
    # --------------------------------------------------

    with ui.column().classes(
        'w-full p-6 gap-6'
    ):

        # --------------------------------------------------
        # Page header
        # --------------------------------------------------

        with ui.row().classes(
            'w-full items-center justify-between'
        ):

            with ui.column().classes('gap-1'):

                ui.label(
                    'Budget Details'
                ).classes(
                    'text-3xl font-bold'
                )

                ui.label(
                    'View the details of this budget.'
                ).classes(
                    'text-gray-600'
                )

            ui.button(
                'Back to Budgets',
                icon='arrow_back',
                on_click=lambda: ui.navigate.to('/budgets')
            ).props(
                'flat'
            )

        # --------------------------------------------------
        # Budget information
        # --------------------------------------------------

        with ui.card().classes(
            'w-full p-6'
        ):

            with ui.column().classes(
                'w-full gap-5'
            ):

                # Month
                with ui.row().classes(
                    'w-full items-center justify-between'
                ):

                    ui.label(
                        'Month'
                    ).classes(
                        'text-gray-500'
                    )

                    ui.label(
                        str(budget['Month'])
                    ).classes(
                        'font-semibold'
                    )

                ui.separator()

                # Category
                with ui.row().classes(
                    'w-full items-center justify-between'
                ):

                    ui.label(
                        'Category'
                    ).classes(
                        'text-gray-500'
                    )

                    ui.label(
                        budget['Category']
                    ).classes(
                        'font-semibold'
                    )

                ui.separator()

                # Limit
                with ui.row().classes(
                    'w-full items-center justify-between'
                ):

                    ui.label(
                        'Monthly Limit'
                    ).classes(
                        'text-gray-500'
                    )

                    ui.label(
                        f"{float(budget['Limit']):,.2f}"
                    ).classes(
                        'text-2xl font-bold'
                    )

                ui.separator()

                # Notes
                with ui.column().classes(
                    'w-full gap-2'
                ):

                    ui.label(
                        'Notes'
                    ).classes(
                        'text-gray-500'
                    )

                    ui.label(
                        budget['Notes'] or 'No notes'
                    ).classes(
                        'font-medium'
                    )

        # --------------------------------------------------
        # Actions
        # --------------------------------------------------

        with ui.row().classes('gap-3'):

            ui.button(
                'Edit Budget',
                icon='edit',
                on_click=lambda: ui.navigate.to(
                    f'/budgets/edit?'
                    f'month={month}&category={category}'
                )
            ).props(
                'color=primary'
            )

            ui.button(
                'Delete Budget',
                icon='delete',
                on_click=delete_dialog.open
            ).props(
                'color=negative'
            )