import math
from datetime import date, timedelta
from unittest.mock import patch

import numpy as np
from sklearn.linear_model import LinearRegression

from ml.prediction.forecast import (
    build_forecast_vector,
    create_future_row,
    forecast_expenses,
    generate_forecast_prediction,
    load_forecast_history,
    validate_forecast_inputs,
)


# ==========================================================
# CONSTANTS
# ==========================================================

FEATURE_NAMES = [
    'expense_lag_1',
    'expense_lag_7',
    'expense_rolling_mean_7',
]

START_DATE = date(
    2026,
    8,
    17,
)


# ==========================================================
# SYNTHETIC MODEL
# ==========================================================

def create_synthetic_model():
    """
    Create a deterministic regression model.

    Formula approximately follows:

        prediction =
            0.5 * lag_1
            + 0.3 * lag_7
            + 0.2 * rolling_mean_7
    """

    X = np.array([
        [100.0, 90.0, 95.0],
        [120.0, 100.0, 110.0],
        [140.0, 120.0, 130.0],
        [160.0, 140.0, 150.0],
        [180.0, 160.0, 170.0],
    ])

    y = np.array([
        87.0,
        104.0,
        121.0,
        138.0,
        155.0,
    ])

    model = LinearRegression()

    model.fit(
        X,
        y,
    )

    return model


# ==========================================================
# SYNTHETIC HISTORICAL DATA
# ==========================================================

def create_historical_data():
    """
    Create enough historical rows for lag and rolling
    features.
    """

    rows = []

    base_date = (
        START_DATE
        - timedelta(days=10)
    )

    for index in range(
        10
    ):

        current_date = (
            base_date
            + timedelta(days=index)
        )

        rows.append({

            'Date':
                current_date,

            'Day_Type':
                'Workday',

            'Work_Status':
                'Working',

            'Health_Impact':
                'Normal',

            'Travel':
                None,

            'Special_Event':
                None,

            'Stress_Level':
                1.0,

            'Notes':
                None,

            'Sleep_Hours':
                7.0,

            'Social_Activity':
                None,

            'Location':
                'Home',

            'Expense_Total':
                float(
                    100
                    + index * 10
                ),

            'Expense_Count':
                2,

            'Income_Total':
                0.0,

            'Income_Count':
                0,

            'Event_Count':
                0,
        })

    return rows


# ==========================================================
# MODEL VALIDATION TESTS
# ==========================================================

def test_invalid_model():

    print(
        '========== INVALID MODEL TEST =========='
    )

    try:

        validate_forecast_inputs(
            model=None,
            feature_names=FEATURE_NAMES,
            start_date=START_DATE,
            days=3,
            future_context=None,
        )

    except ValueError as exc:

        if 'model is required' not in str(exc):

            raise AssertionError(
                'Invalid model error message is incorrect.'
            )

        print(
            'Invalid model handling: PASSED'
        )

        return

    raise AssertionError(
        'None model was accepted.'
    )


# ==========================================================
# MODEL PREDICT METHOD TEST
# ==========================================================

def test_model_without_predict():

    print(
        '========== MODEL WITHOUT PREDICT TEST =========='
    )

    class InvalidModel:
        pass

    try:

        validate_forecast_inputs(
            model=InvalidModel(),
            feature_names=FEATURE_NAMES,
            start_date=START_DATE,
            days=3,
            future_context=None,
        )

    except TypeError as exc:

        if 'predict()' not in str(exc):

            raise AssertionError(
                'Missing predict() error is incorrect.'
            )

        print(
            'Missing predict() handling: PASSED'
        )

        return

    raise AssertionError(
        'Model without predict() was accepted.'
    )


# ==========================================================
# FEATURE NAME TYPE TEST
# ==========================================================

def test_invalid_feature_names():

    print(
        '========== INVALID FEATURE NAMES TEST =========='
    )

    model = create_synthetic_model()

    try:

        validate_forecast_inputs(
            model=model,
            feature_names=tuple(
                FEATURE_NAMES
            ),
            start_date=START_DATE,
            days=3,
            future_context=None,
        )

    except TypeError:

        print(
            'Invalid feature names handling: PASSED'
        )

        return

    raise AssertionError(
        'Non-list feature names were accepted.'
    )


# ==========================================================
# EMPTY FEATURE TEST
# ==========================================================

def test_empty_feature_names():

    print(
        '========== EMPTY FEATURE NAMES TEST =========='
    )

    model = create_synthetic_model()

    try:

        validate_forecast_inputs(
            model=model,
            feature_names=[],
            start_date=START_DATE,
            days=3,
            future_context=None,
        )

    except ValueError:

        print(
            'Empty feature names handling: PASSED'
        )

        return

    raise AssertionError(
        'Empty feature names were accepted.'
    )


# ==========================================================
# FORBIDDEN DATE FEATURE TEST
# ==========================================================

def test_forbidden_date_feature():

    print(
        '========== FORBIDDEN DATE FEATURE TEST =========='
    )

    model = create_synthetic_model()

    try:

        validate_forecast_inputs(
            model=model,
            feature_names=[
                'expense_lag_1',
                'Date',
            ],
            start_date=START_DATE,
            days=3,
            future_context=None,
        )

    except ValueError as exc:

        if 'Date' not in str(exc):

            raise AssertionError(
                'Date feature was not identified.'
            )

        print(
            'Forbidden Date feature handling: PASSED'
        )

        return

    raise AssertionError(
        'Date was accepted as a forecast feature.'
    )


# ==========================================================
# FORBIDDEN TARGET FEATURE TEST
# ==========================================================

def test_forbidden_target_feature():

    print(
        '========== FORBIDDEN TARGET FEATURE TEST =========='
    )

    model = create_synthetic_model()

    try:

        validate_forecast_inputs(
            model=model,
            feature_names=[
                'expense_lag_1',
                'Target_Expense_Total_1D',
            ],
            start_date=START_DATE,
            days=3,
            future_context=None,
        )

    except ValueError as exc:

        if 'Target_Expense_Total_1D' not in str(exc):

            raise AssertionError(
                'Target feature was not identified.'
            )

        print(
            'Forbidden Target feature handling: PASSED'
        )

        return

    raise AssertionError(
        'Target feature was accepted as a forecast feature.'
    )


# ==========================================================
# INVALID DATE TEST
# ==========================================================

def test_invalid_start_date():

    print(
        '========== INVALID START DATE TEST =========='
    )

    model = create_synthetic_model()

    try:

        validate_forecast_inputs(
            model=model,
            feature_names=FEATURE_NAMES,
            start_date='2026-08-17',
            days=3,
            future_context=None,
        )

    except TypeError:

        print(
            'Invalid start date handling: PASSED'
        )

        return

    raise AssertionError(
        'String start date was accepted.'
    )


# ==========================================================
# INVALID DAYS TEST
# ==========================================================

def test_invalid_days():

    print(
        '========== INVALID DAYS TEST =========='
    )

    model = create_synthetic_model()

    for invalid_days in (
        0,
        -1,
    ):

        try:

            validate_forecast_inputs(
                model=model,
                feature_names=FEATURE_NAMES,
                start_date=START_DATE,
                days=invalid_days,
                future_context=None,
            )

        except ValueError:

            continue

        raise AssertionError(
            f'Invalid days value was accepted: '
            f'{invalid_days}'
        )

    print(
        'Invalid days handling: PASSED'
    )


# ==========================================================
# BOOLEAN DAYS TEST
# ==========================================================

def test_boolean_days():

    print(
        '========== BOOLEAN DAYS TEST =========='
    )

    model = create_synthetic_model()

    try:

        validate_forecast_inputs(
            model=model,
            feature_names=FEATURE_NAMES,
            start_date=START_DATE,
            days=True,
            future_context=None,
        )

    except TypeError:

        print(
            'Boolean days handling: PASSED'
        )

        return

    raise AssertionError(
        'Boolean days value was accepted.'
    )


# ==========================================================
# FUTURE CONTEXT TYPE TEST
# ==========================================================

def test_invalid_future_context():

    print(
        '========== INVALID FUTURE CONTEXT TEST =========='
    )

    model = create_synthetic_model()

    try:

        validate_forecast_inputs(
            model=model,
            feature_names=FEATURE_NAMES,
            start_date=START_DATE,
            days=3,
            future_context=[],
        )

    except TypeError:

        print(
            'Invalid future context handling: PASSED'
        )

        return

    raise AssertionError(
        'Invalid future context was accepted.'
    )


# ==========================================================
# FUTURE ROW TEST
# ==========================================================

def test_future_row():

    print(
        '========== FUTURE ROW TEST =========='
    )

    row = create_future_row(
        current_date=START_DATE,
        context={
            'Day_Type':
                'Weekend',

            'Stress_Level':
                3.0,
        },
    )

    if row[
        'Date'
    ] != START_DATE:

        raise AssertionError(
            'Future row date is incorrect.'
        )

    if row[
        'Day_Type'
    ] != 'Weekend':

        raise AssertionError(
            'Future context was not applied.'
        )

    if row[
        'Stress_Level'
    ] != 3.0:

        raise AssertionError(
            'Future numeric context was not applied.'
        )

    if row[
        'Expense_Total'
    ] != 0.0:

        raise AssertionError(
            'Future row contains a non-zero actual expense.'
        )

    print(
        'Future row construction: PASSED'
    )


# ==========================================================
# ACTUAL EXPENSE LEAKAGE TEST
# ==========================================================

def test_future_context_cannot_contain_actual_expense():

    print(
        '========== ACTUAL EXPENSE LEAKAGE TEST =========='
    )

    try:

        create_future_row(
            current_date=START_DATE,
            context={
                'Expense_Total':
                    9999.0,
            },
        )

    except ValueError as exc:

        if 'Expense_Total' not in str(exc):

            raise AssertionError(
                'Expense leakage error is incorrect.'
            )

        print(
            'Actual expense leakage prevention: PASSED'
        )

        return

    raise AssertionError(
        'Actual future expense was accepted.'
    )


# ==========================================================
# TARGET LEAKAGE TEST
# ==========================================================

def test_future_context_cannot_contain_target():

    print(
        '========== TARGET LEAKAGE TEST =========='
    )

    try:

        create_future_row(
            current_date=START_DATE,
            context={
                'Target_Expense_Total_1D':
                    500.0,
            },
        )

    except ValueError:

        print(
            'Target leakage prevention: PASSED'
        )

        return

    raise AssertionError(
        'Target value was accepted in future context.'
    )


# ==========================================================
# VECTOR TEST
# ==========================================================

def test_forecast_vector():

    print(
        '========== FORECAST VECTOR TEST =========='
    )

    features = {
        'expense_rolling_mean_7':
            95.0,

        'expense_lag_7':
            90.0,

        'expense_lag_1':
            100.0,
    }

    vector = build_forecast_vector(
        features,
        FEATURE_NAMES,
    )

    expected = [
        100.0,
        90.0,
        95.0,
    ]

    if vector != expected:

        raise AssertionError(
            'Forecast vector does not preserve '
            'trained feature order.'
        )

    print(
        'Forecast feature ordering: PASSED'
    )


# ==========================================================
# NON-FINITE FEATURE TEST
# ==========================================================

def test_non_finite_feature():

    print(
        '========== NON-FINITE FEATURE TEST =========='
    )

    features = {
        'expense_lag_1':
            float('nan'),

        'expense_lag_7':
            90.0,

        'expense_rolling_mean_7':
            95.0,
    }

    try:

        build_forecast_vector(
            features,
            FEATURE_NAMES,
        )

    except ValueError:

        print(
            'Non-finite feature handling: PASSED'
        )

        return

    raise AssertionError(
        'Non-finite forecast feature was accepted.'
    )


# ==========================================================
# NON-NUMERIC FEATURE TEST
# ==========================================================

def test_non_numeric_feature():

    print(
        '========== NON-NUMERIC FEATURE TEST =========='
    )

    features = {
        'expense_lag_1':
            'not-a-number',

        'expense_lag_7':
            90.0,

        'expense_rolling_mean_7':
            95.0,
    }

    try:

        build_forecast_vector(
            features,
            FEATURE_NAMES,
        )

    except ValueError:

        print(
            'Non-numeric feature handling: PASSED'
        )

        return

    raise AssertionError(
        'Non-numeric forecast feature was accepted.'
    )


# ==========================================================
# PREDICTION NORMALIZATION TEST
# ==========================================================

def test_prediction_normalization():

    print(
        '========== PREDICTION NORMALIZATION TEST =========='
    )

    model = create_synthetic_model()

    vector = [
        100.0,
        90.0,
        95.0,
    ]

    prediction = generate_forecast_prediction(
        model,
        vector,
    )

    if not isinstance(
        prediction,
        float,
    ):

        raise AssertionError(
            'Forecast prediction was not normalized to float.'
        )

    if not math.isfinite(
        prediction
    ):

        raise AssertionError(
            'Forecast prediction is not finite.'
        )

    print(
        'Prediction normalization: PASSED'
    )


# ==========================================================
# NEGATIVE PREDICTION MODEL
# ==========================================================

class NegativeModel:

    def predict(
        self,
        X,
    ):
        return np.array([
            -500.0
        ])


def test_negative_prediction_clamped():

    print(
        '========== NEGATIVE PREDICTION CLAMP TEST =========='
    )

    prediction = generate_forecast_prediction(
        NegativeModel(),
        [
            100.0,
            90.0,
            95.0,
        ],
    )

    if prediction != 0.0:

        raise AssertionError(
            'Negative expense prediction was not clamped to zero.'
        )

    print(
        'Negative prediction protection: PASSED'
    )


# ==========================================================
# NON-FINITE MODEL OUTPUT
# ==========================================================

class NaNModel:

    def predict(
        self,
        X,
    ):
        return np.array([
            float('nan')
        ])


def test_non_finite_prediction():

    print(
        '========== NON-FINITE PREDICTION TEST =========='
    )

    try:

        generate_forecast_prediction(
            NaNModel(),
            [
                100.0,
                90.0,
                95.0,
            ],
        )

    except ValueError as exc:

        if 'non-finite' not in str(exc):

            raise AssertionError(
                'Non-finite prediction error is incorrect.'
            )

        print(
            'Non-finite prediction handling: PASSED'
        )

        return

    raise AssertionError(
        'Non-finite prediction was accepted.'
    )


# ==========================================================
# HISTORICAL DATA LOADING TEST
# ==========================================================

def test_history_loading():

    print(
        '========== HISTORY LOADING TEST =========='
    )

    historical = create_historical_data()

    with patch(
        'ml.prediction.forecast.get_prepared_dataset',
        return_value=historical,
    ):

        history = load_forecast_history()

    if len(history) != 10:

        raise AssertionError(
            'Historical row count is incorrect.'
        )

    if history[
        0
    ]['Date'] >= history[
        -1
    ]['Date']:

        raise AssertionError(
            'Historical data was not sorted.'
        )

    if history is historical:

        raise AssertionError(
            'Forecast history was not copied.'
        )

    print(
        'Historical data loading: PASSED'
    )


# ==========================================================
# CORE FORECAST TEST
# ==========================================================

def test_forecast_multiple_days():

    print(
        '========== MULTI-DAY FORECAST TEST =========='
    )

    model = create_synthetic_model()

    historical = create_historical_data()

    with patch(
        'ml.prediction.forecast.get_prepared_dataset',
        return_value=historical,
    ):

        results = forecast_expenses(
            model=model,
            feature_names=FEATURE_NAMES,
            start_date=START_DATE,
            days=5,
        )

    if len(results) != 5:

        raise AssertionError(
            'Incorrect number of forecast results.'
        )

    for index, result in enumerate(
        results
    ):

        expected_date = (
            START_DATE
            + timedelta(days=index)
        )

        if result[
            'Date'
        ] != expected_date:

            raise AssertionError(
                'Forecast dates are incorrect.'
            )

        if not isinstance(
            result[
                'Predicted_Expense'
            ],
            float,
        ):

            raise AssertionError(
                'Prediction is not a float.'
            )

        if not math.isfinite(
            result[
                'Predicted_Expense'
            ]
        ):

            raise AssertionError(
                'Prediction is not finite.'
            )

        if result[
            'Predicted_Expense'
        ] < 0:

            raise AssertionError(
                'Expense prediction is negative.'
            )

        if set(
            result['Features'].keys()
        ) != set(
            FEATURE_NAMES
        ):

            raise AssertionError(
                'Forecast result contains incorrect features.'
            )

    print(
        'Multi-day forecasting: PASSED'
    )


# ==========================================================
# RECURSIVE FORECAST TEST
# ==========================================================

def test_recursive_forecasting():

    print(
        '========== RECURSIVE FORECAST TEST =========='
    )

    class CountingModel:

        def __init__(self):
            self.inputs = []

        def predict(
            self,
            X,
        ):
            self.inputs.append(
                list(X[0])
            )

            return np.array([
                100.0
                + len(
                    self.inputs
                ) * 10.0
            ])

    model = CountingModel()

    historical = create_historical_data()

    with patch(
        'ml.prediction.forecast.get_prepared_dataset',
        return_value=historical,
    ):

        results = forecast_expenses(
            model=model,
            feature_names=FEATURE_NAMES,
            start_date=START_DATE,
            days=3,
        )

    if len(
        model.inputs
    ) != 3:

        raise AssertionError(
            'Model was not called once per forecast day.'
        )

    predictions = [
        result[
            'Predicted_Expense'
        ]
        for result in results
    ]

    if predictions != [
        110.0,
        120.0,
        130.0,
    ]:

        raise AssertionError(
            'Recursive predictions were not preserved.'
        )

    print(
        'Recursive forecasting: PASSED'
    )


# ==========================================================
# FUTURE CONTEXT TEST
# ==========================================================

def test_future_context():

    print(
        '========== FUTURE CONTEXT TEST =========='
    )

    class ContextAwareModel:

        def __init__(self):
            self.inputs = []

        def predict(
            self,
            X,
        ):
            self.inputs.append(
                list(X[0])
            )

            return np.array([
                100.0
            ])

    model = ContextAwareModel()

    historical = create_historical_data()

    context = {
        START_DATE: {
            'Stress_Level':
                5.0,

            'Sleep_Hours':
                4.0,

            'Day_Type':
                'Weekend',
        }
    }

    with patch(
        'ml.prediction.forecast.get_prepared_dataset',
        return_value=historical,
    ):

        results = forecast_expenses(
            model=model,
            feature_names=FEATURE_NAMES,
            start_date=START_DATE,
            days=1,
            future_context=context,
        )

    if len(results) != 1:

        raise AssertionError(
            'Future context forecast did not produce a result.'
        )

    print(
        'Future context handling: PASSED'
    )


# ==========================================================
# HISTORY IMMUTABILITY TEST
# ==========================================================

def test_history_is_not_modified():

    print(
        '========== HISTORY IMMUTABILITY TEST =========='
    )

    model = create_synthetic_model()

    historical = create_historical_data()

    original = [
        dict(row)
        for row in historical
    ]

    with patch(
        'ml.prediction.forecast.get_prepared_dataset',
        return_value=historical,
    ):

        forecast_expenses(
            model=model,
            feature_names=FEATURE_NAMES,
            start_date=START_DATE,
            days=5,
        )

    if historical != original:

        raise AssertionError(
            'Original historical data was modified.'
        )

    print(
        'Historical data immutability: PASSED'
    )


# ==========================================================
# FUTURE ACTUAL DATE LEAKAGE TEST
# ==========================================================

def test_future_actual_date_is_not_used():

    print(
        '========== FUTURE ACTUAL DATE LEAKAGE TEST =========='
    )

    model = create_synthetic_model()

    historical = create_historical_data()

    future_actual_row = {
        'Date':
            START_DATE,

        'Day_Type':
            'Workday',

        'Work_Status':
            'Working',

        'Health_Impact':
            'Normal',

        'Travel':
            None,

        'Special_Event':
            None,

        'Stress_Level':
            1.0,

        'Notes':
            None,

        'Sleep_Hours':
            7.0,

        'Social_Activity':
            None,

        'Location':
            'Home',

        'Expense_Total':
            999999.0,

        'Expense_Count':
            99,

        'Income_Total':
            0.0,

        'Income_Count':
            0,

        'Event_Count':
            0,
    }

    historical_with_future = (
        historical
        + [
            future_actual_row
        ]
    )

    captured_rows = []

    def fake_build_feature_row(
        target_row,
        previous_rows,
    ):

        captured_rows.append(
            list(previous_rows)
        )

        return {
            'expense_lag_1':
                100.0,

            'expense_lag_7':
                90.0,

            'expense_rolling_mean_7':
                95.0,
        }

    with patch(
        'ml.prediction.forecast.get_prepared_dataset',
        return_value=historical_with_future,
    ), patch(
        'ml.prediction.forecast.build_feature_row',
        side_effect=fake_build_feature_row,
    ):

        forecast_expenses(
            model=model,
            feature_names=FEATURE_NAMES,
            start_date=START_DATE,
            days=1,
        )

    if not captured_rows:

        raise AssertionError(
            'Feature builder was never called.'
        )

    for row in captured_rows[0]:

        if row['Date'] >= START_DATE:

            raise AssertionError(
                'Future/target-day row leaked into '
                'forecast features.'
            )

        if row.get(
            'Expense_Total'
        ) == 999999.0:

            raise AssertionError(
                'Actual future expense leaked into '
                'forecast features.'
            )

    print(
        'Future actual leakage prevention: PASSED'
    )


# ==========================================================
# RECURSIVE TEMPORARY HISTORY TEST
# ==========================================================

def test_predictions_become_temporary_history():

    print(
        '========== TEMPORARY HISTORY TEST =========='
    )

    model = create_synthetic_model()

    historical = create_historical_data()

    captured_previous_rows = []

    def fake_build_feature_row(
        target_row,
        previous_rows,
    ):

        captured_previous_rows.append(
            [
                dict(row)
                for row in previous_rows
            ]
        )

        return {
            'expense_lag_1':
                100.0,

            'expense_lag_7':
                90.0,

            'expense_rolling_mean_7':
                95.0,
        }

    with patch(
        'ml.prediction.forecast.get_prepared_dataset',
        return_value=historical,
    ), patch(
        'ml.prediction.forecast.build_feature_row',
        side_effect=fake_build_feature_row,
    ):

        results = forecast_expenses(
            model=model,
            feature_names=FEATURE_NAMES,
            start_date=START_DATE,
            days=3,
        )

    if len(
        captured_previous_rows
    ) != 3:

        raise AssertionError(
            'Feature builder was not called for every day.'
        )

    first_predictions = [
        result[
            'Predicted_Expense'
        ]
        for result in results
    ]

    second_day_history = (
        captured_previous_rows[1]
    )

    third_day_history = (
        captured_previous_rows[2]
    )

    if not any(
        row.get(
            'Expense_Total'
        ) == first_predictions[0]
        for row in second_day_history
    ):

        raise AssertionError(
            'First prediction was not added to '
            'temporary history.'
        )

    if not any(
        row.get(
            'Expense_Total'
        ) == first_predictions[1]
        for row in third_day_history
    ):

        raise AssertionError(
            'Second prediction was not added to '
            'temporary history.'
        )

    print(
        'Temporary recursive history: PASSED'
    )


# ==========================================================
# RESULT STRUCTURE TEST
# ==========================================================

def test_result_structure():

    print(
        '========== RESULT STRUCTURE TEST =========='
    )

    model = create_synthetic_model()

    historical = create_historical_data()

    with patch(
        'ml.prediction.forecast.get_prepared_dataset',
        return_value=historical,
    ):

        results = forecast_expenses(
            model=model,
            feature_names=FEATURE_NAMES,
            start_date=START_DATE,
            days=1,
        )

    required_keys = {
        'Date',
        'Predicted_Expense',
        'Features',
    }

    if not required_keys.issubset(
        results[0].keys()
    ):

        raise AssertionError(
            'Forecast result is missing required fields.'
        )

    print(
        'Forecast result structure: PASSED'
    )


# ==========================================================
# FULL INTEGRATION TEST
# ==========================================================

def test_full_forecast_integration():

    print(
        '========== FULL FORECAST INTEGRATION TEST =========='
    )

    model = create_synthetic_model()

    historical = create_historical_data()

    context = {
        START_DATE: {
            'Day_Type':
                'Weekend',

            'Stress_Level':
                2.0,

            'Sleep_Hours':
                8.0,
        },

        START_DATE + timedelta(days=1): {
            'Day_Type':
                'Workday',

            'Stress_Level':
                3.0,

            'Sleep_Hours':
                6.0,
        },
    }

    with patch(
        'ml.prediction.forecast.get_prepared_dataset',
        return_value=historical,
    ):

        results = forecast_expenses(
            model=model,
            feature_names=FEATURE_NAMES,
            start_date=START_DATE,
            days=2,
            future_context=context,
        )

    if len(results) != 2:

        raise AssertionError(
            'Integration forecast returned incorrect '
            'number of results.'
        )

    for result in results:

        if not math.isfinite(
            result[
                'Predicted_Expense'
            ]
        ):

            raise AssertionError(
                'Integration prediction is not finite.'
            )

        if result[
            'Predicted_Expense'
        ] < 0:

            raise AssertionError(
                'Integration prediction is negative.'
            )

        if len(
            result['Features']
        ) != len(
            FEATURE_NAMES
        ):

            raise AssertionError(
                'Integration feature count is incorrect.'
            )

    print(
        'Forecast integration: PASSED'
    )


# ==========================================================
# TEST RUNNER
# ==========================================================

def run_all_tests():

    print()
    print(
        '=================================================='
    )
    print(
        '       STRONG FORECAST TEST SUITE'
    )
    print(
        '=================================================='
    )

    # ------------------------------------------------------
    # Input validation
    # ------------------------------------------------------

    test_invalid_model()

    test_model_without_predict()

    test_invalid_feature_names()

    test_empty_feature_names()

    test_forbidden_date_feature()

    test_forbidden_target_feature()

    test_invalid_start_date()

    test_invalid_days()

    test_boolean_days()

    test_invalid_future_context()

    # ------------------------------------------------------
    # Future row
    # ------------------------------------------------------

    test_future_row()

    test_future_context_cannot_contain_actual_expense()

    test_future_context_cannot_contain_target()

    # ------------------------------------------------------
    # Feature vector
    # ------------------------------------------------------

    test_forecast_vector()

    test_non_finite_feature()

    test_non_numeric_feature()

    # ------------------------------------------------------
    # Prediction
    # ------------------------------------------------------

    test_prediction_normalization()

    test_negative_prediction_clamped()

    test_non_finite_prediction()

    # ------------------------------------------------------
    # Historical data
    # ------------------------------------------------------

    test_history_loading()

    test_history_is_not_modified()

    # ------------------------------------------------------
    # Forecasting
    # ------------------------------------------------------

    test_forecast_multiple_days()

    test_recursive_forecasting()

    test_future_context()

    # ------------------------------------------------------
    # Leakage protection
    # ------------------------------------------------------

    test_future_actual_date_is_not_used()

    test_predictions_become_temporary_history()

    # ------------------------------------------------------
    # Result
    # ------------------------------------------------------

    test_result_structure()

    # ------------------------------------------------------
    # Integration
    # ------------------------------------------------------

    test_full_forecast_integration()

    print()
    print(
        '=================================================='
    )
    print(
        '       ALL FORECAST TESTS PASSED'
    )
    print(
        '=================================================='
    )


# ==========================================================
# MAIN
# ==========================================================

if __name__ == '__main__':

    run_all_tests()
