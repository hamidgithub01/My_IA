import math
from unittest.mock import patch

import numpy as np
from sklearn.linear_model import LinearRegression

from ml.prediction.predict import (
    build_prediction_vector,
    predict,
    predict_expense,
    validate_feature_value,
    validate_prediction_features,
)


# ==========================================================
# CONSTANTS
# ==========================================================

DAILY_HORIZONS = {
    '1D': 1,
    '2D': 2,
    '3D': 3,
    '4D': 4,
    '5D': 5,
    '6D': 6,
    '7D': 7,
}

PERIOD_HORIZONS = {
    '8_15D': (8, 15),
    '16_30D': (16, 30),
    '30D': (1, 30),
}

ALL_HORIZONS = [
    *DAILY_HORIZONS.keys(),
    *PERIOD_HORIZONS.keys(),
]


FEATURE_NAMES = [
    'expense_lag_1',
    'expense_lag_7',
    'expense_rolling_mean_7',
]


MODEL_HISTORY_ID = 101


# ==========================================================
# SYNTHETIC MODEL FACTORY
# ==========================================================

def create_synthetic_model(
    offset=10.0,
):
    """
    Create a deterministic synthetic regression model.

    Formula:

        y =
            0.5 * expense_lag_1
            + 0.3 * expense_lag_7
            + 0.2 * expense_rolling_mean_7
            + offset

    This model is completely synthetic.

    No database is used.
    """

    X = np.array([
        [100.0, 90.0, 95.0],
        [120.0, 100.0, 110.0],
        [140.0, 120.0, 130.0],
        [160.0, 140.0, 150.0],
        [180.0, 160.0, 170.0],
    ])

    y = np.array([
        87.0 + offset - 10.0,
        104.0 + offset - 10.0,
        121.0 + offset - 10.0,
        138.0 + offset - 10.0,
        155.0 + offset - 10.0,
    ])

    model = LinearRegression()

    model.fit(
        X,
        y,
    )

    return model


# ==========================================================
# SYNTHETIC MODEL INFO
# ==========================================================

def create_synthetic_model_info(
    target_name='Target_Expense_Total_1D',
    model_history_id=MODEL_HISTORY_ID,
    offset=10.0,
):
    """
    Build the same structure expected by predict().
    """

    return {
        'model':
            create_synthetic_model(
                offset=offset
            ),

        'feature_names':
            FEATURE_NAMES.copy(),

        'training_rows':
            5,

        'target_name':
            target_name,

        'model_history_id':
            model_history_id,
    }


# ==========================================================
# VALID PREDICTION DATA
# ==========================================================

def create_valid_prediction_data():
    return {
        'expense_lag_1':
            100.0,

        'expense_lag_7':
            90.0,

        'expense_rolling_mean_7':
            95.0,
    }


# ==========================================================
# FEATURE VALIDATION
# ==========================================================

def test_validate_prediction_features():

    print(
        '========== FEATURE VALIDATION TEST =========='
    )

    data = create_valid_prediction_data()

    result = validate_prediction_features(
        data,
        FEATURE_NAMES,
    )

    if result is not True:
        raise AssertionError(
            'Valid prediction features were rejected.'
        )

    print(
        'Feature validation: PASSED'
    )


# ==========================================================
# FEATURE NAMES TYPE TEST
# ==========================================================

def test_invalid_feature_names_type():

    print(
        '========== INVALID FEATURE NAMES TYPE TEST =========='
    )

    data = create_valid_prediction_data()

    try:

        validate_prediction_features(
            data,
            tuple(FEATURE_NAMES),
        )

    except TypeError:

        print(
            'Invalid feature names type handling: PASSED'
        )

        return

    raise AssertionError(
        'Non-list feature names were accepted.'
    )


# ==========================================================
# MISSING FEATURE TEST
# ==========================================================

def test_missing_feature():

    print(
        '========== MISSING FEATURE TEST =========='
    )

    data = create_valid_prediction_data()

    del data[
        'expense_lag_7'
    ]

    try:

        validate_prediction_features(
            data,
            FEATURE_NAMES,
        )

    except ValueError as exc:

        if 'expense_lag_7' not in str(exc):

            raise AssertionError(
                'Missing feature error does not '
                'identify the missing feature.'
            )

        print(
            'Missing feature handling: PASSED'
        )

        return

    raise AssertionError(
        'Missing feature was not rejected.'
    )


# ==========================================================
# INVALID DATA TYPE TEST
# ==========================================================

def test_invalid_prediction_data_type():

    print(
        '========== INVALID PREDICTION DATA TEST =========='
    )

    try:

        validate_prediction_features(
            [],
            FEATURE_NAMES,
        )

    except TypeError:

        print(
            'Invalid prediction data handling: PASSED'
        )

        return

    raise AssertionError(
        'Invalid prediction data type was accepted.'
    )


# ==========================================================
# EMPTY FEATURE LIST TEST
# ==========================================================

def test_empty_feature_names():

    print(
        '========== EMPTY FEATURE NAMES TEST =========='
    )

    try:

        validate_prediction_features(
            {},
            [],
        )

    except ValueError:

        print(
            'Empty feature list handling: PASSED'
        )

        return

    raise AssertionError(
        'Empty feature list was accepted.'
    )


# ==========================================================
# FORBIDDEN DATE FEATURE TEST
# ==========================================================

def test_forbidden_date_feature():

    print(
        '========== FORBIDDEN DATE FEATURE TEST =========='
    )

    feature_names = [
        'expense_lag_1',
        'Date',
    ]

    data = {
        'expense_lag_1':
            100.0,

        'Date':
            '2026-08-17',
    }

    try:

        validate_prediction_features(
            data,
            feature_names,
        )

    except ValueError as exc:

        if 'Date' not in str(exc):

            raise AssertionError(
                'Forbidden Date feature was not '
                'identified correctly.'
            )

        print(
            'Forbidden Date feature handling: PASSED'
        )

        return

    raise AssertionError(
        'Date was incorrectly accepted as a model feature.'
    )


# ==========================================================
# FORBIDDEN TARGET FEATURE TEST
# ==========================================================

def test_forbidden_target_feature():

    print(
        '========== FORBIDDEN TARGET FEATURE TEST =========='
    )

    feature_names = [
        'expense_lag_1',
        'Target_Expense_Total_1D',
    ]

    data = {
        'expense_lag_1':
            100.0,

        'Target_Expense_Total_1D':
            120.0,
    }

    try:

        validate_prediction_features(
            data,
            feature_names,
        )

    except ValueError as exc:

        if 'Target_Expense_Total_1D' not in str(exc):

            raise AssertionError(
                'Forbidden target feature was not '
                'identified correctly.'
            )

        print(
            'Forbidden target feature handling: PASSED'
        )

        return

    raise AssertionError(
        'Target feature was incorrectly accepted.'
    )


# ==========================================================
# BOOLEAN FEATURE TEST
# ==========================================================

def test_boolean_feature():

    print(
        '========== BOOLEAN FEATURE TEST =========='
    )

    try:

        validate_feature_value(
            'expense_lag_1',
            True,
        )

    except ValueError:

        print(
            'Boolean feature handling: PASSED'
        )

        return

    raise AssertionError(
        'Boolean feature was incorrectly accepted.'
    )


# ==========================================================
# NON-NUMERIC FEATURE TEST
# ==========================================================

def test_non_numeric_feature():

    print(
        '========== NON-NUMERIC FEATURE TEST =========='
    )

    try:

        validate_feature_value(
            'expense_lag_1',
            'not-a-number',
        )

    except ValueError:

        print(
            'Non-numeric feature handling: PASSED'
        )

        return

    raise AssertionError(
        'Non-numeric feature was incorrectly accepted.'
    )


# ==========================================================
# NUMERIC STRING TEST
# ==========================================================

def test_numeric_string():

    print(
        '========== NUMERIC STRING TEST =========='
    )

    value = validate_feature_value(
        'expense_lag_1',
        '125.5',
    )

    if not isinstance(
        value,
        float,
    ):

        raise AssertionError(
            'Numeric string was not converted to float.'
        )

    if value != 125.5:

        raise AssertionError(
            'Numeric string conversion produced '
            'an incorrect value.'
        )

    print(
        'Numeric string conversion: PASSED'
    )


# ==========================================================
# NAN FEATURE TEST
# ==========================================================

def test_nan_feature():

    print(
        '========== NAN FEATURE TEST =========='
    )

    try:

        validate_feature_value(
            'expense_lag_1',
            float('nan'),
        )

    except ValueError:

        print(
            'NaN feature handling: PASSED'
        )

        return

    raise AssertionError(
        'NaN feature was incorrectly accepted.'
    )


# ==========================================================
# INFINITE FEATURE TEST
# ==========================================================

def test_infinite_feature():

    print(
        '========== INFINITE FEATURE TEST =========='
    )

    try:

        validate_feature_value(
            'expense_lag_1',
            float('inf'),
        )

    except ValueError:

        print(
            'Infinite feature handling: PASSED'
        )

        return

    raise AssertionError(
        'Infinite feature was incorrectly accepted.'
    )


# ==========================================================
# NEGATIVE FEATURE TEST
# ==========================================================

def test_negative_feature():

    print(
        '========== NEGATIVE FEATURE TEST =========='
    )

    value = validate_feature_value(
        'expense_lag_1',
        -100.0,
    )

    if value != -100.0:

        raise AssertionError(
            'Valid negative numeric feature was rejected '
            'or modified.'
        )

    print(
        'Negative feature handling: PASSED'
    )


# ==========================================================
# FEATURE ORDER TEST
# ==========================================================

def test_feature_order():

    print(
        '========== FEATURE ORDER TEST =========='
    )

    data = {
        'expense_rolling_mean_7':
            95.0,

        'expense_lag_7':
            90.0,

        'expense_lag_1':
            100.0,
    }

    vector = build_prediction_vector(
        data,
        FEATURE_NAMES,
    )

    expected = [
        100.0,
        90.0,
        95.0,
    ]

    if vector != expected:

        raise AssertionError(
            'Prediction vector does not preserve '
            'the trained feature order.'
        )

    print(
        'Feature ordering: PASSED'
    )


# ==========================================================
# EXTRA FEATURES TEST
# ==========================================================

def test_extra_features():

    print(
        '========== EXTRA FEATURES TEST =========='
    )

    data = create_valid_prediction_data()

    data[
        'Date'
    ] = '2026-08-17'

    data[
        'some_unused_value'
    ] = 999.0

    vector = build_prediction_vector(
        data,
        FEATURE_NAMES,
    )

    if len(vector) != len(
        FEATURE_NAMES
    ):

        raise AssertionError(
            'Extra input features changed '
            'the prediction vector size.'
        )

    print(
        'Extra feature handling: PASSED'
    )


# ==========================================================
# MODEL PREDICTION TEST
# ==========================================================

def test_prediction():

    print(
        '========== MODEL PREDICTION TEST =========='
    )

    model_info = create_synthetic_model_info()

    data = create_valid_prediction_data()

    with patch(
        'ml.prediction.predict.load_latest_model',
        return_value=model_info,
    ):

        result = predict(
            data
        )

    if not isinstance(
        result,
        dict,
    ):

        raise AssertionError(
            'Prediction did not return a dictionary.'
        )

    if 'prediction' not in result:

        raise AssertionError(
            'Prediction result contains no prediction.'
        )

    if not isinstance(
        result['prediction'],
        float,
    ):

        raise AssertionError(
            'Prediction is not a float.'
        )

    if not math.isfinite(
        result['prediction']
    ):

        raise AssertionError(
            'Prediction is not finite.'
        )

    print(
        'Model prediction: PASSED'
    )


# ==========================================================
# TARGET NAME PRESERVATION TEST
# ==========================================================

def test_target_name_preservation():

    print(
        '========== TARGET NAME PRESERVATION TEST =========='
    )

    model_info = create_synthetic_model_info(
        target_name='Target_Travel_Day_7D'
    )

    data = create_valid_prediction_data()

    with patch(
        'ml.prediction.predict.load_latest_model',
        return_value=model_info,
    ):

        result = predict(
            data
        )

    if result[
        'target_name'
    ] != 'Target_Travel_Day_7D':

        raise AssertionError(
            'Target name was not preserved.'
        )

    print(
        'Target name preservation: PASSED'
    )


# ==========================================================
# MODEL HISTORY ID TEST
# ==========================================================

def test_model_history_id():

    print(
        '========== MODEL HISTORY ID TEST =========='
    )

    model_info = create_synthetic_model_info(
        model_history_id=987
    )

    data = create_valid_prediction_data()

    with patch(
        'ml.prediction.predict.load_latest_model',
        return_value=model_info,
    ):

        result = predict(
            data
        )

    if result[
        'model_history_id'
    ] != 987:

        raise AssertionError(
            'Model history ID was not preserved.'
        )

    print(
        'Model history ID preservation: PASSED'
    )


# ==========================================================
# FEATURE COUNT TEST
# ==========================================================

def test_feature_count():

    print(
        '========== FEATURE COUNT TEST =========='
    )

    model_info = create_synthetic_model_info()

    data = create_valid_prediction_data()

    with patch(
        'ml.prediction.predict.load_latest_model',
        return_value=model_info,
    ):

        result = predict(
            data
        )

    if result[
        'feature_count'
    ] != len(FEATURE_NAMES):

        raise AssertionError(
            'Feature count was not preserved.'
        )

    print(
        'Feature count preservation: PASSED'
    )


# ==========================================================
# PREDICTION PRESERVATION TEST
# ==========================================================

def test_prediction_preservation():

    print(
        '========== PREDICTION PRESERVATION TEST =========='
    )

    model_info = create_synthetic_model_info()

    data = create_valid_prediction_data()

    model = model_info[
        'model'
    ]

    vector = build_prediction_vector(
        data,
        FEATURE_NAMES,
    )

    expected_prediction = float(
        model.predict([
            vector
        ])[0]
    )

    with patch(
        'ml.prediction.predict.load_latest_model',
        return_value=model_info,
    ):

        result = predict(
            data
        )

    actual_prediction = result[
        'prediction'
    ]

    if abs(
        expected_prediction
        - actual_prediction
    ) > 1e-10:

        raise AssertionError(
            'Prediction does not match '
            'the model output.'
        )

    print(
        'Prediction preservation: PASSED'
    )

    print(
        f'Expected prediction: '
        f'{expected_prediction}'
    )

    print(
        f'Actual prediction: '
        f'{actual_prediction}'
    )


# ==========================================================
# NON-FINITE MODEL OUTPUT TEST
# ==========================================================

class NonFiniteModel:

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

    model_info = create_synthetic_model_info()

    model_info[
        'model'
    ] = NonFiniteModel()

    data = create_valid_prediction_data()

    with patch(
        'ml.prediction.predict.load_latest_model',
        return_value=model_info,
    ):

        try:

            predict(
                data
            )

        except ValueError as exc:

            if 'non-finite prediction' not in str(exc):

                raise AssertionError(
                    'Non-finite prediction error '
                    'message is incorrect.'
                )

            print(
                'Non-finite prediction handling: PASSED'
            )

            return

    raise AssertionError(
        'Non-finite model output was accepted.'
    )


# ==========================================================
# NEGATIVE PREDICTION TEST
# ==========================================================

class NegativeModel:

    def predict(
        self,
        X,
    ):
        return np.array([
            -50.0
        ])


def test_negative_prediction_is_preserved():

    print(
        '========== NEGATIVE PREDICTION TEST =========='
    )

    model_info = create_synthetic_model_info(
        target_name='Target_Balance_1D'
    )

    model_info[
        'model'
    ] = NegativeModel()

    data = create_valid_prediction_data()

    with patch(
        'ml.prediction.predict.load_latest_model',
        return_value=model_info,
    ):

        result = predict(
            data
        )

    if result[
        'prediction'
    ] != -50.0:

        raise AssertionError(
            'Negative prediction was incorrectly '
            'clamped or modified.'
        )

    print(
        'Negative prediction preservation: PASSED'
    )


# ==========================================================
# ALL HORIZONS TEST
# ==========================================================

def test_all_horizons():

    print(
        '========== ALL HORIZONS TEST =========='
    )

    data = create_valid_prediction_data()

    predictions = {}

    for index, horizon in enumerate(
        ALL_HORIZONS,
        start=1,
    ):

        target_name = (
            f'Target_Expense_Total_{horizon}'
        )

        model_info = create_synthetic_model_info(
            target_name=target_name,
            model_history_id=100 + index,
            offset=float(index),
        )

        with patch(
            'ml.prediction.predict.load_latest_model',
            return_value=model_info,
        ):

            result = predict(
                data
            )

        if result[
            'target_name'
        ] != target_name:

            raise AssertionError(
                f'{horizon}: target name mismatch.'
            )

        if result[
            'model_history_id'
        ] != 100 + index:

            raise AssertionError(
                f'{horizon}: model history ID mismatch.'
            )

        if not math.isfinite(
            result['prediction']
        ):

            raise AssertionError(
                f'{horizon}: prediction is not finite.'
            )

        predictions[
            horizon
        ] = result[
            'prediction'
        ]

        print(
            f'{horizon}: PASSED'
        )

    if set(
        predictions.keys()
    ) != set(
        ALL_HORIZONS
    ):

        raise AssertionError(
            'Not all horizons produced predictions.'
        )

    print(
        'All horizon predictions: PASSED'
    )


# ==========================================================
# HORIZON SEPARATION TEST
# ==========================================================

def test_horizon_separation():

    print(
        '========== HORIZON SEPARATION TEST =========='
    )

    data = create_valid_prediction_data()

    results = {}

    for index, horizon in enumerate(
        ALL_HORIZONS,
        start=1,
    ):

        target_name = (
            f'Target_Expense_Total_{horizon}'
        )

        model_info = create_synthetic_model_info(
            target_name=target_name,
            model_history_id=200 + index,
            offset=float(index),
        )

        with patch(
            'ml.prediction.predict.load_latest_model',
            return_value=model_info,
        ):

            result = predict(
                data
            )

        results[
            horizon
        ] = result[
            'prediction'
        ]

    unique_predictions = set(
        results.values()
    )

    if len(unique_predictions) != len(
        ALL_HORIZONS
    ):

        raise AssertionError(
            'Different horizons were not kept '
            'independent in the synthetic test.'
        )

    for horizon in ALL_HORIZONS:

        print(
            f'{horizon}: '
            f'{results[horizon]}'
        )

    print(
        'Horizon separation: PASSED'
    )


# ==========================================================
# DAILY HORIZON STRUCTURE TEST
# ==========================================================

def test_daily_horizon_structure():

    print(
        '========== DAILY HORIZON STRUCTURE TEST =========='
    )

    expected = [
        '1D',
        '2D',
        '3D',
        '4D',
        '5D',
        '6D',
        '7D',
    ]

    actual = list(
        DAILY_HORIZONS.keys()
    )

    if actual != expected:

        raise AssertionError(
            'Daily horizon structure is incorrect.'
        )

    if list(
        DAILY_HORIZONS.values()
    ) != [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
    ]:

        raise AssertionError(
            'Daily horizons do not map to '
            'the correct future days.'
        )

    print(
        'Daily horizon structure: PASSED'
    )


# ==========================================================
# PERIOD HORIZON STRUCTURE TEST
# ==========================================================

def test_period_horizon_structure():

    print(
        '========== PERIOD HORIZON STRUCTURE TEST =========='
    )

    expected = {
        '8_15D':
            (8, 15),

        '16_30D':
            (16, 30),

        '30D':
            (1, 30),
    }

    if PERIOD_HORIZONS != expected:

        raise AssertionError(
            'Period horizon structure is incorrect.'
        )

    print(
        '8_15D: T+8 -> T+15'
    )

    print(
        '16_30D: T+16 -> T+30'
    )

    print(
        '30D: T+1 -> T+30'
    )

    print(
        'Period horizon structure: PASSED'
    )


# ==========================================================
# HORIZON UNIQUENESS TEST
# ==========================================================

def test_horizon_uniqueness():

    print(
        '========== HORIZON UNIQUENESS TEST =========='
    )

    if len(
        ALL_HORIZONS
    ) != len(
        set(ALL_HORIZONS)
    ):

        raise AssertionError(
            'Duplicate horizons detected.'
        )

    if len(
        ALL_HORIZONS
    ) != 10:

        raise AssertionError(
            'Expected exactly 10 horizons.'
        )

    print(
        'Horizon uniqueness: PASSED'
    )


# ==========================================================
# TARGET HORIZON NAMING TEST
# ==========================================================

def test_target_horizon_naming():

    print(
        '========== TARGET HORIZON NAMING TEST =========='
    )

    for horizon in ALL_HORIZONS:

        target_name = (
            f'Target_Travel_Day_{horizon}'
        )

        if not target_name.endswith(
            f'_{horizon}'
        ):

            raise AssertionError(
                f'Invalid target naming for {horizon}.'
            )

    print(
        'Target horizon naming: PASSED'
    )


# ==========================================================
# BACKWARD COMPATIBILITY TEST
# ==========================================================

def test_predict_expense():

    print(
        '========== PREDICT EXPENSE WRAPPER TEST =========='
    )

    model_info = create_synthetic_model_info(
        target_name='Target_Expense_Total_1D'
    )

    data = create_valid_prediction_data()

    with patch(
        'ml.prediction.predict.load_latest_model',
        return_value=model_info,
    ):

        result = predict_expense(
            data
        )

    if result[
        'target_name'
    ] != 'Target_Expense_Total_1D':

        raise AssertionError(
            'predict_expense did not preserve '
            'the model target.'
        )

    if 'prediction' not in result:

        raise AssertionError(
            'predict_expense returned no prediction.'
        )

    print(
        'Backward-compatible prediction wrapper: PASSED'
    )


# ==========================================================
# NO MODEL TEST
# ==========================================================

def test_no_model():

    print(
        '========== NO MODEL TEST =========='
    )

    data = create_valid_prediction_data()

    with patch(
        'ml.prediction.predict.load_latest_model',
        return_value=None,
    ):

        try:

            predict(
                data
            )

        except ValueError as exc:

            if 'No trained model' not in str(exc):

                raise AssertionError(
                    'No-model error message is incorrect.'
                )

            print(
                'No-model handling: PASSED'
            )

            return

    raise AssertionError(
        'Prediction did not fail when no model existed.'
    )


# ==========================================================
# INVALID MODEL TEST
# ==========================================================

def test_invalid_loaded_model():

    print(
        '========== INVALID LOADED MODEL TEST =========='
    )

    invalid_model_info = {
        'model':
            None,

        'feature_names':
            FEATURE_NAMES.copy(),

        'target_name':
            'Target_Expense_Total_1D',

        'model_history_id':
            MODEL_HISTORY_ID,
    }

    data = create_valid_prediction_data()

    with patch(
        'ml.prediction.predict.load_latest_model',
        return_value=invalid_model_info,
    ):

        try:

            predict(
                data
            )

        except ValueError as exc:

            if 'Loaded model is missing' not in str(exc):

                raise AssertionError(
                    'Invalid model error message '
                    'is incorrect.'
                )

            print(
                'Invalid loaded model handling: PASSED'
            )

            return

    raise AssertionError(
        'Invalid loaded model was accepted.'
    )


# ==========================================================
# MISSING TARGET TEST
# ==========================================================

def test_missing_target_name():

    print(
        '========== MISSING TARGET NAME TEST =========='
    )

    model_info = create_synthetic_model_info()

    model_info[
        'target_name'
    ] = None

    data = create_valid_prediction_data()

    with patch(
        'ml.prediction.predict.load_latest_model',
        return_value=model_info,
    ):

        try:

            predict(
                data
            )

        except ValueError as exc:

            if 'target name' not in str(exc):

                raise AssertionError(
                    'Missing target name was not '
                    'handled correctly.'
                )

            print(
                'Missing target name handling: PASSED'
            )

            return

    raise AssertionError(
        'Model without target name was accepted.'
    )


# ==========================================================
# MISSING FEATURE NAMES IN MODEL TEST
# ==========================================================

def test_missing_model_feature_names():

    print(
        '========== MISSING MODEL FEATURES TEST =========='
    )

    model_info = create_synthetic_model_info()

    model_info[
        'feature_names'
    ] = []

    data = create_valid_prediction_data()

    with patch(
        'ml.prediction.predict.load_latest_model',
        return_value=model_info,
    ):

        try:

            predict(
                data
            )

        except ValueError as exc:

            if 'no feature names' not in str(exc):

                raise AssertionError(
                    'Missing model feature names '
                    'were not handled correctly.'
                )

            print(
                'Missing model feature handling: PASSED'
            )

            return

    raise AssertionError(
        'Model without feature names was accepted.'
    )


# ==========================================================
# MODEL OUTPUT TYPE TEST
# ==========================================================

class IntegerOutputModel:

    def predict(
        self,
        X,
    ):
        return np.array([
            123
        ])


def test_prediction_output_normalization():

    print(
        '========== PREDICTION OUTPUT NORMALIZATION TEST =========='
    )

    model_info = create_synthetic_model_info()

    model_info[
        'model'
    ] = IntegerOutputModel()

    data = create_valid_prediction_data()

    with patch(
        'ml.prediction.predict.load_latest_model',
        return_value=model_info,
    ):

        result = predict(
            data
        )

    if not isinstance(
        result['prediction'],
        float,
    ):

        raise AssertionError(
            'Prediction was not normalized to float.'
        )

    if result[
        'prediction'
    ] != 123.0:

        raise AssertionError(
            'Prediction normalization produced '
            'an incorrect value.'
        )

    print(
        'Prediction output normalization: PASSED'
    )


# ==========================================================
# NEGATIVE PREDICTION PRESERVATION
# ==========================================================

class NegativeBalanceModel:

    def predict(
        self,
        X,
    ):
        return np.array([
            -250.75
        ])


def test_negative_prediction_preservation():

    print(
        '========== NEGATIVE PREDICTION PRESERVATION TEST =========='
    )

    model_info = create_synthetic_model_info(
        target_name='Target_Balance_1D'
    )

    model_info[
        'model'
    ] = NegativeBalanceModel()

    data = create_valid_prediction_data()

    with patch(
        'ml.prediction.predict.load_latest_model',
        return_value=model_info,
    ):

        result = predict(
            data
        )

    if result[
        'prediction'
    ] != -250.75:

        raise AssertionError(
            'Negative balance prediction was '
            'incorrectly clamped or modified.'
        )

    print(
        'Negative prediction preservation: PASSED'
    )


# ==========================================================
# FULL INTEGRATION TEST
# ==========================================================

def test_full_prediction_integration():

    print(
        '========== FULL PREDICTION INTEGRATION TEST =========='
    )

    model_info = create_synthetic_model_info(
        target_name='Target_Expense_Total_30D',
        model_history_id=555,
    )

    data = create_valid_prediction_data()

    with patch(
        'ml.prediction.predict.load_latest_model',
        return_value=model_info,
    ):

        result = predict(
            data
        )

    required_keys = {
        'prediction',
        'target_name',
        'model_history_id',
        'feature_count',
    }

    if not required_keys.issubset(
        result.keys()
    ):

        raise AssertionError(
            'Prediction result is missing '
            'required fields.'
        )

    if result[
        'target_name'
    ] != 'Target_Expense_Total_30D':

        raise AssertionError(
            'Integration target mismatch.'
        )

    if result[
        'model_history_id'
    ] != 555:

        raise AssertionError(
            'Integration model history ID mismatch.'
        )

    if result[
        'feature_count'
    ] != len(FEATURE_NAMES):

        raise AssertionError(
            'Integration feature count mismatch.'
        )

    if not math.isfinite(
        result['prediction']
    ):

        raise AssertionError(
            'Integration prediction is not finite.'
        )

    print(
        'Prediction integration: PASSED'
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
        '       STRONG PREDICTION TEST SUITE'
    )
    print(
        '=================================================='
    )

    # ------------------------------------------------------
    # Feature validation
    # ------------------------------------------------------

    test_validate_prediction_features()

    test_invalid_feature_names_type()

    test_missing_feature()

    test_invalid_prediction_data_type()

    test_empty_feature_names()

    test_forbidden_date_feature()

    test_forbidden_target_feature()

    # ------------------------------------------------------
    # Feature values
    # ------------------------------------------------------

    test_boolean_feature()

    test_non_numeric_feature()

    test_numeric_string()

    test_nan_feature()

    test_infinite_feature()

    test_negative_feature()

    # ------------------------------------------------------
    # Feature vector
    # ------------------------------------------------------

    test_feature_order()

    test_extra_features()

    # ------------------------------------------------------
    # Basic prediction
    # ------------------------------------------------------

    test_prediction()

    test_target_name_preservation()

    test_model_history_id()

    test_feature_count()

    test_prediction_preservation()

    # ------------------------------------------------------
    # Prediction safety
    # ------------------------------------------------------

    test_non_finite_prediction()

    test_negative_prediction_preservation()

    test_prediction_output_normalization()

    # ------------------------------------------------------
    # Horizons
    # ------------------------------------------------------

    test_all_horizons()

    test_horizon_separation()

    test_daily_horizon_structure()

    test_period_horizon_structure()

    test_horizon_uniqueness()

    test_target_horizon_naming()

    # ------------------------------------------------------
    # Compatibility
    # ------------------------------------------------------

    test_predict_expense()

    # ------------------------------------------------------
    # Error handling
    # ------------------------------------------------------

    test_no_model()

    test_invalid_loaded_model()

    test_missing_target_name()

    test_missing_model_feature_names()

    # ------------------------------------------------------
    # Integration
    # ------------------------------------------------------

    test_full_prediction_integration()

    print()
    print(
        '=================================================='
    )
    print(
        '       ALL PREDICTION TESTS PASSED'
    )
    print(
        '=================================================='
    )


# ==========================================================
# MAIN
# ==========================================================

if __name__ == '__main__':

    run_all_tests()