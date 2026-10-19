
from nicegui import ui

from services.data.days import (
    get_days,
    add_day,
    update_day,
    delete_day,
)


def days_page():
    state = {
        'days': [],
        'search': '',
        'day_type': 'All',
        'work_status': 'All',
        'table': None,
        'count_label': None,
        'workday_label': None,
        'health_label': None,
        'day_type_select': None,
        'work_status_select': None,
        'dialog': None,
        'dialog_title': None,
        'dialog_description': None,
        'editing_day': None,
        'date_input': None,
        'day_type_input': None,
        'work_status_input': None,
        'health_impact_input': None,
        'travel_input': None,
        'special_event_input': None,
        'stress_level_input': None,
        'notes_input': None,
        'sleep_hours_input': None,
        'social_activity_input': None,
        'location_input': None,
    }

    def normalize(value):
        return str(value or '').strip()

    def get_day_types():
        return sorted({
            normalize(day.get('Day_Type'))
            for day in state['days']
            if normalize(day.get('Day_Type'))
        })

    def get_work_statuses():
        return sorted({
            normalize(day.get('Work_Status'))
            for day in state['days']
            if normalize(day.get('Work_Status'))
        })

    def filtered_days():
        search = state['search'].strip().lower()
        day_type = state['day_type']
        work_status = state['work_status']

        result = []

        for day in state['days']:
            current_day_type = normalize(
                day.get('Day_Type')
            )

            current_work_status = normalize(
                day.get('Work_Status')
            )

            if (
                day_type != 'All'
                and current_day_type != day_type
            ):
                continue

            if (
                work_status != 'All'
                and current_work_status != work_status
            ):
                continue

            if search:
                searchable = ' '.join([
                    normalize(day.get('Date')),
                    current_day_type,
                    current_work_status,
                    normalize(day.get('Health_Impact')),
                    normalize(day.get('Travel')),
                    normalize(day.get('Special_Event')),
                    normalize(day.get('Notes')),
                    normalize(day.get('Social_Activity')),
                    normalize(day.get('Location')),
                ]).lower()

                if search not in searchable:
                    continue

            result.append(day)

        return result

    def format_number(value, decimals=1):
        if value is None or value == '':
            return ''

        try:
            return f'{float(value):.{decimals}f}'
        except (TypeError, ValueError):
            return str(value)

    def format_boolean(value):
        text = normalize(value).lower()

        if text in {'yes', 'true', '1', 'y'}:
            return 'Yes'

        if text in {'no', 'false', '0', 'n'}:
            return 'No'

        return normalize(value)

    def refresh_view():
        rows = []

        for day in filtered_days():
            rows.append({
                'date': normalize(day.get('Date')),
                'day_type': normalize(day.get('Day_Type')),
                'work_status': normalize(
                    day.get('Work_Status')
                ),
                'health_impact': normalize(
                    day.get('Health_Impact')
                ),
                'travel': format_boolean(
                    day.get('Travel')
                ),
                'special_event': format_boolean(
                    day.get('Special_Event')
                ),
                'stress_level': format_number(
                    day.get('Stress_Level'),
                    1,
                ),
                'sleep_hours': format_number(
                    day.get('Sleep_Hours'),
                    1,
                ),
                'social_activity': normalize(
                    day.get('Social_Activity')
                ),
                'location': normalize(
                    day.get('Location')
                ),
                'notes': normalize(
                    day.get('Notes')
                ),
            })

        if state['table'] is not None:
            state['table'].rows = rows
            state['table'].update()

        visible_days = filtered_days()

        if state['count_label'] is not None:
            state['count_label'].text = str(
                len(visible_days)
            )

        workday_count = sum(
            1
            for day in visible_days
            if normalize(
                day.get('Day_Type')
            ).lower() in {
                'workday',
                'working day',
            }
        )

        if state['workday_label'] is not None:
            state['workday_label'].text = str(
                workday_count
            )

        health_count = sum(
            1
            for day in visible_days
            if normalize(
                day.get('Health_Impact')
            ).lower() not in {
                '',
                'none',
                'normal',
                'no',
            }
        )

        if state['health_label'] is not None:
            state['health_label'].text = str(
                health_count
            )

    def update_filter_options():
        day_type_select = state['day_type_select']
        work_status_select = state['work_status_select']

        day_type_options = ['All'] + get_day_types()
        work_status_options = ['All'] + get_work_statuses()

        if state['day_type'] not in day_type_options:
            state['day_type'] = 'All'

        if state['work_status'] not in work_status_options:
            state['work_status'] = 'All'

        if day_type_select is not None:
            day_type_select.options = day_type_options
            day_type_select.value = state['day_type']
            day_type_select.update()

        if work_status_select is not None:
            work_status_select.options = work_status_options
            work_status_select.value = state['work_status']
            work_status_select.update()

    def load_days():
        try:
            state['days'] = get_days() or []

        except Exception as exc:
            state['days'] = []

            ui.notify(
                f'Unable to load days: {exc}',
                type='negative',
            )

        update_filter_options()
        refresh_view()

    def set_search(value):
        state['search'] = value or ''
        refresh_view()

    def set_day_type(value):
        state['day_type'] = value or 'All'
        refresh_view()

    def set_work_status(value):
        state['work_status'] = value or 'All'
        refresh_view()

    def clear_filters():
        state['search'] = ''
        state['day_type'] = 'All'
        state['work_status'] = 'All'

        search_input.value = ''
        search_input.update()

        update_filter_options()
        refresh_view()

    def open_day_dialog(day=None):
        state['editing_day'] = day

        editing = day is not None

        state['dialog_title'].text = (
            'Edit Day'
            if editing
            else 'Add Day'
        )

        state['dialog_description'].text = (
            'Update the information for this day.'
            if editing
            else 'Enter the details for your day.'
        )

        if editing:
            state['date_input'].value = normalize(
                day.get('Date')
            )

            state['day_type_input'].value = normalize(
                day.get('Day_Type')
            )

            state['work_status_input'].value = normalize(
                day.get('Work_Status')
            )

            state['health_impact_input'].value = normalize(
                day.get('Health_Impact')
            )

            state['travel_input'].value = normalize(
                day.get('Travel')
            )

            state['special_event_input'].value = normalize(
                day.get('Special_Event')
            )

            state['stress_level_input'].value = (
                day.get('Stress_Level')
            )

            state['notes_input'].value = normalize(
                day.get('Notes')
            )

            state['sleep_hours_input'].value = (
                day.get('Sleep_Hours')
            )

            state['social_activity_input'].value = normalize(
                day.get('Social_Activity')
            )

            state['location_input'].value = normalize(
                day.get('Location')
            )

        else:
            state['date_input'].value = ''
            state['day_type_input'].value = 'Workday'
            state['work_status_input'].value = 'Working'
            state['health_impact_input'].value = 'None'
            state['travel_input'].value = 'No'
            state['special_event_input'].value = 'No'
            state['stress_level_input'].value = None
            state['notes_input'].value = ''
            state['sleep_hours_input'].value = None
            state['social_activity_input'].value = 'Low'
            state['location_input'].value = ''

        for key in (
            'date_input',
            'day_type_input',
            'work_status_input',
            'health_impact_input',
            'travel_input',
            'special_event_input',
            'stress_level_input',
            'notes_input',
            'sleep_hours_input',
            'social_activity_input',
            'location_input',
        ):
            control = state[key]

            if control is not None:
                control.update()

        state['dialog'].open()

    def save_day():
        date = normalize(
            state['date_input'].value
        )

        day_type = normalize(
            state['day_type_input'].value
        )

        work_status = normalize(
            state['work_status_input'].value
        )

        health_impact = normalize(
            state['health_impact_input'].value
        )

        travel = normalize(
            state['travel_input'].value
        )

        special_event = normalize(
            state['special_event_input'].value
        )

        stress_level = state[
            'stress_level_input'
        ].value

        notes = normalize(
            state['notes_input'].value
        )

        sleep_hours = state[
            'sleep_hours_input'
        ].value

        social_activity = normalize(
            state['social_activity_input'].value
        )

        location = normalize(
            state['location_input'].value
        )

        if not date:
            ui.notify(
                'Please select a date.',
                type='warning',
            )
            return

        if not day_type:
            ui.notify(
                'Please select a day type.',
                type='warning',
            )
            return

        if not work_status:
            ui.notify(
                'Please select a work status.',
                type='warning',
            )
            return

        try:
            if stress_level not in (None, ''):
                stress_level = float(
                    stress_level
                )

            if sleep_hours not in (None, ''):
                sleep_hours = float(
                    sleep_hours
                )

            day = state['editing_day']

            if day is None:
                add_day(
                    date,
                    day_type,
                    work_status,
                    health_impact,
                    travel,
                    special_event,
                    stress_level,
                    notes,
                    sleep_hours,
                    social_activity,
                    location,
                )

                message = 'Day added successfully.'

            else:
                update_day(
                    date,
                    day_type,
                    work_status,
                    health_impact,
                    travel,
                    special_event,
                    stress_level,
                    notes,
                    sleep_hours,
                    social_activity,
                    location,
                )

                message = 'Day updated successfully.'

            state['dialog'].close()
            state['editing_day'] = None

            load_days()

            ui.notify(
                message,
                type='positive',
            )

        except Exception as exc:
            ui.notify(
                f'Unable to save day: {exc}',
                type='negative',
            )

    def find_day(row):
        row_date = row.get('date')

        for day in state['days']:
            if normalize(
                day.get('Date')
            ) == row_date:
                return day

        return None

    def confirm_delete(day):
        if day is None:
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
                        'Delete Day'
                    ).classes(
                        'text-xl font-bold text-gray-900'
                    )

                    ui.label(
                        'Are you sure you want to delete this '
                        'day? This action cannot be undone.'
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
                                day,
                            ),
                        ).props(
                            'unelevated no-caps'
                        ).classes(
                            'bg-red-600 text-white'
                        )

        dialog.open()

    def execute_delete(dialog, day):
        try:
            delete_day(
                normalize(day.get('Date'))
            )

            dialog.close()
            load_days()

            ui.notify(
                'Day deleted successfully.',
                type='positive',
            )

        except Exception as exc:
            ui.notify(
                f'Unable to delete day: {exc}',
                type='negative',
            )

    # ======================================================
    # DAY DIALOG
    # ======================================================

    with ui.dialog() as day_dialog:
        state['dialog'] = day_dialog

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
                            'Add Day'
                        ).classes(
                            'text-xl font-bold text-gray-900'
                        )

                        state['dialog_description'] = ui.label(
                            'Enter the details for your day.'
                        ).classes(
                            'text-sm text-gray-500'
                        )

                    ui.button(
                        icon='close',
                        on_click=day_dialog.close,
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
                        'flex-1 min-w-[220px]'
                    )

                    state['day_type_input'] = ui.select(
                        [
                            'Workday',
                            'Holiday',
                            'Weekend',
                        ],
                        value='Workday',
                        label='Day Type',
                    ).props(
                        'outlined'
                    ).classes(
                        'flex-1 min-w-[220px]'
                    )

                with ui.row().classes(
                    'w-full gap-3 flex-wrap'
                ):
                    state['work_status_input'] = ui.select(
                        [
                            'Working',
                            'Off',
                            'Leave',
                            'Vacation',
                        ],
                        value='Working',
                        label='Work Status',
                    ).props(
                        'outlined'
                    ).classes(
                        'flex-1 min-w-[220px]'
                    )

                    state['health_impact_input'] = ui.select(
                        [
                            'None',
                            'Low',
                            'Normal',
                            'Moderate',
                            'Medium',
                            'High',
                        ],
                        value='None',
                        label='Health Impact',
                    ).props(
                        'outlined'
                    ).classes(
                        'flex-1 min-w-[220px]'
                    )

                with ui.row().classes(
                    'w-full gap-3 flex-wrap'
                ):
                    state['travel_input'] = ui.select(
                        [
                            'No',
                            'Yes',
                        ],
                        value='No',
                        label='Travel',
                    ).props(
                        'outlined'
                    ).classes(
                        'flex-1 min-w-[180px]'
                    )

                    state['special_event_input'] = ui.select(
                        [
                            'No',
                            'Yes',
                        ],
                        value='No',
                        label='Special Event',
                    ).props(
                        'outlined'
                    ).classes(
                        'flex-1 min-w-[180px]'
                    )

                    state['social_activity_input'] = ui.select(
                        [
                            'Low',
                            'Moderate',
                            'Medium',
                            'High',
                        ],
                        value='Low',
                        label='Social Activity',
                    ).props(
                        'outlined'
                    ).classes(
                        'flex-1 min-w-[180px]'
                    )

                with ui.row().classes(
                    'w-full gap-3 flex-wrap'
                ):
                    state['stress_level_input'] = ui.number(
                        'Stress Level',
                        min=0,
                        max=10,
                        step=0.1,
                    ).props(
                        'outlined clearable'
                    ).classes(
                        'flex-1 min-w-[220px]'
                    )

                    state['sleep_hours_input'] = ui.number(
                        'Sleep Hours',
                        min=0,
                        max=24,
                        step=0.1,
                    ).props(
                        'outlined clearable'
                    ).classes(
                        'flex-1 min-w-[220px]'
                    )

                state['location_input'] = ui.input(
                    'Location',
                    placeholder='e.g. Home',
                ).props(
                    'outlined'
                ).classes(
                    'w-full'
                )

                state['notes_input'] = ui.textarea(
                    'Notes',
                    placeholder='Additional notes about this day...',
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
                        on_click=day_dialog.close,
                    ).props(
                        'flat no-caps'
                    ).classes(
                        'text-gray-600'
                    )

                    ui.button(
                        'Save Day',
                        icon='check',
                        on_click=save_day,
                    ).props(
                        'unelevated no-caps'
                    ).classes(
                        'bg-primary text-white px-5'
                    )

    # ======================================================
    # PAGE
    # ======================================================

    with ui.column().classes(
        'w-full '
        'max-w-[1600px] '
        'mx-auto '
        'gap-6'
    ):
        with ui.row().classes(
            'w-full items-start justify-between '
            'gap-4 flex-wrap'
        ):
            with ui.column().classes('gap-1'):
                ui.label(
                    'Days'
                ).classes(
                    'text-2xl font-bold text-gray-900'
                )

                ui.label(
                    'Manage and review your daily behavioral context.'
                ).classes(
                    'text-sm text-gray-500'
                )

            ui.button(
                'Add Day',
                icon='add',
                on_click=lambda: open_day_dialog(),
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
            'w-full gap-4 flex-wrap'
        ):
            with ui.card().classes(
                'flex-1 min-w-[220px] p-4 '
                'rounded-[var(--radius-md)] '
                'shadow-none border border-gray-200'
            ):
                ui.label(
                    'Days'
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
                    'Workdays'
                ).classes(
                    'text-xs font-medium text-gray-500'
                )

                state['workday_label'] = ui.label(
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
                    'Health Impact Days'
                ).classes(
                    'text-xs font-medium text-gray-500'
                )

                state['health_label'] = ui.label(
                    '0'
                ).classes(
                    'text-2xl font-bold text-gray-900 mt-1'
                )

        # ==================================================
        # FILTERS
        # ==================================================

        with ui.card().classes(
            'w-full p-4 '
            'rounded-[var(--radius-md)] '
            'shadow-none border border-gray-200'
        ):
            with ui.row().classes(
                'w-full items-end gap-3 flex-wrap'
            ):
                search_input = ui.input(
                    label='Search days',
                    placeholder=(
                        'Search date, notes, location, '
                        'status...'
                    ),
                    on_change=lambda e: set_search(
                        e.value or ''
                    ),
                ).props(
                    'outlined clearable'
                ).classes(
                    'flex-1 min-w-[280px]'
                )

                state['day_type_select'] = ui.select(
                    options=['All'],
                    value='All',
                    label='Day Type',
                    on_change=lambda e: set_day_type(
                        e.value or 'All'
                    ),
                ).props(
                    'outlined'
                ).classes(
                    'w-[210px]'
                )

                state['work_status_select'] = ui.select(
                    options=['All'],
                    value='All',
                    label='Work Status',
                    on_change=lambda e: set_work_status(
                        e.value or 'All'
                    ),
                ).props(
                    'outlined'
                ).classes(
                    'w-[210px]'
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
                        'Day Records'
                    ).classes(
                        'text-base font-semibold text-gray-900'
                    )

                    ui.label(
                        'Your recorded daily context'
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
                    'name': 'day_type',
                    'label': 'Day Type',
                    'field': 'day_type',
                    'align': 'left',
                },
                {
                    'name': 'work_status',
                    'label': 'Work Status',
                    'field': 'work_status',
                    'align': 'left',
                },
                {
                    'name': 'health_impact',
                    'label': 'Health',
                    'field': 'health_impact',
                    'align': 'left',
                },
                {
                    'name': 'travel',
                    'label': 'Travel',
                    'field': 'travel',
                    'align': 'center',
                },
                {
                    'name': 'special_event',
                    'label': 'Event',
                    'field': 'special_event',
                    'align': 'center',
                },
                {
                    'name': 'stress_level',
                    'label': 'Stress',
                    'field': 'stress_level',
                    'align': 'right',
                },
                {
                    'name': 'sleep_hours',
                    'label': 'Sleep',
                    'field': 'sleep_hours',
                    'align': 'right',
                },
                {
                    'name': 'social_activity',
                    'label': 'Social',
                    'field': 'social_activity',
                    'align': 'left',
                },
                {
                    'name': 'location',
                    'label': 'Location',
                    'field': 'location',
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
                row_key='date',
            ).props(
                'flat separator=horizontal hide-pagination'
            ).classes(
                'w-full'
            )

            state['table'].add_slot(
                'body-cell-day_type',
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
                'body-cell-work_status',
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
                'body-cell-health_impact',
                r'''
                <q-td :props="props">
                    <span class="font-medium">
                        {{ props.value || 'None' }}
                    </span>
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
                                'edit-day',
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
                                'delete-day',
                                props.row
                            )"
                        />
                    </div>
                </q-td>
                '''
            )

            state['table'].on(
                'edit-day',
                lambda event: open_day_dialog(
                    find_day(event.args)
                ),
            )

            state['table'].on(
                'delete-day',
                lambda event: confirm_delete(
                    find_day(event.args)
                ),
            )

    load_days()
