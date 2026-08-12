from pathlib import Path
from datetime import date, datetime

from nicegui import ui

from components.header import create_header
from services.data.events import add_event


@ui.page('/events/add')
def add_event_page():

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
    # Page
    # --------------------------------------------------

    with ui.column().classes('events-page'):

        # --------------------------------------------------
        # Header
        # --------------------------------------------------

        with ui.column().classes('events-heading'):

            ui.label(
                'Add Event'
            ).classes('events-title')

            ui.label(
                'Record an important moment or event.'
            ).classes('events-subtitle')

        # --------------------------------------------------
        # Form
        # --------------------------------------------------

        with ui.card().classes('event-form-card'):

            # Form heading

            with ui.row().classes('event-form-heading'):

                ui.icon(
                    'event'
                ).classes('event-form-heading-icon')

                with ui.column().classes(
                    'event-form-heading-text'
                ):

                    ui.label(
                        'Event Information'
                    ).classes(
                        'event-form-title'
                    )

                    ui.label(
                        'Add the details you want to remember.'
                    ).classes(
                        'event-form-subtitle'
                    )

            # --------------------------------------------------
            # Event Type
            # --------------------------------------------------

            event_type_input = ui.input(
                'Event Type *'
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
                    value=date.today().isoformat(),
                ).props(
                    'type=date outlined clearable'
                ).classes(
                    'event-form-input event-date-input'
                )

                time_input = ui.input(
                    'Time',
                    value=datetime.now().strftime('%H:%M'),
                ).props(
                    'type=time outlined clearable'
                ).classes(
                    'event-form-input event-time-input'
                )

            # --------------------------------------------------
            # Description
            # --------------------------------------------------

            description_input = ui.textarea(
                'Description'
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
                        '/events'
                    )
                ).props(
                    'flat'
                ).classes(
                    'event-cancel-button'
                )

                def save_event():

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
                    # Convert Date
                    # ------------------------------------------

                    event_date = None

                    if date_input.value:

                        try:

                            event_date = date.fromisoformat(
                                date_input.value
                            )

                        except ValueError:

                            ui.notify(
                                'Please enter a valid date.',
                                type='negative',
                            )

                            return

                    # ------------------------------------------
                    # Convert Time
                    # ------------------------------------------

                    event_time = None

                    if time_input.value:

                        try:

                            event_time = datetime.strptime(
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
                    # Save
                    # ------------------------------------------

                    add_event(
                        event_date,
                        event_time,
                        event_type,
                        description,
                    )

                    ui.notify(
                        'Event added successfully.',
                        type='positive',
                    )

                    ui.navigate.to(
                        '/events'
                    )

                ui.button(
                    'Save Event',
                    icon='save',
                    on_click=save_event,
                ).classes(
                    'event-save-button'
                )