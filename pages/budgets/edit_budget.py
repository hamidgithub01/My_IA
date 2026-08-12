from datetime import datetime
from decimal import Decimal

from nicegui import ui

from components.header import create_header
from services.data.budgets import (
    get_budget,
    update_budget,
)


@ui.page('/budgets/edit')
def edit_budget_page():

    # --------------------------------------------------
    # Get URL parameters
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
    # Page
    # --------------------------------------------------

    with ui.column().classes(
        'w-full p-6 gap-6'
    ):

        # Page header
        with ui.row().classes(
            'w-full items-center justify-between'
        ):

            with ui.column().classes('gap-1'):

                ui.label(
                    'Edit Budget'
                ).classes(
                    'text-3xl font-bold'
                )

                ui.label(
                    'Update the monthly spending limit.'
                ).classes(
                    'text-gray-600'
                )

            ui.button(
                'Cancel',
                icon='arrow_back',
                on_click=lambda: ui.navigate.to(
                    f'/budgets/details?month={month}&category={category}'
                )
            ).props('flat')

        # --------------------------------------------------
        # Form
        # --------------------------------------------------

        with ui.card().classes(
            'w-full max-w-2xl'
        ):

            with ui.column().classes(
                'w-full gap-5'
            ):

                # Month
                ui.input(
                    label='Month',
                    value=str(budget['Month'])
                ).props(
                    'readonly'
                ).classes(
                    'w-full'
                )

                # Category
                ui.input(
                    label='Category',
                    value=budget['Category']
                ).props(
                    'readonly'
                ).classes(
                    'w-full'
                )

                # Limit
                limit_input = ui.number(
                    label='Monthly Limit',
                    value=float(budget['Limit']),
                    min=0,
                    precision=2
                ).classes(
                    'w-full'
                )

                # Notes
                notes_input = ui.textarea(
                    label='Notes',
                    value=budget['Notes'] or ''
                ).classes(
                    'w-full'
                )

                # --------------------------------------------------
                # Save
                # --------------------------------------------------

                def save_budget():

                    # Validate limit
                    if limit_input.value is None:

                        ui.notify(
                            'Please enter a budget limit.',
                            type='negative'
                        )

                        return

                    try:

                        budget_limit = Decimal(
                            str(limit_input.value)
                        )

                    except Exception:

                        ui.notify(
                            'Invalid budget limit.',
                            type='negative'
                        )

                        return

                    # Prevent negative values
                    if budget_limit < 0:

                        ui.notify(
                            'Budget limit cannot be negative.',
                            type='negative'
                        )

                        return

                    notes = notes_input.value or ''

                    # Update database
                    update_budget(
                        month_date,
                        category,
                        budget_limit,
                        notes
                    )

                    ui.notify(
                        'Budget updated successfully.',
                        type='positive'
                    )

                    # Return to details
                    ui.navigate.to(
                        f'/budgets/details?'
                        f'month={month}&category={category}'
                    )

                ui.button(
                    'Save Changes',
                    icon='save',
                    on_click=save_budget
                ).props(
                    'color=primary'
                ).classes(
                    'w-full'
                )
