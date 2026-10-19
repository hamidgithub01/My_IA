import math
from datetime import date, datetime, timedelta

from ml.features.build import build_feature_row
from ml.preparation.preparation import get_prepared_dataset


# ==========================================================
# CONFIGURATION
# ==========================================================

DEFAULT_FORECAST_DAYS = 30


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
    Validate forecasting inputs before prediction.
    """

    if model is None:
        raise ValueError(
            'Forecast model is required.'
        )

    if not hasattr(model, 'predict'):
        raise TypeError(
            'Forecast model must provide a predict() method.'
        )

    if not isinstance(feature_names, list):
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
            + ', '.join(forbidden_features)
        )

    if isinstance(start_date, datetime):
        start_date = start_date.date()

    if not isinstance(start_date, date):
        raise TypeError(
            'Forecast start_date must be a date.'
        )

    if isinstance(days, bool) or not isinstance(days, int):
        raise TypeError(
            'Forecast days must be an integer.'
        )

    if days <= 0:
        raise ValueError(
            'Forecast days must be greater than zero.'
        )

    if future_context is not None:
        if not isinstance(future_context, dict):
            raise TypeError(
                'future_context must be a dictionary.'
            )

    return start_date


# ==========================================================
# HISTORICAL DATA
# ==========================================================

def load_forecast_history():
    """
    Load historical prepared data.

    The returned data is an in-memory copy.
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
# FUTURE CONTEXT
# ==========================================================

def get_future_context_for_date(
    future_context,
    current_date,
):
    """
    Return validated known future context for a date.
    """

    context = future_context.get(
        current_date,
        {},
    )

    if context is None:
        context = {}

    if not isinstance(context, dict):
        raise TypeError(
            'Future context for a date must be a dictionary.'
        )

    if 'Expense_Total' in context:
        if context['Expense_Total'] is not None:
            raise ValueError(
                'future_context cannot contain actual '
                'Expense_Total for the forecast date.'
            )

    if any(
        key.startswith('Target_')
        for key in context
    ):
        raise ValueError(
            'future_context cannot contain Target_* values.'
        )

    return dict(context)


# ==========================================================
# FUTURE ROW
# ==========================================================

def create_future_row(
    current_date,
    context,
):
    """
    Create a temporary future row.

    This row contains only known contextual information.
    Actual target-day expense is never supplied.
    """

    row = {
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

    if context:
        row.update(context)

    # The actual future outcome is never allowed.
    row['Expense_Total'] = 0.0
    row['Expense_Count'] = 0

    return row


# ==========================================================
# FEATURE VECTOR
# ==========================================================

def build_forecast_vector(
    features,
    feature_names,
):
    """
    Build the model input using the exact trained
    feature order.
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
            numeric_value = float(value)

        except (
            TypeError,
            ValueError,
        ) as exc:

            raise ValueError(
                f'Forecast feature "{feature_name}" '
                'is not numeric.'
            ) from exc

        if not math.isfinite(numeric_value):
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
        prediction = float(prediction)

    except (
        TypeError,
        ValueError,
    ) as exc:

        raise ValueError(
            'Forecast model produced a non-numeric prediction.'
        ) from exc

    if not math.isfinite(prediction):
        raise ValueError(
            'Forecast model produced a non-finite prediction.'
        )

    return max(
        0.0,
        prediction,
    )


# ==========================================================
# FORECAST
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

    Important design rule:

        The model predicts T+1 from the latest known
        information at T.

    Therefore the first forecast is generated from the
    latest available historical row, not from an empty
    artificial row representing the future day.
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

    # ------------------------------------------------------
    # Find the latest real historical date.
    # ------------------------------------------------------

    last_historical_date = max(
        row['Date']
        for row in history
    )

    # ------------------------------------------------------
    # The requested forecast must begin after the latest
    # known historical date.
    # ------------------------------------------------------

    if start_date <= last_historical_date:
        start_date = (
            last_historical_date
            + timedelta(days=1)
        )

    results = []

    forecast_date = start_date

    # ======================================================
    # FORECAST LOOP
    # ======================================================

    for _ in range(days):

        # --------------------------------------------------
        # The model's input date is the previous known date.
        #
        # For example:
        #
        # last real day = Aug 20
        # prediction    = Aug 21
        #
        # The features are built from Aug 20 history.
        # --------------------------------------------------

        previous_date = (
            forecast_date
            - timedelta(days=1)
        )

        previous_rows = [
            row
            for row in history
            if row['Date'] <= previous_date
        ]

        if not previous_rows:
            raise ValueError(
                'No historical rows exist before '
                f'forecast date: {forecast_date}'
            )

        # --------------------------------------------------
        # Use the latest known row as the feature-engineering
        # anchor.
        # --------------------------------------------------

        anchor_row = dict(
            previous_rows[-1]
        )

        # --------------------------------------------------
        # Known future context may be supplied for the
        # forecast date.
        # --------------------------------------------------

        context = get_future_context_for_date(
            future_context,
            forecast_date,
        )

        # --------------------------------------------------
        # Do NOT replace the historical anchor with an
        # empty future row.
        #
        # Only known future contextual fields are applied.
        # --------------------------------------------------

        feature_row = dict(
            anchor_row
        )

        feature_row['Date'] = forecast_date

        for key, value in context.items():

            if key in (
                'Expense_Total',
                'Expense_Count',
                'Target_Expense_Total_1D',
            ):
                continue

            feature_row[key] = value

        # --------------------------------------------------
        # Feature engineering
        #
        # History contains only information known before
        # the forecast date, plus previous predictions.
        # --------------------------------------------------

        features = build_feature_row(
            feature_row,
            previous_rows,
        )

        # --------------------------------------------------
        # Build exact model vector.
        # --------------------------------------------------

        feature_vector = build_forecast_vector(
            features,
            feature_names,
        )

        # --------------------------------------------------
        # Prediction.
        # --------------------------------------------------

        prediction = generate_forecast_prediction(
            model,
            feature_vector,
        )

        # --------------------------------------------------
        # Store result.
        # --------------------------------------------------

        results.append({
            'Date': forecast_date,

            'Predicted_Expense': prediction,

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
        # Recursive forecasting.
        #
        # The prediction becomes temporary history for
        # subsequent forecast days.
        #
        # It is NEVER written to the database.
        # --------------------------------------------------

        predicted_row = dict(
            feature_row
        )

        predicted_row['Date'] = forecast_date

        predicted_row['Expense_Total'] = prediction

        predicted_row['Expense_Count'] = (
            1
            if prediction > 0
            else 0
        )

        history.append(
            predicted_row
        )

        # --------------------------------------------------
        # Next forecast date.
        # --------------------------------------------------

        forecast_date += timedelta(
            days=1
        )

    return results