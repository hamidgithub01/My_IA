
from pathlib import Path
from datetime import date, datetime

from nicegui import ui

from components.header import create_header
from services.data.expenses import add_expense


@ui.page('/expenses/add')
def add_expense_page():

    create_header('Add Expense')

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
    # Page
    # --------------------------------------------------

    with ui.column().classes('expenses-page'):

        # --------------------------------------------------
        # Header
        # --------------------------------------------------

        with ui.column().classes('expenses-heading'):

            ui.label(
                'Add Expense'
            ).classes('expenses-title')

            ui.label(
                'Record a new expense.'
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
                value=date.today().isoformat(),
            ).props(
                'type=date'
            ).classes('expense-input')

            time_input = ui.input(
                'Time',
                value=datetime.now().strftime('%H:%M'),
            ).props(
                'type=time'
            ).classes('expense-input')

            category_input = ui.input(
                'Category'
            ).classes('expense-input')

            description_input = ui.input(
                'Description'
            ).classes('expense-input')

            amount_input = ui.number(
                'Amount',
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

                def save_expense():

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

                    expense_date = date.fromisoformat(
                        date_input.value
                    )

                    expense_time = datetime.strptime(
                        time_input.value,
                        '%H:%M',
                    ).time()

                    amount = float(
                        amount_input.value
                    )

                    # ------------------------------------------
                    # Save
                    # ------------------------------------------

                    add_expense(
                        expense_date,
                        expense_time,
                        category_input.value.strip(),
                        (
                            description_input.value.strip()
                            if description_input.value
                            else ''
                        ),
                        amount,
                    )

                    ui.notify(
                        'Expense added successfully.',
                        type='positive',
                    )

                    ui.navigate.to(
                        '/expenses'
                    )

                ui.button(
                    'Save Expense',
                    icon='save',
                    on_click=save_expense,
                )

