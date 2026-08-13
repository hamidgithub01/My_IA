
from pathlib import Path

from nicegui import ui

from components.layout import create_page_layout
from services.data.health import (
    get_health_records,
    delete_health_record,
)


@ui.page('/health')
def health_records_page():

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
        # HEADER
        # --------------------------------------------------

        with ui.row().classes('health-page-header'):

            with ui.column().classes('health-page-heading'):

                ui.label(
                    'Health Records'
                ).classes('health-page-title')

                ui.label(
                    'Track and manage your health history.'
                ).classes('health-page-subtitle')

            ui.button(
                'Add Health Record',
                icon='add',
                on_click=lambda: ui.navigate.to(
                    '/health/add'
                ),
            ).props(
                'unelevated'
            ).classes('health-add-button')

        # --------------------------------------------------
        # LOAD RECORDS
        # --------------------------------------------------

        records = get_health_records()

        # --------------------------------------------------
        # EMPTY STATE
        # --------------------------------------------------

        if not records:

            with ui.card().classes('health-empty-card'):

                ui.icon(
                    'favorite_border',
                    size='48px',
                )

                ui.label(
                    'No health records found.'
                ).classes('health-empty-title')

                ui.label(
                    'Start tracking your health by adding your first record.'
                ).classes('health-empty-text')

                ui.button(
                    'Add Health Record',
                    icon='add',
                    on_click=lambda: ui.navigate.to(
                        '/health/add'
                    ),
                ).props('unelevated')

            return

        # --------------------------------------------------
        # TABLE
        # --------------------------------------------------

        columns = [
            {
                'name': 'Date',
                'label': 'Date',
                'field': 'Date',
                'sortable': True,
            },
            {
                'name': 'Health_Status',
                'label': 'Health Status',
                'field': 'Health_Status',
                'sortable': True,
            },
            {
                'name': 'Energy_Level',
                'label': 'Energy',
                'field': 'Energy_Level',
                'sortable': True,
            },
            {
                'name': 'Symptoms',
                'label': 'Symptoms',
                'field': 'Symptoms',
            },
            {
                'name': 'Severity',
                'label': 'Severity',
                'field': 'Severity',
                'sortable': True,
            },
            {
                'name': 'Treatment',
                'label': 'Treatment',
                'field': 'Treatment',
            },
            {
                'name': 'Actions',
                'label': 'Actions',
                'field': 'Actions',
                'align': 'right',
            },
        ]

        rows = [
            {
                'Health_ID': record['Health_ID'],
                'Date': record['Date'],
                'Health_Status': record['Health_Status'],
                'Energy_Level': record['Energy_Level'],
                'Symptoms': record['Symptoms'],
                'Severity': record['Severity'],
                'Treatment': record['Treatment'],
                'Actions': '',
            }
            for record in records
        ]

        # --------------------------------------------------
        # DELETE CONFIRMATION
        # --------------------------------------------------

        def confirm_delete(health_id):

            with ui.dialog() as dialog, ui.card().classes(
                'health-delete-dialog'
            ):

                ui.label(
                    'Delete Health Record?'
                ).classes(
                    'text-xl font-semibold'
                )

                ui.label(
                    'This action cannot be undone.'
                ).classes(
                    'text-gray-500'
                )

                with ui.row().classes(
                    'justify-end gap-2 mt-4 w-full'
                ):

                    ui.button(
                        'Cancel',
                        on_click=dialog.close,
                    ).props('flat')

                    def delete_record():

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
                        on_click=delete_record,
                    ).props(
                        'unelevated color=negative'
                    )

            dialog.open()

        # --------------------------------------------------
        # TABLE
        # --------------------------------------------------

        table = ui.table(
            columns=columns,
            rows=rows,
            row_key='Health_ID',
        ).classes(
            'w-full health-records-table'
        )

        # --------------------------------------------------
        # ACTIONS SLOT
        # --------------------------------------------------

        table.add_slot(
            'body-cell-Actions',
            r'''
            <q-td :props="props">
                <div class="row items-center justify-end q-gutter-xs">

                    <q-btn
                        flat
                        round
                        dense
                        icon="visibility"
                        color="primary"
                        @click="$parent.$emit('view', props.row.Health_ID)"
                    >
                        <q-tooltip>
                            View
                        </q-tooltip>
                    </q-btn>

                    <q-btn
                        flat
                        round
                        dense
                        icon="edit"
                        color="secondary"
                        @click="$parent.$emit('edit', props.row.Health_ID)"
                    >
                        <q-tooltip>
                            Edit
                        </q-tooltip>
                    </q-btn>

                    <q-btn
                        flat
                        round
                        dense
                        icon="delete"
                        color="negative"
                        @click="$parent.$emit('delete', props.row.Health_ID)"
                    >
                        <q-tooltip>
                            Delete
                        </q-tooltip>
                    </q-btn>

                </div>
            </q-td>
            '''
        )

        # --------------------------------------------------
        # ACTION HANDLERS
        # --------------------------------------------------

        table.on(
            'view',
            lambda event: ui.navigate.to(
                f"/health/{event.args}"
            ),
        )

        table.on(
            'edit',
            lambda event: ui.navigate.to(
                f"/health/{event.args}/edit"
            ),
        )

        table.on(
            'delete',
            lambda event: confirm_delete(
                event.args
            ),
        )
