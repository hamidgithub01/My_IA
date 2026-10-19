
from nicegui import ui

from services.data.income import (
    get_income,
    add_income,
    update_income,
    delete_income,
)


# ==========================================================
# PAGE
# ==========================================================

def income_page():
    state = {
        'income': [],
        'search': '',
        'income_type': 'All',
        'table': None,
        'total_label': None,
        'count_label': None,
        'types_label': None,
        'type_select': None,
    }

    # ======================================================
    # DATA
    # ======================================================

    def load_income():
        try:
            state['income'] = get_income() or []
        except Exception as exc:
            state['income'] = []
            ui.notify(
                f'Unable to load income: {exc}',
                type='negative',
            )

        update_type_options()
        refresh_view()

    def get_income_types():
        types = {
            str(record.get('Type', '')).strip()
            for record in state['income']
            if record.get('Type')
        }

        return sorted(types)

    def update_type_options():
        if state['type_select'] is None:
            return

        options = ['All'] + get_income_types()

        if state['income_type'] not in options:
            state['income_type'] = 'All'

        state['type_select'].options = options
        state['type_select'].value = state['income_type']
        state['type_select'].update()

    def filtered_income():
        search = state['search'].strip().lower()
        income_type = state['income_type']

        result = []

        for record in state['income']:
            record_type = str(
                record.get('Type', '')
            ).strip()

            source = str(
                record.get('Source', '')
            ).strip()

            description = str(
                record.get('Description', '')
            ).strip()

            if income_type != 'All':
                if record_type != income_type:
                    continue

            if search:
                searchable = (
                    f'{record_type} '
                    f'{source} '
                    f'{description}'
                ).lower()

                if search not in searchable:
                    continue

            result.append(record)

        return result

    def format_time(value):
        if value is None:
            return ''

        if hasattr(value, 'total_seconds'):
            total_seconds = int(
                value.total_seconds()
            )

            hours, remainder = divmod(
                total_seconds,
                3600,
            )

            minutes, seconds = divmod(
                remainder,
                60,
            )

            return (
                f'{hours:02d}:'
                f'{minutes:02d}:'
                f'{seconds:02d}'
            )

        return str(value)

    def refresh_view():
        rows = []

        for record in filtered_income():
            date_value = record.get('Date', '')
            time_value = format_time(
                record.get('Time', '')
            )

            rows.append(
                {
                    'id': record.get('ID'),
                    'date': str(date_value),
                    'time': time_value,
                    'source': str(
                        record.get('Source', '')
                    ),
                    'description': str(
                        record.get('Description', '')
                    ),
                    'amount': float(
                        record.get('Amount') or 0
                    ),
                    'type': str(
                        record.get('Type', '')
                    ),
                }
            )

        if state['table'] is not None:
            state['table'].rows = rows
            state['table'].update()

        total = sum(
            float(record.get('Amount') or 0)
            for record in filtered_income()
        )

        if state['total_label'] is not None:
            state['total_label'].text = (
                f'{total:,.2f}'
            )

        if state['count_label'] is not None:
            state['count_label'].text = str(
                len(filtered_income())
            )

        if state['types_label'] is not None:
            state['types_label'].text = str(
                len(get_income_types())
            )

    def set_search(value):
        state['search'] = value
        refresh_view()

    def set_income_type(value):
        state['income_type'] = value
        refresh_view()

    def clear_filters():
        state['search'] = ''
        state['income_type'] = 'All'

        search_input.value = ''
        search_input.update()

        update_type_options()
        refresh_view()

    # ======================================================
    # CRUD
    # ======================================================

    def open_income_dialog(record=None):
        editing = record is not None

        date_value = ''
        time_value = ''
        source_value = ''
        description_value = ''
        amount_value = None
        type_value = ''

        if editing:
            date_value = str(
                record.get('Date', '')
            )

            time_value = format_time(
                record.get('Time', '')
            )

            source_value = str(
                record.get('Source', '')
            )

            description_value = str(
                record.get('Description', '')
            )

            amount_value = float(
                record.get('Amount') or 0
            )

            type_value = str(
                record.get('Type', '')
            )

        with ui.dialog() as dialog:
            with ui.card().classes(
                'w-full '
                'max-w-[560px] '
                'p-6 '
                'rounded-[var(--radius-md)]'
            ):

                with ui.column().classes(
                    'w-full '
                    'gap-5'
                ):

                    with ui.row().classes(
                        'w-full '
                        'items-start '
                        'justify-between'
                    ):

                        with ui.column().classes(
                            'gap-1'
                        ):

                            ui.label(
                                'Edit Income'
                                if editing
                                else 'Add Income'
                            ).classes(
                                'text-xl '
                                'font-bold '
                                'text-gray-900'
                            )

                            ui.label(
                                'Update the income information below.'
                                if editing
                                else
                                'Enter the details of your income.'
                            ).classes(
                                'text-sm '
                                'text-gray-500'
                            )

                        ui.button(
                            icon='close',
                            on_click=dialog.close,
                        ).props(
                            'flat round dense'
                        ).classes(
                            'text-gray-500'
                        )

                    with ui.row().classes(
                        'w-full '
                        'gap-3 '
                        'flex-wrap'
                    ):

                        date_input = ui.input(
                            'Date',
                            value=date_value,
                        ).props(
                            'outlined '
                            'type=date'
                        ).classes(
                            'flex-1 '
                            'min-w-[200px]'
                        )

                        time_input = ui.input(
                            'Time',
                            value=time_value,
                        ).props(
                            'outlined '
                            'type=time'
                        ).classes(
                            'flex-1 '
                            'min-w-[200px]'
                        )

                    source_input = ui.input(
                        'Source',
                        value=source_value,
                        placeholder='e.g. Salary',
                    ).props(
                        'outlined'
                    ).classes(
                        'w-full'
                    )

                    description_input = ui.input(
                        'Description',
                        value=description_value,
                        placeholder='What was this income for?',
                    ).props(
                        'outlined'
                    ).classes(
                        'w-full'
                    )

                    type_input = ui.input(
                        'Income Type',
                        value=type_value,
                        placeholder='e.g. Salary, Freelance, Other',
                    ).props(
                        'outlined'
                    ).classes(
                        'w-full'
                    )

                    amount_input = ui.number(
                        'Amount',
                        value=amount_value,
                        min=0,
                        step=0.01,
                    ).props(
                        'outlined '
                        'prefix= '
                        'clearable'
                    ).classes(
                        'w-full'
                    )

                    with ui.row().classes(
                        'w-full '
                        'justify-end '
                        'gap-2 '
                        'pt-2'
                    ):

                        ui.button(
                            'Cancel',
                            on_click=dialog.close,
                        ).props(
                            'flat no-caps'
                        ).classes(
                            'text-gray-600'
                        )

                        ui.button(
                            'Save Income',
                            icon='check',
                            on_click=lambda: save_income(
                                dialog=dialog,
                                record=record,
                                date_input=date_input,
                                time_input=time_input,
                                source_input=source_input,
                                description_input=description_input,
                                amount_input=amount_input,
                                type_input=type_input,
                            ),
                        ).props(
                            'unelevated no-caps'
                        ).classes(
                            'bg-primary '
                            'text-white '
                            'px-5'
                        )

        dialog.open()

    def save_income(
        dialog,
        record,
        date_input,
        time_input,
        source_input,
        description_input,
        amount_input,
        type_input,
    ):
        date = (
            date_input.value or ''
        ).strip()

        time = (
            time_input.value or ''
        ).strip()

        source = (
            source_input.value or ''
        ).strip()

        description = (
            description_input.value or ''
        ).strip()

        amount = amount_input.value

        income_type = (
            type_input.value or ''
        ).strip()

        if not date:
            ui.notify(
                'Please select a date.',
                type='warning',
            )
            return

        if not source:
            ui.notify(
                'Please enter an income source.',
                type='warning',
            )
            return

        if not income_type:
            ui.notify(
                'Please enter an income type.',
                type='warning',
            )
            return

        if amount is None:
            ui.notify(
                'Please enter an amount.',
                type='warning',
            )
            return

        try:
            amount = float(amount)

            if amount <= 0:
                ui.notify(
                    'Amount must be greater than zero.',
                    type='warning',
                )
                return

            if record is None:
                add_income(
                    date,
                    time,
                    source,
                    description,
                    amount,
                    income_type,
                )

                message = (
                    'Income added successfully.'
                )

            else:
                update_income(
                    record.get('ID'),
                    date,
                    time,
                    source,
                    description,
                    amount,
                    income_type,
                )

                message = (
                    'Income updated successfully.'
                )

            dialog.close()
            load_income()

            ui.notify(
                message,
                type='positive',
            )

        except Exception as exc:
            ui.notify(
                f'Unable to save income: {exc}',
                type='negative',
            )

    def confirm_delete(record):
        with ui.dialog() as dialog:
            with ui.card().classes(
                'w-full '
                'max-w-[420px] '
                'p-6 '
                'rounded-[var(--radius-md)]'
            ):

                with ui.column().classes(
                    'w-full '
                    'gap-4'
                ):

                    ui.icon(
                        'delete_outline'
                    ).classes(
                        'text-3xl '
                        'text-red-500'
                    )

                    ui.label(
                        'Delete Income'
                    ).classes(
                        'text-xl '
                        'font-bold '
                        'text-gray-900'
                    )

                    ui.label(
                        'Are you sure you want to delete this '
                        'income record? This action cannot be undone.'
                    ).classes(
                        'text-sm '
                        'text-gray-500'
                    )

                    with ui.row().classes(
                        'w-full '
                        'justify-end '
                        'gap-2 '
                        'pt-2'
                    ):

                        ui.button(
                            'Cancel',
                            on_click=dialog.close,
                        ).props(
                            'flat no-caps'
                        )

                        ui.button(
                            'Delete',
                            icon='delete',
                            on_click=lambda: execute_delete(
                                dialog,
                                record,
                            ),
                        ).props(
                            'unelevated no-caps'
                        ).classes(
                            'bg-red-600 '
                            'text-white'
                        )

        dialog.open()

    def execute_delete(dialog, record):
        try:
            delete_income(
                record.get('ID')
            )

            dialog.close()
            load_income()

            ui.notify(
                'Income deleted successfully.',
                type='positive',
            )

        except Exception as exc:
            ui.notify(
                f'Unable to delete income: {exc}',
                type='negative',
            )

    # ======================================================
    # PAGE HEADER
    # ======================================================

    with ui.column().classes(
        'w-full '
        'max-w-[1600px] '
        'mx-auto '
        'gap-6'
    ):

        with ui.row().classes(
            'w-full '
            'items-start '
            'justify-between '
            'gap-4 '
            'flex-wrap'
        ):

            with ui.column().classes(
                'gap-1'
            ):

                ui.label(
                    'Income'
                ).classes(
                    'text-2xl '
                    'font-bold '
                    'text-gray-900'
                )

                ui.label(
                    'Manage, review, and organize your income.'
                ).classes(
                    'text-sm '
                    'text-gray-500'
                )

            ui.button(
                'Add Income',
                icon='add',
                on_click=lambda e: open_income_dialog(),
            ).props(
                'unelevated no-caps'
            ).classes(
                'bg-primary '
                'text-white '
                'px-5 '
                'py-2.5 '
                'rounded-[var(--radius-md)]'
            )

        # ==================================================
        # SUMMARY
        # ==================================================

        with ui.row().classes(
            'w-full '
            'gap-4 '
            'flex-wrap'
        ):

            with ui.card().classes(
                'flex-1 '
                'min-w-[220px] '
                'p-4 '
                'rounded-[var(--radius-md)] '
                'shadow-none '
                'border '
                'border-gray-200'
            ):

                ui.label(
                    'Total Income'
                ).classes(
                    'text-xs '
                    'font-medium '
                    'text-gray-500'
                )

                state['total_label'] = ui.label(
                    '0.00'
                ).classes(
                    'text-2xl '
                    'font-bold '
                    'text-gray-900 '
                    'mt-1'
                )

            with ui.card().classes(
                'flex-1 '
                'min-w-[220px] '
                'p-4 '
                'rounded-[var(--radius-md)] '
                'shadow-none '
                'border '
                'border-gray-200'
            ):

                ui.label(
                    'Transactions'
                ).classes(
                    'text-xs '
                    'font-medium '
                    'text-gray-500'
                )

                state['count_label'] = ui.label(
                    '0'
                ).classes(
                    'text-2xl '
                    'font-bold '
                    'text-gray-900 '
                    'mt-1'
                )

            with ui.card().classes(
                'flex-1 '
                'min-w-[220px] '
                'p-4 '
                'rounded-[var(--radius-md)] '
                'shadow-none '
                'border '
                'border-gray-200'
            ):

                ui.label(
                    'Income Types'
                ).classes(
                    'text-xs '
                    'font-medium '
                    'text-gray-500'
                )

                state['types_label'] = ui.label(
                    '0'
                ).classes(
                    'text-2xl '
                    'font-bold '
                    'text-gray-900 '
                    'mt-1'
                )

        # ==================================================
        # TOOLBAR
        # ==================================================

        with ui.card().classes(
            'w-full '
            'p-4 '
            'rounded-[var(--radius-md)] '
            'shadow-none '
            'border '
            'border-gray-200'
        ):

            with ui.row().classes(
                'w-full '
                'items-end '
                'gap-3 '
                'flex-wrap'
            ):

                search_input = ui.input(
                    label='Search income',
                    placeholder='Search source, description, or type...',
                    on_change=lambda e: set_search(
                        e.value or ''
                    ),
                ).props(
                    'outlined clearable'
                ).classes(
                    'flex-1 '
                    'min-w-[260px]'
                )

                state['type_select'] = ui.select(
                    options=['All'],
                    value='All',
                    label='Income Type',
                    on_change=lambda e: set_income_type(
                        e.value or 'All'
                    ),
                ).props(
                    'outlined'
                ).classes(
                    'w-[220px]'
                )

                ui.button(
                    'Clear',
                    icon='refresh',
                    on_click=clear_filters,
                ).props(
                    'flat no-caps'
                ).classes(
                    'text-gray-600'
                )

        # ==================================================
        # TABLE
        # ==================================================

        with ui.card().classes(
            'w-full '
            'p-0 '
            'overflow-hidden '
            'rounded-[var(--radius-md)] '
            'shadow-none '
            'border '
            'border-gray-200'
        ):

            with ui.row().classes(
                'w-full '
                'items-center '
                'justify-between '
                'px-5 '
                'py-4 '
                'border-b '
                'border-gray-200'
            ):

                with ui.column().classes(
                    'gap-0'
                ):

                    ui.label(
                        'Income Records'
                    ).classes(
                        'text-base '
                        'font-semibold '
                        'text-gray-900'
                    )

                    ui.label(
                        'Your recorded income'
                    ).classes(
                        'text-xs '
                        'text-gray-500'
                    )

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
                    'label': '',
                    'field': 'actions',
                    'align': 'right',
                },
            ]

            state['table'] = ui.table(
                columns=columns,
                rows=[],
                row_key='id',
            ).props(
                'flat '
                'separator=horizontal '
                'hide-pagination'
            ).classes(
                'w-full'
            )

            state['table'].add_slot(
                'body-cell-amount',
                r'''
                <q-td :props="props">
                    <span class="font-semibold text-gray-900">
                        {{ Number(props.value).toLocaleString(
                            undefined,
                            {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2
                            }
                        ) }}
                    </span>
                </q-td>
                '''
            )

            state['table'].add_slot(
                'body-cell-type',
                r'''
                <q-td :props="props">
                    <q-badge
                        color="grey-2"
                        text-color="grey-8"
                        class="px-2 py-1"
                    >
                        {{ props.value }}
                    </q-badge>
                </q-td>
                '''
            )

            state['table'].add_slot(
                'body-cell-actions',
                r'''
                <q-td :props="props">
                    <div class="row items-center justify-end no-wrap">
                        <q-btn
                            flat
                            round
                            dense
                            icon="edit"
                            color="grey-7"
                            @click="$parent.$emit(
                                'edit-income',
                                props.row
                            )"
                        />
                        <q-btn
                            flat
                            round
                            dense
                            icon="delete_outline"
                            color="grey-7"
                            @click="$parent.$emit(
                                'delete-income',
                                props.row
                            )"
                        />
                    </div>
                </q-td>
                '''
            )

            def handle_edit_income(event):
                row = event.args
                record = find_income(row)

                if record is not None:
                    open_income_dialog(record)

            state['table'].on(
                'edit-income',
                handle_edit_income,
            )

            def handle_delete_income(event):
                row = event.args
                record = find_income(row)

                if record is not None:
                    confirm_delete(record)

            state['table'].on(
                'delete-income',
                handle_delete_income,
            )

    # ======================================================
    # HELPERS
    # ======================================================

    def find_income(row):
        income_id = row.get('id')

        for record in state['income']:
            if record.get('ID') == income_id:
                return record

        return None

    # ======================================================
    # INITIAL LOAD
    # ======================================================

    load_income()
