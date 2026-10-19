
from datetime import date, timedelta

from nicegui import ui

from frontend.components import (
    alert_list,
    app_card,
    badge,
    card_header,
    compact_prediction_card,
    empty_chart,
    metric_card,
    recommendation_list,
    section_title,
)

from frontend.services.analysis_service import (
    get_analysis_data,
)

from frontend.services.prediction_service import (
    generate_expense_forecast,
)


# ==========================================================
# PAGE
# ==========================================================

def dashboard_page():
    """
    Render the main Personal Finance AI dashboard.

    The dashboard consumes real data through the frontend
    service layer.
    """

    analysis = get_analysis_data()

    forecast_result = _load_forecast()

    summary = analysis.get(
        'summary',
        {},
    )

    forecast = forecast_result.get(
        'forecast',
        [],
    )

    with ui.column().classes(
        'w-full max-w-7xl mx-auto gap-6'
    ):

        _page_header()

        _key_metrics(
            summary=summary,
            forecast=forecast,
        )

        with ui.grid().classes(
            'w-full '
            'grid-cols-1 '
            'xl:grid-cols-3 '
            'gap-6'
        ):

            _forecast_section(
                forecast=forecast,
            )

            _ai_status_section(
                forecast_result=forecast_result,
            )

        _upcoming_predictions(
            forecast=forecast,
        )

        _forecast_horizons(
            forecast=forecast,
        )

        with ui.grid().classes(
            'w-full '
            'grid-cols-1 '
            'lg:grid-cols-2 '
            'gap-6'
        ):

            _alerts_section()

            _recommendations_section()


# ==========================================================
# FORECAST LOADING
# ==========================================================

def _load_forecast():
    """
    Load the real 30-day expense forecast.

    Forecast errors are returned to the page instead of
    breaking the dashboard.
    """

    try:
        return generate_expense_forecast(
            days=30
        )

    except Exception as exc:
        return {
            'status': 'invalid',
            'forecast': [],
            'error': str(exc),
        }


# ==========================================================
# PAGE HEADER
# ==========================================================

def _page_header():

    with ui.row().classes(
        'w-full '
        'items-center '
        'justify-between '
        'gap-4 '
        'flex-wrap'
    ):

        with ui.column().classes(
            'gap-1 min-w-0'
        ):

            ui.label(
                'Financial Overview'
            ).classes(
                'text-2xl md:text-3xl '
                'font-bold '
                'text-primary-app'
            )

            ui.label(
                'Understand your finances, '
                'anticipate what comes next, '
                'and make better decisions.'
            ).classes(
                'text-sm '
                'text-secondary-app '
                'max-w-2xl'
            )

        ui.button(
            'View predictions',
            icon='auto_awesome',
            on_click=lambda: ui.navigate.to(
                '/predictions'
            ),
        ).props(
            'unelevated no-caps'
        ).classes(
            'app-button '
            'px-4 py-2 '
            'bg-primary '
            'text-white'
        )


# ==========================================================
# KEY METRICS
# ==========================================================

def _key_metrics(
    *,
    summary,
    forecast,
):

    today_expense = _get_today_expense()

    next_7 = _forecast_total(
        forecast[:7]
    )

    next_30 = _forecast_total(
        forecast[:30]
    )

    with ui.grid().classes(
        'w-full '
        'grid-cols-1 '
        'sm:grid-cols-2 '
        'xl:grid-cols-4 '
        'gap-4'
    ):

        metric_card(
            title='Today',
            value=_money(today_expense),
            subtitle='Actual spending',
            icon='today',
        )

        metric_card(
            title='Next 7 Days',
            value=_money(next_7),
            subtitle='Predicted spending',
            icon='calendar_view_week',
        )

        metric_card(
            title='Next 30 Days',
            value=_money(next_30),
            subtitle='Forecast horizon',
            icon='date_range',
        )

        metric_card(
            title='Balance',
            value=_money(
                summary.get(
                    'balance',
                    0.0,
                )
            ),
            subtitle='Income minus expenses',
            icon='account_balance_wallet',
        )


# ==========================================================
# TODAY EXPENSE
# ==========================================================

def _get_today_expense():

    try:
        analysis = get_analysis_data()

        recent_expenses = analysis.get(
            'recent_expenses',
            [],
        )

        today = date.today()

        total = 0.0

        for expense in recent_expenses:

            expense_date = expense.get(
                'Date'
            )

            if expense_date == today:
                amount = expense.get(
                    'Amount'
                )

                if amount is not None:
                    total += float(amount)

        return total

    except Exception:
        return 0.0


# ==========================================================
# FORECAST SECTION
# ==========================================================

def _forecast_section(
    *,
    forecast,
):

    with app_card(
        classes='xl:col-span-2'
    ):

        with ui.row().classes(
            'w-full '
            'items-start '
            'justify-between '
            'gap-4'
        ):

            card_header(
                title='Expense Forecast',
                subtitle=(
                    'Daily predictions for the upcoming days.'
                ),
                icon='show_chart',
            )

            ui.button(
                'Predictions',
                icon='arrow_forward',
                on_click=lambda: ui.navigate.to(
                    '/predictions'
                ),
            ).props(
                'flat no-caps'
            ).classes(
                'shrink-0'
            )

        ui.separator().classes(
            'my-5'
        )

        if not forecast:

            empty_chart(
                title='Forecast unavailable',
                subtitle=(
                    'A valid prediction could not be generated.'
                ),
                icon='show_chart',
                height='320px',
            )

            return

        with ui.column().classes(
            'w-full gap-3'
        ):

            for row in forecast:

                forecast_date = row.get(
                    'Date'
                )

                predicted = row.get(
                    'Predicted_Expense',
                    0.0,
                )

                with ui.row().classes(
                    'w-full '
                    'items-center '
                    'justify-between '
                    'gap-4'
                ):

                    ui.label(
                        _format_date(
                            forecast_date
                        )
                    ).classes(
                        'text-sm '
                        'text-secondary-app'
                    )

                    ui.linear_progress(
                        value=_forecast_bar_value(
                            predicted,
                            forecast,
                        )
                    ).props(
                        'rounded'
                    ).classes(
                        'flex-1'
                    )

                    ui.label(
                        _money(predicted)
                    ).classes(
                        'text-sm '
                        'font-semibold '
                        'text-primary-app '
                        'w-24 '
                        'text-right'
                    )


# ==========================================================
# AI STATUS
# ==========================================================

def _ai_status_section(
    *,
    forecast_result,
):

    forecast_available = bool(
        forecast_result.get(
            'forecast'
        )
    )

    with app_card():

        card_header(
            title='AI Status',
            subtitle=(
                'Current state of the intelligence system.'
            ),
            icon='auto_awesome',
        )

        ui.separator().classes(
            'my-5'
        )

        _status_row(
            icon='auto_awesome',
            label='Predictions',
            value=(
                'Connected'
                if forecast_available
                else 'Unavailable'
            ),
            status=(
                'success'
                if forecast_available
                else 'warning'
            ),
        )

        _status_row(
            icon='analytics',
            label='Analysis',
            value='Connected',
            status='success',
        )

        _status_row(
            icon='account_balance',
            label='Financial data',
            value='Connected',
            status='success',
        )

        _status_row(
            icon='verified',
            label='Reliability',
            value='Developing',
            status='warning',
        )

        ui.separator().classes(
            'my-4'
        )

        if forecast_available:

            badge(
                'AI prediction pipeline connected',
                variant='success',
                icon='check_circle',
            )

        else:

            badge(
                'Prediction pipeline unavailable',
                variant='warning',
                icon='warning',
            )


# ==========================================================
# STATUS ROW
# ==========================================================

def _status_row(
    *,
    icon,
    label,
    value,
    status='neutral',
):

    with ui.row().classes(
        'w-full '
        'items-center '
        'justify-between '
        'py-2'
    ):

        with ui.row().classes(
            'items-center '
            'gap-3 '
            'min-w-0'
        ):

            ui.icon(icon).classes(
                'text-lg '
                'text-secondary-app'
            )

            ui.label(label).classes(
                'text-sm '
                'text-primary-app'
            )

        with ui.row().classes(
            'items-center '
            'gap-2 '
            'shrink-0'
        ):

            ui.element('span').classes(
                f'status-dot '
                f'status-dot-{status}'
            )

            ui.label(value).classes(
                'text-xs '
                'text-secondary-app'
            )


# ==========================================================
# UPCOMING PREDICTIONS
# ==========================================================

def _upcoming_predictions(
    *,
    forecast,
):

    with app_card():

        card_header(
            title='Upcoming Predictions',
            subtitle=(
                'The next seven days, '
                'individually forecast.'
            ),
            icon='calendar_view_week',
        )

        ui.button(
            'Open predictions',
            icon='arrow_forward',
            on_click=lambda: ui.navigate.to(
                '/predictions'
            ),
        ).props(
            'flat no-caps'
        ).classes(
            'mt-3'
        )

        ui.separator().classes(
            'my-5'
        )

        with ui.grid().classes(
            'w-full '
            'grid-cols-1 '
            'sm:grid-cols-2 '
            'md:grid-cols-4 '
            'xl:grid-cols-7 '
            'gap-3'
        ):

            for row in forecast[:7]:

                compact_prediction_card(
                    label=_format_date(
                        row.get('Date')
                    ),
                    value=_money(
                        row.get(
                            'Predicted_Expense',
                            0.0,
                        )
                    ),
                    icon='auto_awesome',
                )


# ==========================================================
# FORECAST HORIZONS
# ==========================================================

def _forecast_horizons(
    *,
    forecast,
):

    with ui.column().classes(
        'w-full gap-4'
    ):

        section_title(
            'Forecast Horizons',
            'Different prediction windows available to the system.',
            icon='date_range',
        )

        with ui.grid().classes(
            'w-full '
            'grid-cols-1 '
            'md:grid-cols-3 '
            'gap-4'
        ):

            _horizon_card(
                title='Days 1–7',
                subtitle='Daily forecasts',
                icon='calendar_today',
                forecast=forecast[:7],
            )

            _horizon_card(
                title='Days 8–15',
                subtitle='Extended forecast',
                icon='date_range',
                forecast=forecast[7:15],
            )

            _horizon_card(
                title='Days 16–30',
                subtitle='Longer forecast horizon',
                icon='calendar_month',
                forecast=forecast[15:30],
            )


# ==========================================================
# HORIZON CARD
# ==========================================================

def _horizon_card(
    *,
    title,
    subtitle,
    icon,
    forecast,
):

    with app_card():

        with ui.row().classes(
            'items-center gap-4'
        ):

            with ui.element('div').classes(
                'app-icon w-10 h-10 shrink-0'
            ):
                ui.icon(icon).classes(
                    'text-xl'
                )

            with ui.column().classes(
                'gap-0'
            ):

                ui.label(title).classes(
                    'text-base '
                    'font-semibold '
                    'text-primary-app'
                )

                ui.label(subtitle).classes(
                    'text-sm '
                    'text-secondary-app'
                )

        with ui.row().classes(
            'items-end '
            'justify-between '
            'mt-5'
        ):

            with ui.column().classes(
                'gap-0'
            ):

                ui.label(
                    _money(
                        _forecast_total(
                            forecast
                        )
                    )
                ).classes(
                    'text-2xl '
                    'font-bold '
                    'text-primary-app'
                )

                ui.label(
                    f'{len(forecast)} forecast days'
                ).classes(
                    'text-xs '
                    'text-muted-app'
                )

            badge(
                'Available'
                if forecast
                else 'Unavailable',
                variant=(
                    'success'
                    if forecast
                    else 'neutral'
                ),
            )


# ==========================================================
# ALERTS
# ==========================================================

def _alerts_section():

    with app_card():

        card_header(
            title='Alerts',
            subtitle=(
                'Important changes detected by the system.'
            ),
            icon='notifications_none',
        )

        ui.separator().classes(
            'my-5'
        )

        alert_list(
            [],
            empty_title='No alerts yet',
            empty_message=(
                'The alert engine is not connected yet. '
                'No alerts are being fabricated.'
            ),
        )


# ==========================================================
# RECOMMENDATIONS
# ==========================================================

def _recommendations_section():

    with app_card():

        card_header(
            title='Recommendations',
            subtitle=(
                'Suggestions generated from your data.'
            ),
            icon='lightbulb_outline',
        )

        ui.separator().classes(
            'my-5'
        )

        recommendation_list(
            [],
            empty_title='No recommendations yet',
            empty_message=(
                'The recommendation engine is not connected yet.'
            ),
        )

        ui.button(
            'Open analysis',
            icon='arrow_forward',
            on_click=lambda: ui.navigate.to(
                '/analysis'
            ),
        ).props(
            'flat no-caps'
        ).classes(
            'mt-4'
        )


# ==========================================================
# HELPERS
# ==========================================================

def _forecast_total(
    forecast,
):

    total = 0.0

    for row in forecast:

        value = row.get(
            'Predicted_Expense'
        )

        if value is not None:
            total += float(value)

    return total


def _forecast_bar_value(
    value,
    forecast,
):

    maximum = max(
        (
            float(
                row.get(
                    'Predicted_Expense',
                    0.0,
                )
            )
            for row in forecast
        ),
        default=0.0,
    )

    if maximum <= 0:
        return 0.0

    return min(
        1.0,
        float(value) / maximum,
    )


def _money(
    value,
):

    try:
        return f'{float(value):,.2f}'
    except (
        TypeError,
        ValueError,
    ):
        return '0.00'


def _format_date(
    value,
):

    if value is None:
        return '—'

    if hasattr(
        value,
        'strftime',
    ):
        return value.strftime(
            '%d %b'
        )

    return str(value)
