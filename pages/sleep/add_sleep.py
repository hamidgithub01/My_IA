from pathlib import Path
from datetime import datetime

from nicegui import ui

from components.layout import create_page_layout
from services.data.sleep import add_sleep_record


@ui.page('/sleep/add')
def add_sleep_page():

    content = create_page_layout(
        title='Add Sleep',
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
        # PAGE HEADER
        # ==================================================

        with ui.column().classes('sleep-form-header'):

            ui.label(
                'Record Sleep'
            ).classes('sleep-page-title')

            ui.label(
                'Describe when, where, and how you slept.'
            ).classes('sleep-page-subtitle')

        # ==================================================
        # FORM
        # ==================================================

        with ui.column().classes(
            'sleep-form-container'
        ):

            # ==================================================
            # TIMING
            # ==================================================

            with ui.card().classes('sleep-form-card'):

                ui.label(
                    'Sleep Timing'
                ).classes('sleep-form-section-title')

                ui.label(
                    'Enter when you went to sleep and when you woke up. '
                    'The system will calculate the duration automatically '
                    'when there were no awakenings.'
                ).classes('sleep-form-help')

                with ui.row().classes('sleep-form-grid'):

                    date = ui.date().props(
                        'outlined'
                    ).classes('w-full')

                    date.props('label="Date"')

                    start_time = ui.input(
                        label='Start Time',
                        placeholder='22:30',
                    ).props(
                        'outlined type=time'
                    ).classes('w-full')

                    end_time = ui.input(
                        label='End Time',
                        placeholder='06:30',
                    ).props(
                        'outlined type=time'
                    ).classes('w-full')

            # ==================================================
            # SLEEP TYPE & AWAKENINGS
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
                    label='Type',
                    value='Night',
                ).props(
                    'outlined'
                ).classes('w-full')

                continuity = ui.select(
                    {
                        'Continuous': 'Continuous',
                        'Interrupted': 'Interrupted',
                        'Highly Interrupted': 'Highly interrupted',
                    },
                    label='Continuity',
                    value='Continuous',
                ).props(
                    'outlined'
                ).classes('w-full')

                awakenings = ui.number(
                    label='Number of Awakenings',
                    min=0,
                    step=1,
                    value=0,
                ).props(
                    'outlined'
                ).classes('w-full')

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

                duration_minutes = ui.number(
                    label='Actual Sleep Duration (minutes)',
                    min=1,
                    step=1,
                ).props(
                    'outlined'
                ).classes('w-full')

            duration_container.set_visibility(False)

            # ==================================================
            # DURATION CALCULATION
            # ==================================================

            def calculate_period_minutes():

                if not start_time.value or not end_time.value:
                    return None

                try:

                    start = datetime.strptime(
                        start_time.value,
                        '%H:%M'
                    )

                    end = datetime.strptime(
                        end_time.value,
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

            def update_duration_mode():

                period_minutes = calculate_period_minutes()

                awakening_count = awakenings.value or 0

                # --------------------------------------------------
                # NO AWAKENINGS
                # --------------------------------------------------

                if awakening_count == 0:

                    duration_container.set_visibility(False)

                    if period_minutes is not None:

                        duration_minutes.value = period_minutes

                        duration_message.set_text(
                            f'Calculated sleep duration: '
                            f'{period_minutes // 60}h '
                            f'{period_minutes % 60}m.'
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
                        f'The total period from sleep start to wake-up '
                        f'is {theoretical_text} ({period_minutes} minutes). '
                        f'Because you reported {int(awakening_count)} '
                        f'awakening(s), your actual sleep duration must '
                        f'be less than {period_minutes} minutes.'
                    )

                else:

                    duration_message.set_text(
                        'Enter the start and end time first. '
                        'The actual sleep duration must be shorter '
                        'than the total sleep period.'
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
                        label='Location',
                    ).props(
                        'outlined'
                    ).classes('w-full')

                    position = ui.select(
                        {
                            'Lying': 'Lying',
                            'Sitting': 'Sitting',
                            'Reclined': 'Reclined',
                            'Other': 'Other',
                        },
                        label='Position',
                    ).props(
                        'outlined'
                    ).classes('w-full')

                    noise_level = ui.select(
                        {
                            'Low': 'Low',
                            'Moderate': 'Moderate',
                            'High': 'High',
                        },
                        label='Noise Level',
                    ).props(
                        'outlined'
                    ).classes('w-full')

                    light_level = ui.select(
                        {
                            'Dark': 'Dark',
                            'Dim': 'Dim',
                            'Bright': 'Bright',
                        },
                        label='Light Level',
                    ).props(
                        'outlined'
                    ).classes('w-full')

                    temperature_level = ui.select(
                        {
                            'Cool': 'Cool',
                            'Comfortable': 'Comfortable',
                            'Warm': 'Warm',
                            'Hot': 'Hot',
                        },
                        label='Temperature',
                    ).props(
                        'outlined'
                    ).classes('w-full')

                    comfort_level = ui.number(
                        label='Comfort Level (0-10)',
                        min=0,
                        max=10,
                        step=1,
                    ).props(
                        'outlined'
                    ).classes('w-full')

            # ==================================================
            # SLEEP QUALITY
            # ==================================================

            with ui.card().classes('sleep-form-card'):

                ui.label(
                    'Sleep Quality'
                ).classes('sleep-form-section-title')

                with ui.row().classes('sleep-form-grid'):

                    sleep_quality = ui.number(
                        label='Sleep Quality (0-10)',
                        min=0,
                        max=10,
                        step=1,
                    ).props(
                        'outlined'
                    ).classes('w-full')

                    stress_before_sleep = ui.number(
                        label='Stress Before Sleep (0-10)',
                        min=0,
                        max=10,
                        step=1,
                    ).props(
                        'outlined'
                    ).classes('w-full')

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
                        label='Caffeine',
                        value='None',
                    ).props(
                        'outlined'
                    ).classes('w-full')

                    screen_before_sleep = ui.select(
                        {
                            'None': 'None',
                            'Low': 'Low',
                            'Moderate': 'Moderate',
                            'High': 'High',
                        },
                        label='Screen Use',
                        value='None',
                    ).props(
                        'outlined'
                    ).classes('w-full')

                before_sleep_activity = ui.input(
                    label='Activity Before Sleep',
                    placeholder='Work, exercise, eating, relaxing...',
                ).props(
                    'outlined'
                ).classes('w-full')

            # ==================================================
            # DREAMS AND NOTES
            # ==================================================

            with ui.card().classes('sleep-form-card'):

                ui.label(
                    'Additional Information'
                ).classes('sleep-form-section-title')

                dreams = ui.textarea(
                    label='Dreams',
                ).props(
                    'outlined'
                ).classes('w-full')

                notes = ui.textarea(
                    label='Notes',
                ).props(
                    'outlined'
                ).classes('w-full')

            # ==================================================
            # ACTIONS
            # ==================================================

            with ui.row().classes('sleep-form-actions'):

                def save_record():

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

                    # ==================================================
                    # CALCULATE TOTAL SLEEP PERIOD
                    # ==================================================

                    period_minutes = calculate_period_minutes()

                    if period_minutes is None:

                        ui.notify(
                            'Please enter valid start and end times.',
                            type='negative',
                        )

                        return

                    # ==================================================
                    # DETERMINE ACTUAL SLEEP DURATION
                    # ==================================================

                    awakening_count = int(
                        awakenings.value or 0
                    )

                    # --------------------------------------------------
                    # NO AWAKENINGS
                    # --------------------------------------------------

                    if awakening_count == 0:

                        actual_duration = period_minutes

                    # --------------------------------------------------
                    # WITH AWAKENINGS
                    # --------------------------------------------------

                    else:

                        if not duration_minutes.value:

                            ui.notify(
                                'Please enter your actual sleep duration.',
                                type='negative',
                            )

                            return

                        actual_duration = int(
                            duration_minutes.value
                        )

                        if actual_duration >= period_minutes:

                            ui.notify(
                                'Actual sleep duration must be less than '
                                'the total sleep period because awakenings '
                                'were reported.',
                                type='negative',
                            )

                            return

                    # ==================================================
                    # SAVE
                    # ==================================================

                    add_sleep_record(
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
                        stress_before_sleep=stress_before_sleep.value,
                        caffeine_before_sleep=caffeine_before_sleep.value,
                        screen_before_sleep=screen_before_sleep.value,
                        before_sleep_activity=before_sleep_activity.value,
                        dreams=dreams.value,
                        notes=notes.value,
                    )

                    ui.notify(
                        'Sleep record added successfully.',
                        type='positive',
                    )

                    ui.navigate.to('/sleep')

                ui.button(
                    'Save Sleep',
                    icon='save',
                    on_click=save_record,
                ).props(
                    'unelevated'
                ).classes('sleep-save-button')

                ui.button(
                    'Cancel',
                    icon='close',
                    on_click=lambda: ui.navigate.to('/sleep'),
                ).props(
                    'flat'
                ).classes('sleep-cancel-button')