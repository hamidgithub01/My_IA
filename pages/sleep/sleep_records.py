from pathlib import Path

from nicegui import ui

from components.layout import create_page_layout
from services.data.sleep import get_sleep_records, delete_sleep_record


@ui.page('/sleep')
def sleep_records_page():

    content = create_page_layout(
        title='Sleep',
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

        records = get_sleep_records()

        # ==================================================
        # PAGE HEADER
        # ==================================================

        with ui.row().classes('sleep-page-header'):

            with ui.column().classes('sleep-header-text'):

                ui.label(
                    'Sleep Records'
                ).classes('sleep-page-title')

                ui.label(
                    'Track sleep sessions, conditions, and recovery quality.'
                ).classes('sleep-page-subtitle')

            ui.button(
                'Add Sleep',
                icon='add',
                on_click=lambda: ui.navigate.to('/sleep/add'),
            ).props('unelevated').classes('sleep-add-button')

        # ==================================================
        # EMPTY STATE
        # ==================================================

        if not records:

            with ui.card().classes('sleep-empty-card'):

                ui.icon(
                    'bedtime',
                    size='64px',
                ).classes('sleep-empty-icon')

                ui.label(
                    'No sleep records yet'
                ).classes('sleep-empty-title')

                ui.label(
                    'Start recording your sleep conditions to build '
                    'a meaningful picture of your sleep patterns.'
                ).classes('sleep-empty-text')

                ui.button(
                    'Record First Sleep',
                    icon='add',
                    on_click=lambda: ui.navigate.to('/sleep/add'),
                ).props('unelevated').classes('sleep-empty-button')

            return

        # ==================================================
        # RECORDS
        # ==================================================

        with ui.column().classes('sleep-records-list'):

            for record in records:

                sleep_id = record['Sleep_ID']

                date = record.get('Date')
                start_time = record.get('Start_Time')
                end_time = record.get('End_Time')

                duration = record.get('Duration_Minutes')
                sleep_type = record.get('Sleep_Type')
                continuity = record.get('Continuity')
                location = record.get('Location')
                position = record.get('Position')
                awakenings = record.get('Awakenings')
                quality = record.get('Sleep_Quality')

                # --------------------------------------------------
                # CARD
                # --------------------------------------------------

                with ui.card().classes('sleep-record-card'):

                    # --------------------------------------------------
                    # TOP
                    # --------------------------------------------------

                    with ui.row().classes('sleep-record-top'):

                        with ui.column().classes('sleep-record-date'):

                            ui.label(
                                str(date)
                            ).classes('sleep-record-date-value')

                            ui.label(
                                str(sleep_type or 'Sleep')
                            ).classes('sleep-record-type')

                        if quality is not None:

                            ui.label(
                                f'Quality {quality}/10'
                            ).classes('sleep-quality-badge')

                    # --------------------------------------------------
                    # MAIN SLEEP INFORMATION
                    # --------------------------------------------------

                    with ui.row().classes('sleep-main-info'):

                        with ui.column().classes('sleep-time-block'):

                            ui.icon(
                                'schedule',
                                size='28px',
                            )

                            with ui.column().classes('sleep-time-values'):

                                ui.label(
                                    f'{start_time} → {end_time}'
                                ).classes('sleep-time')

                                if duration is not None:

                                    hours = int(duration) // 60
                                    minutes = int(duration) % 60

                                    if hours:

                                        duration_text = (
                                            f'{hours}h'
                                            + (
                                                f' {minutes}m'
                                                if minutes
                                                else ''
                                            )
                                        )

                                    else:

                                        duration_text = f'{minutes}m'

                                    ui.label(
                                        duration_text
                                    ).classes('sleep-duration')

                        with ui.column().classes('sleep-condition-block'):

                            if continuity:

                                with ui.row().classes(
                                    'sleep-condition'
                                ):

                                    ui.icon('sync')

                                    ui.label(
                                        str(continuity)
                                    )

                            if location:

                                with ui.row().classes(
                                    'sleep-condition'
                                ):

                                    ui.icon('place')

                                    ui.label(
                                        str(location)
                                    )

                            if position:

                                with ui.row().classes(
                                    'sleep-condition'
                                ):

                                    ui.icon('airline_seat_recline_normal')

                                    ui.label(
                                        str(position)
                                    )

                            if awakenings is not None:

                                with ui.row().classes(
                                    'sleep-condition'
                                ):

                                    ui.icon('notifications')

                                    ui.label(
                                        f'{awakenings} awakenings'
                                    )

                    # --------------------------------------------------
                    # ACTIONS
                    # --------------------------------------------------

                    with ui.row().classes('sleep-record-actions'):

                        ui.button(
                            'Details',
                            icon='visibility',
                            on_click=lambda sleep_id=sleep_id:
                                ui.navigate.to(
                                    f'/sleep/{sleep_id}'
                                ),
                        ).props('flat').classes('sleep-action-button')

                        ui.button(
                            'Edit',
                            icon='edit',
                            on_click=lambda sleep_id=sleep_id:
                                ui.navigate.to(
                                    f'/sleep/{sleep_id}/edit'
                                ),
                        ).props('flat').classes('sleep-action-button')

                        def confirm_delete(
                            sleep_id=sleep_id,
                            record_date=date,
                        ):
                            with ui.dialog() as dialog, ui.card().classes(
                                'sleep-delete-dialog'
                            ):

                                ui.icon(
                                    'warning',
                                    size='48px',
                                ).classes('sleep-delete-warning-icon')

                                ui.label(
                                    'Delete Sleep Record?'
                                ).classes('sleep-delete-dialog-title')

                                ui.label(
                                    f'Are you sure you want to delete the sleep record '
                                    f'from {record_date}?'
                                ).classes('sleep-delete-dialog-text')

                                ui.label(
                                    'This action cannot be undone.'
                                ).classes('sleep-delete-dialog-warning')

                                with ui.row().classes('sleep-delete-dialog-actions'):

                                    ui.button(
                                        'Cancel',
                                        icon='close',
                                        on_click=dialog.close,
                                    ).props(
                                        'flat'
                                    ).classes('sleep-cancel-button')

                                    def execute_delete():

                                        delete_sleep_record(sleep_id)

                                        dialog.close()

                                        ui.notify(
                                            'Sleep record deleted successfully.',
                                            type='positive',
                                        )

                                        ui.navigate.to('/sleep')

                                    ui.button(
                                        'Delete Permanently',
                                        icon='delete_forever',
                                        on_click=execute_delete,
                                    ).props(
                                        'unelevated'
                                    ).classes('sleep-confirm-delete-button')

                            dialog.open()

                        ui.button(
                            'Delete',
                            icon='delete',
                            on_click=confirm_delete,
                        ).props('flat').classes(
                            'sleep-action-button sleep-delete-button'
                        )