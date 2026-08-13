
from pathlib import Path

from nicegui import ui

from components.layout import create_page_layout
from services.data.health import add_health_record


@ui.page('/health/add')
def add_health_page():

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
        # PAGE HEADER
        # --------------------------------------------------

        with ui.column().classes('page-header'):

            ui.label(
                'Add Health Record'
            ).classes('page-title')

            ui.label(
                'Record your health information for this day.'
            ).classes('page-subtitle')

        # --------------------------------------------------
        # FORM CARD
        # --------------------------------------------------

        with ui.card().classes('page-card health-form-card'):

            with ui.column().classes('w-full gap-5'):

                # --------------------------------------------------
                # DATE
                # --------------------------------------------------

                date = ui.date().props(
                    'outlined'
                ).classes('w-full')

                date.props('label="Date"')

                # --------------------------------------------------
                # HEALTH STATUS
                # --------------------------------------------------

                health_status = ui.input(
                    label='Health Status',
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
                ).props(
                    'outlined'
                ).classes('w-full')

                # --------------------------------------------------
                # SYMPTOMS
                # --------------------------------------------------

                symptoms = ui.input(
                    label='Symptoms',
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
                ).props(
                    'outlined'
                ).classes('w-full')

                # --------------------------------------------------
                # TREATMENT
                # --------------------------------------------------

                treatment = ui.input(
                    label='Treatment',
                ).props(
                    'outlined'
                ).classes('w-full')

                # --------------------------------------------------
                # NOTES
                # --------------------------------------------------

                notes = ui.textarea(
                    label='Notes',
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
                        on_click=lambda: ui.navigate.to('/health'),
                    ).props(
                        'flat'
                    )

                    def save_record():

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
                        # SAVE
                        # ------------------------------------------

                        add_health_record(
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
                            'Health record added successfully',
                            type='positive',
                        )

                        ui.navigate.to('/health')

                    ui.button(
                        'Save Health Record',
                        icon='save',
                        on_click=save_record,
                    ).props(
                        'unelevated'
                    )
