from datetime import date, datetime, time, timedelta
from pathlib import Path

from nicegui import ui

from components.header import create_header
from services.data.events import (
    get_event,
    update_event,
)


def format_event_date(event_date):

    if event_date is None:
        return ''

    if isinstance(event_date, date):
        return event_date.isoformat()

    return str(event_date)


def format_event_time(event_time):

    if event_time is None:
        return ''

    if isinstance(event_time, timedelta):

        total_seconds = int(
            event_time.total_seconds()
        )

        hours = (total_seconds // 3600) % 24
        minutes = (total_seconds % 3600) // 60

        return f'{hours:02d}:{minutes:02d}'

    if isinstance(event_time, time):

        return event_time.strftime('%H:%M')

    return str(event_time)[:5]


@ui.page('/events/{event_id}/edit')
def edit_event_page(event_id: int):

    create_header('Events')

    # --------------------------------------------------
    # CSS
    # --------------------------------------------------

    css_file = Path('styles/events.css')

    if css_file.exists():

        css_version = css_file.stat().st_mtime_ns

        ui.add_head_html(
            f'<link rel="stylesheet" '
            f'href="/styles/events.css?v={css_version}">'
        )

    # --------------------------------------------------
    # Load Event
    # --------------------------------------------------

    event = get_event(event_id)

    if not event:

        with ui.column().classes('events-page'):

            with ui.column().classes('event-not-found'):

                ui.icon(
                    'event_busy',
                    size='56px'
                ).classes('event-not-found-icon')

                ui.label(
                    'Event not found'
                ).classes('event-not-found-title')

                ui.label(
                    'The event you are trying to edit '
                    'does not exist.'
                ).classes('event-not-found-text')

                ui.button(
                    'Back to Events',
                    icon='arrow_back',
                    on_click=lambda: ui.navigate.to(
                        '/events'
                    )
                ).classes('event-back-button')

        return

    # --------------------------------------------------
    # Existing Values
    # --------------------------------------------------

    event_date_value = format_event_date(
        event['Date']
    )

    event_time_value = format_event_time(
        event['Time']
    )

    event_type_value = (
        event['Event_Type']
        or ''
    )

    description_value = (
        event['Description']
        or ''
    )

    # --------------------------------------------------
    # Page
    # --------------------------------------------------

    with ui.column().classes('events-page'):

        # --------------------------------------------------
        # Header
        # --------------------------------------------------

        with ui.row().classes(
            'event-details-top'
        ):

            with ui.column().classes(
                'events-heading'
            ):

                ui.label(
                    'Edit Event'
                ).classes(
                    'events-title'
                )

                ui.label(
                    'Update the information about this event.'
                ).classes(
                    'events-subtitle'
                )

            ui.button(
                'Back to Event',
                icon='arrow_back',
                on_click=lambda: ui.navigate.to(
                    f'/events/{event_id}'
                )
            ).props(
                'flat'
            ).classes(
                'event-details-back-button'
            )

        # --------------------------------------------------
        # Form
        # --------------------------------------------------

        with ui.card().classes(
            'event-form-card'
        ):

            # --------------------------------------------------
            # Form Header
            # --------------------------------------------------

            with ui.row().classes(
                'event-form-heading'
            ):

                ui.icon(
                    'edit_calendar'
                ).classes(
                    'event-form-heading-icon'
                )

                with ui.column().classes(
                    'event-form-heading-text'
                ):

                    ui.label(
                        'Event Information'
                    ).classes(
                        'event-form-title'
                    )

                    ui.label(
                        'Modify the details of this event.'
                    ).classes(
                        'event-form-subtitle'
                    )

            # --------------------------------------------------
            # Event Type
            # --------------------------------------------------

            event_type_input = ui.input(
                'Event Type *',
                value=event_type_value,
            ).props(
                'outlined'
            ).classes(
                'event-form-input'
            )

            # --------------------------------------------------
            # Date / Time
            # --------------------------------------------------

            with ui.row().classes(
                'event-form-datetime'
            ):

                date_input = ui.input(
                    'Date',
                    value=event_date_value,
                ).props(
                    'type=date outlined clearable'
                ).classes(
                    'event-form-input event-date-input'
                )

                time_input = ui.input(
                    'Time',
                    value=event_time_value,
                ).props(
                    'type=time outlined clearable'
                ).classes(
                    'event-form-input event-time-input'
                )

            # --------------------------------------------------
            # Description
            # --------------------------------------------------

            description_input = ui.textarea(
                'Description',
                value=description_value,
            ).props(
                'outlined autogrow'
            ).classes(
                'event-form-description'
            )

            # --------------------------------------------------
            # Actions
            # --------------------------------------------------

            with ui.row().classes(
                'event-form-actions'
            ):

                ui.button(
                    'Cancel',
                    icon='arrow_back',
                    on_click=lambda: ui.navigate.to(
                        f'/events/{event_id}'
                    )
                ).props(
                    'flat'
                ).classes(
                    'event-cancel-button'
                )

                def save_changes():

                    # ------------------------------------------
                    # Validation
                    # ------------------------------------------

                    event_type = (
                        event_type_input.value.strip()
                        if event_type_input.value
                        else ''
                    )

                    if not event_type:

                        ui.notify(
                            'Please enter an event type.',
                            type='negative',
                        )

                        return

                    # ------------------------------------------
                    # Date
                    # ------------------------------------------

                    new_date = None

                    if date_input.value:

                        try:

                            new_date = date.fromisoformat(
                                date_input.value
                            )

                        except ValueError:

                            ui.notify(
                                'Please enter a valid date.',
                                type='negative',
                            )

                            return

                    # ------------------------------------------
                    # Time
                    # ------------------------------------------

                    new_time = None

                    if time_input.value:

                        try:

                            new_time = datetime.strptime(
                                time_input.value,
                                '%H:%M',
                            ).time()

                        except ValueError:

                            ui.notify(
                                'Please enter a valid time.',
                                type='negative',
                            )

                            return

                    # ------------------------------------------
                    # Description
                    # ------------------------------------------

                    description = (
                        description_input.value.strip()
                        if description_input.value
                        else ''
                    )

                    # ------------------------------------------
                    # Update
                    # ------------------------------------------

                    update_event(
                        event_id,
                        new_date,
                        new_time,
                        event_type,
                        description,
                    )

                    ui.notify(
                        'Event updated successfully.',
                        type='positive',
                    )

                    ui.navigate.to(
                        f'/events/{event_id}'
                    )

                ui.button(
                    'Save Changes',
                    icon='save',
                    on_click=save_changes,
                ).classes(
                    'event-save-button'
                )