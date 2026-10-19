from nicegui import ui

from services.data.expenses import (
    get_expenses,
    add_expense,
    update_expense,
    delete_expense,
)


def expenses_page():
    state = {
        'expenses': [],
        'search': '',
        'category': 'All',
        'table': None,
        'total_label': None,
        'count_label': None,
        'categories_label': None,
        'category_select': None,
        'dialog': None,
        'dialog_title': None,
        'dialog_description': None,
        'editing_expense': None,
        'date_input': None,
        'time_input': None,
        'category_input': None,
        'description_input': None,
        'amount_input': None,
    }

    def get_categories():
        return sorted({
            str(expense.get('Category', '')).strip()
            for expense in state['expenses']
            if expense.get('Category')
        })

    def filtered_expenses():
        search = state['search'].strip().lower()
        category = state['category']

        result = []

        for expense in state['expenses']:
            expense_category = str(
                expense.get('Category', '')
            ).strip()

            description = str(
                expense.get('Description', '')
            ).strip()

            if category != 'All' and expense_category != category:
                continue

            if search:
                searchable = (
                    f'{expense_category} {description}'
                ).lower()

                if search not in searchable:
                    continue

            result.append(expense)

        return result

    def format_time(value):
        if value is None or value == '':
            return ''

        if hasattr(value, 'total_seconds'):
            total_seconds = int(value.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f'{hours:02d}:{minutes:02d}:{seconds:02d}'

        return str(value)

    def refresh_view():
        rows = []

        for expense in filtered_expenses():
            rows.append({
                'id': expense.get('ID'),
                'date': str(expense.get('Date', '') or ''),
                'time': format_time(expense.get('Time')),
                'category': str(
                    expense.get('Category', '') or ''
                ),
                'description': str(
                    expense.get('Description', '') or ''
                ),
                'amount': float(
                    expense.get('Amount') or 0
                ),
            })

        if state['table'] is not None:
            state['table'].rows = rows
            state['table'].update()

        total = sum(
            float(expense.get('Amount') or 0)
            for expense in filtered_expenses()
        )

        if state['total_label'] is not None:
            state['total_label'].text = f'{total:,.2f}'

        if state['count_label'] is not None:
            state['count_label'].text = str(
                len(filtered_expenses())
            )

        if state['categories_label'] is not None:
            state['categories_label'].text = str(
                len(get_categories())
            )

    def update_category_options():
        select = state['category_select']

        if select is None:
            return

        options = ['All'] + get_categories()

        if state['category'] not in options:
            state['category'] = 'All'

        select.options = options
        select.value = state['category']
        select.update()

    def load_expenses():
        try:
            state['expenses'] = get_expenses() or []
        except Exception as exc:
            state['expenses'] = []

            ui.notify(
                f'Unable to load expenses: {exc}',
                type='negative',
            )

        update_category_options()
        refresh_view()

    def set_search(value):
        state['search'] = value or ''
        refresh_view()

    def set_category(value):
        state['category'] = value or 'All'
        refresh_view()

    def clear_filters():
        state['search'] = ''
        state['category'] = 'All'

        search_input.value = ''
        search_input.update()

        update_category_options()
        refresh_view()

    def open_expense_dialog(expense=None):
        state['editing_expense'] = expense

        editing = expense is not None

        state['dialog_title'].text = (
            'Edit Expense'
            if editing
            else 'Add Expense'
        )

        state['dialog_description'].text = (
            'Update the expense information below.'
            if editing
            else 'Enter the details of your expense.'
        )

        if editing:
            state['date_input'].value = str(
                expense.get('Date', '') or ''
            )

            state['time_input'].value = format_time(
                expense.get('Time')
            )

            state['category_input'].value = str(
                expense.get('Category', '') or ''
            )

            state['description_input'].value = str(
                expense.get('Description', '') or ''
            )

            state['amount_input'].value = float(
                expense.get('Amount') or 0
            )

        else:
            state['date_input'].value = ''
            state['time_input'].value = ''
            state['category_input'].value = ''
            state['description_input'].value = ''
            state['amount_input'].value = None

        state['date_input'].update()
        state['time_input'].update()
        state['category_input'].update()
        state['description_input'].update()
        state['amount_input'].update()

        state['dialog'].open()

    def save_expense():
        date = (state['date_input'].value or '').strip()
        time = (state['time_input'].value or '').strip()
        category = (
            state['category_input'].value or ''
        ).strip()
        description = (
            state['description_input'].value or ''
        ).strip()
        amount = state['amount_input'].value

        if not date:
            ui.notify(
                'Please select a date.',
                type='warning',
            )
            return

        if not category:
            ui.notify(
                'Please enter a category.',
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

            expense = state['editing_expense']

            if expense is None:
                add_expense(
                    date,
                    time,
                    category,
                    description,
                    amount,
                )

                message = 'Expense added successfully.'

            else:
                update_expense(
                    expense.get('ID'),
                    date,
                    time,
                    category,
                    description,
                    amount,
                )

                message = 'Expense updated successfully.'

            state['dialog'].close()
            state['editing_expense'] = None

            load_expenses()

            ui.notify(
                message,
                type='positive',
            )

        except Exception as exc:
            ui.notify(
                f'Unable to save expense: {exc}',
                type='negative',
            )

    def find_expense(row):
        expense_id = row.get('id')

        for expense in state['expenses']:
            if expense.get('ID') == expense_id:
                return expense

        return None

    def confirm_delete(expense):
        if expense is None:
            return

        with ui.dialog() as dialog:
            with ui.card().classes(
                'w-full '
                'max-w-[420px] '
                'p-6 '
                'rounded-[var(--radius-md)]'
            ):
                with ui.column().classes(
                    'w-full gap-4'
                ):
                    ui.icon(
                        'delete_outline'
                    ).classes(
                        'text-3xl text-red-500'
                    )

                    ui.label(
                        'Delete Expense'
                    ).classes(
                        'text-xl font-bold text-gray-900'
                    )

                    ui.label(
                        'Are you sure you want to delete this '
                        'expense? This action cannot be undone.'
                    ).classes(
                        'text-sm text-gray-500'
                    )

                    with ui.row().classes(
                        'w-full justify-end gap-2 pt-2'
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
                                expense,
                            ),
                        ).props(
                            'unelevated no-caps'
                        ).classes(
                            'bg-red-600 text-white'
                        )

        dialog.open()

    def execute_delete(dialog, expense):
        try:
            delete_expense(expense.get('ID'))

            dialog.close()
            load_expenses()

            ui.notify(
                'Expense deleted successfully.',
                type='positive',
            )

        except Exception as exc:
            ui.notify(
                f'Unable to delete expense: {exc}',
                type='negative',
            )

    with ui.dialog() as expense_dialog:
        state['dialog'] = expense_dialog

        with ui.card().classes(
            'w-full '
            'max-w-[560px] '
            'p-6 '
            'rounded-[var(--radius-md)]'
        ):
            with ui.column().classes(
                'w-full gap-5'
            ):
                with ui.row().classes(
                    'w-full items-start justify-between'
                ):
                    with ui.column().classes(
                        'gap-1'
                    ):
                        state['dialog_title'] = ui.label(
                            'Add Expense'
                        ).classes(
                            'text-xl font-bold text-gray-900'
                        )

                        state['dialog_description'] = ui.label(
                            'Enter the details of your expense.'
                        ).classes(
                            'text-sm text-gray-500'
                        )

                    ui.button(
                        icon='close',
                        on_click=expense_dialog.close,
                    ).props(
                        'flat round dense'
                    ).classes(
                        'text-gray-500'
                    )

                with ui.row().classes(
                    'w-full gap-3 flex-wrap'
                ):
                    state['date_input'] = ui.input(
                        'Date'
                    ).props(
                        'outlined type=date'
                    ).classes(
                        'flex-1 min-w-[200px]'
                    )

                    state['time_input'] = ui.input(
                        'Time'
                    ).props(
                        'outlined type=time'
                    ).classes(
                        'flex-1 min-w-[200px]'
                    )

                state['category_input'] = ui.input(
                    'Category',
                    placeholder='e.g. Food',
                ).props(
                    'outlined'
                ).classes(
                    'w-full'
                )

                state['description_input'] = ui.input(
                    'Description',
                    placeholder='What was this expense for?',
                ).props(
                    'outlined'
                ).classes(
                    'w-full'
                )

                state['amount_input'] = ui.number(
                    'Amount',
                    min=0,
                    step=0.01,
                ).props(
                    'outlined clearable'
                ).classes(
                    'w-full'
                )

                with ui.row().classes(
                    'w-full justify-end gap-2 pt-2'
                ):
                    ui.button(
                        'Cancel',
                        on_click=expense_dialog.close,
                    ).props(
                        'flat no-caps'
                    ).classes(
                        'text-gray-600'
                    )

                    ui.button(
                        'Save Expense',
                        icon='check',
                        on_click=save_expense,
                    ).props(
                        'unelevated no-caps'
                    ).classes(
                        'bg-primary text-white px-5'
                    )

    with ui.column().classes(
        'w-full '
        'max-w-[1600px] '
        'mx-auto '
        'gap-6'
    ):
        with ui.row().classes(
            'w-full items-start justify-between gap-4 flex-wrap'
        ):
            with ui.column().classes('gap-1'):
                ui.label(
                    'Expenses'
                ).classes(
                    'text-2xl font-bold text-gray-900'
                )

                ui.label(
                    'Manage, review, and organize your expenses.'
                ).classes(
                    'text-sm text-gray-500'
                )

            ui.button(
                'Add Expense',
                icon='add',
                on_click=lambda: open_expense_dialog(),
            ).props(
                'unelevated no-caps'
            ).classes(
                'bg-primary '
                'text-white '
                'px-5 '
                'py-2.5 '
                'rounded-[var(--radius-md)]'
            )

        with ui.row().classes(
            'w-full gap-4 flex-wrap'
        ):
            with ui.card().classes(
                'flex-1 min-w-[220px] p-4 '
                'rounded-[var(--radius-md)] '
                'shadow-none border border-gray-200'
            ):
                ui.label(
                    'Total Expenses'
                ).classes(
                    'text-xs font-medium text-gray-500'
                )

                state['total_label'] = ui.label(
                    '0.00'
                ).classes(
                    'text-2xl font-bold text-gray-900 mt-1'
                )

            with ui.card().classes(
                'flex-1 min-w-[220px] p-4 '
                'rounded-[var(--radius-md)] '
                'shadow-none border border-gray-200'
            ):
                ui.label(
                    'Transactions'
                ).classes(
                    'text-xs font-medium text-gray-500'
                )

                state['count_label'] = ui.label(
                    '0'
                ).classes(
                    'text-2xl font-bold text-gray-900 mt-1'
                )

            with ui.card().classes(
                'flex-1 min-w-[220px] p-4 '
                'rounded-[var(--radius-md)] '
                'shadow-none border border-gray-200'
            ):
                ui.label(
                    'Categories'
                ).classes(
                    'text-xs font-medium text-gray-500'
                )

                state['categories_label'] = ui.label(
                    '0'
                ).classes(
                    'text-2xl font-bold text-gray-900 mt-1'
                )

        with ui.card().classes(
            'w-full p-4 '
            'rounded-[var(--radius-md)] '
            'shadow-none border border-gray-200'
        ):
            with ui.row().classes(
                'w-full items-end gap-3 flex-wrap'
            ):
                search_input = ui.input(
                    label='Search expenses',
                    placeholder='Search description or category...',
                    on_change=lambda e: set_search(
                        e.value or ''
                    ),
                ).props(
                    'outlined clearable'
                ).classes(
                    'flex-1 min-w-[260px]'
                )

                state['category_select'] = ui.select(
                    options=['All'],
                    value='All',
                    label='Category',
                    on_change=lambda e: set_category(
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

        with ui.card().classes(
            'w-full p-0 overflow-hidden '
            'rounded-[var(--radius-md)] '
            'shadow-none border border-gray-200'
        ):
            with ui.row().classes(
                'w-full items-center justify-between '
                'px-5 py-4 border-b border-gray-200'
            ):
                with ui.column().classes('gap-0'):
                    ui.label(
                        'Expense Records'
                    ).classes(
                        'text-base font-semibold text-gray-900'
                    )

                    ui.label(
                        'Your recorded expenses'
                    ).classes(
                        'text-xs text-gray-500'
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
                'flat separator=horizontal hide-pagination'
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
                'body-cell-category',
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
                                'edit-expense',
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
                                'delete-expense',
                                props.row
                            )"
                        />
                    </div>
                </q-td>
                '''
            )

            state['table'].on(
                'edit-expense',
                lambda event: open_expense_dialog(
                    find_expense(event.args)
                ),
            )

            state['table'].on(
                'delete-expense',
                lambda event: confirm_delete(
                    find_expense(event.args)
                ),
            )

    load_expenses()