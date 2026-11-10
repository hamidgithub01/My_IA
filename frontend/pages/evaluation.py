from nicegui import ui

from frontend.services.evaluation_service import (
    load_evaluation_page_data,
)


# ==========================================================
# DESIGN
# ==========================================================

COLORS = {
    'primary': '#2563EB',
    'success': '#16A34A',
    'warning': '#D97706',
    'danger': '#DC2626',
    'purple': '#7C3AED',
    'cyan': '#0891B2',
    'text': '#172033',
    'muted': '#64748B',
    'border': '#E2E8F0',
    'background': '#F8FAFC',
}


# ==========================================================
# FORMATTING
# ==========================================================

def _number(value, decimals=2):
    if value is None:
        return 'Not available'

    if isinstance(value, bool):
        return 'Yes' if value else 'No'

    if isinstance(value, (int, float)):
        return f'{value:,.{decimals}f}'

    return str(value)


def _date(value):
    if not value:
        return 'Not recorded'

    return str(value).replace('T', ' ')[:19]


def _target_label(name):
    return (
        str(name or 'Unknown')
        .replace('Target_', '')
        .replace('_', ' ')
        .strip()
    )


def _task_type(record):
    value = (
        record.get('target_task')
        or record.get('target_type')
        or record.get('model_type')
        or ''
    )

    value = str(value).lower()

    if 'regression' in value:
        return 'regression'

    if 'classification' in value:
        return 'classification'

    return 'unknown'


def _metric_display_name(name):
    names = {
        'accuracy': 'Accuracy',
        'precision': 'Precision',
        'recall': 'Recall',
        'f1': 'F1 Score',
        'f1_score': 'F1 Score',
        'mae': 'Average Prediction Error',
        'rmse': 'Large Error Sensitivity',
        'r_squared': 'Explained Variation',
        'r2': 'Explained Variation',
    }

    return names.get(
        str(name).lower(),
        str(name).replace('_', ' ').title(),
    )


def _metric_explanation(name):
    explanations = {
        'accuracy': (
            'How often the model makes the correct prediction '
            'across all tested cases.'
        ),
        'precision': (
            'When the model predicts a particular class, '
            'how often that prediction is correct.'
        ),
        'recall': (
            'How many of the actual cases belonging to a class '
            'the model successfully identifies.'
        ),
        'f1': (
            'A combined measure of Precision and Recall. '
            'It helps show whether the model balances both.'
        ),
        'f1_score': (
            'A combined measure of Precision and Recall. '
            'It helps show whether the model balances both.'
        ),
        'mae': (
            'The average distance between the model predictions '
            'and the actual results. Lower is generally better.'
        ),
        'rmse': (
            'Measures prediction errors while giving larger mistakes '
            'more influence. Lower is generally better.'
        ),
        'r_squared': (
            'Shows how much variation in the actual results '
            'is explained by the model. It can also be negative.'
        ),
        'r2': (
            'Shows how much variation in the actual results '
            'is explained by the model. It can also be negative.'
        ),
    }

    return explanations.get(
        str(name).lower(),
        'A measurement recorded during model testing.',
    )


def _metric_value(name, value):
    if value is None:
        return 'Not available'

    key = str(name).lower()

    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)

    percentage_metrics = {
        'accuracy',
        'precision',
        'recall',
        'f1',
        'f1_score',
    }

    if key in percentage_metrics:
        return f'{number * 100:.1f}%'

    return f'{number:,.4f}'


def _metric_color(name):
    key = str(name).lower()

    if key in {
        'accuracy',
        'precision',
        'recall',
        'f1',
        'f1_score',
    }:
        return COLORS['success']

    if key in {'mae', 'rmse'}:
        return COLORS['primary']

    if key in {'r_squared', 'r2'}:
        return COLORS['purple']

    return COLORS['cyan']


# ==========================================================
# STATUS EXPLANATIONS
# ==========================================================

def _evaluation_status(record):
    status = record.get(
        'evaluation_validity_status'
    )

    if status == 'valid':
        return {
            'label': 'Test checks passed',
            'description': (
                'The available evaluation checks passed. '
                'This does not automatically guarantee good predictions.'
            ),
            'color': COLORS['success'],
            'icon': 'check_circle',
        }

    if status == 'invalid':
        return {
            'label': 'Test needs attention',
            'description': (
                'The evaluation did not meet one or more required checks. '
                'Its results should not be treated as a reliable quality measure.'
            ),
            'color': COLORS['danger'],
            'icon': 'warning',
        }

    return {
        'label': 'More information needed',
        'description': (
            'The saved information is not sufficient to confirm '
            'whether the evaluation was valid.'
        ),
        'color': COLORS['warning'],
        'icon': 'info',
    }


def _chronological_status(record):
    value = record.get(
        'chronological_boundary_valid'
    )

    if value is True:
        return {
            'label': 'Time order checked',
            'description': (
                'The training data ends before the testing data begins. '
                'This is an important check for time-based predictions.'
            ),
            'color': COLORS['success'],
            'icon': 'schedule',
        }

    if value is False:
        return {
            'label': 'Time order problem',
            'description': (
                'The training and testing date ranges overlap or are not '
                'in the expected order. The evaluation needs attention.'
            ),
            'color': COLORS['danger'],
            'icon': 'warning',
        }

    return {
        'label': 'Time order not confirmed',
        'description': (
            'The saved information does not allow us to confirm '
            'that the model was tested on later dates.'
        ),
        'color': COLORS['warning'],
        'icon': 'help_outline',
    }


# ==========================================================
# REUSABLE COMPONENTS
# ==========================================================

def _section_title(title, subtitle=None, icon=None):
    with ui.row().classes('w-full items-center gap-3'):
        if icon:
            ui.icon(
                icon
            ).style(
                f'font-size: 25px; color: {COLORS["primary"]};'
            )

        with ui.column().classes('gap-0'):
            ui.label(title).style(
                'font-size: 20px; font-weight: 750; color: #172033;'
            )

            if subtitle:
                ui.label(subtitle).style(
                    'font-size: 13px; color: #64748B;'
                )


def _stat_card(title, value, description, icon, color):
    with ui.card().classes('flex-1').style(
        'min-width: 185px; padding: 18px; '
        'border: 1px solid #E2E8F0; border-radius: 15px; '
        'box-shadow: 0 2px 8px rgba(15,23,42,0.04);'
    ):
        with ui.row().classes('w-full items-center justify-between'):
            ui.label(title).style(
                'font-size: 13px; color: #64748B; font-weight: 600;'
            )

            ui.icon(icon).style(
                f'font-size: 23px; color: {color};'
            )

        ui.label(str(value)).style(
            f'font-size: 30px; font-weight: 800; color: {color};'
        )

        ui.label(description).style(
            'font-size: 12px; color: #64748B;'
        )


def _notice(title, description, color, icon):
    with ui.card().classes('w-full').style(
        f'border: 1px solid {color}40; '
        f'border-left: 5px solid {color}; '
        'border-radius: 12px; padding: 14px; '
        'background: #FFFFFF; box-shadow: none;'
    ):
        with ui.row().classes('items-start gap-3'):
            ui.icon(icon).style(
                f'font-size: 25px; color: {color};'
            )

            with ui.column().classes('gap-1'):
                ui.label(title).style(
                    f'font-weight: 750; color: {color}; font-size: 14px;'
                )

                ui.label(description).style(
                    'font-size: 13px; color: #475569; line-height: 1.6;'
                )


def _information_item(title, value):
    with ui.column().classes('gap-1'):
        ui.label(title).style(
            'font-size: 12px; color: #64748B;'
        )

        ui.label(
            'Not available' if value is None else str(value)
        ).style(
            'font-size: 14px; font-weight: 650; color: #172033; '
            'overflow-wrap: anywhere;'
        )


# ==========================================================
# OVERVIEW
# ==========================================================

def _render_overview(overview):
    _section_title(
        'Your Models at a Glance',
        'A simple overview of the models available in your system.',
        'dashboard',
    )

    with ui.row().classes('w-full flex-wrap gap-3'):
        _stat_card(
            'Available Models',
            overview.get('registered_targets', 0),
            'Different prediction tasks',
            'psychology',
            COLORS['primary'],
        )

        _stat_card(
            'Saved Versions',
            overview.get('registered_versions', 0),
            'Model versions stored in your system',
            'inventory_2',
            COLORS['purple'],
        )

        _stat_card(
            'With Test Results',
            overview.get('versions_with_evaluation', 0),
            'Versions with recorded test measurements',
            'fact_check',
            COLORS['cyan'],
        )

        _stat_card(
            'Currently Active',
            overview.get('active_versions', 0),
            'Versions currently used for predictions',
            'check_circle',
            COLORS['success'],
        )

    with ui.row().classes('w-full flex-wrap gap-3'):
        _stat_card(
            'Checks Passed',
            overview.get('valid_evaluations', 0),
            'Evaluations whose validity was confirmed',
            'verified',
            COLORS['success'],
        )

        _stat_card(
            'Need Attention',
            overview.get('invalid_evaluations', 0),
            'Evaluations that failed required checks',
            'warning',
            COLORS['danger'],
        )

        _stat_card(
            'Not Yet Confirmed',
            overview.get('unknown_evaluations', 0),
            'Evaluations without enough saved evidence',
            'help_outline',
            COLORS['warning'],
        )

    unknown = overview.get(
        'unknown_evaluations',
        0,
    )

    invalid = overview.get(
        'invalid_evaluations',
        0,
    )

    if invalid:
        _notice(
            'Some evaluations need attention',
            (
                f'{invalid} model version(s) did not pass the recorded '
                'evaluation checks. Their results should be reviewed '
                'before relying on them.'
            ),
            COLORS['danger'],
            'warning',
        )

    elif unknown:
        _notice(
            'More test information is needed',
            (
                f'{unknown} model version(s) do not have enough saved '
                'information to confirm the validity of their test results. '
                'This does not mean that these models are inaccurate.'
            ),
            COLORS['warning'],
            'info',
        )

    else:
        _notice(
            'Evaluation checks completed',
            (
                'The available evaluation records passed the recorded '
                'validity checks. Always consider the actual metrics '
                'and the type of prediction before judging performance.'
            ),
            COLORS['success'],
            'check_circle',
        )


# ==========================================================
# METRICS
# ==========================================================

def _render_metrics(record):
    metrics = record.get(
        'evaluation_metrics'
    ) or {}

    if not isinstance(metrics, dict) or not metrics:
        _notice(
            'No test results available',
            (
                'This model does not have recorded test measurements. '
                'Its prediction quality cannot be assessed from this page.'
            ),
            COLORS['warning'],
            'analytics',
        )

        return

    task = _task_type(record)

    if task == 'classification':
        introduction = (
            'These measurements describe how well the model assigns '
            'items to categories during testing.'
        )

    elif task == 'regression':
        introduction = (
            'These measurements describe how close the model predictions '
            'were to the actual numerical results during testing.'
        )

    else:
        introduction = (
            'These measurements were recorded during model testing. '
            'Their meaning depends on the type of prediction task.'
        )

    ui.label(introduction).style(
        'font-size: 13px; color: #64748B;'
    )

    with ui.grid(columns=2).classes('w-full gap-3'):
        for name, value in metrics.items():
            key = str(name).lower()
            color = _metric_color(key)

            with ui.card().classes('w-full').style(
                'padding: 15px; border: 1px solid #E2E8F0; '
                'border-radius: 13px; box-shadow: none;'
            ):
                ui.label(
                    _metric_display_name(name)
                ).style(
                    'font-size: 14px; font-weight: 750; color: #172033;'
                )

                ui.label(
                    _metric_value(name, value)
                ).style(
                    f'font-size: 25px; font-weight: 800; color: {color};'
                )

                ui.label(
                    _metric_explanation(name)
                ).style(
                    'font-size: 12px; line-height: 1.6; color: #64748B;'
                )


# ==========================================================
# MODEL VERSION
# ==========================================================

def _render_model_status(record):
    evaluation = _evaluation_status(record)
    chronology = _chronological_status(record)

    with ui.row().classes('w-full flex-wrap gap-2'):
        with ui.row().classes(
            'items-center gap-2'
        ).style(
            f'background: {evaluation["color"]}12; '
            f'color: {evaluation["color"]}; '
            'padding: 7px 11px; border-radius: 20px;'
        ):
            ui.icon(evaluation['icon']).style('font-size: 17px')
            ui.label(evaluation['label']).style(
                'font-size: 12px; font-weight: 700;'
            )

        with ui.row().classes(
            'items-center gap-2'
        ).style(
            f'background: {chronology["color"]}12; '
            f'color: {chronology["color"]}; '
            'padding: 7px 11px; border-radius: 20px;'
        ):
            ui.icon(chronology['icon']).style('font-size: 17px')
            ui.label(chronology['label']).style(
                'font-size: 12px; font-weight: 700;'
            )

        if record.get('is_active'):
            ui.badge(
                'Used for predictions',
                color='positive',
            ).props('rounded')

        if record.get('evaluation_data_status') == 'metrics_recorded':
            ui.badge(
                'Test results saved',
                color='info',
            ).props('rounded')

        else:
            ui.badge(
                'No test results saved',
                color='warning',
            ).props('rounded')


def _render_version(record):
    version = record.get('version', 'Unknown')
    target = _target_label(
        record.get('target_name')
    )

    evaluation = _evaluation_status(record)
    chronology = _chronological_status(record)

    with ui.card().classes('w-full').style(
        'border: 1px solid #E2E8F0; border-radius: 16px; '
        'padding: 18px; box-shadow: 0 3px 12px rgba(15,23,42,0.04);'
    ):
        with ui.row().classes(
            'w-full items-center justify-between'
        ):
            with ui.column().classes('gap-1'):
                ui.label(target).style(
                    'font-size: 17px; font-weight: 800; color: #172033;'
                )

                ui.label(f'Model version {version}').style(
                    'font-size: 12px; color: #64748B;'
                )

            if record.get('is_active'):
                ui.badge(
                    'ACTIVE',
                    color='positive',
                ).props('rounded')

        _render_model_status(record)

        ui.separator()

        # Basic information

        _section_title(
            'About This Model',
            'The main information about this prediction model.',
            'smart_toy',
        )

        with ui.grid(columns=2).classes('w-full gap-3'):
            _information_item(
                'Prediction type',
                _task_type(record).title(),
            )

            _information_item(
                'Algorithm',
                record.get('algorithm'),
            )

            _information_item(
                'Training examples',
                _number(record.get('training_rows'), 0),
            )

            _information_item(
                'Testing examples',
                _number(record.get('test_rows'), 0),
            )

            _information_item(
                'Created',
                _date(record.get('trained_at')),
            )

            _information_item(
                'Main measurement',
                _metric_display_name(
                    record.get('primary_metric')
                ) if record.get('primary_metric') else None,
            )

        ui.separator()

        _section_title(
            'How Did It Perform?',
            'Understand the recorded test results.',
            'analytics',
        )

        _render_metrics(record)

        # Explain evaluation validity

        ui.separator()

        _section_title(
            'Can We Trust This Test?',
            'Checks that help determine whether the test results can be relied upon.',
            'verified_user',
        )

        _notice(
            evaluation['label'],
            evaluation['description'],
            evaluation['color'],
            evaluation['icon'],
        )

        _notice(
            chronology['label'],
            chronology['description'],
            chronology['color'],
            chronology['icon'],
        )

        # Advanced details

        with ui.expansion(
            'More details about this test',
            icon='manage_search',
        ).classes('w-full').style(
            'border: 1px solid #E2E8F0; border-radius: 10px; '
            'padding: 5px 10px;'
        ):
            ui.label(
                'These details help explain how the model was tested. '
                'You do not need to understand them to use the application.'
            ).style(
                'font-size: 12px; color: #64748B;'
            )

            with ui.grid(columns=2).classes('w-full gap-3'):
                _information_item(
                    'Training period starts',
                    _date(record.get('training_date_start')),
                )

                _information_item(
                    'Training period ends',
                    _date(record.get('training_date_end')),
                )

                _information_item(
                    'Testing period starts',
                    _date(record.get('testing_date_start')),
                )

                _information_item(
                    'Testing period ends',
                    _date(record.get('testing_date_end')),
                )

                _information_item(
                    'Evaluation status',
                    record.get('evaluation_status'),
                )

                _information_item(
                    'Evaluation validity',
                    record.get('evaluation_valid'),
                )

                _information_item(
                    'Chronological test',
                    record.get('chronological_evaluation'),
                )

                _information_item(
                    'Chronological boundary',
                    record.get('chronological_boundary_valid'),
                )

                _information_item(
                    'Actual test examples',
                    record.get('actual_test_rows'),
                )

                _information_item(
                    'Minimum test examples required',
                    record.get('min_test_rows'),
                )

                _information_item(
                    'Test data proportion',
                    record.get('test_ratio'),
                )

                _information_item(
                    'Classification averaging method',
                    record.get('classification_average'),
                )

                _information_item(
                    'Number of training classes',
                    record.get('training_class_count'),
                )

                _information_item(
                    'Number of test classes',
                    record.get('class_count'),
                )

                _information_item(
                    'Training target variation',
                    record.get('training_target_has_variation'),
                )

                _information_item(
                    'Unique training target values',
                    record.get('training_target_unique_count'),
                )

            ui.label(
                'Training date range'
            ).style(
                'font-size: 13px; font-weight: 700; margin-top: 12px;'
            )

            _information_item(
                'Start → End',
                (
                    f"{_date(record.get('training_date_start'))}"
                    f" → "
                    f"{_date(record.get('training_date_end'))}"
                ),
            )

            ui.label(
                'Testing date range'
            ).style(
                'font-size: 13px; font-weight: 700; margin-top: 12px;'
            )

            _information_item(
                'Start → End',
                (
                    f"{_date(record.get('testing_date_start'))}"
                    f" → "
                    f"{_date(record.get('testing_date_end'))}"
                ),
            )


# ==========================================================
# LEGACY HISTORY
# ==========================================================

def _render_legacy_history(records):
    with ui.expansion(
        f'Previous evaluation records ({len(records)})',
        icon='history',
    ).classes('w-full').style(
        'border: 1px solid #E2E8F0; border-radius: 12px; '
        'padding: 8px 12px;'
    ):
        ui.label(
            'These are older evaluation records saved by a previous '
            'version of the system. They are shown separately from '
            'the current registered model versions.'
        ).style(
            'font-size: 13px; color: #64748B;'
        )

        for record in records:
            with ui.card().classes('w-full').style(
                'border: 1px solid #E2E8F0; border-radius: 10px; '
                'padding: 14px; box-shadow: none;'
            ):
                with ui.row().classes(
                    'w-full items-center justify-between'
                ):
                    ui.label(
                        _target_label(record.get('target_name'))
                    ).style(
                        'font-weight: 750;'
                    )

                    ui.badge(
                        'PREVIOUS RECORD',
                        color='grey',
                    )

                ui.label(
                    f"Algorithm: {record.get('algorithm') or 'Not recorded'}"
                ).style(
                    'font-size: 12px; color: #64748B;'
                )

                ui.label(
                    f"Date: {_date(record.get('trained_at'))}"
                ).style(
                    'font-size: 12px; color: #64748B;'
                )

                ui.label(
                    'Recorded test measurements'
                ).style(
                    'font-size: 13px; font-weight: 700; margin-top: 8px;'
                )

                _render_metrics(record)


# ==========================================================
# PAGE
# ==========================================================

def evaluation_page():
    ui.label('Model Performance').style(
        'font-size: 28px; font-weight: 850; color: #172033;'
    )

    ui.label(
        'Understand how your prediction models perform, '
        'what their results mean, and how much confidence '
        'you can place in their tests.'
    ).style(
        'font-size: 14px; color: #64748B; line-height: 1.7;'
    )

    try:
        data = load_evaluation_page_data()

    except Exception:
        _notice(
            'Unable to load model information',
            (
                'The system could not retrieve the evaluation records. '
                'Please try again later.'
            ),
            COLORS['danger'],
            'error',
        )
        return

    if data.get('status') != 'success':
        _notice(
            'Evaluation information is unavailable',
            'The system could not load the model evaluation records.',
            COLORS['danger'],
            'error',
        )
        return

    overview = data.get('overview') or {}
    versions = data.get('versions') or []
    legacy_history = data.get('legacy_history') or []
    errors = data.get('errors') or []

    ui.separator()

    _render_overview(overview)

    ui.separator()

    _section_title(
        'Explore Your Models',
        'Choose a prediction task to see how its model versions performed.',
        'search',
    )

    targets = sorted({
        record.get('target_name')
        for record in versions
        if record.get('target_name')
    })

    if not targets:
        _notice(
            'No models are available yet',
            (
                'Once your system has trained and saved its first model, '
                'you will be able to review its performance here.'
            ),
            COLORS['warning'],
            'model_training',
        )

    else:
        options = {
            target: _target_label(target)
            for target in targets
        }

        search = ui.input(
            'Search for a prediction task',
            placeholder='For example: Expenses, Income, Activity...',
        ).props(
            'outlined clearable'
        ).classes(
            'w-full'
        )

        target_select = ui.select(
            options=options,
            value=targets[0],
            label='Choose a prediction task',
        ).props(
            'outlined'
        ).classes(
            'w-full'
        )

        versions_container = ui.column().classes(
            'w-full gap-4'
        )

        def render_versions():
            selected_target = target_select.value

            versions_container.clear()

            selected = [
                record
                for record in versions
                if record.get('target_name') == selected_target
            ]

            selected.sort(
                key=lambda record: str(
                    record.get('trained_at') or ''
                ),
                reverse=True,
            )

            with versions_container:
                if not selected:
                    _notice(
                        'No saved versions found',
                        'There are no saved model versions for this task.',
                        COLORS['warning'],
                        'info',
                    )
                    return

                ui.label(
                    f'{len(selected)} saved version(s)'
                ).style(
                    'font-size: 13px; color: #64748B;'
                )

                for record in selected:
                    _render_version(record)

        def filter_targets():
            query = (
                search.value or ''
            ).strip().lower()

            filtered = {
                target: label
                for target, label in options.items()
                if (
                    query in target.lower()
                    or query in label.lower()
                )
            }

            current = target_select.value

            target_select.options = filtered

            if current not in filtered:
                target_select.value = next(
                    iter(filtered),
                    None,
                )

            target_select.update()
            render_versions()

        search.on(
            'update:model-value',
            lambda _: filter_targets(),
        )

        target_select.on_value_change(
            lambda _: render_versions()
        )

        render_versions()

    ui.separator()

    _section_title(
        'Previous Records',
        'Older evaluation information, kept separate from current model versions.',
        'history',
    )

    _render_legacy_history(
        legacy_history
    )

    if errors:
        with ui.expansion(
            f'Information loading issues ({len(errors)})',
            icon='info',
        ).classes('w-full'):
            ui.label(
                'Some records could not be loaded. '
                'The available information is shown above.'
            ).style(
                'font-size: 13px; color: #64748B;'
            )