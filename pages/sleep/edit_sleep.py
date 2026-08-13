

from pathlib import Path
from datetime import datetime
from datetime import timedelta
from nicegui import ui

from components.layout import create_page_layout
from services.data.sleep import (
    get_sleep_record,
    update_sleep_record,
)


@ui.page('/sleep/{sleep_id}/edit')
def edit_sleep_page(sleep_id: int):

    content = create_page_layout(
        title='Edit Sleep',
        active_page='Sleep',
    )

    with content:

        # ==================================================
        # PAGE CSS
        # ==================================================

        css_file = Path('styles/sleep.css')

        if css_file.exists():

            css_version = css_file.stat().st_mtime_ns

            ui.add_head_html(
                f'<link rel="stylesheet" '
                f'href="/styles/sleep.css?v={css_version}">'
            )

        # ==================================================
        # DATA
        # ==================================================

        record = get_sleep_record(sleep_id)

        if not record:

            with ui.column().classes('sleep-not-found'):

                ui.icon(
                    'bedtime',
                    size='64px',
                )

                ui.label(
                    'Sleep record not found.'
                ).classes('text-xl font-semibold')

                ui.button(
                    'Back to Sleep',
                    icon='arrow_back',
                    on_click=lambda: ui.navigate.to('/sleep'),
                )

            return

        # ==================================================
        # HELPERS
        # ==================================================
        def format_time(value):

            if value is None:
                return None

            if isinstance(value, timedelta):

                total_seconds = int(
                    value.total_seconds()
                )

                hours = (
                    total_seconds // 3600
                ) % 24

                minutes = (
                    total_seconds % 3600
                ) // 60

                return f'{hours:02d}:{minutes:02d}'

            return str(value)[:5]

        def safe_number(value):

            if value is None or value == '':

                return None

            try:

                return float(value)

            except (ValueError, TypeError):

                return None

        def safe_integer(value, default=0):

            if value is None or value == '':

                return default

            try:

                return int(float(value))

            except (ValueError, TypeError):

                return default

        # ==================================================
        # PAGE HEADER
        # ==================================================

        with ui.row().classes('sleep-page-header'):

            with ui.column().classes('sleep-header-text'):

                ui.label(
                    'Edit Sleep Record'
                ).classes('sleep-page-title')

                ui.label(
                    'Update the details of this sleep session.'
                ).classes('sleep-page-subtitle')

            ui.button(
                'Back to Details',
                icon='arrow_back',
                on_click=lambda: ui.navigate.to(
                    f'/sleep/{sleep_id}'
                ),
            ).props(
                'flat'
            ).classes('sleep-action-button')

        # ==================================================
        # FORM
        # ==================================================

        with ui.column().classes('sleep-form-container'):

            # ==================================================
            # TIMING
            # ==================================================

            with ui.card().classes('sleep-form-card'):

                ui.label(
                    'Sleep Timing'
                ).classes('sleep-form-section-title')

                ui.label(
                    'Enter when you went to sleep and when you woke up. '
                    'If there were no awakenings, the system calculates '
                    'the sleep duration automatically.'
                ).classes('sleep-form-help')

                with ui.row().classes('sleep-form-grid'):

                    # --------------------------------------------------
                    # DATE
                    # --------------------------------------------------

                    date = ui.date(
                        value=record.get('Date'),
                    ).props(
                        'outlined'
                    ).classes('w-full')

                    date.props(
                        'label="Date"'
                    )

                    # --------------------------------------------------
                    # START TIME
                    # --------------------------------------------------

                    start_time = ui.input(
                        value=format_time(record.get('Start_Time'))
                    ).props(
                        'outlined type=time'
                    ).classes('w-full')

                    start_time.props(
                        'label="Start Time"'
                    )

                    # --------------------------------------------------
                    # END TIME
                    # --------------------------------------------------

                    end_time = ui.input(
                        value=format_time(record.get('End_Time'))
                    ).props(
                        'outlined type=time'
                    ).classes('w-full')

                    end_time.props(
                        'label="End Time"'
                    )

            # ==================================================
            # SLEEP PATTERN
            # ==================================================

            with ui.card().classes('sleep-form-card'):

                ui.label(
                    'Sleep Pattern'
                ).classes('sleep-form-section-title')

                sleep_type = ui.select(
                    {
                        'Night': 'Night sleep',
                        'Nap': 'Nap',
                        'Daytime': 'Daytime sleep',
                        'Other': 'Other',
                    },
                    value=record.get(
                        'Sleep_Type'
                    ),
                ).props(
                    'outlined'
                ).classes('w-full')

                sleep_type.props(
                    'label="Type"'
                )

                continuity = ui.select(
                    {
                        'Continuous': 'Continuous',
                        'Interrupted': 'Interrupted',
                        'Highly Interrupted': 'Highly interrupted',
                    },
                    value=record.get(
                        'Continuity'
                    ),
                ).props(
                    'outlined'
                ).classes('w-full')

                continuity.props(
                    'label="Continuity"'
                )

                # --------------------------------------------------
                # AWAKENINGS
                # --------------------------------------------------

                existing_awakenings = safe_integer(
                    record.get('Awakenings'),
                    0,
                )

                awakenings = ui.number(
                    value=existing_awakenings,
                    min=0,
                    step=1,
                ).props(
                    'outlined'
                ).classes('w-full')

                awakenings.props(
                    'label="Number of Awakenings"'
                )

            # ==================================================
            # ACTUAL SLEEP DURATION
            # ==================================================

            duration_container = ui.column().classes(
                'w-full gap-3'
            )

            with duration_container:

                duration_message = ui.label(
                    ''
                ).classes('sleep-form-help')

                existing_duration = safe_integer(
                    record.get('Duration_Minutes'),
                    0,
                )

                duration_minutes = ui.number(
                    value=(
                        existing_duration
                        if existing_duration > 0
                        else None
                    ),
                    min=1,
                    step=1,
                ).props(
                    'outlined'
                ).classes('w-full')

                duration_minutes.props(
                    'label="Actual Sleep Duration (minutes)"'
                )

            # ==================================================
            # DURATION CALCULATION
            # ==================================================

            def calculate_period_minutes():

                if not start_time.value or not end_time.value:

                    return None

                try:

                    start = datetime.strptime(
                        str(start_time.value),
                        '%H:%M'
                    )

                    end = datetime.strptime(
                        str(end_time.value),
                        '%H:%M'
                    )

                    minutes = (
                        end.hour * 60
                        + end.minute
                        - start.hour * 60
                        - start.minute
                    )

                    if minutes <= 0:

                        minutes += 24 * 60

                    return minutes

                except (ValueError, TypeError):

                    return None

            # ==================================================
            # UPDATE DURATION MODE
            # ==================================================

            def update_duration_mode():

                period_minutes = calculate_period_minutes()

                awakening_count = safe_integer(
                    awakenings.value,
                    0,
                )

                # --------------------------------------------------
                # NO AWAKENINGS
                # --------------------------------------------------

                if awakening_count == 0:

                    duration_container.set_visibility(False)

                    if period_minutes is not None:

                        duration_minutes.value = period_minutes

                        hours = period_minutes // 60
                        minutes = period_minutes % 60

                        if minutes:

                            duration_text = (
                                f'{hours}h {minutes}m'
                            )

                        else:

                            duration_text = f'{hours}h'

                        duration_message.set_text(
                            f'Calculated sleep duration: '
                            f'{duration_text}.'
                        )

                    else:

                        duration_minutes.value = None

                        duration_message.set_text(
                            'Enter the start and end time to calculate '
                            'sleep duration automatically.'
                        )

                    return

                # --------------------------------------------------
                # WITH AWAKENINGS
                # --------------------------------------------------

                duration_container.set_visibility(True)

                if period_minutes is not None:

                    hours = period_minutes // 60
                    minutes = period_minutes % 60

                    if minutes:

                        theoretical_text = (
                            f'{hours}h {minutes}m'
                        )

                    else:

                        theoretical_text = f'{hours}h'

                    duration_message.set_text(
                        f'The total period from sleep start to '
                        f'wake-up is {theoretical_text} '
                        f'({period_minutes} minutes). '
                        f'Because you reported '
                        f'{awakening_count} awakening(s), '
                        f'your actual sleep duration must be '
                        f'less than {period_minutes} minutes.'
                    )

                else:

                    duration_message.set_text(
                        'Enter the start and end time first. '
                        'The actual sleep duration must be shorter '
                        'than the total sleep period.'
                    )

            duration_container.set_visibility(
                existing_awakenings > 0
            )

            # ==================================================
            # REACTIVE EVENTS
            # ==================================================

            awakenings.on_value_change(
                lambda _: update_duration_mode()
            )

            start_time.on_value_change(
                lambda _: update_duration_mode()
            )

            end_time.on_value_change(
                lambda _: update_duration_mode()
            )

            # ==================================================
            # INITIAL CALCULATION
            # ==================================================

            update_duration_mode()

            # ==================================================
            # ENVIRONMENT
            # ==================================================

            with ui.card().classes('sleep-form-card'):

                ui.label(
                    'Sleep Environment'
                ).classes('sleep-form-section-title')

                with ui.row().classes('sleep-form-grid'):

                    location = ui.select(
                        {
                            'Bed': 'Bed',
                            'Sofa': 'Sofa',
                            'Car': 'Car',
                            'Chair': 'Chair',
                            'Floor': 'Floor',
                            'Other': 'Other',
                        },
                        value=record.get(
                            'Location'
                        ),
                    ).props(
                        'outlined'
                    ).classes('w-full')

                    location.props(
                        'label="Location"'
                    )

                    position = ui.select(
                        {
                            'Lying': 'Lying',
                            'Sitting': 'Sitting',
                            'Reclined': 'Reclined',
                            'Other': 'Other',
                        },
                        value=record.get(
                            'Position'
                        ),
                    ).props(
                        'outlined'
                    ).classes('w-full')

                    position.props(
                        'label="Position"'
                    )

                    noise_level = ui.select(
                        {
                            'Low': 'Low',
                            'Moderate': 'Moderate',
                            'High': 'High',
                        },
                        value=record.get(
                            'Noise_Level'
                        ),
                    ).props(
                        'outlined'
                    ).classes('w-full')

                    noise_level.props(
                        'label="Noise Level"'
                    )

                    light_level = ui.select(
                        {
                            'Dark': 'Dark',
                            'Dim': 'Dim',
                            'Bright': 'Bright',
                        },
                        value=record.get(
                            'Light_Level'
                        ),
                    ).props(
                        'outlined'
                    ).classes('w-full')

                    light_level.props(
                        'label="Light Level"'
                    )

                    temperature_level = ui.select(
                        {
                            'Cool': 'Cool',
                            'Comfortable': 'Comfortable',
                            'Warm': 'Warm',
                            'Hot': 'Hot',
                        },
                        value=record.get(
                            'Temperature_Level'
                        ),
                    ).props(
                        'outlined'
                    ).classes('w-full')

                    temperature_level.props(
                        'label="Temperature"'
                    )

                    comfort_value = safe_number(
                        record.get('Comfort_Level')
                    )

                    comfort_level = ui.number(
                        value=comfort_value,
                        min=0,
                        max=10,
                        step=1,
                    ).props(
                        'outlined'
                    ).classes('w-full')

                    comfort_level.props(
                        'label="Comfort Level (0-10)"'
                    )

            # ==================================================
            # SLEEP QUALITY
            # ==================================================

            with ui.card().classes('sleep-form-card'):

                ui.label(
                    'Sleep Quality'
                ).classes('sleep-form-section-title')

                with ui.row().classes('sleep-form-grid'):

                    quality_value = safe_number(
                        record.get('Sleep_Quality')
                    )

                    sleep_quality = ui.number(
                        value=quality_value,
                        min=0,
                        max=10,
                        step=1,
                    ).props(
                        'outlined'
                    ).classes('w-full')

                    sleep_quality.props(
                        'label="Sleep Quality (0-10)"'
                    )

                    stress_value = safe_number(
                        record.get('Stress_Before_Sleep')
                    )

                    stress_before_sleep = ui.number(
                        value=stress_value,
                        min=0,
                        max=10,
                        step=1,
                    ).props(
                        'outlined'
                    ).classes('w-full')

                    stress_before_sleep.props(
                        'label="Stress Before Sleep (0-10)"'
                    )

            # ==================================================
            # PRE-SLEEP FACTORS
            # ==================================================

            with ui.card().classes('sleep-form-card'):

                ui.label(
                    'Before Sleep'
                ).classes('sleep-form-section-title')

                with ui.row().classes('sleep-form-grid'):

                    caffeine_before_sleep = ui.select(
                        {
                            'None': 'None',
                            'Low': 'Low',
                            'Moderate': 'Moderate',
                            'High': 'High',
                        },
                        value=record.get(
                            'Caffeine_Before_Sleep'
                        ),
                    ).props(
                        'outlined'
                    ).classes('w-full')

                    caffeine_before_sleep.props(
                        'label="Caffeine"'
                    )

                    screen_before_sleep = ui.select(
                        {
                            'None': 'None',
                            'Low': 'Low',
                            'Moderate': 'Moderate',
                            'High': 'High',
                        },
                        value=record.get(
                            'Screen_Before_Sleep'
                        ),
                    ).props(
                        'outlined'
                    ).classes('w-full')

                    screen_before_sleep.props(
                        'label="Screen Use"'
                    )

                before_sleep_activity = ui.input(
                    value=record.get(
                        'Before_Sleep_Activity'
                    ),
                    placeholder=(
                        'Work, exercise, eating, relaxing...'
                    ),
                ).props(
                    'outlined'
                ).classes('w-full')

                before_sleep_activity.props(
                    'label="Activity Before Sleep"'
                )

            # ==================================================
            # DREAMS AND NOTES
            # ==================================================

            with ui.card().classes('sleep-form-card'):

                ui.label(
                    'Additional Information'
                ).classes('sleep-form-section-title')

                dreams = ui.textarea(
                    value=record.get('Dreams'),
                ).props(
                    'outlined'
                ).classes('w-full')

                dreams.props(
                    'label="Dreams"'
                )

                notes = ui.textarea(
                    value=record.get('Notes'),
                ).props(
                    'outlined'
                ).classes('w-full')

                notes.props(
                    'label="Notes"'
                )

            # ==================================================
            # ACTIONS
            # ==================================================

            with ui.row().classes(
                'sleep-form-actions'
            ):

                # ==================================================
                # SAVE
                # ==================================================

                def save_record():

                    # --------------------------------------------------
                    # REQUIRED FIELDS
                    # --------------------------------------------------

                    if not date.value:

                        ui.notify(
                            'Date is required.',
                            type='negative',
                        )

                        return

                    if not start_time.value:

                        ui.notify(
                            'Start time is required.',
                            type='negative',
                        )

                        return

                    if not end_time.value:

                        ui.notify(
                            'End time is required.',
                            type='negative',
                        )

                        return

                    # --------------------------------------------------
                    # CALCULATE TOTAL PERIOD
                    # --------------------------------------------------

                    period_minutes = (
                        calculate_period_minutes()
                    )

                    if period_minutes is None:

                        ui.notify(
                            'Please enter valid start and end times.',
                            type='negative',
                        )

                        return

                    # --------------------------------------------------
                    # AWAKENINGS
                    # --------------------------------------------------

                    awakening_count = safe_integer(
                        awakenings.value,
                        0,
                    )

                    if awakening_count < 0:

                        ui.notify(
                            'Number of awakenings cannot be negative.',
                            type='negative',
                        )

                        return

                    # --------------------------------------------------
                    # DETERMINE ACTUAL DURATION
                    # --------------------------------------------------

                    if awakening_count == 0:

                        actual_duration = period_minutes

                    else:

                        if not duration_minutes.value:

                            ui.notify(
                                'Please enter your actual sleep '
                                'duration.',
                                type='negative',
                            )

                            return

                        actual_duration = safe_integer(
                            duration_minutes.value,
                            0,
                        )

                        if actual_duration <= 0:

                            ui.notify(
                                'Actual sleep duration must be greater '
                                'than zero.',
                                type='negative',
                            )

                            return

                        if actual_duration >= period_minutes:

                            ui.notify(
                                'Actual sleep duration must be less '
                                'than the total sleep period because '
                                'awakenings were reported.',
                                type='negative',
                            )

                            return

                    # --------------------------------------------------
                    # SAVE
                    # --------------------------------------------------

                    update_sleep_record(
                        sleep_id=sleep_id,
                        date=date.value,
                        start_time=start_time.value,
                        end_time=end_time.value,
                        duration_minutes=actual_duration,
                        sleep_type=sleep_type.value,
                        continuity=continuity.value,
                        location=location.value,
                        position=position.value,
                        awakenings=awakening_count,
                        sleep_quality=sleep_quality.value,
                        noise_level=noise_level.value,
                        light_level=light_level.value,
                        temperature_level=temperature_level.value,
                        comfort_level=comfort_level.value,
                        stress_before_sleep=(
                            stress_before_sleep.value
                        ),
                        caffeine_before_sleep=(
                            caffeine_before_sleep.value
                        ),
                        screen_before_sleep=(
                            screen_before_sleep.value
                        ),
                        before_sleep_activity=(
                            before_sleep_activity.value
                        ),
                        dreams=dreams.value,
                        notes=notes.value,
                    )

                    ui.notify(
                        'Sleep record updated successfully.',
                        type='positive',
                    )

                    ui.navigate.to(
                        f'/sleep/{sleep_id}'
                    )

                # --------------------------------------------------
                # SAVE BUTTON
                # --------------------------------------------------

                ui.button(
                    'Save Changes',
                    icon='save',
                    on_click=save_record,
                ).props(
                    'unelevated'
                ).classes(
                    'sleep-save-button'
                )

                # --------------------------------------------------
                # CANCEL BUTTON
                # --------------------------------------------------

                ui.button(
                    'Cancel',
                    icon='close',
                    on_click=lambda: ui.navigate.to(
                        f'/sleep/{sleep_id}'
                    ),
                ).props(
                    'flat'
                ).classes(
                    'sleep-cancel-button'
                )
