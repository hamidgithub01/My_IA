from nicegui import ui

from frontend.components import (
    app_card,
    card_header,
    metric_card,
    prediction_card,
    prediction_summary,
    empty_chart,
    section_title,
    badge,
)


# ==========================================================
# PREDICTIONS PAGE
# ==========================================================

def predictions_page():

    with ui.column().classes(
        'w-full '
        'min-w-0 '
        'gap-6'
    ):

        _page_header()

        _overview_section()

        _forecast_section()

        _prediction_details_section()

        _model_status_section()


# ==========================================================
# PAGE HEADER
# ==========================================================

def _page_header():

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
                'AI-powered forecasts based on your financial history.'
            ).classes(
                'text-sm '
                'text-secondary-app'
            )

        with ui.row().classes(
            'items-center '
            'gap-2'
        ):

            badge(
                'AI Active',
                variant='success',
                icon='auto_awesome',
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
# OVERVIEW
# ==========================================================

def _overview_section():

    with ui.column().classes(
        'w-full '
        'gap-3'
    ):

        section_title(
            'Prediction Overview',
            'Current AI forecast indicators',
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
                title='Next Month Spending',
                value='$2,480',
                subtitle='Expected total spending',
                icon='payments',
            )

            metric_card(
                title='Income Forecast',
                value='$4,250',
                subtitle='Expected income',
                icon='account_balance',
            )

            metric_card(
                title='Savings Forecast',
                value='$1,770',
                subtitle='Expected monthly savings',
                icon='savings',
            )

            metric_card(
                title='Prediction Confidence',
                value='92%',
                subtitle='Model confidence',
                icon='verified',
            )


# ==========================================================
# FORECAST
# ==========================================================

def _forecast_section():

    with ui.column().classes(
        'w-full '
        'gap-3'
    ):

        section_title(
            'Financial Forecast',
            'Expected financial activity over the coming period',
        )

        with ui.element('div').classes(
            'grid '
            'grid-cols-1 '
            'xl:grid-cols-3 '
            'gap-4 '
            'w-full'
        ):

            with app_card(
                title='Spending Forecast',
                subtitle='Next 6 months',
                icon='show_chart',
                classes='xl:col-span-2',
            ):

                empty_chart(
                    title='Spending forecast',
                    message=(
                        'Forecast visualization will appear here '
                        'when prediction data is available.'
                    ),
                    icon='show_chart',
                )

            with app_card(
                title='Forecast Summary',
                subtitle='AI-generated outlook',
                icon='auto_awesome',
            ):

                prediction_summary(
                    title='Overall outlook',
                    value='Stable',
                    description=(
                        'Your projected spending remains within '
                        'the expected range.'
                    ),
                )

                with ui.separator().classes(
                    'my-4'
                ):

                    pass

                with ui.column().classes(
                    'w-full '
                    'gap-3'
                ):

                    _forecast_row(
                        'Spending trend',
                        'Stable',
                        'neutral',
                    )

                    _forecast_row(
                        'Income trend',
                        'Positive',
                        'success',
                    )

                    _forecast_row(
                        'Savings trend',
                        'Improving',
                        'success',
                    )


# ==========================================================
# FORECAST ROW
# ==========================================================

def _forecast_row(
    label,
    value,
    variant='neutral',
):

    with ui.row().classes(
        'w-full '
        'items-center '
        'justify-between '
        'gap-3'
    ):

        ui.label(
            label
        ).classes(
            'text-sm '
            'text-secondary-app'
        )

        badge(
            value,
            variant=variant,
        )


# ==========================================================
# PREDICTION DETAILS
# ==========================================================

def _prediction_details_section():

    with ui.column().classes(
        'w-full '
        'gap-3'
    ):

        section_title(
            'Upcoming Predictions',
            'Key financial predictions generated by the AI system',
        )

        with ui.element('div').classes(
            'grid '
            'grid-cols-1 '
            'md:grid-cols-2 '
            'xl:grid-cols-3 '
            'gap-4 '
            'w-full'
        ):

            prediction_card(
                title='Monthly Spending',
                value='$2,480',
                description=(
                    'Expected spending for the next month.'
                ),
                icon='payments',
            )

            prediction_card(
                title='Available Savings',
                value='$1,770',
                description=(
                    'Estimated amount available after expenses.'
                ),
                icon='savings',
            )

            prediction_card(
                title='Financial Risk',
                value='Low',
                description=(
                    'Current spending pattern indicates low '
                    'financial risk.'
                ),
                icon='shield',
            )


# ==========================================================
# MODEL STATUS
# ==========================================================

def _model_status_section():

    with app_card(
        title='AI Prediction System',
        subtitle='Prediction model reliability and status',
        icon='psychology',
    ):

        with ui.element('div').classes(
            'grid '
            'grid-cols-1 '
            'sm:grid-cols-2 '
            'lg:grid-cols-4 '
            'gap-4 '
            'w-full'
        ):

            _status_item(
                'Model Status',
                'Reliable',
                'success',
            )

            _status_item(
                'Data Quality',
                'Excellent',
                'success',
            )

            _status_item(
                'Monitoring',
                'Active',
                'info',
            )

            _status_item(
                'Last Update',
                'Today',
                'neutral',
            )


# ==========================================================
# STATUS ITEM
# ==========================================================

def _status_item(
    label,
    value,
    variant='neutral',
):

    with ui.column().classes(
        'gap-1 '
        'min-w-0'
    ):

        ui.label(
            label
        ).classes(
            'text-xs '
            'text-secondary-app'
        )

        badge(
            value,
            variant=variant,
        )