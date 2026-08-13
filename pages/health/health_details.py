
from pathlib import Path

from nicegui import ui

from components.layout import create_page_layout
from services.data.health import (
    get_health_record,
    delete_health_record,
)


@ui.page('/health/{health_id}')
def health_details_page(health_id: int):

    content = create_page_layout(
        title='Health',
        active_page='Health',
    )

    with content:

        # ==================================================
        # PAGE CSS
        # ==================================================

        css_file = Path('styles/health.css')

        if css_file.exists():
            css_version = css_file.stat().st_mtime_ns

            ui.add_head_html(
                f'<link rel="stylesheet" '
                f'href="/styles/health.css?v={css_version}">'
            )

        # ==================================================
        # LOAD RECORD
        # ==================================================

        record = get_health_record(health_id)

        if not record:

            with ui.column().classes('health-empty-state'):

                ui.icon(
                    'health_and_safety',
                    size='64px',
                )

                ui.label(
                    'Health Record Not Found'
                ).classes('health-empty-title')

                ui.label(
                    'The requested health record could not be found.'
                ).classes('health-empty-text')

                ui.button(
                    'Back to Health Records',
                    icon='arrow_back',
                    on_click=lambda: ui.navigate.to('/health'),
                ).props('unelevated')

            return

        # ==================================================
        # PAGE HEADER
        # ==================================================

        with ui.row().classes('health-details-header'):

            with ui.column().classes('health-heading'):

                ui.label(
                    'Health Record'
                ).classes('health-details-title')

                ui.label(
                    f"Record #{record['Health_ID']} • {record['Date']}"
                ).classes('health-details-subtitle')

            with ui.row().classes('health-header-actions'):

                ui.button(
                    'Back',
                    icon='arrow_back',
                    on_click=lambda: ui.navigate.to('/health'),
                ).props('flat')

                ui.button(
                    'Edit',
                    icon='edit',
                    on_click=lambda: ui.navigate.to(
                        f'/health/{health_id}/edit'
                    ),
                ).props('unelevated')

        # ==================================================
        # SUMMARY CARDS
        # ==================================================

        with ui.row().classes('health-summary-grid'):

            # --------------------------------------------------
            # Health Status
            # --------------------------------------------------

            with ui.card().classes(
                'health-summary-card health-status-card'
            ):

                with ui.row().classes('health-summary-top'):

                    ui.icon(
                        'favorite',
                        size='30px',
                    )

                    ui.label(
                        'Health Status'
                    ).classes('health-summary-label')

                ui.label(
                    record['Health_Status'] or 'Not specified'
                ).classes('health-summary-value')

            # --------------------------------------------------
            # Energy
            # --------------------------------------------------

            with ui.card().classes(
                'health-summary-card'
            ):

                with ui.row().classes('health-summary-top'):

                    ui.icon(
                        'bolt',
                        size='30px',
                    )

                    ui.label(
                        'Energy Level'
                    ).classes('health-summary-label')

                energy = record['Energy_Level']

                ui.label(
                    f'{energy} / 100'
                    if energy is not None
                    else 'Not specified'
                ).classes('health-summary-value')

            # --------------------------------------------------
            # Severity
            # --------------------------------------------------

            with ui.card().classes(
                'health-summary-card'
            ):

                with ui.row().classes('health-summary-top'):

                    ui.icon(
                        'warning',
                        size='30px',
                    )

                    ui.label(
                        'Severity'
                    ).classes('health-summary-label')

                severity = record['Severity']

                ui.label(
                    f'{severity} / 10'
                    if severity is not None
                    else 'Not specified'
                ).classes('health-summary-value')

        # ==================================================
        # HEALTH INFORMATION
        # ==================================================

        with ui.card().classes('health-information-card'):

            ui.label(
                'Health Information'
            ).classes('health-section-title')

            # --------------------------------------------------
            # Symptoms
            # --------------------------------------------------

            with ui.column().classes('health-info-section'):

                with ui.row().classes('health-info-heading'):

                    ui.icon('sick')

                    ui.label(
                        'Symptoms'
                    )

                ui.label(
                    record['Symptoms'] or 'No symptoms recorded.'
                ).classes('health-info-value')

            # --------------------------------------------------
            # Treatment
            # --------------------------------------------------

            with ui.column().classes('health-info-section'):

                with ui.row().classes('health-info-heading'):

                    ui.icon('medication')

                    ui.label(
                        'Treatment'
                    )

                ui.label(
                    record['Treatment'] or 'No treatment recorded.'
                ).classes('health-info-value')

            # --------------------------------------------------
            # Notes
            # --------------------------------------------------

            with ui.column().classes('health-info-section'):

                with ui.row().classes('health-info-heading'):

                    ui.icon('notes')

                    ui.label(
                        'Notes'
                    )

                ui.label(
                    record['Notes'] or 'No additional notes.'
                ).classes('health-info-value')

        # ==================================================
        # RECORD METADATA
        # ==================================================

        with ui.card().classes('health-metadata-card'):

            ui.label(
                'Record Information'
            ).classes('health-section-title')

            with ui.row().classes('health-metadata-grid'):

                with ui.column():

                    ui.label(
                        'Record ID'
                    ).classes('health-metadata-label')

                    ui.label(
                        str(record['Health_ID'])
                    ).classes('health-metadata-value')

                with ui.column():

                    ui.label(
                        'Date'
                    ).classes('health-metadata-label')

                    ui.label(
                        str(record['Date'])
                    ).classes('health-metadata-value')

        # ==================================================
        # DANGER ZONE
        # ==================================================

        with ui.card().classes('health-danger-card'):

            with ui.row().classes('health-danger-content'):

                with ui.column().classes('health-danger-info'):

                    ui.label(
                        'Danger Zone'
                    ).classes('health-danger-title')

                    ui.label(
                        'Deleting this record is permanent and '
                        'cannot be undone.'
                    ).classes('health-danger-text')

                def confirm_delete():

                    with ui.dialog() as dialog:

                        with ui.card().classes(
                            'health-delete-dialog'
                        ):

                            ui.icon(
                                'warning',
                                size='48px',
                            ).classes('health-delete-icon')

                            ui.label(
                                'Delete Health Record?'
                            ).classes(
                                'health-delete-title'
                            )

                            ui.label(
                                'Are you sure you want to permanently '
                                'delete this health record?'
                            ).classes(
                                'health-delete-text'
                            )

                            with ui.row().classes(
                                'health-delete-actions'
                            ):

                                ui.button(
                                    'Cancel',
                                    on_click=dialog.close,
                                ).props('flat')

                                def perform_delete():

                                    delete_health_record(
                                        health_id
                                    )

                                    dialog.close()

                                    ui.notify(
                                        'Health record deleted successfully.',
                                        type='positive',
                                    )

                                    ui.navigate.to('/health')

                                ui.button(
                                    'Delete',
                                    icon='delete',
                                    on_click=perform_delete,
                                ).props(
                                    'unelevated color=negative'
                                )

                    dialog.open()

                ui.button(
                    'Delete Record',
                    icon='delete',
                    on_click=confirm_delete,
                ).props(
                    'unelevated color=negative'
                )
