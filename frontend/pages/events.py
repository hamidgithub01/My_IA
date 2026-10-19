
from nicegui import ui

from services.data.events import (
    get_events,
    add_event,
    update_event,
    delete_event,
)


def events_page():
    state = {
        'events': [],
        'search': '',
        'event_type': 'All',
        'table': None,
        'count_label': None,
        'types_label': None,
        'type_select': None,
        'dialog': None,
        'dialog_title': None,
        'dialog_description': None,
        'editing_event': None,
        'date_input': None,
        'time_input': None,
        'event_type_input': None,
        'description_input': None,
    }

    def get_event_types():
        return sorted({
            str(event.get('Event_Type', '')).strip()
            for event in state['events']
            if event.get('Event_Type')
        })

    def filtered_events():
        search = state['search'].strip().lower()
        event_type = state['event_type']

        result = []

        for event in state['events']:
            current_type = str(
                event.get('Event_Type', '')
            ).strip()

            description = str(
                event.get('Description', '')
            ).strip()

            if event_type != 'All' and current_type != event_type:
                continue

            if search:
                searchable = (
                    f'{current_type} {description}'
                ).lower()

                if search not in searchable:
                    continue

            result.append(event)

        return result

    def format_time(value):
        if value is None or value == '':
            return ''

        if hasattr(value, 'total_seconds'):
            total_seconds = int(value.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            return f'{hours:02d}:{minutes:02d}:{seconds:02d}'

        value = str(value)

        if len(value) >= 5:
            return value[:5]

        return value

    def refresh_view():
        rows = []

        for event in filtered_events():
            rows.append({
                'id': event.get('ID'),
                'date': str(
                    event.get('Date', '') or ''
                ),
                'time': format_time(
                    event.get('Time')
                ),
                'event_type': str(
                    event.get('Event_Type', '') or ''
                ),
                'description': str(
                    event.get('Description', '') or ''
                ),
            })

        if state['table'] is not None:
            state['table'].rows = rows
            state['table'].update()

        if state['count_label'] is not None:
            state['count_label'].text = str(
                len(filtered_events())
            )

        if state['types_label'] is not None:
            state['types_label'].text = str(
                len(get_event_types())
            )

    def update_type_options():
        select = state['type_select']

        if select is None:
            return

        options = ['All'] + get_event_types()

        if state['event_type'] not in options:
            state['event_type'] = 'All'

        select.options = options
        select.value = state['event_type']
        select.update()

    def load_events():
        try:
            state['events'] = get_events() or []

        except Exception as exc:
            state['events'] = []

            ui.notify(
                f'Unable to load events: {exc}',
                type='negative',
            )

        update_type_options()
        refresh_view()

    def set_search(value):
        state['search'] = value or ''
        refresh_view()

    def set_event_type(value):
        state['event_type'] = value or 'All'
        refresh_view()

    def clear_filters():
        state['search'] = ''
        state['event_type'] = 'All'

        search_input.value = ''
        search_input.update()

        update_type_options()
        refresh_view()

    def open_event_dialog(event=None):
        state['editing_event'] = event

        editing = event is not None

        state['dialog_title'].text = (
            'Edit Event'
            if editing
            else 'Add Event'
        )

        state['dialog_description'].text = (
            'Update the event information below.'
            if editing
            else 'Enter the details of your event.'
        )

        if editing:
            state['date_input'].value = str(
                event.get('Date', '') or ''
            )

            state['time_input'].value = format_time(
                event.get('Time')
            )

            state['event_type_input'].value = str(
                event.get('Event_Type', '') or ''
            )

            state['description_input'].value = str(
                event.get('Description', '') or ''
            )

        else:
            state['date_input'].value = ''
            state['time_input'].value = ''
            state['event_type_input'].value = ''
            state['description_input'].value = ''

        state['date_input'].update()
        state['time_input'].update()
        state['event_type_input'].update()
        state['description_input'].update()

        state['dialog'].open()

    def save_event():
        date = (
            state['date_input'].value or ''
        ).strip()

        time = (
            state['time_input'].value or ''
        ).strip()

        event_type = (
            state['event_type_input'].value or ''
        ).strip()

        description = (
            state['description_input'].value or ''
        ).strip()

        if not date:
            ui.notify(
                'Please select a date.',
                type='warning',
            )
            return

        if not event_type:
            ui.notify(
                'Please enter an event type.',
                type='warning',
            )
            return

        try:
            event = state['editing_event']

            if event is None:
                add_event(
                    date,
                    time,
                    event_type,
                    description,
                )

                message = 'Event added successfully.'

            else:
                update_event(
                    event.get('ID'),
                    date,
                    time,
                    event_type,
                    description,
                )

                message = 'Event updated successfully.'

            state['dialog'].close()
            state['editing_event'] = None

            load_events()

            ui.notify(
                message,
                type='positive',
            )

        except Exception as exc:
            ui.notify(
                f'Unable to save event: {exc}',
                type='negative',
            )

    def find_event(row):
        event_id = row.get('id')

        for event in state['events']:
            if event.get('ID') == event_id:
                return event

        return None

    def confirm_delete(event):
        if event is None:
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
                        'Delete Event'
                    ).classes(
                        'text-xl font-bold text-gray-900'
                    )

                    ui.label(
                        'Are you sure you want to delete this '
                        'event? This action cannot be undone.'
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
                                event,
                            ),
                        ).props(
                            'unelevated no-caps'
                        ).classes(
                            'bg-red-600 text-white'
                        )

        dialog.open()

    def execute_delete(dialog, event):
        try:
            delete_event(
                event.get('ID')
            )

            dialog.close()
            load_events()

            ui.notify(
                'Event deleted successfully.',
                type='positive',
            )

        except Exception as exc:
            ui.notify(
                f'Unable to delete event: {exc}',
                type='negative',
            )

    with ui.dialog() as event_dialog:
        state['dialog'] = event_dialog

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
                            'Add Event'
                        ).classes(
                            'text-xl font-bold text-gray-900'
                        )

                        state['dialog_description'] = ui.label(
                            'Enter the details of your event.'
                        ).classes(
                            'text-sm text-gray-500'
                        )

                    ui.button(
                        icon='close',
                        on_click=event_dialog.close,
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

                state['event_type_input'] = ui.input(
                    'Event Type',
                    placeholder='e.g. Appointment',
                ).props(
                    'outlined'
                ).classes(
                    'w-full'
                )

                state['description_input'] = ui.input(
                    'Description',
                    placeholder='What happened or what is planned?',
                ).props(
                    'outlined type=textarea'
                ).classes(
                    'w-full'
                )

                with ui.row().classes(
                    'w-full justify-end gap-2 pt-2'
                ):
                    ui.button(
                        'Cancel',
                        on_click=event_dialog.close,
                    ).props(
                        'flat no-caps'
                    ).classes(
                        'text-gray-600'
                    )

                    ui.button(
                        'Save Event',
                        icon='check',
                        on_click=save_event,
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
                    'Events'
                ).classes(
                    'text-2xl font-bold text-gray-900'
                )

                ui.label(
                    'Manage, review, and organize your events.'
                ).classes(
                    'text-sm text-gray-500'
                )

            ui.button(
                'Add Event',
                icon='add',
                on_click=lambda: open_event_dialog(),
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
                    'Events'
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
                    'Event Types'
                ).classes(
                    'text-xs font-medium text-gray-500'
                )

                state['types_label'] = ui.label(
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
                    label='Search events',
                    placeholder='Search description or event type...',
                    on_change=lambda e: set_search(
                        e.value or ''
                    ),
                ).props(
                    'outlined clearable'
                ).classes(
                    'flex-1 min-w-[260px]'
                )

                state['type_select'] = ui.select(
                    options=['All'],
                    value='All',
                    label='Event Type',
                    on_change=lambda e: set_event_type(
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
                        'Event Records'
                    ).classes(
                        'text-base font-semibold text-gray-900'
                    )

                    ui.label(
                        'Your recorded events'
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
                    'name': 'event_type',
                    'label': 'Event Type',
                    'field': 'event_type',
                    'align': 'left',
                },
                {
                    'name': 'description',
                    'label': 'Description',
                    'field': 'description',
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
                'body-cell-event_type',
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
                                'edit-event',
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
                                'delete-event',
                                props.row
                            )"
                        />
                    </div>
                </q-td>
                '''
            )

            state['table'].on(
                'edit-event',
                lambda event: open_event_dialog(
                    find_event(event.args)
                ),
            )

            state['table'].on(
                'delete-event',
                lambda event: confirm_delete(
                    find_event(event.args)
                ),
            )

    load_events()
