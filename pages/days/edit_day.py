from pathlib import Path

from nicegui import ui

from components.header import create_header
from services.data.days import get_day, update_day


@ui.page('/days/{day_date}/edit')
def edit_day_page(day_date: str):

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
                    'Edit Day'
                ).classes('days-title')

                ui.label(
                    'Update the details of your daily record.'
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
                    value=str(day['Date'])
                ).props(
                    'type=date'
                ).classes('days-form-input')

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
                    value=day['Day_Type']
                ).classes('days-form-input days-select-input')

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
                    value=day['Work_Status']
                ).classes('days-form-input days-select-input')

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
                    value=day['Health_Impact']
                ).classes('days-form-input days-select-input')

                # --------------------------------------------------
                # Travel
                # --------------------------------------------------

                travel_input = ui.select(
                    [
                        'No',
                        'Yes',
                    ],
                    label='Travel',
                    value=day['Travel']
                ).classes('days-form-input days-select-input')

                # --------------------------------------------------
                # Special Event
                # --------------------------------------------------

                special_event_input = ui.input(
                    'Special Event',
                    value=day['Special_Event'] or ''
                ).classes('days-form-input days-select-input')

                # --------------------------------------------------
                # Stress Level
                # 1 - 10
                # --------------------------------------------------

                stress_level_input = ui.number(
                    'Stress Level',
                    value=day['Stress_Level'],
                    min=0,
                    max=10,
                    step=1
                ).classes('days-form-input days-select-input')

                # --------------------------------------------------
                # Notes
                # --------------------------------------------------

                notes_input = ui.textarea(
                    'Notes',
                    value=day['Notes'] or ''
                ).classes('days-form-input days-select-input')

                # --------------------------------------------------
                # Sleep Hours
                # --------------------------------------------------

                sleep_hours_input = ui.number(
                    'Sleep Hours',
                    value=day['Sleep_Hours'],
                    min=0,
                    max=24,
                    step=0.5
                ).classes('days-form-input days-select-input')

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
                    value=day['Social_Activity']
                ).classes('days-form-input days-select-input')

                # --------------------------------------------------
                # Location
                # --------------------------------------------------

                location_input = ui.input(
                    'Location',
                    value=day['Location'] or ''
                ).classes('days-form-input')

                # --------------------------------------------------
                # Actions
                # --------------------------------------------------

                with ui.row().classes('days-form-actions'):

                    ui.button(
                        'Cancel',
                        icon='arrow_back',
                        on_click=lambda: ui.navigate.to(
                            f'/days/{day_date}'
                        )
                    ).props('flat')

                    def save_changes():

                        new_date = date_input.value
                        day_type = day_type_input.value
                        work_status = work_status_input.value
                        health_impact = health_impact_input.value
                        travel = travel_input.value
                        special_event = (
                            special_event_input.value
                        )
                        stress_level = (
                            stress_level_input.value
                        )
                        notes = notes_input.value
                        sleep_hours = (
                            sleep_hours_input.value
                        )
                        social_activity = (
                            social_activity_input.value
                        )
                        location = location_input.value

                        # --------------------------------------------------
                        # Validation
                        # --------------------------------------------------

                        if not new_date:
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

                        if stress_level is None:
                            ui.notify(
                                'Stress Level is required.',
                                type='negative'
                            )
                            return

                        if not 1 <= float(stress_level) <= 10:
                            ui.notify(
                                'Stress Level must be between 1 and 10.',
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
                        # Update
                        # --------------------------------------------------

                        update_day(
                            new_date,
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
                            'Daily record updated successfully.',
                            type='positive'
                        )

                        ui.navigate.to(
                            f'/days/{new_date}'
                        )

                    ui.button(
                        'Save Changes',
                        icon='save',
                        on_click=save_changes
                    ).props(
                        'color=primary'
                    )