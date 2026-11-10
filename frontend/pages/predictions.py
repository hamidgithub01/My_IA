from nicegui import ui

from frontend.components import (
    app_card,
    metric_card,
    section_title,
    badge,
)

from frontend.services.prediction_service import (
    load_predictions_page_data,
    get_prediction_model_versions,
)

# ==========================================================
# PREDICTIONS PAGE
# ==========================================================

def predictions_page():

    state = {
        "kind": "expenses",
        "model_version": None,
        "compare_version": None,
    }

    options = {
        "expenses": {
            "target_name": "Target_Expense_Total_1D",
            "value_key": "Predicted_Expense",
            "label": "Expenses",
            "unit": "expense",
            "plural": "expenses",
        },
        "income": {
            "target_name": "Target_Income_Total_1D",
            "value_key": "Predicted_Income",
            "label": "Income",
            "unit": "income",
            "plural": "income",
        },
    }

    _add_predictions_styles()

    @ui.refreshable
    def render_page():

        config = options[state["kind"]]

        model_versions = get_prediction_model_versions(
            config["target_name"]
        )

        selected_version = state["model_version"]
        compare_version = state["compare_version"]

        if compare_version and compare_version == (selected_version or model_versions.get("active_version")):
            compare_version = None
            state["compare_version"] = None

        data = load_predictions_page_data(
            target_name=config["target_name"],
            value_key=config["value_key"],
            model_version=selected_version,
        )

        comparison_data = None
        if compare_version:
            comparison_data = load_predictions_page_data(
                target_name=config["target_name"],
                value_key=config["value_key"],
                model_version=compare_version,
            )

        with ui.column().classes(
            'predictions-page w-full min-w-0 gap-6'
        ):

            _page_header(
                data,
                state,
                options,
                model_versions,
                render_page.refresh,
            )

            _quality_notice(data)

            _prediction_overview(data, config)

            _forecast_section(data, config)

            if compare_version:
                _version_comparison(
                    data,
                    comparison_data,
                    config,
                    primary_version=data.get("model", {}).get("version"),
                    compare_version=compare_version,
                )

            _prediction_domains()

            _future_outlook()

            _prediction_intelligence(data)

    render_page()


# ==========================================================
# PAGE HEADER
# ==========================================================

def _page_header(data, state, options, model_versions, refresh_page):

    status = data.get('status')

    with ui.row().classes(
        'predictions-hero w-full items-start justify-between gap-4 flex-wrap'
    ):

        with ui.column().classes(
            'gap-1 '
            'min-w-0'
        ):

            ui.label(
                'Predictions'
            ).classes(
                'text-2xl md:text-3xl font-extrabold text-white tracking-tight'
            )

            ui.label(
                'A forward-looking view of your finances, behavior, routines, and personal life.'
            ).classes(
                'text-sm text-blue-50/90 max-w-2xl leading-6'
            )

        with ui.row().classes(
            'items-center '
            'gap-2 '
            'flex-wrap'
        ):

            ui.select(
                options={
                    key: config['label']
                    for key, config in options.items()
                },
                value=state['kind'],
                label='Forecast type',
                on_change=lambda event: _change_prediction_type(
                    event.value,
                    state,
                    refresh_page,
                ),
            ).props(
                'outlined dense options-dense dark'
            ).classes(
                'min-w-40 predictions-control'
            )

            version_options = {'': 'Active version (default)'}
            for version in reversed(model_versions.get('versions', [])):
                active = version == model_versions.get('active_version')
                version_options[version] = f"{version}{' · ACTIVE' if active else ''}"
            ui.select(
                options=version_options,
                value=state.get('model_version') or '',
                label='Model version',
                on_change=lambda event: _change_model_version(
                    event.value, state, refresh_page
                ),
            ).props('outlined dense options-dense dark').classes('min-w-52 predictions-control')

            compare_options = {
                version: version
                for version in reversed(model_versions.get('versions', []))
                if version != (state.get('model_version') or model_versions.get('active_version'))
            }
            if compare_options:
                ui.select(
                    options=compare_options,
                    value=state.get('compare_version'),
                    label='Compare with',
                    on_change=lambda event: _change_compare_version(
                        event.value, state, refresh_page
                    ),
                ).props('outlined dense options-dense clearable dark').classes('min-w-40 predictions-control')

            if status == 'valid':
                badge(
                    'Prediction Ready',
                    variant='success',
                    icon='check_circle',
                )
            else:
                badge(
                    'No Prediction Data',
                    variant='neutral',
                    icon='info_outline',
                )

            ui.button(
                'Refresh',
                icon='refresh',
                on_click=refresh_page,
            ).props(
                'unelevated no-caps'
            ).classes(
                'predictions-refresh'
            )


def _change_prediction_type(kind, state, refresh_page):

    if kind not in ('expenses', 'income'):
        return

    state['kind'] = kind
    state['model_version'] = None
    state['compare_version'] = None
    refresh_page()


def _change_model_version(version, state, refresh_page):
    state['model_version'] = version or None

    selected_primary = state['model_version']
    if selected_primary is None:
        # None means the active version; the active version is resolved on refresh.
        state['compare_version'] = None

    refresh_page()


def _change_compare_version(version, state, refresh_page):
    state['compare_version'] = version or None
    refresh_page()


# ==========================================================
# VERSION COMPARISON
# ==========================================================

def _version_comparison(primary_data, compare_data, config, primary_version, compare_version):
    with ui.column().classes('w-full gap-3'):
        section_title(
            'Model Version Comparison',
            'Side-by-side comparison of forecasts generated by two registered versions. Differences are not accuracy scores.',
            icon='compare_arrows',
        )

        if not compare_data or compare_data.get('status') != 'valid':
            ui.label(
                'The comparison version could not generate a valid forecast.'
            ).classes('text-sm text-warning')
            if compare_data and compare_data.get('error'):
                ui.label(str(compare_data['error'])).classes('text-xs text-secondary-app')
            return

        primary_forecast = primary_data.get('forecast') or []
        compare_forecast = compare_data.get('forecast') or []
        value_key = config['value_key']

        primary_by_date = {
            str(row.get('Date')): float(row.get(value_key) or 0)
            for row in primary_forecast if row.get('Date') is not None
        }
        compare_by_date = {
            str(row.get('Date')): float(row.get(value_key) or 0)
            for row in compare_forecast if row.get('Date') is not None
        }
        common_dates = sorted(set(primary_by_date) & set(compare_by_date))

        primary_total = sum(primary_by_date[d] for d in common_dates)
        compare_total = sum(compare_by_date[d] for d in common_dates)
        difference = primary_total - compare_total

        with ui.element('div').classes('grid grid-cols-1 md:grid-cols-3 gap-3 w-full'):
            metric_card(
                title=f'{primary_version or "Selected version"} total',
                value=_money(primary_total),
                subtitle=f'{len(common_dates)} matching forecast days',
                icon='model_training',
            )
            metric_card(
                title=f'{compare_version} total',
                value=_money(compare_total),
                subtitle=f'{len(common_dates)} matching forecast days',
                icon='compare',
            )
            metric_card(
                title='Difference (first − second)',
                value=_money(difference),
                subtitle='Positive means the first version predicts more',
                icon='difference',
            )

        if not common_dates:
            ui.label(
                'The two versions have no matching forecast dates, so a day-by-day comparison is unavailable.'
            ).classes('text-sm text-secondary-app')
            return

        with app_card(
            title='Daily Forecast Differences',
            subtitle='Values are compared only on dates present in both forecasts.',
            icon='table_chart',
        ):
            with ui.column().classes('w-full gap-2'):
                with ui.row().classes('w-full items-center gap-2 font-semibold text-xs text-secondary-app'):
                    ui.label('Date').classes('flex-1')
                    ui.label(str(primary_version or 'Selected')).classes('w-28 text-right')
                    ui.label(str(compare_version)).classes('w-28 text-right')
                    ui.label('Difference').classes('w-28 text-right')
                for date in common_dates:
                    first = primary_by_date[date]
                    second = compare_by_date[date]
                    with ui.row().classes('w-full items-center gap-2 py-2 border-b border-gray-100'):
                        ui.label(date).classes('flex-1 text-xs text-primary-app')
                        ui.label(_money(first)).classes('w-28 text-right text-xs')
                        ui.label(_money(second)).classes('w-28 text-right text-xs')
                        ui.label(_money(first - second)).classes('w-28 text-right text-xs font-semibold')


# ==========================================================
# VISUAL THEME AND QUALITY NOTICE
# ==========================================================

def _add_predictions_styles():
    ui.add_head_html('''
    <style>
      .predictions-page { color: #172554; }
      .predictions-hero {
        padding: 28px 30px; border-radius: 24px;
        background: linear-gradient(120deg, #123b78 0%, #2563eb 52%, #7c3aed 100%);
        box-shadow: 0 16px 38px rgba(37, 99, 235, .20);
        color: white; position: relative; overflow: hidden;
      }
      .predictions-hero:after {
        content: ''; position: absolute; width: 250px; height: 250px;
        right: -65px; top: -135px; border-radius: 50%;
        background: rgba(255,255,255,.10); pointer-events: none;
      }
      .predictions-hero > * { position: relative; z-index: 1; }
      .predictions-control .q-field__control {
        background: rgba(255,255,255,.96); border-radius: 12px;
      }
      /* The controls have white surfaces inside a dark Quasar context.
         Force a dark foreground so selected values remain visible. */
      .predictions-control,
      .predictions-control .q-field__native,
      .predictions-control .q-field__input,
      .predictions-control .q-field__native span,
      .predictions-control .q-field__label,
      .predictions-control .q-field__marginal,
      .predictions-control .q-icon {
        color: #1e293b !important;
      }
      .predictions-control input,
      .predictions-control .q-field__native input {
        color: #1e293b !important;
        -webkit-text-fill-color: #1e293b !important;
      }
      .predictions-refresh {
        background: #fff !important; color: #1d4ed8 !important;
        border-radius: 12px !important; font-weight: 700 !important;
        min-height: 40px;
      }
      .predictions-quality {
        border: 1px solid #bfdbfe; border-left: 5px solid #3b82f6;
        background: linear-gradient(110deg,#eff6ff,#f5f3ff);
        border-radius: 18px; padding: 17px 20px;
        box-shadow: 0 8px 22px rgba(59,130,246,.07);
      }
      .predictions-page .app-card,
      .predictions-page .q-card {
        border-radius: 18px !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 8px 24px rgba(15,23,42,.055) !important;
      }
      .predictions-page .metric-card {
        border-radius: 18px !important;
        border: 1px solid #dbeafe !important;
        background: linear-gradient(145deg,#ffffff,#eff6ff) !important;
        box-shadow: 0 8px 22px rgba(37,99,235,.08) !important;
      }
      .predictions-page .section-title,
      .predictions-page h2 { letter-spacing: -.02em; }
      .predictions-page .forecast-highlight {
        background: linear-gradient(135deg,#ecfeff,#eff6ff);
        border: 1px solid #bae6fd; border-radius: 14px;
      }
      .predictions-page .prediction-row:hover {
        background: #f1f5ff; border-radius: 12px;
      }
      @media (max-width: 640px) {
        .predictions-hero { padding: 21px 18px; border-radius: 18px; }
      }
    </style>
    ''')

def _quality_notice(data):
    status = data.get('status')
    model = data.get('model') or {}
    version = model.get('version') or 'selected model'

    if status != 'valid':
        title = 'Forecast unavailable'
        message = (
            'The selected model did not produce a usable forecast. '
            'This is a data or prediction-availability status, not a quality score.'
        )
        icon_name = 'info'
    else:
        title = 'Model quality: not evaluated yet'
        message = (
            f'{version} generated a forecast, but its historical predictive quality '
            'has not yet been established here. A reliable quality label requires '
            'comparing past predictions with actual outcomes using suitable metrics '
            'and enough test observations.'
        )
        icon_name = 'analytics'

    with ui.row().classes('predictions-quality w-full items-start gap-3 no-wrap'):
        ui.icon(icon_name).classes('text-2xl text-blue-600 mt-1')
        with ui.column().classes('gap-1 min-w-0'):
            ui.label(title).classes('text-sm font-bold text-blue-950')
            ui.label(message).classes('text-sm leading-6 text-blue-900')
            ui.label('Blue = insufficient evaluation evidence · Green / yellow / red will be based on measured historical performance.')\
                .classes('text-xs font-medium text-blue-700')


# ==========================================================
# PREDICTION OVERVIEW
# ==========================================================

def _prediction_overview(data, config):

    summary = data.get(
        'summary',
        {},
    )

    forecast_days = summary.get(
        'days',
        0,
    )

    total = summary.get(
        'total',
        0.0,
    )

    average = summary.get(
        'average_daily',
        0.0,
    )

    maximum = summary.get(
        'maximum',
        0.0,
    )

    with ui.column().classes(
        'w-full '
        'gap-3'
    ):

        section_title(
            'Prediction Overview',
            'Current forward-looking indicators generated from available prediction data.',
            icon='auto_awesome',
        )

        with ui.element('div').classes(
            'grid '
            'grid-cols-1 '
            'sm:grid-cols-2 '
            'xl:grid-cols-4 '
            'gap-4 '
            'w-full'
        ):

            metric_card(
                title='Forecast Horizon',
                value=f'{forecast_days} days',
                subtitle='Available future predictions',
                icon='calendar_month',
            )

            metric_card(
                title='Predicted Total',
                value=_money(total),
                subtitle=f'Total predicted {config["plural"]}',
                icon='payments',
            )

            metric_card(
                title='Daily Average',
                value=_money(average),
                subtitle=f'Average predicted {config["unit"]}',
                icon='show_chart',
            )

            metric_card(
                title='Highest Predicted Day',
                value=_money(maximum),
                subtitle=f'Maximum predicted {config["unit"]}',
                icon='trending_up',
            )


# ==========================================================
# FORECAST SECTION
# ==========================================================

def _forecast_section(data, config):

    forecast = data.get(
        'forecast',
        [],
    )

    summary = data.get(
        'summary',
        {},
    )

    with ui.column().classes(
        'w-full '
        'gap-3'
    ):

        section_title(
            'Future Forecast',
            'The actual prediction timeline produced by the registered model.',
            icon='timeline',
        )

        with ui.element('div').classes(
            'grid '
            'grid-cols-1 '
            'xl:grid-cols-3 '
            'gap-4 '
            'w-full'
        ):

            with app_card(
                title='Prediction Timeline',
                subtitle=_forecast_range(summary),
                icon='show_chart',
                classes='xl:col-span-2',
            ):

                if forecast:

                    _forecast_timeline(
                        forecast,
                        config,
                    )

                else:

                    _no_prediction_state(
                        title='No prediction data yet',
                        message=(
                            'The prediction interface is ready. '
                            'Once real data is available and a model '
                            'has been trained, future predictions will appear here.'
                        ),
                        icon='show_chart',
                    )

            with app_card(
                title='Forecast Summary',
                subtitle='What the current forecast tells us',
                icon='insights',
            ):

                _summary_block(
                    summary,
                    config,
                )


# ==========================================================
# FORECAST TIMELINE
# ==========================================================

def _forecast_timeline(
    forecast,
    config,
):

    with ui.column().classes(
        'w-full '
        'gap-2 '
        'max-h-96 '
        'overflow-y-auto'
    ):

        for index, row in enumerate(
            forecast
        ):

            prediction_date = row.get(
                'Date'
            )

            value = row.get(
                config["value_key"],
                0.0,
            )

            _forecast_row(
                prediction_date,
                value,
                index,
                config,
            )


# ==========================================================
# FORECAST ROW
# ==========================================================

def _forecast_row(
    prediction_date,
    value,
    index,
    config,
):

    with ui.row().classes(
        'w-full '
        'items-center '
        'gap-3 '
        'py-2.5 '
        'border-b border-blue-50 prediction-row transition-colors'
    ):

        with ui.element('div').classes(
            'w-8 '
            'h-8 '
            'rounded-full '
            'bg-[var(--surface-soft)] '
            'flex '
            'items-center '
            'justify-center '
            'shrink-0'
        ):

            ui.label(
                str(index + 1)
            ).classes(
                'text-xs '
                'font-semibold '
                'text-secondary-app'
            )

        with ui.column().classes(
            'gap-0 '
            'min-w-0 '
            'flex-1'
        ):

            ui.label(
                _format_date(prediction_date)
            ).classes(
                'text-sm '
                'font-medium '
                'text-primary-app'
            )

            ui.label(
                f'Predicted {config["unit"]}'
            ).classes(
                'text-xs '
                'text-muted-app'
            )

        ui.label(
            _money(value)
        ).classes(
            'text-sm '
            'font-bold '
            'text-primary-app'
        )


# ==========================================================
# SUMMARY
# ==========================================================

def _summary_block(
    summary,
    config,
):

    total = summary.get(
        'total',
        0.0,
    )

    average = summary.get(
        'average_daily',
        0.0,
    )

    minimum = summary.get(
        'minimum',
        0.0,
    )

    maximum = summary.get(
        'maximum',
        0.0,
    )

    days = summary.get(
        'days',
        0,
    )

    with ui.column().classes(
        'w-full '
        'gap-4'
    ):

        _summary_item(
            f'Predicted {config["plural"]} total',
            _money(total),
            'payments',
        )

        _summary_item(
            'Average per day',
            _money(average),
            'calculate',
        )

        _summary_item(
            'Lowest predicted day',
            _money(minimum),
            'trending_down',
        )

        _summary_item(
            'Highest predicted day',
            _money(maximum),
            'trending_up',
        )

        with ui.separator().classes(
            'my-1'
        ):

            _summary_item(
                'Forecast days',
                str(days),
                'calendar_month',
            )


def _summary_item(
    label,
    value,
    icon,
):

    with ui.row().classes(
        'w-full '
        'items-center '
        'gap-3'
    ):

        with ui.element('div').classes(
            'app-icon '
            'w-9 '
            'h-9 '
            'shrink-0'
        ):

            ui.icon(
                icon
            ).classes(
                'text-lg'
            )

        with ui.column().classes(
            'gap-0 '
            'min-w-0 '
            'flex-1'
        ):

            ui.label(
                label
            ).classes(
                'text-xs '
                'text-secondary-app'
            )

            ui.label(
                value
            ).classes(
                'text-sm '
                'font-semibold '
                'text-primary-app'
            )


# ==========================================================
# PREDICTION DOMAINS
# ==========================================================

def _prediction_domains():

    with ui.column().classes(
        'w-full '
        'gap-3'
    ):

        section_title(
            'Personal Prediction Domains',
            'The prediction layer is designed to grow beyond financial forecasting.',
            icon='hub',
        )

        with ui.element('div').classes(
            'grid '
            'grid-cols-1 '
            'sm:grid-cols-2 '
            'xl:grid-cols-3 '
            'gap-4 '
            'w-full'
        ):

            _domain_card(
                'Financial',
                'Future spending, income, savings, budgets and financial risk.',
                'account_balance',
                'Ready',
                'success',
            )

            _domain_card(
                'Behavior',
                'Future behavior, recurring habits and behavioral changes.',
                'psychology',
                'Ready',
                'success',
            )

            _domain_card(
                'Daily Life',
                'Future daily patterns, activity and contextual changes.',
                'calendar_month',
                'Ready',
                'success',
            )

            _domain_card(
                'Health',
                'Future health-related trends based on available personal data.',
                'favorite',
                'Ready',
                'success',
            )

            _domain_card(
                'Sleep',
                'Future sleep patterns and changes over time.',
                'bedtime',
                'Ready',
                'success',
            )

            _domain_card(
                'Goals & Risk',
                'Future progress, possible risks and important opportunities.',
                'track_changes',
                'Ready',
                'success',
            )


# ==========================================================
# DOMAIN CARD
# ==========================================================

def _domain_card(
    title,
    description,
    icon,
    status,
    variant,
):

    with ui.card().classes(
        'app-card '
        'w-full '
        'min-w-0 '
        'p-5 '
        'rounded-2xl '
        'border '
        'border-gray-200 '
        'shadow-sm '
        'bg-white'
    ):

        with ui.row().classes(
            'w-full '
            'items-start '
            'gap-3'
        ):

            with ui.element('div').classes(
                'app-icon '
                'w-10 '
                'h-10 '
                'shrink-0'
            ):

                ui.icon(
                    icon
                ).classes(
                    'text-xl'
                )

            with ui.column().classes(
                'gap-1 '
                'min-w-0 '
                'flex-1'
            ):

                with ui.row().classes(
                    'items-center '
                    'justify-between '
                    'gap-2'
                ):

                    ui.label(
                        title
                    ).classes(
                        'text-sm '
                        'font-semibold '
                        'text-primary-app'
                    )

                    badge(
                        status,
                        variant=variant,
                    )

                ui.label(
                    description
                ).classes(
                    'text-xs '
                    'leading-5 '
                    'text-secondary-app'
                )


# ==========================================================
# FUTURE OUTLOOK
# ==========================================================

def _future_outlook():

    with app_card(
        title='Future Outlook',
        subtitle='The system should transform personal history into a forward-looking understanding of what may happen next.',
        icon='visibility',
    ):

        with ui.element('div').classes(
            'grid '
            'grid-cols-1 '
            'md:grid-cols-3 '
            'gap-4 '
            'w-full'
        ):

            _outlook_item(
                'What is likely to continue?',
                'Recurring patterns and behaviors that remain consistent.',
                'repeat',
            )

            _outlook_item(
                'What may change?',
                'Emerging trends and deviations from normal behavior.',
                'trending_up',
            )

            _outlook_item(
                'What deserves attention?',
                'Potential future risks, changes and opportunities.',
                'priority_high',
            )


def _outlook_item(
    title,
    description,
    icon,
):

    with ui.column().classes(
        'gap-2 '
        'p-4 '
        'rounded-xl '
        'bg-[var(--surface-soft)] '
        'min-h-32'
    ):

        ui.icon(
            icon
        ).classes(
            'text-xl '
            'text-primary'
        )

        ui.label(
            title
        ).classes(
            'text-sm '
            'font-semibold '
            'text-primary-app'
        )

        ui.label(
            description
        ).classes(
            'text-xs '
            'leading-5 '
            'text-secondary-app'
        )


# ==========================================================
# PREDICTION INTELLIGENCE
# ==========================================================

def _prediction_intelligence(data):

    model = data.get(
        'model',
        {},
    )

    target_name = model.get(
        'target_name'
    )

    version = model.get(
        'version'
    )

    feature_count = model.get(
        'feature_count'
    )

    with app_card(
        title='Prediction Intelligence',
        subtitle='Technical information about the prediction system.',
        icon='verified',
    ):

        with ui.element('div').classes(
            'grid '
            'grid-cols-1 '
            'sm:grid-cols-2 '
            'lg:grid-cols-4 '
            'gap-4 '
            'w-full'
        ):

            _intelligence_item(
                'Model',
                target_name or 'Not available',
                'psychology',
            )

            _intelligence_item(
                'Version',
                version or 'Not available',
                'new_releases',
            )

            _intelligence_item(
                'Features',
                (
                    str(feature_count)
                    if feature_count is not None
                    else 'Not available'
                ),
                'tune',
            )

            _intelligence_item(
                'System',
                'Prediction engine',
                'auto_awesome',
            )


def _intelligence_item(
    title,
    value,
    icon,
):

    with ui.column().classes(
        'gap-1 '
        'min-w-0'
    ):

        with ui.row().classes(
            'items-center '
            'gap-2'
        ):

            ui.icon(
                icon
            ).classes(
                'text-lg '
                'text-primary'
            )

            ui.label(
                title
            ).classes(
                'text-xs '
                'text-secondary-app'
            )

        ui.label(
            value
        ).classes(
            'text-sm '
            'font-semibold '
            'text-primary-app '
            'break-words'
        )


# ==========================================================
# EMPTY STATE
# ==========================================================

def _no_prediction_state(
    title,
    message,
    icon,
):

    with ui.column().classes(
        'w-full '
        'min-h-72 '
        'items-center '
        'justify-center '
        'text-center '
        'p-6 '
        'gap-2'
    ):

        with ui.element('div').classes(
            'app-icon '
            'w-14 '
            'h-14'
        ):

            ui.icon(
                icon
            ).classes(
                'text-2xl'
            )

        ui.label(
            title
        ).classes(
            'text-sm '
            'font-semibold '
            'text-primary-app '
            'mt-2'
        )

        ui.label(
            message
        ).classes(
            'text-xs '
            'text-secondary-app '
            'max-w-lg'
        )


# ==========================================================
# HELPERS
# ==========================================================

def _money(
    value,
):

    try:

        number = float(
            value or 0
        )

    except (
        TypeError,
        ValueError,
    ):

        number = 0.0

    return f'${number:,.2f}'


def _format_date(
    value,
):

    if value is None:
        return 'Unknown date'

    return str(
        value
    )


def _forecast_range(
    summary,
):

    first_day = summary.get(
        'first_day'
    )

    last_day = summary.get(
        'last_day'
    )

    if not first_day or not last_day:

        return 'Waiting for prediction data'

    return (
        f'{first_day} → {last_day}'
    )
