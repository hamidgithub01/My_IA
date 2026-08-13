
from pathlib import Path

from nicegui import ui

from components.layout import create_page_layout
from services.data.health import (
    get_health_record,
    update_health_record,
)


@ui.page('/health/{health_id}/edit')
def edit_health_page(health_id: int):

    # ==================================================
    # SHARED APPLICATION LAYOUT
    # ==================================================

    content = create_page_layout(
        title='Health',
        active_page='Health',
    )

    # ==================================================
    # PAGE CONTENT
    # ==================================================

    with content:

        # --------------------------------------------------
        # PAGE CSS
        # --------------------------------------------------

        css_file = Path('styles/health.css')

        if css_file.exists():
            css_version = css_file.stat().st_mtime_ns

            ui.add_head_html(
                f'<link rel="stylesheet" '
                f'href="/styles/health.css?v={css_version}">'
            )

        # --------------------------------------------------
        # LOAD RECORD
        # --------------------------------------------------

        record = get_health_record(health_id)

        if not record:

            with ui.column().classes('page-header'):

                ui.label(
                    'Health Record Not Found'
                ).classes('page-title')

                ui.label(
                    'The requested health record does not exist.'
                ).classes('page-subtitle')

            ui.button(
                'Back to Health Records',
                icon='arrow_back',
                on_click=lambda: ui.navigate.to('/health'),
            ).props('flat')

            return

        # --------------------------------------------------
        # PAGE HEADER
        # --------------------------------------------------

        with ui.column().classes('page-header'):

            ui.label(
                'Edit Health Record'
            ).classes('page-title')

            ui.label(
                f"Record #{record['Health_ID']}"
            ).classes('page-subtitle')

        # --------------------------------------------------
        # FORM CARD
        # --------------------------------------------------

        with ui.card().classes(
            'page-card health-form-card'
        ):

            with ui.column().classes('w-full gap-5'):

                # --------------------------------------------------
                # DATE
                # --------------------------------------------------

                date = ui.date(
                    value=str(record['Date'])
                    if record['Date'] is not None
                    else None
                ).props(
                    'outlined'
                ).classes('w-full')

                date.props('label="Date"')

                # --------------------------------------------------
                # HEALTH STATUS
                # --------------------------------------------------

                health_status = ui.input(
                    label='Health Status',
                    value=record['Health_Status'] or '',
                ).props(
                    'outlined'
                ).classes('w-full')

                # --------------------------------------------------
                # ENERGY LEVEL
                # --------------------------------------------------

                energy_level = ui.number(
                    label='Energy Level',
                    min=0,
                    max=100,
                    step=1,
                    value=record['Energy_Level'],
                ).props(
                    'outlined'
                ).classes('w-full')

                # --------------------------------------------------
                # SYMPTOMS
                # --------------------------------------------------

                symptoms = ui.input(
                    label='Symptoms',
                    value=record['Symptoms'] or '',
                ).props(
                    'outlined'
                ).classes('w-full')

                # --------------------------------------------------
                # SEVERITY
                # --------------------------------------------------

                severity = ui.number(
                    label='Severity',
                    min=0,
                    max=10,
                    step=1,
                    value=record['Severity'],
                ).props(
                    'outlined'
                ).classes('w-full')

                # --------------------------------------------------
                # TREATMENT
                # --------------------------------------------------

                treatment = ui.input(
                    label='Treatment',
                    value=record['Treatment'] or '',
                ).props(
                    'outlined'
                ).classes('w-full')

                # --------------------------------------------------
                # NOTES
                # --------------------------------------------------

                notes = ui.textarea(
                    label='Notes',
                    value=record['Notes'] or '',
                ).props(
                    'outlined'
                ).classes('w-full')

                # --------------------------------------------------
                # ACTIONS
                # --------------------------------------------------

                with ui.row().classes(
                    'w-full justify-end gap-3 pt-2'
                ):

                    ui.button(
                        'Cancel',
                        icon='close',
                        on_click=lambda: ui.navigate.to(
                            f"/health/{record['Health_ID']}"
                        ),
                    ).props('flat')

                    def save_changes():

                        # ------------------------------------------
                        # VALIDATION
                        # ------------------------------------------

                        if not date.value:
                            ui.notify(
                                'Date is required',
                                type='negative',
                            )
                            return

                        if not health_status.value:
                            ui.notify(
                                'Health Status is required',
                                type='negative',
                            )
                            return

                        # ------------------------------------------
                        # UPDATE
                        # ------------------------------------------

                        update_health_record(
                            health_id=record['Health_ID'],
                            date=date.value,
                            health_status=health_status.value,
                            energy_level=energy_level.value,
                            symptoms=symptoms.value,
                            severity=severity.value,
                            treatment=treatment.value,
                            notes=notes.value,
                        )

                        # ------------------------------------------
                        # SUCCESS
                        # ------------------------------------------

                        ui.notify(
                            'Health record updated successfully',
                            type='positive',
                        )

                        ui.navigate.to(
                            f"/health/{record['Health_ID']}"
                        )

                    ui.button(
                        'Save Changes',
                        icon='save',
                        on_click=save_changes,
                    ).props('unelevated')
