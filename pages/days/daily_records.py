from pathlib import Path

from nicegui import ui

from components.header import create_header
from services.data.days import get_days, delete_day

@ui.page('/days')
def daily_records_page():

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

    days = get_days()

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
                    'Days'
                ).classes('days-title')

                ui.label(
                    'Manage and review your daily records.'
                ).classes('days-subtitle')

            ui.button(
                'Add Day',
                icon='add',
                on_click=lambda: ui.navigate.to(
                    '/days/add'
                )
            ).classes('add-day-button')

        # --------------------------------------------------
        # Daily Records Table
        # --------------------------------------------------

        with ui.card().classes('days-table-card'):

            ui.label(
                'Daily Records'
            ).classes('days-section-title')

            if not days:

                with ui.column().classes('days-empty'):

                    ui.icon(
                        'calendar_month',
                        size='48px'
                    )

                    ui.label(
                        'No daily records found.'
                    ).classes('days-empty-title')

                    ui.label(
                        'Add your first daily record to get started.'
                    ).classes('days-empty-text')

                    ui.button(
                        'Add Day',
                        icon='add',
                        on_click=lambda: ui.navigate.to(
                            '/days/add'
                        )
                    )

            else:

                columns = [
                    {
                        'name': 'date',
                        'label': 'Date',
                        'field': 'date',
                        'align': 'left',
                    },
                    {
                        'name': 'day_type',
                        'label': 'Day Type',
                        'field': 'day_type',
                        'align': 'left',
                    },
                    {
                        'name': 'work_status',
                        'label': 'Work Status',
                        'field': 'work_status',
                        'align': 'left',
                    },
                    {
                        'name': 'health_impact',
                        'label': 'Health Impact',
                        'field': 'health_impact',
                        'align': 'left',
                    },
                    {
                        'name': 'travel',
                        'label': 'Travel',
                        'field': 'travel',
                        'align': 'left',
                    },
                    {
                        'name': 'special_event',
                        'label': 'Special Event',
                        'field': 'special_event',
                        'align': 'left',
                    },
                    {
                        'name': 'stress_level',
                        'label': 'Stress Level',
                        'field': 'stress_level',
                        'align': 'left',
                    },
                    {
                        'name': 'sleep_hours',
                        'label': 'Sleep Hours',
                        'field': 'sleep_hours',
                        'align': 'right',
                    },
                    {
                        'name': 'social_activity',
                        'label': 'Social Activity',
                        'field': 'social_activity',
                        'align': 'left',
                    },
                    {
                        'name': 'location',
                        'label': 'Location',
                        'field': 'location',
                        'align': 'left',
                    },
                    {
                        'name': 'actions',
                        'label': 'Actions',
                        'field': 'actions',
                        'align': 'right',
                    },
                ]

                rows = []

                for day in days:

                    rows.append({
                        'date': str(day['Date']),
                        'day_type': day['Day_Type'] or '',
                        'work_status': day['Work_Status'] or '',
                        'health_impact': day['Health_Impact'] or '',
                        'travel': day['Travel'] or '',
                        'special_event': day['Special_Event'] or '',
                        'stress_level': day['Stress_Level'] or '',
                        'sleep_hours': (
                            str(day['Sleep_Hours'])
                            if day['Sleep_Hours'] is not None
                            else ''
                        ),
                        'social_activity': (
                            day['Social_Activity'] or ''
                        ),
                        'location': day['Location'] or '',
                    })

                table = ui.table(
                    columns=columns,
                    rows=rows,
                    row_key='date',
                ).classes('days-table')

                table.add_slot(
                    'body-cell-actions',
                    r'''
                    <q-td :props="props">
                        <div class="day-actions">

                            <q-btn
                                flat
                                round
                                dense
                                icon="visibility"
                                color="primary"
                                @click="$parent.$emit(
                                    'view-day',
                                    props.row
                                )"
                            />

                            <q-btn
                                flat
                                round
                                dense
                                icon="edit"
                                color="primary"
                                @click="$parent.$emit(
                                    'edit-day',
                                    props.row
                                )"
                            />

                            <q-btn
                                flat
                                round
                                dense
                                icon="delete"
                                color="negative"
                                @click="$parent.$emit(
                                    'delete-day',
                                    props.row
                                )"
                            />

                        </div>
                    </q-td>
                    '''
                )

                table.on(
                    'view-day',
                    lambda event: ui.navigate.to(
                        f"/days/{event.args['date']}"
                    )
                )

                table.on(
                    'edit-day',
                    lambda event: ui.navigate.to(
                        f"/days/{event.args['date']}/edit"
                    )
                )

                def delete_day_record(event):

                    day_date = event.args['date']

                    with ui.dialog() as dialog:

                        with ui.card().classes(
                            'delete-dialog'
                        ):

                            ui.label(
                                'Delete Daily Record'
                            ).classes(
                                'delete-dialog-title'
                            )

                            ui.label(
                                'Are you sure you want to '
                                'delete this daily record?'
                            ).classes(
                                'delete-dialog-text'
                            )

                            with ui.row().classes(
                                'delete-dialog-actions'
                            ):

                                ui.button(
                                    'Cancel',
                                    on_click=dialog.close
                                ).props('flat')

                                def confirm_delete():

                                    delete_day(
                                        day_date
                                    )

                                    dialog.close()

                                    ui.navigate.to(
                                        '/days'
                                    )

                                ui.button(
                                    'Delete',
                                    icon='delete',
                                    on_click=confirm_delete
                                ).props(
                                    'color=negative'
                                )

                    dialog.open()

                table.on(
                    'delete-day',
                    delete_day_record
                )