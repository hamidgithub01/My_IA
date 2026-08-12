from pathlib import Path

from nicegui import ui

from components.header import create_header
from services.data.days import get_day

@ui.page('/days/{day_date}')
def day_details_page(day_date: str):


    create_header('Days')

    # --------------------------------------------------
    # CSS
    # --------------------------------------------------

    css_file = Path('styles/days.css')

    if css_file.exists():
        css_version = css_file.stat().st_mtime_ns

        ui.add_head_html(
            f'<link rel="stylesheet" '
            f'href="/styles/days.css?v={css_version}">'
        )

    # --------------------------------------------------
    # Data
    # --------------------------------------------------

    day = get_day(day_date)

    # --------------------------------------------------
    # Page
    # --------------------------------------------------

    with ui.column().classes('days-page'):

        # --------------------------------------------------
        # Page Header
        # --------------------------------------------------

        with ui.row().classes('days-header'):

            with ui.column().classes('days-heading'):

                ui.label(
                    'Day Details'
                ).classes('days-title')

                ui.label(
                    'Review the details of your daily record.'
                ).classes('days-subtitle')

        # --------------------------------------------------
        # Not Found
        # --------------------------------------------------

        if not day:

            with ui.card().classes('days-form-card'):

                with ui.column().classes('days-empty'):

                    ui.icon(
                        'event_busy',
                        size='48px'
                    )

                    ui.label(
                        'Daily record not found.'
                    ).classes('days-empty-title')

                    ui.label(
                        f'No daily record exists for {day_date}.'
                    ).classes('days-empty-text')

                    ui.button(
                        'Back to Days',
                        icon='arrow_back',
                        on_click=lambda: ui.navigate.to(
                            '/days'
                        )
                    )

        else:

            # --------------------------------------------------
            # Information Card
            # --------------------------------------------------

            with ui.card().classes('days-details-card'):

                ui.label(
                    'Daily Information'
                ).classes('days-section-title')

                # --------------------------------------------------
                # Date
                # --------------------------------------------------

                with ui.row().classes('days-detail-row'):

                    ui.label(
                        'Date'
                    ).classes('days-detail-label')

                    ui.label(
                        str(day['Date'])
                    ).classes('days-detail-value')

                # --------------------------------------------------
                # Day Type
                # --------------------------------------------------

                with ui.row().classes('days-detail-row'):

                    ui.label(
                        'Day Type'
                    ).classes('days-detail-label')

                    ui.label(
                        day['Day_Type'] or ''
                    ).classes('days-detail-value')

                # --------------------------------------------------
                # Work Status
                # --------------------------------------------------

                with ui.row().classes('days-detail-row'):

                    ui.label(
                        'Work Status'
                    ).classes('days-detail-label')

                    ui.label(
                        day['Work_Status'] or ''
                    ).classes('days-detail-value')

                # --------------------------------------------------
                # Health Impact
                # --------------------------------------------------

                with ui.row().classes('days-detail-row'):

                    ui.label(
                        'Health Impact'
                    ).classes('days-detail-label')

                    ui.label(
                        day['Health_Impact'] or ''
                    ).classes('days-detail-value')

                # --------------------------------------------------
                # Travel
                # --------------------------------------------------

                with ui.row().classes('days-detail-row'):

                    ui.label(
                        'Travel'
                    ).classes('days-detail-label')

                    ui.label(
                        day['Travel'] or ''
                    ).classes('days-detail-value')

                # --------------------------------------------------
                # Special Event
                # --------------------------------------------------

                with ui.row().classes('days-detail-row'):

                    ui.label(
                        'Special Event'
                    ).classes('days-detail-label')

                    ui.label(
                        day['Special_Event'] or ''
                    ).classes('days-detail-value')

                # --------------------------------------------------
                # Stress Level
                # --------------------------------------------------

                with ui.row().classes('days-detail-row'):

                    ui.label(
                        'Stress Level'
                    ).classes('days-detail-label')

                    ui.label(
                        day['Stress_Level'] or ''
                    ).classes('days-detail-value')

                # --------------------------------------------------
                # Notes
                # --------------------------------------------------

                with ui.row().classes('days-detail-row'):

                    ui.label(
                        'Notes'
                    ).classes('days-detail-label')

                    ui.label(
                        day['Notes'] or ''
                    ).classes(
                        'days-detail-value days-detail-notes'
                    )

                # --------------------------------------------------
                # Sleep Hours
                # --------------------------------------------------

                with ui.row().classes('days-detail-row'):

                    ui.label(
                        'Sleep Hours'
                    ).classes('days-detail-label')

                    ui.label(
                        str(day['Sleep_Hours'])
                        if day['Sleep_Hours'] is not None
                        else ''
                    ).classes('days-detail-value')

                # --------------------------------------------------
                # Social Activity
                # --------------------------------------------------

                with ui.row().classes('days-detail-row'):

                    ui.label(
                        'Social Activity'
                    ).classes('days-detail-label')

                    ui.label(
                        day['Social_Activity'] or ''
                    ).classes('days-detail-value')

                # --------------------------------------------------
                # Location
                # --------------------------------------------------

                with ui.row().classes('days-detail-row'):

                    ui.label(
                        'Location'
                    ).classes('days-detail-label')

                    ui.label(
                        day['Location'] or ''
                    ).classes('days-detail-value')

                # --------------------------------------------------
                # Actions
                # --------------------------------------------------

                with ui.row().classes('days-form-actions'):

                    ui.button(
                        'Back',
                        icon='arrow_back',
                        on_click=lambda: ui.navigate.to(
                            '/days'
                        )
                    ).props('flat')

                    ui.button(
                        'Edit',
                        icon='edit',
                        on_click=lambda: ui.navigate.to(
                            f'/days/{day_date}/edit'
                        )
                    ).props('color=primary')
