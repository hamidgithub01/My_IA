from datetime import date
from pathlib import Path

from nicegui import ui

from components.header import create_header
from services.data.days import add_day

@ui.page('/days/add')
def add_day_page():


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
    # Page
    # --------------------------------------------------

    with ui.column().classes('days-page'):

        # --------------------------------------------------
        # Page Header
        # --------------------------------------------------

        with ui.row().classes('days-header'):

            with ui.column().classes('days-heading'):

                ui.label(
                    'Add Day'
                ).classes('days-title')

                ui.label(
                    'Record the details of your day.'
                ).classes('days-subtitle')

        # --------------------------------------------------
        # Form
        # --------------------------------------------------

        with ui.card().classes('days-form-card'):

            ui.label(
                'Daily Information'
            ).classes('days-section-title')

            # --------------------------------------------------
            # Date
            # --------------------------------------------------

            date_input = ui.input(
                'Date',
                value=str(date.today())
            ).props(
                'type=date'
            ).classes(
                'days-form-input days-date-input'
            )

            # --------------------------------------------------
            # Day Type
            # --------------------------------------------------

            day_type_input = ui.select(
                [
                    'Normal',
                    'Workday',
                    'Weekend',
                    'Holiday',
                    'Sick Day',
                    'Travel Day',
                    'Special Day',
                ],
                label='Day Type',
                value='Normal'
            ).classes(
                'days-form-input days-select-input'
            )

            # --------------------------------------------------
            # Work Status
            # --------------------------------------------------

            work_status_input = ui.select(
                [
                    'Working',
                    'Off',
                    'Vacation',
                    'Sick Leave',
                ],
                label='Work Status',
                value='Working'
            ).classes(
                'days-form-input days-select-input'
            )

            # --------------------------------------------------
            # Health Impact
            # --------------------------------------------------

            health_impact_input = ui.select(
                [
                    'Normal',
                    'Low',
                    'Moderate',
                    'High',
                ],
                label='Health Impact',
                value='Normal'
            ).classes(
                'days-form-input days-select-input'
            )

            # --------------------------------------------------
            # Travel
            # --------------------------------------------------

            travel_input = ui.select(
                [
                    'No',
                    'Yes',
                ],
                label='Travel',
                value='No'
            ).classes(
                'days-form-input days-select-input'
            )

            # --------------------------------------------------
            # Special Event
            # --------------------------------------------------

            special_event_input = ui.input(
                'Special Event'
            ).classes(
                'days-form-input days-special-event-input'
            )

            # --------------------------------------------------
            # Stress Level
            # --------------------------------------------------

            stress_level_input = ui.select(
                [
                    'Low',
                    'Moderate',
                    'High',
                ],
                label='Stress Level',
                value='Low'
            ).classes(
                'days-form-input days-select-input'
            )

            # --------------------------------------------------
            # Notes
            # --------------------------------------------------

            notes_input = ui.textarea(
                'Notes'
            ).classes(
                'days-form-input days-notes-input'
            )

            # --------------------------------------------------
            # Sleep Hours
            # --------------------------------------------------

            sleep_hours_input = ui.number(
                'Sleep Hours',
                min=0,
                max=24,
                step=0.5
            ).classes(
                'days-form-input days-sleep-input'
            )

            # --------------------------------------------------
            # Social Activity
            # --------------------------------------------------

            social_activity_input = ui.select(
                [
                    'None',
                    'Low',
                    'Moderate',
                    'High',
                ],
                label='Social Activity',
                value='None'
            ).classes(
                'days-form-input days-select-input'
            )

            # --------------------------------------------------
            # Location
            # --------------------------------------------------

            location_input = ui.input(
                'Location'
            ).classes(
                'days-form-input days-location-input'
            )

            # --------------------------------------------------
            # Actions
            # --------------------------------------------------

            with ui.row().classes('days-form-actions'):

                ui.button(
                    'Cancel',
                    icon='arrow_back',
                    on_click=lambda: ui.navigate.to(
                        '/days'
                    )
                ).props('flat')

                def save_day():

                    day_date = date_input.value
                    day_type = day_type_input.value
                    work_status = work_status_input.value
                    health_impact = health_impact_input.value
                    travel = travel_input.value

                    special_event = (
                        special_event_input.value
                    )

                    stress_level = stress_level_input.value
                    notes = notes_input.value
                    sleep_hours = sleep_hours_input.value

                    social_activity = (
                        social_activity_input.value
                    )

                    location = location_input.value

                    # --------------------------------------------------
                    # Validation
                    # --------------------------------------------------

                    if not day_date:
                        ui.notify(
                            'Date is required.',
                            type='negative'
                        )
                        return

                    if not day_type:
                        ui.notify(
                            'Day Type is required.',
                            type='negative'
                        )
                        return

                    if not work_status:
                        ui.notify(
                            'Work Status is required.',
                            type='negative'
                        )
                        return

                    if not health_impact:
                        ui.notify(
                            'Health Impact is required.',
                            type='negative'
                        )
                        return

                    if not travel:
                        ui.notify(
                            'Travel is required.',
                            type='negative'
                        )
                        return

                    if not stress_level:
                        ui.notify(
                            'Stress Level is required.',
                            type='negative'
                        )
                        return

                    if not social_activity:
                        ui.notify(
                            'Social Activity is required.',
                            type='negative'
                        )
                        return

                    # --------------------------------------------------
                    # Save
                    # --------------------------------------------------

                    add_day(
                        day_date,
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

                    ui.notify(
                        'Daily record added successfully.',
                        type='positive'
                    )

                    ui.navigate.to(
                        '/days'
                    )

                ui.button(
                    'Save Day',
                    icon='save',
                    on_click=save_day
                ).props(
                    'color=primary'
                )
