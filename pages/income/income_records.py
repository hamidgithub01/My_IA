from pathlib import Path

from nicegui import ui

from services.data.income import get_income
from components.header import create_header

@ui.page('/income')
def income_records_page():


    create_header('Income')

    # --------------------------------------------------
    # CSS
    # --------------------------------------------------

    css_file = Path('styles/income.css')

    if css_file.exists():
        css_version = css_file.stat().st_mtime_ns

        ui.add_head_html(
            f'<link rel="stylesheet" '
            f'href="/styles/income.css?v={css_version}">'
        )

    # --------------------------------------------------
    # Data
    # --------------------------------------------------

    incomes = get_income()

    # --------------------------------------------------
    # Page
    # --------------------------------------------------

    with ui.column().classes('income-page'):

        # --------------------------------------------------
        # Page Header
        # --------------------------------------------------

        with ui.row().classes('income-header'):

            with ui.column().classes('income-heading'):

                ui.label(
                    'Income'
                ).classes('income-title')

                ui.label(
                    'Manage and review your income.'
                ).classes('income-subtitle')

            ui.button(
                'Add Income',
                icon='add',
                on_click=lambda: ui.navigate.to(
                    '/income/add'
                )
            ).classes('add-income-button')

        # --------------------------------------------------
        # Income Table
        # --------------------------------------------------

        with ui.card().classes('income-table-card'):

            ui.label(
                'Income Records'
            ).classes('income-section-title')

            if not incomes:

                with ui.column().classes('income-empty'):

                    ui.icon(
                        'payments',
                        size='48px'
                    )

                    ui.label(
                        'No income found.'
                    ).classes('income-empty-title')

                    ui.label(
                        'Add your first income record to get started.'
                    ).classes('income-empty-text')

                    ui.button(
                        'Add Income',
                        icon='add',
                        on_click=lambda: ui.navigate.to(
                            '/income/add'
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
                        'name': 'source',
                        'label': 'Source',
                        'field': 'source',
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
                        'name': 'type',
                        'label': 'Type',
                        'field': 'type',
                        'align': 'left',
                    },
                    {
                        'name': 'actions',
                        'label': 'Actions',
                        'field': 'actions',
                        'align': 'right',
                    },
                ]

                rows = []

                for income in incomes:

                    rows.append({
                        'id': income['ID'],
                        'date': str(income['Date']),
                        'time': str(income['Time']),
                        'source': income['Source'],
                        'description': (
                            income['Description'] or ''
                        ),
                        'amount': (
                            f"{float(income['Amount']):,.2f}"
                        ),
                        'type': income['Type'],
                    })

                table = ui.table(
                    columns=columns,
                    rows=rows,
                    row_key='id',
                ).classes('income-table')

                table.add_slot(
                    'body-cell-actions',
                    r'''
                    <q-td :props="props">
                        <div class="income-actions">

                            <q-btn
                                flat
                                round
                                dense
                                icon="visibility"
                                color="primary"
                                @click="$parent.$emit(
                                    'view-income',
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
                                    'edit-income',
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
                                    'delete-income',
                                    props.row
                                )"
                            />

                        </div>
                    </q-td>
                    '''
                )

                table.on(
                    'view-income',
                    lambda event: ui.navigate.to(
                        f"/income/{event.args['id']}"
                    )
                )

                table.on(
                    'edit-income',
                    lambda event: ui.navigate.to(
                        f"/income/{event.args['id']}/edit"
                    )
                )

                def delete_income_record(event):

                    income_id = event.args['id']

                    with ui.dialog() as dialog:

                        with ui.card().classes(
                            'delete-dialog'
                        ):

                            ui.label(
                                'Delete Income'
                            ).classes(
                                'delete-dialog-title'
                            )

                            ui.label(
                                'Are you sure you want to '
                                'delete this income record?'
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

                                    from services.data.income import (
                                        delete_income
                                    )

                                    delete_income(income_id)

                                    dialog.close()

                                    ui.navigate.to(
                                        '/income'
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
                    'delete-income',
                    delete_income_record
                )
