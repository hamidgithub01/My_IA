import math
from datetime import date, datetime, timedelta

from ml.features.build import build_feature_row
from ml.preparation.preparation import get_prepared_dataset


# ==========================================================
# VALIDATION
# ==========================================================

def validate_forecast_inputs(
    model,
    feature_names,
    start_date,
    days,
    future_context,
):
    """
    Validate forecasting inputs before any prediction
    operation is performed.
    """

    if model is None:
        raise ValueError(
            'Forecast model is required.'
        )

    if not hasattr(
        model,
        'predict',
    ):
        raise TypeError(
            'Forecast model must provide a predict() method.'
        )

    if not isinstance(
        feature_names,
        list,
    ):
        raise TypeError(
            'Forecast feature names must be a list.'
        )

    if not feature_names:
        raise ValueError(
            'Forecast model contains no feature names.'
        )

    forbidden_features = [
        feature
        for feature in feature_names
        if (
            feature == 'Date'
            or feature.startswith('Target_')
        )
    ]

    if forbidden_features:
        raise ValueError(
            'Forbidden forecast features detected: '
            + ', '.join(
                forbidden_features
            )
        )

    if isinstance(
        start_date,
        datetime,
    ):
        start_date = start_date.date()

    if not isinstance(
        start_date,
        date,
    ):
        raise TypeError(
            'Forecast start_date must be a date.'
        )

    if isinstance(
        days,
        bool,
    ) or not isinstance(
        days,
        int,
    ):
        raise TypeError(
            'Forecast days must be an integer.'
        )

    if days <= 0:
        raise ValueError(
            'Forecast days must be greater than zero.'
        )

    if future_context is not None:

        if not isinstance(
            future_context,
            dict,
        ):
            raise TypeError(
                'future_context must be a dictionary.'
            )

    return start_date


# ==========================================================
# HISTORICAL DATA
# ==========================================================

def load_forecast_history():
    """
    Load and validate historical prepared data.

    The returned list is a temporary in-memory copy.
    """

    historical_data = get_prepared_dataset()

    if not historical_data:
        raise ValueError(
            'No historical data available for forecasting.'
        )

    history = [
        dict(row)
        for row in historical_data
    ]

    for row in history:

        if 'Date' not in row:
            raise ValueError(
                'Historical row contains no Date field.'
            )

    history.sort(
        key=lambda row: row['Date']
    )

    return history


# ==========================================================
# FUTURE ROW
# ==========================================================

def create_future_row(
    current_date,
    context,
):
    """
    Create the base row for one future date.

    No actual target-day outcome is inserted.
    """

    row = {
        'Date':
            current_date,

        'Day_Type':
            None,

        'Work_Status':
            None,

        'Health_Impact':
            None,

        'Travel':
            None,

        'Special_Event':
            None,

        'Stress_Level':
            0.0,

        'Notes':
            None,

        'Sleep_Hours':
            0.0,

        'Social_Activity':
            None,

        'Location':
            None,

        'Expense_Total':
            0.0,

        'Expense_Count':
            0,

        'Income_Total':
            0.0,

        'Income_Count':
            0,

        'Event_Count':
            0,
    }

    if context:

        if not isinstance(
            context,
            dict,
        ):
            raise TypeError(
                'Future context for a date must be a dictionary.'
            )

        row.update(
            context
        )

    # ------------------------------------------------------
    # The target-day actual expense must never be supplied
    # by future context.
    # ------------------------------------------------------

    if (
        'Expense_Total' in context
        and context['Expense_Total'] is not None
    ):
        raise ValueError(
            'future_context cannot contain actual '
            'Expense_Total for the forecast date.'
        )

    if (
        'Target_Expense_Total_1D' in context
        or any(
            key.startswith('Target_')
            for key in context
        )
    ):
        raise ValueError(
            'future_context cannot contain Target_* values.'
        )

    return row


# ==========================================================
# FEATURE VECTOR
# ==========================================================

def build_forecast_vector(
    features,
    feature_names,
):
    """
    Build the model input using the exact trained feature
    order.
    """

    vector = []

    for feature_name in feature_names:

        value = features.get(
            feature_name,
            0.0,
        )

        if value is None:
            value = 0.0

        try:

            numeric_value = float(
                value
            )

        except (
            TypeError,
            ValueError,
        ) as exc:

            raise ValueError(
                f'Forecast feature "{feature_name}" '
                'is not numeric.'
            ) from exc

        if not math.isfinite(
            numeric_value
        ):
            raise ValueError(
                f'Forecast feature "{feature_name}" '
                'contains a non-finite value.'
            )

        vector.append(
            numeric_value
        )

    return vector


# ==========================================================
# MODEL PREDICTION
# ==========================================================

def generate_forecast_prediction(
    model,
    feature_vector,
):
    """
    Generate and validate one forecast prediction.
    """

    prediction = model.predict(
        [feature_vector]
    )[0]

    try:

        prediction = float(
            prediction
        )

    except (
        TypeError,
        ValueError,
    ) as exc:

        raise ValueError(
            'Forecast model produced a non-numeric prediction.'
        ) from exc

    if not math.isfinite(
        prediction
    ):
        raise ValueError(
            'Forecast model produced a non-finite prediction.'
        )

    # ------------------------------------------------------
    # Expense predictions cannot be negative.
    # ------------------------------------------------------

    return max(
        0.0,
        prediction,
    )


# ==========================================================
# EXPENSE FORECAST
# ==========================================================

def forecast_expenses(
    model,
    feature_names,
    start_date,
    days=30,
    future_context=None,
):
    """
    Forecast expenses for consecutive future days.

    Forecasting rules:

        1. Historical data is the model's memory.
        2. The target day's actual expense is never used.
        3. Known future contextual information may be used.
        4. Earlier predictions become temporary history.
        5. Temporary predictions are never written to the DB.
        6. The model is never retrained during forecasting.

    Returns:

        [
            {
                'Date': date,
                'Predicted_Expense': float,
                'Features': {...}
            },
            ...
        ]
    """

    start_date = validate_forecast_inputs(
        model=model,
        feature_names=feature_names,
        start_date=start_date,
        days=days,
        future_context=future_context,
    )

    history = load_forecast_history()

    if future_context is None:
        future_context = {}

    results = []

    current_date = start_date

    # ======================================================
    # FORECAST LOOP
    # ======================================================

    for _ in range(
        days
    ):

        # --------------------------------------------------
        # Future context
        # --------------------------------------------------

        context = future_context.get(
            current_date,
            {},
        )

        # --------------------------------------------------
        # Create target row
        #
        # We deliberately do NOT copy an actual future
        # database row into the target.
        # --------------------------------------------------

        target_row = create_future_row(
            current_date=current_date,
            context=context,
        )

        # --------------------------------------------------
        # Historical rows strictly before target date
        #
        # This guarantees that the target day's actual
        # outcome cannot leak into its own features.
        # --------------------------------------------------

        previous_rows = [
            row
            for row in history
            if row['Date'] < current_date
        ]

        if not previous_rows:
            raise ValueError(
                'No historical rows exist before '
                f'forecast date: {current_date}'
            )

        # --------------------------------------------------
        # Feature engineering
        # --------------------------------------------------

        features = build_feature_row(
            target_row,
            previous_rows,
        )

        # --------------------------------------------------
        # Model vector
        # --------------------------------------------------

        feature_vector = build_forecast_vector(
            features,
            feature_names,
        )

        # --------------------------------------------------
        # Prediction
        # --------------------------------------------------

        prediction = generate_forecast_prediction(
            model,
            feature_vector,
        )

        # --------------------------------------------------
        # Store result
        # --------------------------------------------------

        results.append({
            'Date':
                current_date,

            'Predicted_Expense':
                prediction,

            'Features': {
                feature:
                    features.get(
                        feature,
                        0.0,
                    )
                for feature in feature_names
            },
        })

        # --------------------------------------------------
        # Recursive forecasting
        #
        # The prediction becomes historical information
        # for later forecast dates.
        #
        # This row exists ONLY in memory.
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
        # Next forecast date
        # --------------------------------------------------

        current_date += timedelta(
            days=1
        )

    return results