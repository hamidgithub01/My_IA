
from nicegui import ui

from services.data.budgets import (
    get_budgets,
    get_budget,
    add_budget,
    update_budget,
    delete_budget,
)


# ==========================================================
# PAGE
# ==========================================================

def budgets_page():
    state = {
        'budgets': [],
        'search': '',
        'month_filter': 'All',
        'table': None,
        'total_label': None,
        'count_label': None,
        'categories_label': None,
        'month_select': None,
    }

    # ======================================================
    # MONTH HELPERS
    # ======================================================

    def normalize_month(value):
        """
        Convert a database DATE or user value into YYYY-MM.

        Examples:
            2026-08-01 -> 2026-08
            2026-08    -> 2026-08
        """

        if value is None:
            return ''

        value = str(value).strip()

        if len(value) >= 7:
            value = value[:7]

        if len(value) != 7:
            return ''

        if value[4] != '-':
            return ''

        year = value[:4]
        month = value[5:]

        if not year.isdigit() or not month.isdigit():
            return ''

        month_number = int(month)

        if month_number < 1 or month_number > 12:
            return ''

        return f'{year}-{month_number:02d}'

    def month_to_database(value):
        """
        Convert YYYY-MM from the UI into YYYY-MM-01
        for the MySQL DATE column.
        """

        month = normalize_month(value)

        if not month:
            return ''

        return f'{month}-01'

    # ======================================================
    # DATA
    # ======================================================

    def load_budgets():
        try:
            state['budgets'] = get_budgets() or []

        except Exception as exc:
            state['budgets'] = []

            ui.notify(
                f'Unable to load budgets: {exc}',
                type='negative',
            )

        update_month_options()
        refresh_view()

    def get_months():
        months = {
            normalize_month(
                record.get('Month')
            )
            for record in state['budgets']
            if normalize_month(
                record.get('Month')
            )
        }

        return sorted(
            months,
            reverse=True,
        )

    def get_categories():
        categories = {
            str(
                record.get('Category', '')
            ).strip()
            for record in state['budgets']
            if record.get('Category')
        }

        return sorted(categories)

    def update_month_options():
        if state['month_select'] is None:
            return

        options = ['All'] + get_months()

        if state['month_filter'] not in options:
            state['month_filter'] = 'All'

        state['month_select'].options = options
        state['month_select'].value = state['month_filter']
        state['month_select'].update()

    def filtered_budgets():
        search = state['search'].strip().lower()
        month_filter = state['month_filter']

        result = []

        for record in state['budgets']:
            month = normalize_month(
                record.get('Month')
            )

            category = str(
                record.get('Category', '')
            ).strip()

            notes = str(
                record.get('Notes', '')
            ).strip()

            if month_filter != 'All':
                if month != month_filter:
                    continue

            if search:
                searchable = (
                    f'{month} '
                    f'{category} '
                    f'{notes}'
                ).lower()

                if search not in searchable:
                    continue

            result.append(record)

        return result

    def refresh_view():
        filtered = filtered_budgets()

        rows = []

        for record in filtered:
            month = normalize_month(
                record.get('Month')
            )

            category = str(
                record.get('Category', '')
            ).strip()

            budget_limit = float(
                record.get('Limit') or 0
            )

            rows.append(
                {
                    'budget_key': (
                        f'{month}|{category}'
                    ),
                    'month': month,
                    'category': category,
                    'limit': budget_limit,
                    'notes': str(
                        record.get('Notes', '')
                    ),
                }
            )

        if state['table'] is not None:
            state['table'].rows = rows
            state['table'].update()

        total = sum(
            float(
                record.get('Limit') or 0
            )
            for record in filtered
        )

        if state['total_label'] is not None:
            state['total_label'].text = (
                f'{total:,.2f}'
            )

        if state['count_label'] is not None:
            state['count_label'].text = str(
                len(filtered)
            )

        if state['categories_label'] is not None:
            categories = {
                str(
                    record.get('Category', '')
                ).strip()
                for record in filtered
                if record.get('Category')
            }

            state['categories_label'].text = str(
                len(categories)
            )

    def set_search(value):
        state['search'] = value
        refresh_view()

    def set_month_filter(value):
        state['month_filter'] = value
        refresh_view()

    def clear_filters():
        state['search'] = ''
        state['month_filter'] = 'All'

        search_input.value = ''
        search_input.update()

        update_month_options()
        refresh_view()

    # ======================================================
    # CRUD
    # ======================================================

    def open_budget_dialog(record=None):
        editing = record is not None

        month_value = ''
        category_value = ''
        limit_value = None
        notes_value = ''

        if editing:
            # Database stores YYYY-MM-01.
            # UI displays YYYY-MM.
            month_value = normalize_month(
                record.get('Month')
            )

            category_value = str(
                record.get('Category', '')
            ).strip()

            raw_limit = record.get('Limit')

            if raw_limit is not None:
                try:
                    limit_value = float(
                        raw_limit
                    )
                except (
                    TypeError,
                    ValueError,
                ):
                    limit_value = None

            notes_value = str(
                record.get('Notes', '')
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

                    # --------------------------------------
                    # HEADER
                    # --------------------------------------

                    with ui.row().classes(
                        'w-full '
                        'items-start '
                        'justify-between'
                    ):

                        with ui.column().classes(
                            'gap-1'
                        ):

                            ui.label(
                                'Edit Budget'
                                if editing
                                else 'Add Budget'
                            ).classes(
                                'text-xl '
                                'font-bold '
                                'text-gray-900'
                            )

                            ui.label(
                                'Update the budget information below.'
                                if editing
                                else
                                'Enter the details of your budget.'
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

                    # --------------------------------------
                    # MONTH
                    # --------------------------------------

                    month_input = ui.input(
                        'Month',
                        value=month_value,
                    ).props(
                        'outlined '
                        'type=month'
                    ).classes(
                        'w-full'
                    )

                    ui.label(
                        'Select the month for this budget.'
                    ).classes(
                        'text-xs '
                        'text-gray-500 '
                        '-mt-3'
                    )

                    # --------------------------------------
                    # CATEGORY
                    # --------------------------------------

                    category_input = ui.input(
                        'Category',
                        value=category_value,
                        placeholder=(
                            'e.g. Food, Transport, Housing'
                        ),
                    ).props(
                        'outlined'
                    ).classes(
                        'w-full'
                    )

                    # --------------------------------------
                    # LIMIT
                    # --------------------------------------

                    limit_input = ui.number(
                        'Budget Limit',
                        value=limit_value,
                        min=0,
                        step=0.01,
                    ).props(
                        'outlined clearable'
                    ).classes(
                        'w-full'
                    )

                    # --------------------------------------
                    # NOTES
                    # --------------------------------------

                    notes_input = ui.textarea(
                        'Notes',
                        value=notes_value,
                        placeholder=(
                            'Optional notes about this budget...'
                        ),
                    ).props(
                        'outlined'
                    ).classes(
                        'w-full'
                    )

                    # --------------------------------------
                    # ACTIONS
                    # --------------------------------------

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
                            'Save Budget',
                            icon='check',
                            on_click=lambda: save_budget(
                                dialog=dialog,
                                record=record,
                                month_input=month_input,
                                category_input=category_input,
                                limit_input=limit_input,
                                notes_input=notes_input,
                            ),
                        ).props(
                            'unelevated no-caps'
                        ).classes(
                            'bg-primary '
                            'text-white '
                            'px-5'
                        )

        dialog.open()

    def save_budget(
        dialog,
        record,
        month_input,
        category_input,
        limit_input,
        notes_input,
    ):
        # UI value: YYYY-MM
        month = normalize_month(
            month_input.value
        )

        # Database value: YYYY-MM-01
        database_month = month_to_database(
            month
        )

        category = (
            category_input.value or ''
        ).strip()

        notes = (
            notes_input.value or ''
        ).strip()

        limit = limit_input.value

        # ----------------------------------------------
        # VALIDATION
        # ----------------------------------------------

        if not month:
            ui.notify(
                'Please select a valid month.',
                type='warning',
            )
            return

        if not category:
            ui.notify(
                'Please enter a category.',
                type='warning',
            )
            return

        if limit is None:
            ui.notify(
                'Please enter a budget limit.',
                type='warning',
            )
            return

        try:
            limit = float(limit)

            if limit < 0:
                ui.notify(
                    'Budget limit cannot be negative.',
                    type='warning',
                )
                return

            # ------------------------------------------
            # ADD
            # ------------------------------------------

            if record is None:

                existing = get_budget(
                    database_month,
                    category,
                )

                if existing is not None:
                    ui.notify(
                        'A budget already exists for this month and category.',
                        type='warning',
                    )
                    return

                add_budget(
                    database_month,
                    category,
                    limit,
                    notes,
                )

                message = (
                    'Budget added successfully.'
                )

            # ------------------------------------------
            # UPDATE
            # ------------------------------------------

            else:
                original_month = normalize_month(
                    record.get('Month')
                )

                original_database_month = month_to_database(
                    original_month
                )

                original_category = str(
                    record.get('Category', '')
                ).strip()

                # --------------------------------------
                # KEY CHANGED
                # --------------------------------------

                if (
                    month != original_month
                    or category != original_category
                ):

                    existing = get_budget(
                        database_month,
                        category,
                    )

                    if existing is not None:
                        ui.notify(
                            'A budget already exists for this month and category.',
                            type='warning',
                        )
                        return

                    delete_budget(
                        original_database_month,
                        original_category,
                    )

                    add_budget(
                        database_month,
                        category,
                        limit,
                        notes,
                    )

                # --------------------------------------
                # SAME KEY
                # --------------------------------------

                else:
                    update_budget(
                        original_database_month,
                        original_category,
                        limit,
                        notes,
                    )

                message = (
                    'Budget updated successfully.'
                )

            dialog.close()

            load_budgets()

            ui.notify(
                message,
                type='positive',
            )

        except Exception as exc:
            ui.notify(
                f'Unable to save budget: {exc}',
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
                        'Delete Budget'
                    ).classes(
                        'text-xl '
                        'font-bold '
                        'text-gray-900'
                    )

                    ui.label(
                        'Are you sure you want to delete this '
                        'budget? This action cannot be undone.'
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
            month = normalize_month(
                record.get('Month')
            )

            category = str(
                record.get('Category', '')
            ).strip()

            if not month:
                ui.notify(
                    'Unable to determine the budget month.',
                    type='negative',
                )
                return

            if not category:
                ui.notify(
                    'Unable to determine the budget category.',
                    type='negative',
                )
                return

            database_month = month_to_database(
                month
            )

            delete_budget(
                database_month,
                category,
            )

            dialog.close()

            load_budgets()

            ui.notify(
                'Budget deleted successfully.',
                type='positive',
            )

        except Exception as exc:
            ui.notify(
                f'Unable to delete budget: {exc}',
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
                    'Budgets'
                ).classes(
                    'text-2xl '
                    'font-bold '
                    'text-gray-900'
                )

                ui.label(
                    'Manage, review, and organize your budgets.'
                ).classes(
                    'text-sm '
                    'text-gray-500'
                )

            ui.button(
                'Add Budget',
                icon='add',
                on_click=lambda: open_budget_dialog(),
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
                    'Total Budget'
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
                    'Budget Records'
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
                    'Categories'
                ).classes(
                    'text-xs '
                    'font-medium '
                    'text-gray-500'
                )

                state['categories_label'] = ui.label(
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
                    label='Search budgets',
                    placeholder=(
                        'Search month, category, or notes...'
                    ),
                    on_change=lambda e: set_search(
                        e.value or ''
                    ),
                ).props(
                    'outlined clearable'
                ).classes(
                    'flex-1 '
                    'min-w-[260px]'
                )

                state['month_select'] = ui.select(
                    options=['All'],
                    value='All',
                    label='Month',
                    on_change=lambda e: set_month_filter(
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
                        'Budget Records'
                    ).classes(
                        'text-base '
                        'font-semibold '
                        'text-gray-900'
                    )

                    ui.label(
                        'Your recorded budgets'
                    ).classes(
                        'text-xs '
                        'text-gray-500'
                    )

            columns = [
                {
                    'name': 'month',
                    'label': 'Month',
                    'field': 'month',
                    'align': 'left',
                },
                {
                    'name': 'category',
                    'label': 'Category',
                    'field': 'category',
                    'align': 'left',
                },
                {
                    'name': 'limit',
                    'label': 'Budget Limit',
                    'field': 'limit',
                    'align': 'right',
                },
                {
                    'name': 'notes',
                    'label': 'Notes',
                    'field': 'notes',
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
                row_key='budget_key',
            ).props(
                'flat '
                'separator=horizontal '
                'hide-pagination'
            ).classes(
                'w-full'
            )

            # ----------------------------------------------
            # LIMIT
            # ----------------------------------------------

            state['table'].add_slot(
                'body-cell-limit',
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

            # ----------------------------------------------
            # CATEGORY
            # ----------------------------------------------

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

            # ----------------------------------------------
            # ACTIONS
            # ----------------------------------------------

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
                                'edit-budget',
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
                                'delete-budget',
                                props.row
                            )"
                        />

                    </div>
                </q-td>
                '''
            )

            # ----------------------------------------------
            # EDIT EVENT
            # ----------------------------------------------

            def handle_edit_budget(event):
                row = event.args

                record = find_budget(row)

                if record is not None:
                    open_budget_dialog(
                        record
                    )

            state['table'].on(
                'edit-budget',
                handle_edit_budget,
            )

            # ----------------------------------------------
            # DELETE EVENT
            # ----------------------------------------------

            def handle_delete_budget(event):
                row = event.args

                record = find_budget(row)

                if record is not None:
                    confirm_delete(
                        record
                    )

            state['table'].on(
                'delete-budget',
                handle_delete_budget,
            )

    # ======================================================
    # HELPERS
    # ======================================================

    def find_budget(row):
        month = normalize_month(
            row.get('month')
        )

        category = str(
            row.get('category', '')
        ).strip()

        for record in state['budgets']:

            record_month = normalize_month(
                record.get('Month')
            )

            record_category = str(
                record.get('Category', '')
            ).strip()

            if (
                record_month == month
                and record_category == category
            ):
                return record

        return None

    # ======================================================
    # INITIAL LOAD
    # ======================================================

    load_budgets()
