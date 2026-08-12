from pathlib import Path

from nicegui import ui

from components.header import create_header
from services.data.expenses import (
    get_expense,
    delete_expense,
)


@ui.page('/expenses/{expense_id}')
def expense_details_page(expense_id: int):

    create_header('Expense Details')

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
    # Page
    # --------------------------------------------------

    with ui.column().classes('expenses-page'):

        with ui.row().classes('expense-details-header'):

            with ui.column().classes('expenses-heading'):

                ui.label(
                    'Expense Details'
                ).classes('expenses-title')

                ui.label(
                    'View the complete expense information.'
                ).classes('expenses-subtitle')

        # --------------------------------------------------
        # Details Card
        # --------------------------------------------------

        with ui.card().classes('expense-details-card'):

            ui.label(
                'Expense Information'
            ).classes('expenses-section-title')

            # ID
            with ui.row().classes('expense-detail-row'):

                ui.label(
                    'ID'
                ).classes('expense-detail-label')

                ui.label(
                    str(expense['ID'])
                ).classes('expense-detail-value')

            ui.separator()

            # Date
            with ui.row().classes('expense-detail-row'):

                ui.label(
                    'Date'
                ).classes('expense-detail-label')

                ui.label(
                    str(expense['Date'])
                ).classes('expense-detail-value')

            ui.separator()

            # Time
            with ui.row().classes('expense-detail-row'):

                ui.label(
                    'Time'
                ).classes('expense-detail-label')

                ui.label(
                    str(expense['Time'])[:5]
                ).classes('expense-detail-value')

            ui.separator()

            # Category
            with ui.row().classes('expense-detail-row'):

                ui.label(
                    'Category'
                ).classes('expense-detail-label')

                ui.label(
                    expense['Category'] or ''
                ).classes('expense-detail-value')

            ui.separator()

            # Description
            with ui.row().classes('expense-detail-row'):

                ui.label(
                    'Description'
                ).classes('expense-detail-label')

                ui.label(
                    expense['Description'] or '—'
                ).classes('expense-detail-value')

            ui.separator()

            # Amount
            with ui.row().classes('expense-detail-row'):

                ui.label(
                    'Amount'
                ).classes('expense-detail-label')

                ui.label(
                    f"{float(expense['Amount']):,.2f}"
                ).classes(
                    'expense-detail-value expense-detail-amount'
                )

            # --------------------------------------------------
            # Actions
            # --------------------------------------------------

            with ui.row().classes(
                'expense-details-actions'
            ):

                ui.button(
                    'Back',
                    icon='arrow_back',
                    on_click=lambda: ui.navigate.to(
                        '/expenses'
                    )
                ).props('flat')

                ui.button(
                    'Edit',
                    icon='edit',
                    on_click=lambda: ui.navigate.to(
                        f"/expenses/{expense_id}/edit"
                    )
                )

                def delete_current_expense():

                    delete_expense(expense_id)

                    ui.notify(
                        'Expense deleted successfully.',
                        type='positive',
                    )

                    ui.navigate.to(
                        '/expenses'
                    )

                ui.button(
                    'Delete',
                    icon='delete',
                    on_click=delete_current_expense,
                ).props(
                    'color=negative'
                )