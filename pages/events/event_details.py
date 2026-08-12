from datetime import time, timedelta
from pathlib import Path

from nicegui import ui

from components.header import create_header
from services.data.events import (
    get_event,
    delete_event,
)


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

    return str(event_time)[:5]


@ui.page('/events/{event_id}')
def event_details_page(event_id: int):

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
                    'The event you are looking for does not exist '
                    'or has already been deleted.'
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
    # Format Values
    # --------------------------------------------------

    event_date = event['Date']
    event_time = format_event_time(event['Time'])

    description = (
        event['Description'].strip()
        if event['Description']
        else ''
    )

    # --------------------------------------------------
    # Page
    # --------------------------------------------------

    with ui.column().classes('events-page'):

        # --------------------------------------------------
        # Header
        # --------------------------------------------------

        with ui.row().classes('event-details-top'):

            with ui.column().classes('events-heading'):

                ui.label(
                    'Event Details'
                ).classes('events-title')

                ui.label(
                    'View the complete information about this event.'
                ).classes('events-subtitle')

            ui.button(
                'Back to Events',
                icon='arrow_back',
                on_click=lambda: ui.navigate.to(
                    '/events'
                )
            ).props(
                'flat'
            ).classes(
                'event-details-back-button'
            )

        # --------------------------------------------------
        # Event Hero
        # --------------------------------------------------

        with ui.card().classes('event-details-card'):

            with ui.column().classes(
                'event-details-content'
            ):

                # Event icon

                with ui.element(
                    'div'
                ).classes('event-details-icon'):

                    ui.icon(
                        'event'
                    )

                # Event type

                ui.label(
                    event['Event_Type']
                ).classes(
                    'event-details-type'
                )

                # Date and time

                with ui.row().classes(
                    'event-details-meta'
                ):

                    if event_date:

                        with ui.row().classes(
                            'event-details-meta-item'
                        ):

                            ui.icon(
                                'calendar_today'
                            )

                            ui.label(
                                event_date.strftime(
                                    '%d %B %Y'
                                )
                            )

                    if event_time:

                        with ui.row().classes(
                            'event-details-meta-item'
                        ):

                            ui.icon(
                                'schedule'
                            )

                            ui.label(
                                event_time
                            )

                # Description

                if description:

                    with ui.column().classes(
                        'event-details-description'
                    ):

                        ui.label(
                            'Description'
                        ).classes(
                            'event-details-description-title'
                        )

                        ui.label(
                            description
                        ).classes(
                            'event-details-description-text'
                        )

                else:

                    with ui.column().classes(
                        'event-details-no-description'
                    ):

                        ui.icon(
                            'notes'
                        )

                        ui.label(
                            'No description was added to this event.'
                        )

                # --------------------------------------------------
                # Actions
                # --------------------------------------------------

                with ui.row().classes(
                    'event-details-actions'
                ):

                    ui.button(
                        'Edit Event',
                        icon='edit',
                        on_click=lambda: ui.navigate.to(
                            f'/events/{event_id}/edit'
                        )
                    ).classes(
                        'event-details-edit-button'
                    )

                    def delete_current_event():

                        delete_event(event_id)

                        ui.notify(
                            'Event deleted successfully.',
                            type='positive',
                        )

                        ui.navigate.to(
                            '/events'
                        )

                    ui.button(
                        'Delete',
                        icon='delete',
                        on_click=delete_current_event,
                    ).props(
                        'color=negative'
                    ).classes(
                        'event-details-delete-button'
                    )