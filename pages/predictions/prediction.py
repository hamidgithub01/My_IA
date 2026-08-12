from pathlib import Path
from datetime import date

from nicegui import ui

from components.header import create_header
from services.predictions.predictor import (
    get_expense_prediction,
)


@ui.page('/prediction')
def prediction_page():

    create_header('Prediction')

    # --------------------------------------------------
    # CSS
    # --------------------------------------------------

    css_file = Path('styles/prediction.css')

    if css_file.exists():

        css_version = css_file.stat().st_mtime_ns

        ui.add_head_html(
            f'<link rel="stylesheet" '
            f'href="/styles/prediction.css?v={css_version}">'
        )

    # --------------------------------------------------
    # Page State
    # --------------------------------------------------

    selected_date = ui.date(
        value=date.today()
    ).classes('prediction-date-input')

    result_container = ui.column().classes(
        'prediction-result-container'
    )

    # --------------------------------------------------
    # Prediction
    # --------------------------------------------------

    def run_prediction():

        result_container.clear()

        if not selected_date.value:

            with result_container:

                ui.label(
                    'Please select a date.'
                ).classes(
                    'prediction-error'
                )

            return

        try:

            target_date = selected_date.value

            if isinstance(target_date, str):
                target_date = date.fromisoformat(
                    target_date
                )

            result = get_expense_prediction(
                target_date
            )

            predicted_expense = (
                result['Predicted_Expense']
            )

            features = result['Features']

            with result_container:

                # --------------------------------------
                # Main Result
                # --------------------------------------

                with ui.card().classes(
                    'prediction-result-card'
                ):

                    with ui.column().classes(
                        'prediction-result-content'
                    ):

                        ui.icon(
                            'auto_awesome',
                            size='42px'
                        ).classes(
                            'prediction-result-icon'
                        )

                        ui.label(
                            'Predicted Expense'
                        ).classes(
                            'prediction-result-label'
                        )

                        ui.label(
                            f'{predicted_expense:,.2f}'
                        ).classes(
                            'prediction-result-value'
                        )

                        ui.label(
                            f'Prediction for '
                            f'{target_date}'
                        ).classes(
                            'prediction-result-date'
                        )

                # --------------------------------------
                # Features
                # --------------------------------------

                with ui.card().classes(
                    'prediction-features-card'
                ):

                    ui.label(
                        'Model Input'
                    ).classes(
                        'prediction-section-title'
                    )

                    ui.label(
                        'The financial and behavioral '
                        'features used by the model.'
                    ).classes(
                        'prediction-section-subtitle'
                    )

                    feature_rows = []

                    for name, value in features.items():

                        feature_rows.append({
                            'feature': name,
                            'value': str(value),
                        })

                    columns = [
                        {
                            'name': 'feature',
                            'label': 'Feature',
                            'field': 'feature',
                            'align': 'left',
                        },
                        {
                            'name': 'value',
                            'label': 'Value',
                            'field': 'value',
                            'align': 'right',
                        },
                    ]

                    ui.table(
                        columns=columns,
                        rows=feature_rows,
                        row_key='feature',
                    ).classes(
                        'prediction-features-table'
                    )

        except ValueError as error:

            with result_container:

                ui.label(
                    str(error)
                ).classes(
                    'prediction-error'
                )

        except Exception:

            with result_container:

                ui.label(
                    'Unable to generate prediction.'
                ).classes(
                    'prediction-error'
                )

    # --------------------------------------------------
    # Page
    # --------------------------------------------------

    with ui.column().classes(
        'prediction-page'
    ):

        # --------------------------------------------------
        # Header
        # --------------------------------------------------

        with ui.row().classes(
            'prediction-header'
        ):

            with ui.column().classes(
                'prediction-heading'
            ):

                ui.label(
                    'Expense Prediction'
                ).classes(
                    'prediction-title'
                )

                ui.label(
                    'Use the trained AI model to estimate '
                    'your total expense for a recorded day.'
                ).classes(
                    'prediction-subtitle'
                )

        # --------------------------------------------------
        # Input
        # --------------------------------------------------

        with ui.card().classes(
            'prediction-input-card'
        ):

            ui.label(
                'Select Date'
            ).classes(
                'prediction-section-title'
            )

            ui.label(
                'Choose a date with available financial '
                'and behavioral data.'
            ).classes(
                'prediction-section-subtitle'
            )

            with ui.row().classes(
                'prediction-input-row'
            ):

                selected_date

                ui.button(
                    'Predict Expense',
                    icon='auto_awesome',
                    on_click=run_prediction,
                ).classes(
                    'prediction-button'
                )

        # --------------------------------------------------
        # Result
        # --------------------------------------------------

        with result_container:
            pass