
from pathlib import Path

from nicegui import ui

from components.layout import create_page_layout
from services.data.sleep import (
    get_sleep_record,
    delete_sleep_record,
)


@ui.page('/sleep/{sleep_id}')
def sleep_details_page(sleep_id: int):

    content = create_page_layout(
        title='Sleep Details',
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

                ui.label(
                    'The requested sleep session does not exist '
                    'or may have been deleted.'
                )

                ui.button(
                    'Back to Sleep',
                    icon='arrow_back',
                    on_click=lambda: ui.navigate.to('/sleep'),
                ).props('unelevated')

            return

        # ==================================================
        # HELPERS
        # ==================================================

        def value_or_dash(value):

            if value is None or value == '':

                return '—'

            return str(value)

        def duration_text(minutes):

            if minutes is None:

                return '—'

            minutes = int(minutes)

            hours = minutes // 60
            remaining_minutes = minutes % 60

            if hours and remaining_minutes:

                return f'{hours}h {remaining_minutes}m'

            if hours:

                return f'{hours}h'

            return f'{remaining_minutes}m'

        def calculate_period_minutes():

            start = record.get('Start_Time')
            end = record.get('End_Time')

            if not start or not end:
                return None

            try:

                start_hour, start_minute = map(
                    int,
                    str(start).split(':')[:2]
                )

                end_hour, end_minute = map(
                    int,
                    str(end).split(':')[:2]
                )

                minutes = (
                    end_hour * 60
                    + end_minute
                    - start_hour * 60
                    - start_minute
                )

                if minutes <= 0:
                    minutes += 24 * 60

                return minutes

            except (ValueError, TypeError):

                return None

        def info_item(icon, label, value):

            with ui.column().classes('sleep-detail-item'):

                with ui.row().classes('sleep-detail-item-heading'):

                    ui.icon(
                        icon,
                        size='20px',
                    )

                    ui.label(
                        label
                    ).classes('sleep-detail-label')

                ui.label(
                    value_or_dash(value)
                ).classes('sleep-detail-value')

        # ==================================================
        # SLEEP CALCULATIONS
        # ==================================================

        actual_duration = record.get('Duration_Minutes')
        period_minutes = calculate_period_minutes()

        awakenings = record.get('Awakenings') or 0

        has_interruptions = (
            awakenings is not None
            and int(awakenings) > 0
            and period_minutes is not None
            and actual_duration is not None
        )

        lost_minutes = None

        if has_interruptions:

            lost_minutes = (
                period_minutes - int(actual_duration)
            )

        # ==================================================
        # HEADER
        # ==================================================

        with ui.row().classes('sleep-details-header'):

            with ui.column().classes(
                'sleep-details-title-group'
            ):

                with ui.row().classes('sleep-details-kicker'):

                    ui.icon(
                        'bedtime',
                        size='20px',
                    )

                    ui.label(
                        'SLEEP SESSION'
                    )

                ui.label(
                    value_or_dash(record.get('Date'))
                ).classes('sleep-page-title')

                ui.label(
                    'A detailed view of this sleep session and '
                    'the conditions surrounding it.'
                ).classes('sleep-details-date')

            with ui.row().classes('sleep-details-actions'):

                ui.button(
                    'Back',
                    icon='arrow_back',
                    on_click=lambda: ui.navigate.to('/sleep'),
                ).props(
                    'flat'
                ).classes('sleep-action-button')

                ui.button(
                    'Edit',
                    icon='edit',
                    on_click=lambda:
                        ui.navigate.to(
                            f'/sleep/{sleep_id}/edit'
                        ),
                ).props(
                    'unelevated'
                ).classes('sleep-edit-button')

                # ==================================================
                # DELETE CONFIRMATION
                # ==================================================

                def delete_record():

                    with ui.dialog() as dialog:

                        with ui.card().classes(
                            'sleep-delete-dialog'
                        ):

                            ui.icon(
                                'warning',
                                size='48px',
                            ).classes(
                                'sleep-delete-warning-icon'
                            )

                            ui.label(
                                'Delete Sleep Record?'
                            ).classes(
                                'sleep-delete-dialog-title'
                            )

                            ui.label(
                                f'You are about to delete the sleep '
                                f'session from '
                                f'{value_or_dash(record.get("Date"))}.'
                            ).classes(
                                'sleep-delete-dialog-text'
                            )

                            ui.label(
                                'This action cannot be undone.'
                            ).classes(
                                'sleep-delete-dialog-warning'
                            )

                            with ui.row().classes(
                                'sleep-delete-dialog-actions'
                            ):

                                ui.button(
                                    'Cancel',
                                    icon='close',
                                    on_click=dialog.close,
                                ).props(
                                    'flat'
                                ).classes(
                                    'sleep-cancel-button'
                                )

                                def confirm_delete():

                                    delete_sleep_record(
                                        sleep_id
                                    )

                                    dialog.close()

                                    ui.notify(
                                        'Sleep record deleted successfully.',
                                        type='positive',
                                    )

                                    ui.navigate.to('/sleep')

                                ui.button(
                                    'Delete Permanently',
                                    icon='delete_forever',
                                    on_click=confirm_delete,
                                ).props(
                                    'unelevated'
                                ).classes(
                                    'sleep-confirm-delete-button'
                                )

                    dialog.open()

                ui.button(
                    'Delete',
                    icon='delete',
                    on_click=delete_record,
                ).props(
                    'flat'
                ).classes(
                    'sleep-delete-button'
                )

        # ==================================================
        # HERO
        # ==================================================

        with ui.card().classes('sleep-session-hero'):

            with ui.column().classes(
                'sleep-session-hero-main'
            ):

                with ui.row().classes(
                    'sleep-session-type-row'
                ):

                    ui.icon(
                        'bedtime',
                        size='30px',
                    )

                    ui.label(
                        value_or_dash(
                            record.get('Sleep_Type')
                        )
                    ).classes(
                        'sleep-session-type'
                    )

                ui.label(
                    f'{value_or_dash(record.get("Start_Time"))}'
                    f'  →  '
                    f'{value_or_dash(record.get("End_Time"))}'
                ).classes(
                    'sleep-session-time'
                )

                ui.label(
                    'Actual Sleep'
                ).classes(
                    'sleep-session-duration-label'
                )

                ui.label(
                    duration_text(actual_duration)
                ).classes(
                    'sleep-session-duration'
                )

            # ==================================================
            # QUALITY SCORE
            # ==================================================

            if record.get('Sleep_Quality') is not None:

                with ui.column().classes(
                    'sleep-session-quality'
                ):

                    ui.label(
                        'QUALITY'
                    ).classes(
                        'sleep-session-quality-label'
                    )

                    ui.label(
                        f'{record.get("Sleep_Quality")}/10'
                    ).classes(
                        'sleep-session-quality-score'
                    )

                    ui.label(
                        'Self-rated'
                    ).classes(
                        'sleep-session-quality-caption'
                    )

        # ==================================================
        # DURATION INSIGHT
        # ==================================================

        if period_minutes is not None:

            with ui.card().classes(
                'sleep-duration-insight'
            ):

                with ui.row().classes(
                    'sleep-duration-insight-header'
                ):

                    ui.icon(
                        'timelapse',
                        size='24px',
                    )

                    ui.label(
                        'Sleep Duration Analysis'
                    ).classes(
                        'sleep-details-section-title'
                    )

                with ui.row().classes(
                    'sleep-duration-comparison'
                ):

                    with ui.column().classes(
                        'sleep-duration-stat'
                    ):

                        ui.label(
                            'Sleep period'
                        ).classes(
                            'sleep-duration-stat-label'
                        )

                        ui.label(
                            duration_text(period_minutes)
                        ).classes(
                            'sleep-duration-stat-value'
                        )

                        ui.label(
                            'Start → wake-up'
                        ).classes(
                            'sleep-duration-stat-caption'
                        )

                    with ui.column().classes(
                        'sleep-duration-stat sleep-duration-actual'
                    ):

                        ui.label(
                            'Actual sleep'
                        ).classes(
                            'sleep-duration-stat-label'
                        )

                        ui.label(
                            duration_text(actual_duration)
                        ).classes(
                            'sleep-duration-stat-value'
                        )

                        ui.label(
                            'Recorded sleep time'
                        ).classes(
                            'sleep-duration-stat-caption'
                        )

                    if has_interruptions:

                        with ui.column().classes(
                            'sleep-duration-stat sleep-duration-lost'
                        ):

                            ui.label(
                                'Interrupted time'
                            ).classes(
                                'sleep-duration-stat-label'
                            )

                            ui.label(
                                duration_text(lost_minutes)
                            ).classes(
                                'sleep-duration-stat-value'
                            )

                            ui.label(
                                f'{int(awakenings)} awakening(s)'
                            ).classes(
                                'sleep-duration-stat-caption'
                            )

                if has_interruptions:

                    ui.label(
                        f'The sleep period lasted '
                        f'{duration_text(period_minutes)}, but the '
                        f'recorded actual sleep was '
                        f'{duration_text(actual_duration)} because '
                        f'{int(awakenings)} awakening(s) occurred.'
                    ).classes(
                        'sleep-duration-insight-text'
                    )

                else:

                    ui.label(
                        'No awakenings were recorded, so the actual '
                        'sleep duration matches the complete sleep period.'
                    ).classes(
                        'sleep-duration-insight-text'
                    )

        # ==================================================
        # SLEEP PATTERN
        # ==================================================

        with ui.card().classes(
            'sleep-details-card sleep-details-card-pattern'
        ):

            ui.label(
                'Sleep Pattern'
            ).classes(
                'sleep-details-section-title'
            )

            ui.label(
                'How the sleep session was structured.'
            ).classes(
                'sleep-details-section-subtitle'
            )

            with ui.row().classes(
                'sleep-details-grid'
            ):

                info_item(
                    'sync',
                    'Continuity',
                    record.get('Continuity'),
                )

                info_item(
                    'notifications',
                    'Awakenings',
                    record.get('Awakenings'),
                )

                info_item(
                    'schedule',
                    'Started',
                    record.get('Start_Time'),
                )

                info_item(
                    'schedule',
                    'Ended',
                    record.get('End_Time'),
                )

        # ==================================================
        # ENVIRONMENT
        # ==================================================

        with ui.card().classes(
            'sleep-details-card'
        ):

            ui.label(
                'Sleep Environment'
            ).classes(
                'sleep-details-section-title'
            )

            ui.label(
                'The physical conditions in which the sleep occurred.'
            ).classes(
                'sleep-details-section-subtitle'
            )

            with ui.row().classes(
                'sleep-details-grid'
            ):

                info_item(
                    'place',
                    'Location',
                    record.get('Location'),
                )

                info_item(
                    'airline_seat_recline_normal',
                    'Position',
                    record.get('Position'),
                )

                info_item(
                    'volume_up',
                    'Noise Level',
                    record.get('Noise_Level'),
                )

                info_item(
                    'light_mode',
                    'Light Level',
                    record.get('Light_Level'),
                )

                info_item(
                    'thermostat',
                    'Temperature',
                    record.get('Temperature_Level'),
                )

                info_item(
                    'weekend',
                    'Comfort Level',
                    (
                        f'{record.get("Comfort_Level")}/10'
                        if record.get('Comfort_Level') is not None
                        else None
                    ),
                )

        # ==================================================
        # RECOVERY & QUALITY
        # ==================================================

        with ui.card().classes(
            'sleep-details-card'
        ):

            ui.label(
                'Recovery & Quality'
            ).classes(
                'sleep-details-section-title'
            )

            ui.label(
                'Subjective indicators that may help the model '
                'understand recovery and sleep quality.'
            ).classes(
                'sleep-details-section-subtitle'
            )

            with ui.row().classes(
                'sleep-details-grid'
            ):

                info_item(
                    'star',
                    'Sleep Quality',
                    (
                        f'{record.get("Sleep_Quality")}/10'
                        if record.get('Sleep_Quality') is not None
                        else None
                    ),
                )

                info_item(
                    'psychology',
                    'Stress Before Sleep',
                    (
                        f'{record.get("Stress_Before_Sleep")}/10'
                        if record.get('Stress_Before_Sleep') is not None
                        else None
                    ),
                )

        # ==================================================
        # BEFORE SLEEP
        # ==================================================

        with ui.card().classes(
            'sleep-details-card'
        ):

            ui.label(
                'Before Sleep'
            ).classes(
                'sleep-details-section-title'
            )

            ui.label(
                'Factors recorded before going to sleep.'
            ).classes(
                'sleep-details-section-subtitle'
            )

            with ui.row().classes(
                'sleep-details-grid'
            ):

                info_item(
                    'coffee',
                    'Caffeine',
                    record.get('Caffeine_Before_Sleep'),
                )

                info_item(
                    'phone_android',
                    'Screen Use',
                    record.get('Screen_Before_Sleep'),
                )

                info_item(
                    'directions_run',
                    'Activity',
                    record.get('Before_Sleep_Activity'),
                )

        # ==================================================
        # DREAMS
        # ==================================================

        if record.get('Dreams'):

            with ui.card().classes(
                'sleep-details-card sleep-text-card'
            ):

                with ui.row().classes(
                    'sleep-text-card-title'
                ):

                    ui.icon(
                        'auto_awesome',
                        size='24px',
                    )

                    ui.label(
                        'Dreams'
                    ).classes(
                        'sleep-details-section-title'
                    )

                ui.label(
                    record.get('Dreams')
                ).classes(
                    'sleep-details-long-text'
                )

        # ==================================================
        # NOTES
        # ==================================================

        if record.get('Notes'):

            with ui.card().classes(
                'sleep-details-card sleep-text-card'
            ):

                with ui.row().classes(
                    'sleep-text-card-title'
                ):

                    ui.icon(
                        'notes',
                        size='24px',
                    )

                    ui.label(
                        'Notes'
                    ).classes(
                        'sleep-details-section-title'
                    )

                ui.label(
                    record.get('Notes')
                ).classes(
                    'sleep-details-long-text'
                )

        # ==================================================
        # FOOTER ACTIONS
        # ==================================================

        with ui.row().classes(
            'sleep-details-footer-actions'
        ):

            ui.button(
                'Back to Sleep Records',
                icon='arrow_back',
                on_click=lambda: ui.navigate.to('/sleep'),
            ).props(
                'flat'
            ).classes(
                'sleep-action-button'
            )

            ui.button(
                'Edit This Session',
                icon='edit',
                on_click=lambda:
                    ui.navigate.to(
                        f'/sleep/{sleep_id}/edit'
                    ),
            ).props(
                'unelevated'
            ).classes(
                'sleep-edit-button'
            )
