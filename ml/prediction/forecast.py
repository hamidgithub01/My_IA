from datetime import timedelta

from ml.features.build import build_feature_row
from ml.preparation.preparation import get_prepared_dataset


def forecast_expenses(
    model,
    feature_names,
    start_date,
    days=30,
    future_context=None,
):
    """
    Forecast expenses for future days.

    Rules:

    - Historical data is used as the model's memory.
    - The target day's actual expense is never used.
    - Future predictions are added to temporary history.
    - Later predictions can therefore use earlier predictions.
    - Known future contextual information may be supplied
      through future_context.
    - The model is not retrained during forecasting.

    Args:
        model:
            Trained forecasting model.

        feature_names:
            Exact feature names used by the trained model.

        start_date:
            First date to forecast.

        days:
            Number of future days to forecast.

        future_context:
            Optional dictionary:

                {
                    date: {
                        'Day_Type': ...,
                        'Work_Status': ...,
                        'Health_Impact': ...,
                        'Travel': ...,
                        'Special_Event': ...,
                        'Stress_Level': ...,
                        'Sleep_Hours': ...,
                        'Social_Activity': ...,
                        'Location': ...,
                    }
                }

    Returns:
        List of dictionaries containing:

            Date
            Predicted_Expense
            Features
    """

    if days <= 0:
        raise ValueError(
            'Forecast days must be greater than zero.'
        )

    historical_data = get_prepared_dataset()

    if not historical_data:
        raise ValueError(
            'No historical data available for forecasting.'
        )

    # ------------------------------------------------------
    # Sort historical data
    # ------------------------------------------------------

    history = sorted(
        historical_data,
        key=lambda row: row['Date'],
    )

    # ------------------------------------------------------
    # Future context
    # ------------------------------------------------------

    if future_context is None:
        future_context = {}

    results = []

    current_date = start_date

    # ------------------------------------------------------
    # Forecast each future day
    # ------------------------------------------------------

    for _ in range(days):

        # --------------------------------------------------
        # Check whether information for this future date
        # has already been supplied.
        # --------------------------------------------------

        context = future_context.get(
            current_date,
            {},
        )

        # --------------------------------------------------
        # Check historical database
        # --------------------------------------------------

        existing_row = next(
            (
                row
                for row in history
                if row['Date'] == current_date
            ),
            None,
        )

        # --------------------------------------------------
        # Build target row
        # --------------------------------------------------

        if existing_row is not None:

            target_row = dict(
                existing_row
            )

        else:

            target_row = {
                'Date': current_date,

                'Day_Type': None,
                'Work_Status': None,
                'Health_Impact': None,
                'Travel': None,
                'Special_Event': None,

                'Stress_Level': 0.0,
                'Notes': None,
                'Sleep_Hours': 0.0,

                'Social_Activity': None,
                'Location': None,

                'Expense_Total': 0.0,
                'Expense_Count': 0,

                'Income_Total': 0.0,
                'Income_Count': 0,

                'Event_Count': 0,
            }

        # --------------------------------------------------
        # Apply known future information
        # --------------------------------------------------

        target_row.update(
            context
        )

        # --------------------------------------------------
        # Historical rows only
        #
        # Current target date is excluded.
        # --------------------------------------------------

        previous_rows = [
            row
            for row in history
            if row['Date'] < current_date
        ]

        # --------------------------------------------------
        # Build features
        # --------------------------------------------------

        features = build_feature_row(
            target_row,
            previous_rows,
        )

        # --------------------------------------------------
        # Build model input
        # --------------------------------------------------

        feature_vector = [
            float(
                features.get(
                    feature,
                    0.0,
                )
                or 0.0
            )
            for feature in feature_names
        ]

        # --------------------------------------------------
        # Prediction
        # --------------------------------------------------

        prediction = float(
            model.predict(
                [feature_vector]
            )[0]
        )

        # Expenses cannot be negative.
        prediction = max(
            0.0,
            prediction,
        )

        # --------------------------------------------------
        # Save result
        # --------------------------------------------------

        results.append({
            'Date': current_date,

            'Predicted_Expense':
                prediction,

            'Features': {
                feature: features.get(
                    feature,
                    0.0,
                )
                for feature in feature_names
            },
        })

        # --------------------------------------------------
        # Add prediction to temporary history
        #
        # This is NOT written to the database.
        # It only allows later forecast days to use
        # earlier predictions as historical information.
        # --------------------------------------------------

        predicted_row = dict(
            target_row
        )

        predicted_row[
            'Expense_Total'
        ] = prediction

        history.append(
            predicted_row
        )

        # --------------------------------------------------
        # Next day
        # --------------------------------------------------

        current_date += timedelta(
            days=1
        )

    return results