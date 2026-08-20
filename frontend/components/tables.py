from nicegui import ui


def data_table(
    *,
    columns,
    rows,
    row_key='id',
    title=None,
    subtitle=None,
    pagination=None,
    dense=False,
):
    with ui.card().classes(
        'app-card w-full '
        'p-0 '
        'rounded-2xl '
        'border border-gray-200 '
        'shadow-sm '
        'bg-white '
        'overflow-hidden'
    ):
        if title or subtitle:
            with ui.column().classes(
                'w-full gap-0 p-5'
            ):
                if title:
                    ui.label(title).classes(
                        'text-base font-semibold '
                        'text-primary-app'
                    )

                if subtitle:
                    ui.label(subtitle).classes(
                        'text-sm text-secondary-app mt-0.5'
                    )

        table = ui.table(
            columns=columns,
            rows=rows,
            row_key=row_key,
            pagination=pagination,
        ).classes(
            'w-full'
        )

        if dense:
            table.props('dense')

        table.add_slot(
            'no-data',
            '''
            <div class="w-full flex flex-col items-center
                        justify-center py-12 gap-2">
                <q-icon
                    name="table_rows"
                    size="32px"
                    class="text-gray-300"
                />
                <div
                    class="text-sm font-medium text-gray-500"
                >
                    No data available
                </div>
                <div
                    class="text-xs text-gray-400"
                >
                    Data will appear here when available.
                </div>
            </div>
            ''',
        )

        return table


def simple_table(
    *,
    headers,
    rows,
):
    with ui.element('div').classes(
        'w-full overflow-x-auto'
    ):
        with ui.element('table').classes(
            'app-table min-w-full'
        ):
            with ui.element('thead'):
                with ui.element('tr'):
                    for header in headers:
                        ui.label(header).classes(
                            'font-semibold'
                        ).style(
                            'display: table-cell;'
                        )

            with ui.element('tbody'):
                for row in rows:
                    with ui.element('tr'):
                        for value in row:
                            ui.label(
                                str(value)
                            ).classes(
                                'text-sm text-primary-app'
                            ).style(
                                'display: table-cell;'
                            )


def table_toolbar(
    *,
    title=None,
    subtitle=None,
    search_placeholder='Search...',
):
    with ui.row().classes(
        'w-full items-center '
        'justify-between '
        'gap-4 flex-wrap'
    ):
        if title or subtitle:
            with ui.column().classes(
                'gap-0'
            ):
                if title:
                    ui.label(title).classes(
                        'text-lg font-semibold '
                        'text-primary-app'
                    )

                if subtitle:
                    ui.label(subtitle).classes(
                        'text-sm text-secondary-app'
                    )

        search = ui.input(
            placeholder=search_placeholder,
        ).props(
            'outlined dense clearable'
        ).classes(
            'w-full sm:w-64'
        )

        return search