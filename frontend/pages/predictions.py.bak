from nicegui import ui

from frontend.components import (
    app_card,
    metric_card,
    section_title,
    badge,
)

from frontend.services.prediction_service import (
    load_predictions_page_data,
)


# ==========================================================
# PREDICTIONS PAGE
# ==========================================================

def predictions_page():

    data = load_predictions_page_data()

    with ui.column().classes(
        'w-full '
        'min-w-0 '
        'gap-6'
    ):

        _page_header(data)

        _prediction_overview(data)

        _forecast_section(data)

        _prediction_domains()

        _future_outlook()

        _prediction_intelligence(data)


# ==========================================================
# PAGE HEADER
# ==========================================================

def _page_header(data):

    status = data.get('status')

    with ui.row().classes(
        'w-full '
        'items-start '
        'justify-between '
        'gap-4 '
        'flex-wrap'
    ):

        with ui.column().classes(
            'gap-1 '
            'min-w-0'
        ):

            ui.label(
                'Predictions'
            ).classes(
                'text-2xl '
                'md:text-3xl '
                'font-bold '
                'text-primary-app'
            )

            ui.label(
                'A forward-looking view of your finances, behavior, routines, and personal life.'
            ).classes(
                'text-sm '
                'text-secondary-app'
            )

        with ui.row().classes(
            'items-center '
            'gap-2 '
            'flex-wrap'
        ):

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
            ).props(
                'unelevated no-caps'
            ).classes(
                'app-button'
            )


# ==========================================================
# PREDICTION OVERVIEW
# ==========================================================

def _prediction_overview(data):

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
                subtitle='Total predicted expenses',
                icon='payments',
            )

            metric_card(
                title='Daily Average',
                value=_money(average),
                subtitle='Average predicted expense',
                icon='show_chart',
            )

            metric_card(
                title='Highest Predicted Day',
                value=_money(maximum),
                subtitle='Maximum predicted expense',
                icon='trending_up',
            )


# ==========================================================
# FORECAST SECTION
# ==========================================================

def _forecast_section(data):

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
                        forecast
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
                    summary
                )


# ==========================================================
# FORECAST TIMELINE
# ==========================================================

def _forecast_timeline(
    forecast,
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
                'Predicted_Expense'
            )

            _forecast_row(
                prediction_date,
                value,
                index,
            )


# ==========================================================
# FORECAST ROW
# ==========================================================

def _forecast_row(
    prediction_date,
    value,
    index,
):

    with ui.row().classes(
        'w-full '
        'items-center '
        'gap-3 '
        'py-2.5 '
        'border-b '
        'border-gray-100'
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
                'Predicted expense'
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
            'Predicted total',
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
