from datetime import time, timedelta
from pathlib import Path

from nicegui import ui

from components.header import create_header
from services.data.events import get_events

def format_event_time(event_time):
    if event_time is None:
        return None

    if isinstance(event_time, timedelta):
        total_seconds = int(event_time.total_seconds())

        hours = (total_seconds // 3600) % 24
        minutes = (total_seconds % 3600) // 60

        return f'{hours:02d}:{minutes:02d}'

    if isinstance(event_time, time):
        return event_time.strftime('%H:%M')

    return str(event_time)

@ui.page('/events')
def event_records_page():

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
    # Data
    # --------------------------------------------------

    events = get_events()

    # --------------------------------------------------
    # Page
    # --------------------------------------------------

    with ui.column().classes('events-page'):

        # --------------------------------------------------
        # Page Header
        # --------------------------------------------------

        with ui.row().classes('events-header'):

            with ui.column().classes('events-heading'):

                ui.label(
                    'Events'
                ).classes('events-title')

                ui.label(
                    'Track important moments and events in your life.'
                ).classes('events-subtitle')

            ui.button(
                'Add Event',
                icon='add',
                on_click=lambda: ui.navigate.to(
                    '/events/add'
                )
            ).classes('events-add-button')

        # --------------------------------------------------
        # Timeline
        # --------------------------------------------------

        if not events:

            with ui.column().classes('events-empty'):

                ui.icon(
                    'event_note',
                    size='64px'
                ).classes('events-empty-icon')

                ui.label(
                    'No events yet'
                ).classes('events-empty-title')

                ui.label(
                    'Start recording important moments in your life.'
                ).classes('events-empty-text')

                ui.button(
                    'Add Your First Event',
                    icon='add',
                    on_click=lambda: ui.navigate.to(
                        '/events/add'
                    )
                ).classes('events-empty-button')

        else:

            with ui.column().classes('events-timeline'):

                current_date = None

                for event in events:

                    event_date = event['Date']
                    event_time = format_event_time(event['Time'])

                    if event_date != current_date:

                        current_date = event_date

                        with ui.row().classes(
                            'event-group-date'
                        ):

                            ui.label(
                                event_date.strftime('%d %b %Y')
                            )

                    with ui.row().classes('event-item'):

                        # Timeline marker
                        with ui.column().classes(
                            'event-marker-column'
                        ):

                            ui.element(
                                'div'
                            ).classes('event-marker')

                        # Event card
                        with ui.card().classes(
                            'event-card'
                        ):

                            with ui.row().classes(
                                'event-card-header'
                            ):

                                with ui.column().classes(
                                    'event-card-heading'
                                ):

                                    ui.label(
                                        event['Event_Type']
                                    ).classes('event-type')


                                    if event_time:
                                        ui.label(
                                            event_time
                                        ).classes('event-time')

                                with ui.row().classes(
                                    'event-actions'
                                ):

                                    ui.button(
                                        icon='visibility',
                                        on_click=lambda event_id=event[
                                            'ID'
                                        ]: ui.navigate.to(
                                            f'/events/{event_id}'
                                        )
                                    ).props(
                                        'flat round dense'
                                    ).classes(
                                        'event-action event-view-action'
                                    )

                                    ui.button(
                                        icon='edit',
                                        on_click=lambda event_id=event[
                                            'ID'
                                        ]: ui.navigate.to(
                                            f'/events/{event_id}/edit'
                                        )
                                    ).props(
                                        'flat round dense'
                                    ).classes(
                                        'event-action event-edit-action'
                                    )

                                    def create_delete_dialog(
                                        event_id
                                    ):

                                        with ui.dialog() as dialog:

                                            with ui.card().classes(
                                                'event-delete-dialog'
                                            ):

                                                ui.icon(
                                                    'delete_outline',
                                                    size='40px'
                                                ).classes(
                                                    'event-delete-icon'
                                                )

                                                ui.label(
                                                    'Delete Event'
                                                ).classes(
                                                    'event-delete-title'
                                                )

                                                ui.label(
                                                    'Are you sure you want '
                                                    'to delete this event?'
                                                ).classes(
                                                    'event-delete-text'
                                                )

                                                with ui.row().classes(
                                                    'event-delete-actions'
                                                ):

                                                    ui.button(
                                                        'Cancel',
                                                        on_click=dialog.close
                                                    ).props(
                                                        'flat'
                                                    )

                                                    def confirm_delete():

                                                        from services.data.events import (
                                                            delete_event
                                                        )

                                                        delete_event(
                                                            event_id
                                                        )

                                                        dialog.close()

                                                        ui.navigate.to(
                                                            '/events'
                                                        )

                                                    ui.button(
                                                        'Delete',
                                                        icon='delete',
                                                        on_click=confirm_delete
                                                    ).props(
                                                        'color=negative'
                                                    )

                                        dialog.open()

                                    ui.button(
                                        icon='delete',
                                        on_click=lambda event_id=event[
                                            'ID'
                                        ]: create_delete_dialog(
                                            event_id
                                        )
                                    ).props(
                                        'flat round dense'
                                    ).classes(
                                        'event-action event-delete-action'
                                    )

                            if event['Description']:

                                ui.label(
                                    event['Description']
                                ).classes(
                                    'event-description'
                                )