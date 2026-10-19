
from nicegui import ui

from services.data.health import (
    get_health_records,
    add_health_record,
    update_health_record,
    delete_health_record,
)


def health_page():
    state = {
        'records': [],
        'search': '',
        'status': 'All',
        'table': None,
        'total_label': None,
        'count_label': None,
        'healthy_label': None,
        'severity_label': None,
        'status_select': None,
        'dialog': None,
        'dialog_title': None,
        'dialog_description': None,
        'editing_record': None,
        'date_input': None,
        'status_input': None,
        'energy_input': None,
        'symptoms_input': None,
        'severity_input': None,
        'treatment_input': None,
        'physical_activity_input': None,
        'sugar_intake_input': None,
        'sleep_quality_input': None,
        'water_intake_input': None,
        'notes_input': None,
    }

    def get_statuses():
        return sorted({
            str(record.get('Health_Status', '')).strip()
            for record in state['records']
            if record.get('Health_Status')
        })

    def filtered_records():
        search = state['search'].strip().lower()
        status = state['status']

        result = []

        for record in state['records']:
            record_status = str(
                record.get('Health_Status', '')
            ).strip()

            if status != 'All' and record_status != status:
                continue

            if search:
                searchable = ' '.join([
                    record_status,
                    str(record.get('Symptoms', '') or ''),
                    str(record.get('Treatment', '') or ''),
                    str(record.get('Physical_Activity', '') or ''),
                    str(record.get('Sugar_Intake', '') or ''),
                    str(record.get('Sleep_Quality', '') or ''),
                    str(record.get('Water_Intake', '') or ''),
                    str(record.get('Notes', '') or ''),
                ]).lower()

                if search not in searchable:
                    continue

            result.append(record)

        return result

    def format_date(value):
        if value is None or value == '':
            return ''

        if hasattr(value, 'strftime'):
            return value.strftime('%Y-%m-%d')

        return str(value)

    def format_number(value):
        if value is None or value == '':
            return ''

        try:
            return f'{float(value):.2f}'
        except (TypeError, ValueError):
            return str(value)

    def refresh_view():
        rows = []

        for record in filtered_records():
            rows.append({
                'id': record.get('Health_ID'),
                'date': format_date(record.get('Date')),
                'status': str(
                    record.get('Health_Status', '') or ''
                ),
                'energy': format_number(
                    record.get('Energy_Level')
                ),
                'symptoms': str(
                    record.get('Symptoms', '') or ''
                ),
                'severity': int(
                    record.get('Severity') or 0
                ),
                'treatment': str(
                    record.get('Treatment', '') or ''
                ),
                'physical_activity': str(
                    record.get('Physical_Activity', '') or ''
                ),
                'sugar_intake': str(
                    record.get('Sugar_Intake', '') or ''
                ),
                'sleep_quality': str(
                    record.get('Sleep_Quality', '') or ''
                ),
                'water_intake': str(
                    record.get('Water_Intake', '') or ''
                ),
                'notes': str(
                    record.get('Notes', '') or ''
                ),
            })

        if state['table'] is not None:
            state['table'].rows = rows
            state['table'].update()

        records = filtered_records()

        if state['count_label'] is not None:
            state['count_label'].text = str(len(records))

        if state['total_label'] is not None:
            state['total_label'].text = (
                f'{len(state["records"])}'
            )

        healthy_count = sum(
            1
            for record in records
            if str(
                record.get('Health_Status', '')
            ).strip().lower()
            in {
                'healthy',
                'good',
                'normal',
                'well',
            }
        )

        if state['healthy_label'] is not None:
            state['healthy_label'].text = str(
                healthy_count
            )

        severity_values = [
            int(record.get('Severity') or 0)
            for record in records
        ]

        average_severity = (
            sum(severity_values) / len(severity_values)
            if severity_values
            else 0
        )

        if state['severity_label'] is not None:
            state['severity_label'].text = (
                f'{average_severity:.1f}'
            )

    def update_status_options():
        select = state['status_select']

        if select is None:
            return

        options = ['All'] + get_statuses()

        if state['status'] not in options:
            state['status'] = 'All'

        select.options = options
        select.value = state['status']
        select.update()

    def load_records():
        try:
            state['records'] = get_health_records() or []

        except Exception as exc:
            state['records'] = []

            ui.notify(
                f'Unable to load health records: {exc}',
                type='negative',
            )

        update_status_options()
        refresh_view()

    def set_search(value):
        state['search'] = value or ''
        refresh_view()

    def set_status(value):
        state['status'] = value or 'All'
        refresh_view()

    def clear_filters():
        state['search'] = ''
        state['status'] = 'All'

        search_input.value = ''
        search_input.update()

        update_status_options()
        refresh_view()

    def open_health_dialog(record=None):
        state['editing_record'] = record

        editing = record is not None

        state['dialog_title'].text = (
            'Edit Health Record'
            if editing
            else 'Add Health Record'
        )

        state['dialog_description'].text = (
            'Update the health information below.'
            if editing
            else 'Enter the details of your health record.'
        )

        if editing:
            state['date_input'].value = format_date(
                record.get('Date')
            )

            state['status_input'].value = str(
                record.get('Health_Status', '') or ''
            )

            state['energy_input'].value = (
                float(record.get('Energy_Level'))
                if record.get('Energy_Level') is not None
                else None
            )

            state['symptoms_input'].value = str(
                record.get('Symptoms', '') or ''
            )

            state['severity_input'].value = int(
                record.get('Severity') or 0
            )

            state['treatment_input'].value = str(
                record.get('Treatment', '') or ''
            )

            state['physical_activity_input'].value = str(
                record.get('Physical_Activity', '') or ''
            )

            state['sugar_intake_input'].value = str(
                record.get('Sugar_Intake', '') or ''
            )

            state['sleep_quality_input'].value = str(
                record.get('Sleep_Quality', '') or ''
            )

            state['water_intake_input'].value = str(
                record.get('Water_Intake', '') or ''
            )

            state['notes_input'].value = str(
                record.get('Notes', '') or ''
            )

        else:
            state['date_input'].value = ''
            state['status_input'].value = ''
            state['energy_input'].value = None
            state['symptoms_input'].value = ''
            state['severity_input'].value = 0
            state['treatment_input'].value = ''
            state['physical_activity_input'].value = ''
            state['sugar_intake_input'].value = ''
            state['sleep_quality_input'].value = ''
            state['water_intake_input'].value = ''
            state['notes_input'].value = ''

        for key in (
            'date_input',
            'status_input',
            'energy_input',
            'symptoms_input',
            'severity_input',
            'treatment_input',
            'physical_activity_input',
            'sugar_intake_input',
            'sleep_quality_input',
            'water_intake_input',
            'notes_input',
        ):
            state[key].update()

        state['dialog'].open()

    def save_health_record():
        date = (
            state['date_input'].value or ''
        ).strip()

        health_status = (
            state['status_input'].value or ''
        ).strip()

        energy_level = state['energy_input'].value

        symptoms = (
            state['symptoms_input'].value or ''
        ).strip()

        severity = state['severity_input'].value

        treatment = (
            state['treatment_input'].value or ''
        ).strip()

        physical_activity = (
            state['physical_activity_input'].value or ''
        ).strip()

        sugar_intake = (
            state['sugar_intake_input'].value or ''
        ).strip()

        sleep_quality = (
            state['sleep_quality_input'].value or ''
        ).strip()

        water_intake = (
            state['water_intake_input'].value or ''
        ).strip()

        notes = (
            state['notes_input'].value or ''
        ).strip()

        if not date:
            ui.notify(
                'Please select a date.',
                type='warning',
            )
            return

        if not health_status:
            ui.notify(
                'Please enter a health status.',
                type='warning',
            )
            return

        try:
            if energy_level in ('', None):
                energy_level = None
            else:
                energy_level = float(energy_level)

            if severity in ('', None):
                severity = 0
            else:
                severity = int(severity)

            if severity < 0:
                ui.notify(
                    'Severity cannot be negative.',
                    type='warning',
                )
                return

            record = state['editing_record']

            if record is None:
                add_health_record(
                    date,
                    health_status,
                    energy_level,
                    symptoms,
                    severity,
                    treatment,
                    physical_activity,
                    sugar_intake,
                    sleep_quality,
                    water_intake,
                    notes,
                )

                message = (
                    'Health record added successfully.'
                )

            else:
                update_health_record(
                    record.get('Health_ID'),
                    date,
                    health_status,
                    energy_level,
                    symptoms,
                    severity,
                    treatment,
                    physical_activity,
                    sugar_intake,
                    sleep_quality,
                    water_intake,
                    notes,
                )

                message = (
                    'Health record updated successfully.'
                )

            state['dialog'].close()
            state['editing_record'] = None

            load_records()

            ui.notify(
                message,
                type='positive',
            )

        except Exception as exc:
            ui.notify(
                f'Unable to save health record: {exc}',
                type='negative',
            )

    def find_record(row):
        health_id = row.get('id')

        for record in state['records']:
            if record.get('Health_ID') == health_id:
                return record

        return None

    def confirm_delete(record):
        if record is None:
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
                        'Delete Health Record'
                    ).classes(
                        'text-xl font-bold text-gray-900'
                    )

                    ui.label(
                        'Are you sure you want to delete this '
                        'health record? This action cannot be undone.'
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
                                record,
                            ),
                        ).props(
                            'unelevated no-caps'
                        ).classes(
                            'bg-red-600 text-white'
                        )

        dialog.open()

    def execute_delete(dialog, record):
        try:
            delete_health_record(
                record.get('Health_ID')
            )

            dialog.close()
            load_records()

            ui.notify(
                'Health record deleted successfully.',
                type='positive',
            )

        except Exception as exc:
            ui.notify(
                f'Unable to delete health record: {exc}',
                type='negative',
            )

    with ui.dialog() as health_dialog:
        state['dialog'] = health_dialog

        with ui.card().classes(
            'w-full '
            'max-w-[760px] '
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
                            'Add Health Record'
                        ).classes(
                            'text-xl font-bold text-gray-900'
                        )

                        state['dialog_description'] = ui.label(
                            'Enter the details of your health record.'
                        ).classes(
                            'text-sm text-gray-500'
                        )

                    ui.button(
                        icon='close',
                        on_click=health_dialog.close,
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

                    state['status_input'] = ui.input(
                        'Health Status',
                        placeholder='e.g. Healthy, Normal, Sick',
                    ).props(
                        'outlined'
                    ).classes(
                        'flex-1 min-w-[200px]'
                    )

                with ui.row().classes(
                    'w-full gap-3 flex-wrap'
                ):
                    state['energy_input'] = ui.number(
                        'Energy Level',
                        min=0,
                        max=100,
                        step=0.01,
                    ).props(
                        'outlined clearable'
                    ).classes(
                        'flex-1 min-w-[180px]'
                    )

                    state['severity_input'] = ui.number(
                        'Severity',
                        min=0,
                        step=1,
                    ).props(
                        'outlined'
                    ).classes(
                        'flex-1 min-w-[180px]'
                    )

                state['symptoms_input'] = ui.input(
                    'Symptoms',
                    placeholder='Describe symptoms...',
                ).props(
                    'outlined'
                ).classes(
                    'w-full'
                )

                state['treatment_input'] = ui.input(
                    'Treatment',
                    placeholder='Treatment or medication...',
                ).props(
                    'outlined'
                ).classes(
                    'w-full'
                )

                with ui.row().classes(
                    'w-full gap-3 flex-wrap'
                ):
                    state['physical_activity_input'] = ui.input(
                        'Physical Activity',
                        placeholder='e.g. Walking, Gym',
                    ).props(
                        'outlined'
                    ).classes(
                        'flex-1 min-w-[220px]'
                    )

                    state['sugar_intake_input'] = ui.input(
                        'Sugar Intake',
                        placeholder='e.g. Low, Medium, High',
                    ).props(
                        'outlined'
                    ).classes(
                        'flex-1 min-w-[220px]'
                    )

                with ui.row().classes(
                    'w-full gap-3 flex-wrap'
                ):
                    state['sleep_quality_input'] = ui.input(
                        'Sleep Quality',
                        placeholder='e.g. Poor, Good, Excellent',
                    ).props(
                        'outlined'
                    ).classes(
                        'flex-1 min-w-[220px]'
                    )

                    state['water_intake_input'] = ui.input(
                        'Water Intake',
                        placeholder='e.g. Low, Adequate, High',
                    ).props(
                        'outlined'
                    ).classes(
                        'flex-1 min-w-[220px]'
                    )

                state['notes_input'] = ui.textarea(
                    'Notes',
                    placeholder='Additional notes...',
                ).props(
                    'outlined'
                ).classes(
                    'w-full'
                )

                with ui.row().classes(
                    'w-full justify-end gap-2 pt-2'
                ):
                    ui.button(
                        'Cancel',
                        on_click=health_dialog.close,
                    ).props(
                        'flat no-caps'
                    ).classes(
                        'text-gray-600'
                    )

                    ui.button(
                        'Save Health Record',
                        icon='check',
                        on_click=save_health_record,
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
            with ui.column().classes(
                'gap-1'
            ):
                ui.label(
                    'Health'
                ).classes(
                    'text-2xl font-bold text-gray-900'
                )

                ui.label(
                    'Track, review, and manage your health records.'
                ).classes(
                    'text-sm text-gray-500'
                )

            ui.button(
                'Add Health Record',
                icon='add',
                on_click=lambda: open_health_dialog(),
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
                    'Total Records'
                ).classes(
                    'text-xs font-medium text-gray-500'
                )

                state['total_label'] = ui.label(
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
                    'Filtered Records'
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
                    'Healthy Records'
                ).classes(
                    'text-xs font-medium text-gray-500'
                )

                state['healthy_label'] = ui.label(
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
                    'Avg. Severity'
                ).classes(
                    'text-xs font-medium text-gray-500'
                )

                state['severity_label'] = ui.label(
                    '0.0'
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
                    label='Search health records',
                    placeholder=(
                        'Search status, symptoms, treatment, '
                        'activity, or notes...'
                    ),
                    on_change=lambda e: set_search(
                        e.value or ''
                    ),
                ).props(
                    'outlined clearable'
                ).classes(
                    'flex-1 min-w-[280px]'
                )

                state['status_select'] = ui.select(
                    options=['All'],
                    value='All',
                    label='Health Status',
                    on_change=lambda e: set_status(
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
                with ui.column().classes(
                    'gap-0'
                ):
                    ui.label(
                        'Health Records'
                    ).classes(
                        'text-base font-semibold text-gray-900'
                    )

                    ui.label(
                        'Your recorded health information'
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
                    'name': 'status',
                    'label': 'Status',
                    'field': 'status',
                    'align': 'left',
                },
                {
                    'name': 'energy',
                    'label': 'Energy',
                    'field': 'energy',
                    'align': 'right',
                },
                {
                    'name': 'symptoms',
                    'label': 'Symptoms',
                    'field': 'symptoms',
                    'align': 'left',
                },
                {
                    'name': 'severity',
                    'label': 'Severity',
                    'field': 'severity',
                    'align': 'right',
                },
                {
                    'name': 'physical_activity',
                    'label': 'Activity',
                    'field': 'physical_activity',
                    'align': 'left',
                },
                {
                    'name': 'sleep_quality',
                    'label': 'Sleep',
                    'field': 'sleep_quality',
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
                'flat separator=horizontal hide-pagination'
            ).classes(
                'w-full'
            )

            state['table'].add_slot(
                'body-cell-status',
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
                'body-cell-energy',
                r'''
                <q-td :props="props">
                    <span class="font-semibold text-gray-900">
                        {{ props.value || '—' }}
                    </span>
                </q-td>
                '''
            )

            state['table'].add_slot(
                'body-cell-severity',
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
                                'edit-health',
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
                                'delete-health',
                                props.row
                            )"
                        />
                    </div>
                </q-td>
                '''
            )

            state['table'].on(
                'edit-health',
                lambda event: open_health_dialog(
                    find_record(event.args)
                ),
            )

            state['table'].on(
                'delete-health',
                lambda event: confirm_delete(
                    find_record(event.args)
                ),
            )

    load_records()
