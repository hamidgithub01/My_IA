
from pathlib import Path
from datetime import date, datetime

from nicegui import ui

from components.header import create_header
from services.data.expenses import (
    get_expense,
    update_expense,
)


@ui.page('/expenses/{expense_id}/edit')
def edit_expense_page(expense_id: int):

    create_header('Edit Expense')

    # --------------------------------------------------
    # CSS
    # --------------------------------------------------

    css_file = Path('styles/expenses.css')

    if css_file.exists():
        css_version = css_file.stat().st_mtime_ns

        ui.add_head_html(
            f'<link rel="stylesheet" '
            f'href="/styles/expenses.css?v={css_version}">'
        )

    # --------------------------------------------------
    # Load expense
    # --------------------------------------------------

    expense = get_expense(expense_id)

    if not expense:

        with ui.column().classes('expenses-page'):

            ui.label(
                'Expense not found.'
            ).classes('expenses-title')

            ui.button(
                'Back to Expenses',
                icon='arrow_back',
                on_click=lambda: ui.navigate.to(
                    '/expenses'
                )
            )

        return

    # --------------------------------------------------
    # Prepare existing values
    # --------------------------------------------------

    expense_date = expense['Date']

    if isinstance(expense_date, date):
        expense_date_value = expense_date.isoformat()
    else:
        expense_date_value = str(expense_date)

    expense_time = expense['Time']

    if hasattr(expense_time, 'seconds'):
        total_seconds = expense_time.seconds
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60

        expense_time_value = (
            f'{hours:02d}:{minutes:02d}'
        )
    else:
        expense_time_value = str(expense_time)[:5]

    # --------------------------------------------------
    # Page
    # --------------------------------------------------

    with ui.column().classes('expenses-page'):

        with ui.column().classes('expenses-heading'):

            ui.label(
                'Edit Expense'
            ).classes('expenses-title')

            ui.label(
                'Update the expense information.'
            ).classes('expenses-subtitle')

        # --------------------------------------------------
        # Form
        # --------------------------------------------------

        with ui.card().classes('expense-form-card'):

            ui.label(
                'Expense Information'
            ).classes('expenses-section-title')

            date_input = ui.input(
                'Date',
                value=expense_date_value,
            ).props(
                'type=date'
            ).classes('expense-input')

            time_input = ui.input(
                'Time',
                value=expense_time_value,
            ).props(
                'type=time'
            ).classes('expense-input')

            category_input = ui.input(
                'Category',
                value=expense['Category'] or '',
            ).classes('expense-input')

            description_input = ui.input(
                'Description',
                value=expense['Description'] or '',
            ).classes('expense-input')

            amount_input = ui.number(
                'Amount',
                value=float(expense['Amount']),
                min=0,
                step=0.01,
            ).classes('expense-input')

            # --------------------------------------------------
            # Actions
            # --------------------------------------------------

            with ui.row().classes(
                'expense-form-actions'
            ):

                ui.button(
                    'Cancel',
                    icon='arrow_back',
                    on_click=lambda: ui.navigate.to(
                        '/expenses'
                    )
                ).props('flat')

                def save_changes():

                    # ------------------------------------------
                    # Validation
                    # ------------------------------------------

                    if not date_input.value:

                        ui.notify(
                            'Please enter a date.',
                            type='negative',
                        )

                        return

                    if not time_input.value:

                        ui.notify(
                            'Please enter a time.',
                            type='negative',
                        )

                        return

                    if not category_input.value:

                        ui.notify(
                            'Please enter a category.',
                            type='negative',
                        )

                        return

                    if (
                        amount_input.value is None
                        or float(amount_input.value) <= 0
                    ):

                        ui.notify(
                            'Please enter a valid amount.',
                            type='negative',
                        )

                        return

                    # ------------------------------------------
                    # Convert values
                    # ------------------------------------------

                    new_date = date.fromisoformat(
                        date_input.value
                    )

                    new_time = datetime.strptime(
                        time_input.value,
                        '%H:%M',
                    ).time()

                    new_amount = float(
                        amount_input.value
                    )

                    # ------------------------------------------
                    # Update
                    # ------------------------------------------

                    update_expense(
                        expense_id,
                        new_date,
                        new_time,
                        category_input.value.strip(),
                        (
                            description_input.value.strip()
                            if description_input.value
                            else ''
                        ),
                        new_amount,
                    )

                    ui.notify(
                        'Expense updated successfully.',
                        type='positive',
                    )

                    ui.navigate.to(
                        '/expenses'
                    )

                ui.button(
                    'Save Changes',
                    icon='save',
                    on_click=save_changes,
                )
