
from pathlib import Path

from nicegui import ui

from components.header import create_header
from services.data.expenses import get_expenses


@ui.page('/expenses')
def expense_records_page():

    create_header('Expenses')

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
    # Data
    # --------------------------------------------------

    expenses = get_expenses()

    # --------------------------------------------------
    # Page
    # --------------------------------------------------

    with ui.column().classes('expenses-page'):

        # --------------------------------------------------
        # Page Header
        # --------------------------------------------------

        with ui.row().classes('expenses-header'):

            with ui.column().classes('expenses-heading'):

                ui.label(
                    'Expenses'
                ).classes('expenses-title')

                ui.label(
                    'Manage and review your expenses.'
                ).classes('expenses-subtitle')

            ui.button(
                'Add Expense',
                icon='add',
                on_click=lambda: ui.navigate.to(
                    '/expenses/add'
                )
            ).classes('add-expense-button')

        # --------------------------------------------------
        # Expense Table
        # --------------------------------------------------

        with ui.card().classes('expenses-table-card'):

            ui.label(
                'Expense Records'
            ).classes('expenses-section-title')

            if not expenses:

                with ui.column().classes('expenses-empty'):

                    ui.icon(
                        'receipt_long',
                        size='48px'
                    )

                    ui.label(
                        'No expenses found.'
                    ).classes('expenses-empty-title')

                    ui.label(
                        'Add your first expense to get started.'
                    ).classes('expenses-empty-text')

                    ui.button(
                        'Add Expense',
                        icon='add',
                        on_click=lambda: ui.navigate.to(
                            '/expenses/add'
                        )
                    )

            else:

                columns = [
                    {
                        'name': 'date',
                        'label': 'Date',
                        'field': 'date',
                        'align': 'left',
                    },
                    {
                        'name': 'time',
                        'label': 'Time',
                        'field': 'time',
                        'align': 'left',
                    },
                    {
                        'name': 'category',
                        'label': 'Category',
                        'field': 'category',
                        'align': 'left',
                    },
                    {
                        'name': 'description',
                        'label': 'Description',
                        'field': 'description',
                        'align': 'left',
                    },
                    {
                        'name': 'amount',
                        'label': 'Amount',
                        'field': 'amount',
                        'align': 'right',
                    },
                    {
                        'name': 'actions',
                        'label': 'Actions',
                        'field': 'actions',
                        'align': 'right',
                    },
                ]

                rows = []

                for expense in expenses:

                    rows.append({
                        'id': expense['ID'],
                        'date': str(expense['Date']),
                        'time': str(expense['Time']),
                        'category': expense['Category'],
                        'description': (
                            expense['Description'] or ''
                        ),
                        'amount': (
                            f"{float(expense['Amount']):,.2f}"
                        ),
                    })

                table = ui.table(
                    columns=columns,
                    rows=rows,
                    row_key='id',
                ).classes('expenses-table')

                table.add_slot(
                    'body-cell-actions',
                    r'''
                    <q-td :props="props">
                        <div class="expense-actions">

                            <q-btn
                                flat
                                round
                                dense
                                icon="visibility"
                                color="primary"
                                @click="$parent.$emit(
                                    'view-expense',
                                    props.row
                                )"
                            />

                            <q-btn
                                flat
                                round
                                dense
                                icon="edit"
                                color="primary"
                                @click="$parent.$emit(
                                    'edit-expense',
                                    props.row
                                )"
                            />

                            <q-btn
                                flat
                                round
                                dense
                                icon="delete"
                                color="negative"
                                @click="$parent.$emit(
                                    'delete-expense',
                                    props.row
                                )"
                            />

                        </div>
                    </q-td>
                    '''
                )

                table.on(
                    'view-expense',
                    lambda event: ui.navigate.to(
                        f"/expenses/{event.args['id']}"
                    )
                )

                table.on(
                    'edit-expense',
                    lambda event: ui.navigate.to(
                        f"/expenses/{event.args['id']}/edit"
                    )
                )

                def delete_expense(event):

                    expense_id = event.args['id']

                    with ui.dialog() as dialog:

                        with ui.card().classes(
                            'delete-dialog'
                        ):

                            ui.label(
                                'Delete Expense'
                            ).classes(
                                'delete-dialog-title'
                            )

                            ui.label(
                                'Are you sure you want to '
                                'delete this expense?'
                            ).classes(
                                'delete-dialog-text'
                            )

                            with ui.row().classes(
                                'delete-dialog-actions'
                            ):

                                ui.button(
                                    'Cancel',
                                    on_click=dialog.close
                                ).props('flat')

                                def confirm_delete():

                                    from services.data.expenses import (
                                        delete_expense
                                    )

                                    delete_expense(
                                        expense_id
                                    )

                                    dialog.close()

                                    ui.navigate.to(
                                        '/expenses'
                                    )

                                ui.button(
                                    'Delete',
                                    icon='delete',
                                    on_click=confirm_delete
                                ).props(
                                    'color=negative'
                                )

                    dialog.open()

                table.on(
                    'delete-expense',
                    delete_expense
                )