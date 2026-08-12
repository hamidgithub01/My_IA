from datetime import date

from nicegui import ui

from components.header import create_header
from services.data.budgets import add_budget


@ui.page('/budgets/add')
def add_budget_page():
    create_header('Add Budget')

    with ui.column().classes('w-full max-w-2xl mx-auto p-6 gap-4'):

        ui.label('Add New Budget').classes(
            'text-2xl font-bold'
        )

        ui.label(
            'Create a monthly spending limit for a category.'
        ).classes('text-gray-600')

        # Month
        month = ui.date(
            value=date.today().replace(day=1)
        ).props('mask="YYYY-MM-DD"')

        # Category
        category = ui.input(
            label='Category',
            placeholder='e.g. Rent, Food, Transport'
        ).classes('w-full')

        # Limit
        budget_limit = ui.number(
            label='Budget Limit',
            min=0,
            precision=2,
            format='%.2f'
        ).classes('w-full')

        # Notes
        notes = ui.textarea(
            label='Notes',
            placeholder='Optional notes...'
        ).classes('w-full')

        # Status message
        message = ui.label().classes('text-sm')

        def save_budget():
            # Validation
            if not month.value:
                message.set_text('Please select a month.')
                return

            if not category.value or not category.value.strip():
                message.set_text('Please enter a category.')
                return

            if budget_limit.value is None or budget_limit.value <= 0:
                message.set_text('Budget limit must be greater than 0.')
                return

            try:
                selected_month = date.fromisoformat(
                    month.value
                ).replace(day=1)

                add_budget(
                    selected_month,
                    category.value.strip(),
                    budget_limit.value,
                    notes.value.strip() if notes.value else '',
                )

                ui.notify(
                    'Budget added successfully!',
                    type='positive'
                )

                ui.navigate.to('/budgets')

            except Exception as e:
                message.set_text(
                    f'Error while saving budget: {e}'
                )

        def cancel():
            ui.navigate.to('/budgets')

        with ui.row().classes('gap-3'):

            ui.button(
                'Save Budget',
                icon='save',
                on_click=save_budget
            ).props('color=primary')

            ui.button(
                'Cancel',
                icon='close',
                on_click=cancel
            ).props('flat')