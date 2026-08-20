from nicegui import ui

from frontend.components import (
    alert_list,
    app_card,
    badge,
    card_header,
    compact_prediction_card,
    empty_chart,
    metric_card,
    prediction_summary,
    recommendation_list,
    section_title,
)


def dashboard_page():
    """
    Render the main Personal Finance AI dashboard.

    The dashboard is UI-first.
    Backend and ML data will be connected later
    through the frontend services layer.
    """

    with ui.column().classes(
        'w-full max-w-7xl mx-auto gap-6'
    ):

        # ==================================================
        # PAGE HEADER
        # ==================================================

        _page_header()

        # ==================================================
        # KEY METRICS
        # ==================================================

        _key_metrics()

        # ==================================================
        # MAIN INTELLIGENCE AREA
        # ==================================================

        with ui.grid().classes(
            'w-full '
            'grid-cols-1 '
            'xl:grid-cols-3 '
            'gap-6'
        ):

            _forecast_section()

            _ai_status_section()

        # ==================================================
        # UPCOMING PREDICTIONS
        # ==================================================

        _upcoming_predictions()

        # ==================================================
        # FORECAST HORIZONS
        # ==================================================

        _forecast_horizons()

        # ==================================================
        # INSIGHTS
        # ==================================================

        with ui.grid().classes(
            'w-full '
            'grid-cols-1 '
            'lg:grid-cols-2 '
            'gap-6'
        ):

            _alerts_section()

            _recommendations_section()


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

def _key_metrics():

    with ui.grid().classes(
        'w-full '
        'grid-cols-1 '
        'sm:grid-cols-2 '
        'xl:grid-cols-4 '
        'gap-4'
    ):

        metric_card(
            title='Today',
            value='—',
            subtitle='Actual spending',
            icon='today',
        )

        metric_card(
            title='Next 7 Days',
            value='—',
            subtitle='Predicted spending',
            icon='calendar_view_week',
        )

        metric_card(
            title='Next 30 Days',
            value='—',
            subtitle='Forecast horizon',
            icon='date_range',
        )

        metric_card(
            title='Reliability',
            value='—',
            subtitle='Prediction reliability',
            icon='verified',
            status='neutral',
        )


# ==========================================================
# FORECAST SECTION
# ==========================================================

def _forecast_section():

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

        empty_chart(
            title='Forecast chart',
            subtitle=(
                'Forecast data will appear here '
                'when predictions are available.'
            ),
            icon='show_chart',
            height='320px',
        )


# ==========================================================
# AI STATUS
# ==========================================================

def _ai_status_section():

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
            value='Available',
            status='success',
        )

        _status_row(
            icon='verified',
            label='Reliability',
            value='Pending data',
            status='warning',
        )

        _status_row(
            icon='analytics',
            label='Analysis',
            value='Available',
            status='success',
        )

        _status_row(
            icon='notifications_none',
            label='Alerts',
            value='Not available',
            status='neutral',
        )

        ui.separator().classes(
            'my-4'
        )

        badge(
            'AI system operational',
            variant='success',
            icon='check_circle',
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

def _upcoming_predictions():

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

            days = [
                'Tomorrow',
                'Day 2',
                'Day 3',
                'Day 4',
                'Day 5',
                'Day 6',
                'Day 7',
            ]

            for day in days:
                compact_prediction_card(
                    label=day,
                    value='—',
                    icon='auto_awesome',
                )


# ==========================================================
# FORECAST HORIZONS
# ==========================================================

def _forecast_horizons():

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
            )

            _horizon_card(
                title='Days 8–15',
                subtitle='Extended forecast',
                icon='date_range',
            )

            _horizon_card(
                title='Days 16–30',
                subtitle='Longer forecast horizon',
                icon='calendar_month',
            )


# ==========================================================
# HORIZON CARD
# ==========================================================

def _horizon_card(
    *,
    title,
    subtitle,
    icon,
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
                    '—'
                ).classes(
                    'text-2xl '
                    'font-bold '
                    'text-primary-app'
                )

                ui.label(
                    'Predicted spending'
                ).classes(
                    'text-xs '
                    'text-muted-app'
                )

            badge(
                'Pending',
                variant='neutral',
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
                'Important financial alerts will appear '
                'here when the alert system has data.'
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
                'Suggestions generated from your financial data.'
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
                'Personalized recommendations will appear '
                'here when the intelligence system has data.'
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