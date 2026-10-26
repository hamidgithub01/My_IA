from nicegui import ui

from ml.models.registry import (
    get_active_model_version,
    load_model_metadata,
)


# ==========================================================
# PAGE
# ==========================================================

def features_page():
    state = {
        'features': [],
        'search': '',
        'category_filter': 'All',
        'table': None,
        'total_label': None,
        'category_count_label': None,
        'target_label': None,
        'algorithm_label': None,
        'version_label': None,
        'status_label': None,
        'category_select': None,
        'error': None,
        'metadata': {},
    }

    # ======================================================
    # FEATURE CLASSIFICATION
    # ======================================================

    def classify_feature(name):
        if (
            name.startswith('Day_of_')
            or name in {
                'Month',
                'Quarter',
                'Is_Weekend',
                'Is_Month_Start',
                'Is_Month_End',
                'Week_of_Month',
            }
            or name.startswith('Days_From_')
            or name.startswith('Days_To_')
        ):
            return 'Temporal'

        if name.startswith(
            ('Known_Plan_', 'Known_Recurring_')
        ):
            return 'Known Future'

        if name.startswith('Previous_Day_'):
            return 'Previous Day'

        if name.startswith('Same_Weekday_'):
            return 'Historical'

        if name.startswith('Lag_'):
            return 'Lag'

        if name.startswith('Rolling_'):
            return 'Rolling'

        return 'Other'

    def build_feature_rows():
        rows = []

        for index, name in enumerate(
            state['features'],
            start=1,
        ):
            rows.append({
                'position': index,
                'name': name,
                'category': classify_feature(name),
            })

        return rows

    # ======================================================
    # DATA
    # ======================================================

    def load_feature_metadata():
        try:
            target_name = 'Target_Expense_Total_1D'

            version = get_active_model_version(
                target_name
            )

            if not version:
                raise ValueError(
                    'No active model version is registered.'
                )

            result = load_model_metadata(
                target_name,
                version,
            )

            if not isinstance(result, dict):
                raise ValueError(
                    'The metadata loader returned an invalid result.'
                )

            if result.get('status') != 'valid':
                raise ValueError(
                    'The active model metadata is not valid.'
                )

            metadata = result.get('metadata')

            if not isinstance(metadata, dict):
                raise ValueError(
                    'The model metadata is missing or invalid.'
                )

            feature_names = metadata.get('feature_names')

            if (
                not isinstance(feature_names, list)
                or not feature_names
                or not all(
                    isinstance(name, str) and name.strip()
                    for name in feature_names
                )
            ):
                raise ValueError(
                    'No valid feature names were found in the metadata.'
                )

            state['metadata'] = metadata
            state['features'] = feature_names
            state['error'] = None

        except Exception as exc:
            state['metadata'] = {}
            state['features'] = []
            state['error'] = str(exc)

        refresh_view()

    # ======================================================
    # FILTERS
    # ======================================================

    def filtered_features():
        search = state['search'].strip().lower()
        category_filter = state['category_filter']

        result = []

        for row in build_feature_rows():
            if (
                category_filter != 'All'
                and row['category'] != category_filter
            ):
                continue

            if search and search not in (
                f"{row['name']} {row['category']} "
                f"{row['position']}"
            ).lower():
                continue

            result.append(row)

        return result

    def refresh_view():
        filtered = filtered_features()

        if state['table'] is not None:
            state['table'].rows = filtered
            state['table'].update()

        if state['total_label'] is not None:
            state['total_label'].text = str(
                len(state['features'])
            )

        if state['category_count_label'] is not None:
            state['category_count_label'].text = str(
                len({
                    row['category']
                    for row in build_feature_rows()
                })
            )

        metadata = state['metadata']

        if state['target_label'] is not None:
            state['target_label'].text = str(
                metadata.get('target_name', '—')
            )

        if state['algorithm_label'] is not None:
            state['algorithm_label'].text = str(
                metadata.get('algorithm', '—')
            )

        if state['version_label'] is not None:
            state['version_label'].text = str(
                metadata.get('version', '—')
            )

        if state['status_label'] is not None:
            if state['error']:
                state['status_label'].text = (
                    'Metadata unavailable'
                )
                state['status_label'].classes(
                    add='text-red-600',
                    remove='text-green-700',
                )
            else:
                state['status_label'].text = 'Valid'
                state['status_label'].classes(
                    add='text-green-700',
                    remove='text-red-600',
                )

        if state['error'] and state['error_label'] is not None:
            state['error_label'].text = state['error']

    def set_search(value):
        state['search'] = value or ''
        refresh_view()

    def set_category_filter(value):
        state['category_filter'] = value or 'All'
        refresh_view()

    def clear_filters():
        state['search'] = ''
        state['category_filter'] = 'All'

        search_input.value = ''
        search_input.update()

        if state['category_select'] is not None:
            state['category_select'].value = 'All'
            state['category_select'].update()

        refresh_view()

    # ======================================================
    # PAGE HEADER
    # ======================================================

    with ui.column().classes(
        'w-full '
        'max-w-[1600px] '
        'mx-auto '
        'gap-6'
    ):

        with ui.row().classes(
            'w-full '
            'items-start '
            'justify-between '
            'gap-4 '
            'flex-wrap'
        ):

            with ui.column().classes('gap-1'):

                ui.label('Features').classes(
                    'text-2xl '
                    'font-bold '
                    'text-gray-900'
                )

                ui.label(
                    'Inspect the input features registered for the active ML model.'
                ).classes(
                    'text-sm '
                    'text-gray-500'
                )

        # ==================================================
        # SUMMARY
        # ==================================================

        with ui.row().classes(
            'w-full '
            'gap-4 '
            'flex-wrap'
        ):

            with ui.card().classes(
                'flex-1 min-w-[220px] p-4 '
                'rounded-[var(--radius-md)] '
                'shadow-none border border-gray-200'
            ):

                ui.label('Registered Features').classes(
                    'text-xs font-medium text-gray-500'
                )

                state['total_label'] = ui.label('0').classes(
                    'text-2xl font-bold text-gray-900 mt-1'
                )

            with ui.card().classes(
                'flex-1 min-w-[220px] p-4 '
                'rounded-[var(--radius-md)] '
                'shadow-none border border-gray-200'
            ):

                ui.label('Feature Groups').classes(
                    'text-xs font-medium text-gray-500'
                )

                state['category_count_label'] = ui.label(
                    '0'
                ).classes(
                    'text-2xl font-bold text-gray-900 mt-1'
                )

            with ui.card().classes(
                'flex-1 min-w-[220px] p-4 '
                'rounded-[var(--radius-md)] '
                'shadow-none border border-gray-200'
            ):

                ui.label('Active Model').classes(
                    'text-xs font-medium text-gray-500'
                )

                state['version_label'] = ui.label('—').classes(
                    'text-2xl font-bold text-gray-900 mt-1'
                )

        # ==================================================
        # MODEL INFORMATION
        # ==================================================

        with ui.card().classes(
            'w-full p-4 rounded-[var(--radius-md)] '
            'shadow-none border border-gray-200'
        ):

            ui.label('Model Metadata').classes(
                'text-base font-semibold text-gray-900'
            )

            ui.label(
                'Information read from the active model metadata file.'
            ).classes(
                'text-xs text-gray-500 mb-3'
            )

            with ui.row().classes(
                'w-full gap-6 flex-wrap'
            ):

                with ui.column().classes('gap-1 min-w-[220px]'):
                    ui.label('Target').classes(
                        'text-xs text-gray-500'
                    )

                    state['target_label'] = ui.label(
                        '—'
                    ).classes(
                        'text-sm font-semibold text-gray-900'
                    )

                with ui.column().classes('gap-1 min-w-[180px]'):
                    ui.label('Algorithm').classes(
                        'text-xs text-gray-500'
                    )

                    state['algorithm_label'] = ui.label(
                        '—'
                    ).classes(
                        'text-sm font-semibold text-gray-900'
                    )

                with ui.column().classes('gap-1 min-w-[180px]'):
                    ui.label('Metadata Status').classes(
                        'text-xs text-gray-500'
                    )

                    state['status_label'] = ui.label(
                        'Checking...'
                    ).classes(
                        'text-sm font-semibold'
                    )

            state['error_label'] = ui.label('').classes(
                'text-sm text-red-600 mt-3'
            )

        # ==================================================
        # TOOLBAR
        # ==================================================

        with ui.card().classes(
            'w-full p-4 rounded-[var(--radius-md)] '
            'shadow-none border border-gray-200'
        ):

            with ui.row().classes(
                'w-full items-end gap-3 flex-wrap'
            ):

                search_input = ui.input(
                    label='Search features',
                    placeholder='Search by name, group, or position...',
                    on_change=lambda e: set_search(e.value),
                ).props(
                    'outlined clearable'
                ).classes(
                    'flex-1 min-w-[260px]'
                )

                state['category_select'] = ui.select(
                    options=[
                        'All',
                        'Temporal',
                        'Known Future',
                        'Previous Day',
                        'Historical',
                        'Lag',
                        'Rolling',
                        'Other',
                    ],
                    value='All',
                    label='Feature Group',
                    on_change=lambda e: set_category_filter(
                        e.value
                    ),
                ).props(
                    'outlined'
                ).classes(
                    'w-[220px]'
                )

                ui.button(
                    'Clear',
                    icon='refresh',
                    on_click=clear_filters,
                ).props(
                    'flat no-caps'
                ).classes(
                    'text-gray-600'
                )

        # ==================================================
        # FEATURE TABLE
        # ==================================================

        with ui.card().classes(
            'w-full p-0 overflow-hidden '
            'rounded-[var(--radius-md)] '
            'shadow-none border border-gray-200'
        ):

            with ui.row().classes(
                'w-full items-center justify-between '
                'px-5 py-4 border-b border-gray-200'
            ):

                with ui.column().classes('gap-0'):
                    ui.label('Feature Registry').classes(
                        'text-base font-semibold text-gray-900'
                    )

                    ui.label(
                        'Features are displayed in their registered model order.'
                    ).classes(
                        'text-xs text-gray-500'
                    )

            columns = [
                {
                    'name': 'position',
                    'label': '#',
                    'field': 'position',
                    'align': 'left',
                },
                {
                    'name': 'name',
                    'label': 'Feature Name',
                    'field': 'name',
                    'align': 'left',
                },
                {
                    'name': 'category',
                    'label': 'Group',
                    'field': 'category',
                    'align': 'left',
                },
            ]

            state['table'] = ui.table(
                columns=columns,
                rows=[],
                row_key='position',
            ).props(
                'flat separator=horizontal hide-pagination'
            ).classes('w-full')

            state['table'].add_slot(
                'body-cell-category',
                r'''
                <q-td :props="props">
                    <q-badge
                        color="grey-2"
                        text-color="grey-8"
                        class="px-2 py-1"
                    >
                        {{ props.value }}
                    </q-badge>
                </q-td>
                '''
            )

    # ======================================================
    # INITIAL LOAD
    # ======================================================

    load_feature_metadata()
