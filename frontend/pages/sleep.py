
from datetime import datetime, timedelta

from nicegui import ui

from services.data.sleep import (
    get_sleep_records,
    add_sleep_record,
    update_sleep_record,
    delete_sleep_record,
)


def sleep_page():
    state = {
        'records': [],
        'search': '',
        'sleep_type': 'All',
        'quality': 'All',
        'table': None,
        'total_label': None,
        'count_label': None,
        'average_duration_label': None,
        'dialog': None,
        'dialog_title': None,
        'dialog_description': None,
        'editing_record': None,
        'date_input': None,
        'start_time_input': None,
        'end_time_input': None,
        'duration_input': None,
        'sleep_type_input': None,
        'continuity_input': None,
        'location_input': None,
        'position_input': None,
        'awakenings_input': None,
        'sleep_quality_input': None,
        'noise_level_input': None,
        'light_level_input': None,
        'temperature_level_input': None,
        'comfort_level_input': None,
        'stress_input': None,
        'caffeine_input': None,
        'screen_input': None,
        'before_sleep_activity_input': None,
        'dreams_input': None,
        'notes_input': None,
        'sleep_type_select': None,
        'quality_select': None,
        'duration_hint': None,
    }

    def value(record, key, default=''):
        result = record.get(key, default)
        return default if result is None else result

    def format_time(value):
        if value is None or value == '':
            return ''

        if hasattr(value, 'total_seconds'):
            total_seconds = int(value.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f'{hours:02d}:{minutes:02d}:{seconds:02d}'

        return str(value)

    def format_duration(minutes):
        if minutes is None or minutes == '':
            return ''

        try:
            minutes = int(float(minutes))
        except (TypeError, ValueError):
            return str(minutes)

        hours, remaining = divmod(minutes, 60)

        if hours:
            return f'{hours}h {remaining:02d}m'

        return f'{remaining}m'

    def calculate_duration_minutes(start_time, end_time):
        """
        Calculate elapsed sleep time from start and end time.

        If the end time is earlier than the start time,
        the sleep session is assumed to cross midnight.
        """

        if not start_time or not end_time:
            return None

        try:
            start = datetime.strptime(
                start_time[:5],
                '%H:%M',
            )

            end = datetime.strptime(
                end_time[:5],
                '%H:%M',
            )

        except (TypeError, ValueError):
            return None

        if end <= start:
            end += timedelta(days=1)

        duration = int(
            (end - start).total_seconds() / 60
        )

        if duration <= 0:
            return None

        return duration

    def continuity_is_interrupted():
        continuity = str(
            state['continuity_input'].value or ''
        ).strip().lower()

        return continuity in {
            'interrupted',
            'مقاطع',
            'متقطع',
        }

    def has_awakenings():
        value = state['awakenings_input'].value

        if value in (None, ''):
            return False

        try:
            return int(float(value)) > 0
        except (TypeError, ValueError):
            return False

    def duration_requires_manual_entry():
        return (
            continuity_is_interrupted()
            or has_awakenings()
        )

    def update_duration_field():
        if (
            state['duration_input'] is None
            or state['start_time_input'] is None
            or state['end_time_input'] is None
        ):
            return

        if duration_requires_manual_entry():
            state['duration_input'].props(
                'outlined clearable'
            )

            state['duration_input'].enable()

            if state['duration_hint'] is not None:
                state['duration_hint'].text = (
                    'Enter the actual sleep duration after '
                    'accounting for awakenings or interruptions.'
                )

            return

        start_time = str(
            state['start_time_input'].value or ''
        ).strip()

        end_time = str(
            state['end_time_input'].value or ''
        ).strip()

        duration = calculate_duration_minutes(
            start_time,
            end_time,
        )

        if duration is not None:
            state['duration_input'].value = duration
            state['duration_input'].update()

            if state['duration_hint'] is not None:
                state['duration_hint'].text = (
                    f'Calculated automatically: '
                    f'{format_duration(duration)}'
                )
        else:
            state['duration_input'].value = None
            state['duration_input'].update()

            if state['duration_hint'] is not None:
                state['duration_hint'].text = (
                    'Duration will be calculated automatically '
                    'from the start and end time.'
                )

        state['duration_input'].disable()

    def get_sleep_types():
        return sorted({
            str(value(record, 'Sleep_Type')).strip()
            for record in state['records']
            if value(record, 'Sleep_Type')
        })

    def get_qualities():
        return sorted({
            str(value(record, 'Sleep_Quality')).strip()
            for record in state['records']
            if value(record, 'Sleep_Quality')
        })

    def filtered_records():
        search = state['search'].strip().lower()
        sleep_type = state['sleep_type']
        quality = state['quality']

        result = []

        for record in state['records']:
            record_type = str(
                value(record, 'Sleep_Type')
            ).strip()

            record_quality = str(
                value(record, 'Sleep_Quality')
            ).strip()

            if sleep_type != 'All' and record_type != sleep_type:
                continue

            if quality != 'All' and record_quality != quality:
                continue

            if search:
                searchable = ' '.join([
                    str(value(record, 'Date')),
                    record_type,
                    record_quality,
                    str(value(record, 'Location')),
                    str(value(record, 'Position')),
                    str(value(record, 'Continuity')),
                    str(value(record, 'Dreams')),
                    str(value(record, 'Notes')),
                ]).lower()

                if search not in searchable:
                    continue

            result.append(record)

        return result

    def refresh_view():
        records = filtered_records()
        rows = []

        for record in records:
            rows.append({
                'id': value(record, 'Sleep_ID'),
                'date': str(value(record, 'Date')),
                'start_time': format_time(
                    value(record, 'Start_Time')
                ),
                'end_time': format_time(
                    value(record, 'End_Time')
                ),
                'duration': format_duration(
                    value(record, 'Duration_Minutes')
                ),
                'sleep_type': str(
                    value(record, 'Sleep_Type')
                ),
                'quality': str(
                    value(record, 'Sleep_Quality')
                ),
                'continuity': str(
                    value(record, 'Continuity')
                ),
                'awakenings': value(
                    record,
                    'Awakenings',
                ),
            })

        if state['table'] is not None:
            state['table'].rows = rows
            state['table'].update()

        durations = []

        for record in records:
            duration = value(
                record,
                'Duration_Minutes',
            )

            if duration not in ('', None):
                try:
                    durations.append(float(duration))
                except (TypeError, ValueError):
                    pass

        average_duration = (
            sum(durations) / len(durations)
            if durations
            else 0
        )

        if state['count_label'] is not None:
            state['count_label'].text = str(len(records))

        if state['total_label'] is not None:
            state['total_label'].text = (
                f'{sum(durations) / 60:.1f} h'
                if durations
                else '0.0 h'
            )

        if state['average_duration_label'] is not None:
            state['average_duration_label'].text = (
                f'{average_duration / 60:.1f} h'
            )

    def update_filter_options():
        if state['sleep_type_select'] is not None:
            options = ['All'] + get_sleep_types()

            if state['sleep_type'] not in options:
                state['sleep_type'] = 'All'

            state['sleep_type_select'].options = options
            state['sleep_type_select'].value = state['sleep_type']
            state['sleep_type_select'].update()

        if state['quality_select'] is not None:
            options = ['All'] + get_qualities()

            if state['quality'] not in options:
                state['quality'] = 'All'

            state['quality_select'].options = options
            state['quality_select'].value = state['quality']
            state['quality_select'].update()

    def load_records():
        try:
            state['records'] = get_sleep_records() or []

        except Exception as exc:
            state['records'] = []

            ui.notify(
                f'Unable to load sleep records: {exc}',
                type='negative',
            )

        update_filter_options()
        refresh_view()

    def set_search(value):
        state['search'] = value or ''
        refresh_view()

    def set_sleep_type(value):
        state['sleep_type'] = value or 'All'
        refresh_view()

    def set_quality(value):
        state['quality'] = value or 'All'
        refresh_view()

    def clear_filters():
        state['search'] = ''
        state['sleep_type'] = 'All'
        state['quality'] = 'All'

        search_input.value = ''
        search_input.update()

        update_filter_options()
        refresh_view()

    def set_input(input_element, value):
        input_element.value = value
        input_element.update()

    def open_sleep_dialog(record=None):
        state['editing_record'] = record

        editing = record is not None

        state['dialog_title'].text = (
            'Edit Sleep Record'
            if editing
            else 'Add Sleep Record'
        )

        state['dialog_description'].text = (
            'Update the sleep information below.'
            if editing
            else 'Enter the details of your sleep record.'
        )

        if editing:
            set_input(
                state['date_input'],
                str(value(record, 'Date')),
            )

            set_input(
                state['start_time_input'],
                format_time(value(record, 'Start_Time')),
            )

            set_input(
                state['end_time_input'],
                format_time(value(record, 'End_Time')),
            )

            set_input(
                state['duration_input'],
                value(record, 'Duration_Minutes'),
            )

            set_input(
                state['sleep_type_input'],
                str(value(record, 'Sleep_Type')),
            )

            set_input(
                state['continuity_input'],
                str(value(record, 'Continuity')),
            )

            set_input(
                state['location_input'],
                str(value(record, 'Location')),
            )

            set_input(
                state['position_input'],
                str(value(record, 'Position')),
            )

            set_input(
                state['awakenings_input'],
                value(record, 'Awakenings'),
            )

            set_input(
                state['sleep_quality_input'],
                str(value(record, 'Sleep_Quality')),
            )

            set_input(
                state['noise_level_input'],
                str(value(record, 'Noise_Level')),
            )

            set_input(
                state['light_level_input'],
                str(value(record, 'Light_Level')),
            )

            set_input(
                state['temperature_level_input'],
                str(value(record, 'Temperature_Level')),
            )

            set_input(
                state['comfort_level_input'],
                str(value(record, 'Comfort_Level')),
            )

            set_input(
                state['stress_input'],
                str(value(record, 'Stress_Before_Sleep')),
            )

            set_input(
                state['caffeine_input'],
                str(value(record, 'Caffeine_Before_Sleep')),
            )

            set_input(
                state['screen_input'],
                str(value(record, 'Screen_Before_Sleep')),
            )

            set_input(
                state['before_sleep_activity_input'],
                str(value(record, 'Before_Sleep_Activity')),
            )

            set_input(
                state['dreams_input'],
                str(value(record, 'Dreams')),
            )

            set_input(
                state['notes_input'],
                str(value(record, 'Notes')),
            )

        else:
            set_input(state['date_input'], '')
            set_input(state['start_time_input'], '')
            set_input(state['end_time_input'], '')
            set_input(state['duration_input'], None)
            set_input(state['sleep_type_input'], '')
            set_input(state['continuity_input'], 'Continuous')
            set_input(state['location_input'], '')
            set_input(state['position_input'], '')
            set_input(state['awakenings_input'], 0)
            set_input(state['sleep_quality_input'], '')
            set_input(state['noise_level_input'], '')
            set_input(state['light_level_input'], '')
            set_input(state['temperature_level_input'], '')
            set_input(state['comfort_level_input'], '')
            set_input(state['stress_input'], '')
            set_input(state['caffeine_input'], '')
            set_input(state['screen_input'], '')
            set_input(state['before_sleep_activity_input'], '')
            set_input(state['dreams_input'], '')
            set_input(state['notes_input'], '')

        update_duration_field()
        state['dialog'].open()

    def save_sleep_record():
        date = str(
            state['date_input'].value or ''
        ).strip()

        start_time = str(
            state['start_time_input'].value or ''
        ).strip()

        end_time = str(
            state['end_time_input'].value or ''
        ).strip()

        duration_minutes = (
            state['duration_input'].value
        )

        sleep_type = str(
            state['sleep_type_input'].value or ''
        ).strip()

        continuity = str(
            state['continuity_input'].value or ''
        ).strip()

        location = str(
            state['location_input'].value or ''
        ).strip()

        position = str(
            state['position_input'].value or ''
        ).strip()

        awakenings = (
            state['awakenings_input'].value
        )

        sleep_quality = str(
            state['sleep_quality_input'].value or ''
        ).strip()

        noise_level = str(
            state['noise_level_input'].value or ''
        ).strip()

        light_level = str(
            state['light_level_input'].value or ''
        ).strip()

        temperature_level = str(
            state['temperature_level_input'].value or ''
        ).strip()

        comfort_level = str(
            state['comfort_level_input'].value or ''
        ).strip()

        stress_before_sleep = str(
            state['stress_input'].value or ''
        ).strip()

        caffeine_before_sleep = str(
            state['caffeine_input'].value or ''
        ).strip()

        screen_before_sleep = str(
            state['screen_input'].value or ''
        ).strip()

        before_sleep_activity = str(
            state['before_sleep_activity_input'].value or ''
        ).strip()

        dreams = str(
            state['dreams_input'].value or ''
        ).strip()

        notes = str(
            state['notes_input'].value or ''
        ).strip()

        if not date:
            ui.notify(
                'Please select a date.',
                type='warning',
            )
            return

        if not start_time:
            ui.notify(
                'Please enter the start time.',
                type='warning',
            )
            return

        if not end_time:
            ui.notify(
                'Please enter the end time.',
                type='warning',
            )
            return

        try:
            if awakenings in (None, ''):
                awakenings = 0
            else:
                awakenings = int(
                    float(awakenings)
                )

            if awakenings < 0:
                ui.notify(
                    'Awakenings cannot be negative.',
                    type='warning',
                )
                return

            manual_duration_required = (
                continuity.lower() == 'interrupted'
                or awakenings > 0
            )

            if manual_duration_required:
                if duration_minutes in (None, ''):
                    ui.notify(
                        'Please enter the actual sleep duration '
                        'because the sleep was interrupted.',
                        type='warning',
                    )
                    return

                duration_minutes = int(
                    float(duration_minutes)
                )

            else:
                duration_minutes = calculate_duration_minutes(
                    start_time,
                    end_time,
                )

                if duration_minutes is None:
                    ui.notify(
                        'Unable to calculate the sleep duration '
                        'from the selected times.',
                        type='warning',
                    )
                    return

            if duration_minutes <= 0:
                ui.notify(
                    'Duration must be greater than zero.',
                    type='warning',
                )
                return

            record = state['editing_record']

            if record is None:
                add_sleep_record(
                    date,
                    start_time,
                    end_time,
                    duration_minutes,
                    sleep_type,
                    continuity,
                    location,
                    position,
                    awakenings,
                    sleep_quality,
                    noise_level,
                    light_level,
                    temperature_level,
                    comfort_level,
                    stress_before_sleep,
                    caffeine_before_sleep,
                    screen_before_sleep,
                    before_sleep_activity,
                    dreams,
                    notes,
                )

                message = (
                    'Sleep record added successfully.'
                )

            else:
                update_sleep_record(
                    record.get('Sleep_ID'),
                    date,
                    start_time,
                    end_time,
                    duration_minutes,
                    sleep_type,
                    continuity,
                    location,
                    position,
                    awakenings,
                    sleep_quality,
                    noise_level,
                    light_level,
                    temperature_level,
                    comfort_level,
                    stress_before_sleep,
                    caffeine_before_sleep,
                    screen_before_sleep,
                    before_sleep_activity,
                    dreams,
                    notes,
                )

                message = (
                    'Sleep record updated successfully.'
                )

            state['dialog'].close()
            state['editing_record'] = None

            load_records()

            ui.notify(
                message,
                type='positive',
            )

        except ValueError:
            ui.notify(
                'Please enter valid numeric values.',
                type='warning',
            )

        except Exception as exc:
            ui.notify(
                f'Unable to save sleep record: {exc}',
                type='negative',
            )

    def find_record(row):
        sleep_id = row.get('id')

        for record in state['records']:
            if record.get('Sleep_ID') == sleep_id:
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
                        'Delete Sleep Record'
                    ).classes(
                        'text-xl font-bold text-gray-900'
                    )

                    ui.label(
                        'Are you sure you want to delete this '
                        'sleep record? This action cannot be undone.'
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
            delete_sleep_record(
                record.get('Sleep_ID')
            )

            dialog.close()
            load_records()

            ui.notify(
                'Sleep record deleted successfully.',
                type='positive',
            )

        except Exception as exc:
            ui.notify(
                f'Unable to delete sleep record: {exc}',
                type='negative',
            )

    with ui.dialog() as sleep_dialog:
        state['dialog'] = sleep_dialog

        with ui.card().classes(
            'w-full '
            'max-w-[900px] '
            'max-h-[90vh] '
            'overflow-y-auto '
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
                            'Add Sleep Record'
                        ).classes(
                            'text-xl font-bold text-gray-900'
                        )

                        state['dialog_description'] = ui.label(
                            'Enter the details of your sleep record.'
                        ).classes(
                            'text-sm text-gray-500'
                        )

                    ui.button(
                        icon='close',
                        on_click=sleep_dialog.close,
                    ).props(
                        'flat round dense'
                    ).classes(
                        'text-gray-500'
                    )

                ui.label(
                    'Basic Information'
                ).classes(
                    'text-base font-semibold text-gray-900'
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

                    state['start_time_input'] = ui.input(
                        'Start Time'
                    ).props(
                        'outlined type=time'
                    ).classes(
                        'flex-1 min-w-[180px]'
                    )

                    state['end_time_input'] = ui.input(
                        'End Time'
                    ).props(
                        'outlined type=time'
                    ).classes(
                        'flex-1 min-w-[180px]'
                    )

                with ui.row().classes(
                    'w-full gap-3 flex-wrap'
                ):
                    with ui.column().classes(
                        'flex-1 min-w-[200px] gap-1'
                    ):
                        state['duration_input'] = ui.number(
                            'Duration (minutes)',
                            min=1,
                            step=1,
                        ).props(
                            'outlined clearable'
                        )

                        state['duration_hint'] = ui.label(
                            'Duration will be calculated automatically '
                            'from the start and end time.'
                        ).classes(
                            'text-xs text-gray-500'
                        )

                    state['sleep_type_input'] = ui.input(
                        'Sleep Type',
                        placeholder='e.g. Night, Nap',
                    ).props(
                        'outlined'
                    ).classes(
                        'flex-1 min-w-[200px]'
                    )

                    state['continuity_input'] = ui.select(
                        options=[
                            'Continuous',
                            'Interrupted',
                        ],
                        label='Continuity',
                        value='Continuous',
                        on_change=lambda e: (
                            update_duration_field()
                        ),
                    ).props(
                        'outlined'
                    ).classes(
                        'flex-1 min-w-[200px]'
                    )

                with ui.row().classes(
                    'w-full gap-3 flex-wrap'
                ):
                    state['location_input'] = ui.input(
                        'Location',
                        placeholder='e.g. Home',
                    ).props(
                        'outlined'
                    ).classes(
                        'flex-1 min-w-[200px]'
                    )

                    state['position_input'] = ui.input(
                        'Position',
                        placeholder='e.g. Side, Back',
                    ).props(
                        'outlined'
                    ).classes(
                        'flex-1 min-w-[200px]'
                    )

                    state['awakenings_input'] = ui.number(
                        'Awakenings',
                        min=0,
                        step=1,
                        value=0,
                        on_change=lambda e: (
                            update_duration_field()
                        ),
                    ).props(
                        'outlined clearable'
                    ).classes(
                        'flex-1 min-w-[180px]'
                    )

                state['start_time_input'].on(
                    'change',
                    lambda: update_duration_field(),
                )

                state['end_time_input'].on(
                    'change',
                    lambda: update_duration_field(),
                )

                ui.separator()

                ui.label(
                    'Sleep Quality & Environment'
                ).classes(
                    'text-base font-semibold text-gray-900'
                )

                with ui.row().classes(
                    'w-full gap-3 flex-wrap'
                ):
                    state['sleep_quality_input'] = ui.input(
                        'Sleep Quality',
                        placeholder='e.g. Good, Fair, Poor',
                    ).props(
                        'outlined'
                    ).classes(
                        'flex-1 min-w-[200px]'
                    )

                    state['noise_level_input'] = ui.input(
                        'Noise Level',
                        placeholder='e.g. Low, Medium, High',
                    ).props(
                        'outlined'
                    ).classes(
                        'flex-1 min-w-[200px]'
                    )

                    state['light_level_input'] = ui.input(
                        'Light Level',
                        placeholder='e.g. Dark, Moderate, Bright',
                    ).props(
                        'outlined'
                    ).classes(
                        'flex-1 min-w-[200px]'
                    )

                with ui.row().classes(
                    'w-full gap-3 flex-wrap'
                ):
                    state['temperature_level_input'] = ui.input(
                        'Temperature Level',
                        placeholder='e.g. Cold, Comfortable, Hot',
                    ).props(
                        'outlined'
                    ).classes(
                        'flex-1 min-w-[200px]'
                    )

                    state['comfort_level_input'] = ui.input(
                        'Comfort Level',
                        placeholder='e.g. Low, Medium, High',
                    ).props(
                        'outlined'
                    ).classes(
                        'flex-1 min-w-[200px]'
                    )

                ui.separator()

                ui.label(
                    'Before Sleep'
                ).classes(
                    'text-base font-semibold text-gray-900'
                )

                with ui.row().classes(
                    'w-full gap-3 flex-wrap'
                ):
                    state['stress_input'] = ui.input(
                        'Stress Before Sleep',
                    ).props(
                        'outlined'
                    ).classes(
                        'flex-1 min-w-[220px]'
                    )

                    state['caffeine_input'] = ui.input(
                        'Caffeine Before Sleep',
                    ).props(
                        'outlined'
                    ).classes(
                        'flex-1 min-w-[220px]'
                    )

                    state['screen_input'] = ui.input(
                        'Screen Before Sleep',
                    ).props(
                        'outlined'
                    ).classes(
                        'flex-1 min-w-[220px]'
                    )

                state['before_sleep_activity_input'] = ui.input(
                    'Activity Before Sleep',
                    placeholder='What were you doing before sleeping?',
                ).props(
                    'outlined'
                ).classes(
                    'w-full'
                )

                ui.separator()

                ui.label(
                    'Notes'
                ).classes(
                    'text-base font-semibold text-gray-900'
                )

                state['dreams_input'] = ui.textarea(
                    'Dreams',
                    placeholder='Dreams or notable sleep experiences...',
                ).props(
                    'outlined'
                ).classes(
                    'w-full'
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
                        on_click=sleep_dialog.close,
                    ).props(
                        'flat no-caps'
                    ).classes(
                        'text-gray-600'
                    )

                    ui.button(
                        'Save Sleep Record',
                        icon='check',
                        on_click=save_sleep_record,
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
                    'Sleep'
                ).classes(
                    'text-2xl font-bold text-gray-900'
                )

                ui.label(
                    'Track, review, and organize your sleep records.'
                ).classes(
                    'text-sm text-gray-500'
                )

            ui.button(
                'Add Sleep Record',
                icon='add',
                on_click=lambda: open_sleep_dialog(),
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
                    'Total Sleep'
                ).classes(
                    'text-xs font-medium text-gray-500'
                )

                state['total_label'] = ui.label(
                    '0.0 h'
                ).classes(
                    'text-2xl font-bold text-gray-900 mt-1'
                )

            with ui.card().classes(
                'flex-1 min-w-[220px] p-4 '
                'rounded-[var(--radius-md)] '
                'shadow-none border border-gray-200'
            ):
                ui.label(
                    'Sleep Records'
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
                    'Average Duration'
                ).classes(
                    'text-xs font-medium text-gray-500'
                )

                state['average_duration_label'] = ui.label(
                    '0.0 h'
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
                    label='Search sleep records',
                    placeholder=(
                        'Search type, quality, location, '
                        'continuity, dreams, or notes...'
                    ),
                    on_change=lambda e: set_search(
                        e.value or ''
                    ),
                ).props(
                    'outlined clearable'
                ).classes(
                    'flex-1 min-w-[280px]'
                )

                state['sleep_type_select'] = ui.select(
                    options=['All'],
                    value='All',
                    label='Sleep Type',
                    on_change=lambda e: set_sleep_type(
                        e.value or 'All'
                    ),
                ).props(
                    'outlined'
                ).classes(
                    'w-[200px]'
                )

                state['quality_select'] = ui.select(
                    options=['All'],
                    value='All',
                    label='Quality',
                    on_change=lambda e: set_quality(
                        e.value or 'All'
                    ),
                ).props(
                    'outlined'
                ).classes(
                    'w-[200px]'
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
                        'Sleep Records'
                    ).classes(
                        'text-base font-semibold text-gray-900'
                    )

                    ui.label(
                        'Your recorded sleep sessions'
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
                    'name': 'start_time',
                    'label': 'Start',
                    'field': 'start_time',
                    'align': 'left',
                },
                {
                    'name': 'end_time',
                    'label': 'End',
                    'field': 'end_time',
                    'align': 'left',
                },
                {
                    'name': 'duration',
                    'label': 'Duration',
                    'field': 'duration',
                    'align': 'left',
                },
                {
                    'name': 'sleep_type',
                    'label': 'Type',
                    'field': 'sleep_type',
                    'align': 'left',
                },
                {
                    'name': 'quality',
                    'label': 'Quality',
                    'field': 'quality',
                    'align': 'left',
                },
                {
                    'name': 'continuity',
                    'label': 'Continuity',
                    'field': 'continuity',
                    'align': 'left',
                },
                {
                    'name': 'awakenings',
                    'label': 'Awakenings',
                    'field': 'awakenings',
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
                'body-cell-duration',
                r'''
                <q-td :props="props">
                    <span class="font-semibold text-gray-900">
                        {{ props.value }}
                    </span>
                </q-td>
                '''
            )

            state['table'].add_slot(
                'body-cell-sleep_type',
                r'''
                <q-td :props="props">
                    <q-badge
                        color="grey-2"
                        text-color="grey-8"
                        class="px-2 py-1"
                    >
                        {{ props.value || '—' }}
                    </q-badge>
                </q-td>
                '''
            )

            state['table'].add_slot(
                'body-cell-quality',
                r'''
                <q-td :props="props">
                    <q-badge
                        color="grey-2"
                        text-color="grey-8"
                        class="px-2 py-1"
                    >
                        {{ props.value || '—' }}
                    </q-badge>
                </q-td>
                '''
            )

            state['table'].add_slot(
                'body-cell-continuity',
                r'''
                <q-td :props="props">
                    <q-badge
                        color="grey-2"
                        text-color="grey-8"
                        class="px-2 py-1"
                    >
                        {{ props.value || '—' }}
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
                                'edit-sleep',
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
                                'delete-sleep',
                                props.row
                            )"
                        />
                    </div>
                </q-td>
                '''
            )

            state['table'].on(
                'edit-sleep',
                lambda event: open_sleep_dialog(
                    find_record(event.args)
                ),
            )

            state['table'].on(
                'delete-sleep',
                lambda event: confirm_delete(
                    find_record(event.args)
                ),
            )

    load_records()
