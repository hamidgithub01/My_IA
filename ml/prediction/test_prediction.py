
import math
from unittest.mock import patch

import numpy as np

from ml.models.registry import REGISTRY_VALID

from ml.prediction.predict import (
    PREDICTION_INVALID,
    PREDICTION_MODEL_NOT_FOUND,
    PREDICTION_VALID,
    _validate_features,
    _validate_numeric_feature,
    validate_feature_schema,
    build_feature_vector,
    load_latest_registered_model,
    predict_from_registered_model,
    predict,
)


# ==========================================================
# CONSTANTS
# ==========================================================

TARGET_NAME = 'Target_Expense_Total_1D'

MODEL_VERSION = 'v1'

FEATURE_NAMES = [
    'expense_lag_1',
    'expense_lag_7',
    'expense_rolling_mean_7',
]


# ==========================================================
# SYNTHETIC MODEL
# ==========================================================

class SyntheticRegressionModel:

    def predict(
        self,
        X,
    ):
        """
        Deterministic synthetic regression model.

        Formula:

            prediction =
                0.5 * feature_1
                + 0.3 * feature_2
                + 0.2 * feature_3
                + 10
        """

        row = X[0]

        return np.array([
            (
                0.5 * row[0]
                + 0.3 * row[1]
                + 0.2 * row[2]
                + 10.0
            )
        ])


# ==========================================================
# VALID FEATURES
# ==========================================================

def create_valid_features():

    return {
        'expense_lag_1':
            100.0,

        'expense_lag_7':
            90.0,

        'expense_rolling_mean_7':
            95.0,
    }


# ==========================================================
# VALID MODEL METADATA
# ==========================================================

def create_valid_metadata():

    return {
        'feature_names':
            FEATURE_NAMES.copy(),

        'target_name':
            TARGET_NAME,

        'target_task':
            'forecast',

        'target_type':
            'continuous',

        'model_type':
            'regression',

        'algorithm':
            'SyntheticRegressionModel',

        'trained_at':
            '2026-08-17T00:00:00',
    }


# ==========================================================
# VALID REGISTERED MODEL
# ==========================================================

def create_valid_model_info():

    metadata = create_valid_metadata()

    return {
        'status':
            PREDICTION_VALID,

        'target_name':
            TARGET_NAME,

        'version':
            MODEL_VERSION,

        'model':
            SyntheticRegressionModel(),

        'metadata':
            metadata,

        'model_path':
            'models/test/model.pkl',

        'metadata_path':
            'models/test/metadata.json',
    }


# ==========================================================
# NUMERIC FEATURE VALIDATION
# ==========================================================

def test_numeric_feature_integer():

    print(
        '========== NUMERIC INTEGER TEST =========='
    )

    result = _validate_numeric_feature(
        100,
        'expense_lag_1',
    )

    if result != 100.0:

        raise AssertionError(
            'Integer feature was not converted to float.'
        )

    if not isinstance(
        result,
        float,
    ):

        raise AssertionError(
            'Integer feature did not become float.'
        )

    print(
        'Numeric integer validation: PASSED'
    )


def test_numeric_feature_float():

    print(
        '========== NUMERIC FLOAT TEST =========='
    )

    result = _validate_numeric_feature(
        125.5,
        'expense_lag_1',
    )

    if result != 125.5:

        raise AssertionError(
            'Float feature was modified.'
        )

    print(
        'Numeric float validation: PASSED'
    )


def test_numeric_feature_string():

    print(
        '========== NUMERIC STRING TEST =========='
    )

    result = _validate_numeric_feature(
        '125.5',
        'expense_lag_1',
    )

    if result != 125.5:

        raise AssertionError(
            'Numeric string was not converted correctly.'
        )

    print(
        'Numeric string validation: PASSED'
    )


def test_numeric_feature_boolean():

    print(
        '========== BOOLEAN FEATURE TEST =========='
    )

    try:

        _validate_numeric_feature(
            True,
            'expense_lag_1',
        )

    except ValueError:

        print(
            'Boolean feature handling: PASSED'
        )

        return

    raise AssertionError(
        'Boolean feature was accepted.'
    )


def test_numeric_feature_none():

    print(
        '========== NONE FEATURE TEST =========='
    )

    try:

        _validate_numeric_feature(
            None,
            'expense_lag_1',
        )

    except ValueError:

        print(
            'None feature handling: PASSED'
        )

        return

    raise AssertionError(
        'None feature was accepted.'
    )


def test_numeric_feature_invalid_string():

    print(
        '========== INVALID STRING FEATURE TEST =========='
    )

    try:

        _validate_numeric_feature(
            'not-a-number',
            'expense_lag_1',
        )

    except ValueError:

        print(
            'Invalid string feature handling: PASSED'
        )

        return

    raise AssertionError(
        'Invalid string feature was accepted.'
    )


def test_numeric_feature_nan():

    print(
        '========== NAN FEATURE TEST =========='
    )

    try:

        _validate_numeric_feature(
            float('nan'),
            'expense_lag_1',
        )

    except ValueError:

        print(
            'NaN feature handling: PASSED'
        )

        return

    raise AssertionError(
        'NaN feature was accepted.'
    )


def test_numeric_feature_infinite():

    print(
        '========== INFINITE FEATURE TEST =========='
    )

    try:

        _validate_numeric_feature(
            float('inf'),
            'expense_lag_1',
        )

    except ValueError:

        print(
            'Infinite feature handling: PASSED'
        )

        return

    raise AssertionError(
        'Infinite feature was accepted.'
    )


def test_numeric_feature_negative():

    print(
        '========== NEGATIVE FEATURE TEST =========='
    )

    result = _validate_numeric_feature(
        -100.0,
        'expense_lag_1',
    )

    if result != -100.0:

        raise AssertionError(
            'Negative numeric feature was modified.'
        )

    print(
        'Negative feature handling: PASSED'
    )


# ==========================================================
# FEATURES VALIDATION
# ==========================================================

def test_valid_features():

    print(
        '========== VALID FEATURES TEST =========='
    )

    data = create_valid_features()

    result = _validate_features(
        data
    )

    if result != data:

        raise AssertionError(
            'Valid features were modified.'
        )

    print(
        'Valid features: PASSED'
    )


def test_features_must_be_dictionary():

    print(
        '========== FEATURES TYPE TEST =========='
    )

    invalid_values = [
        None,
        [],
        (),
        'invalid',
        123,
    ]

    for value in invalid_values:

        try:

            _validate_features(
                value
            )

        except ValueError:

            continue

        raise AssertionError(
            f'Invalid features value was accepted: {value!r}'
        )

    print(
        'Features type validation: PASSED'
    )


def test_empty_features():

    print(
        '========== EMPTY FEATURES TEST =========='
    )

    try:

        _validate_features(
            {}
        )

    except ValueError:

        print(
            'Empty features handling: PASSED'
        )

        return

    raise AssertionError(
        'Empty features were accepted.'
    )


# ==========================================================
# FEATURE SCHEMA VALIDATION
# ==========================================================

def test_valid_feature_schema():

    print(
        '========== VALID FEATURE SCHEMA TEST =========='
    )

    features = create_valid_features()

    result = validate_feature_schema(
        features,
        FEATURE_NAMES,
    )

    if result is not True:

        raise AssertionError(
            'Valid feature schema was rejected.'
        )

    print(
        'Valid feature schema: PASSED'
    )


def test_missing_feature():

    print(
        '========== MISSING FEATURE TEST =========='
    )

    features = create_valid_features()

    del features[
        'expense_lag_7'
    ]

    try:

        validate_feature_schema(
            features,
            FEATURE_NAMES,
        )

    except ValueError as exc:

        if 'expense_lag_7' not in str(exc):

            raise AssertionError(
                'Missing feature was not identified '
                'correctly.'
            )

        print(
            'Missing feature handling: PASSED'
        )

        return

    raise AssertionError(
        'Missing feature was accepted.'
    )


def test_unexpected_feature():

    print(
        '========== UNEXPECTED FEATURE TEST =========='
    )

    features = create_valid_features()

    features[
        'unknown_feature'
    ] = 999.0

    try:

        validate_feature_schema(
            features,
            FEATURE_NAMES,
        )

    except ValueError as exc:

        if 'unknown_feature' not in str(exc):

            raise AssertionError(
                'Unexpected feature was not identified.'
            )

        print(
            'Unexpected feature handling: PASSED'
        )

        return

    raise AssertionError(
        'Unexpected feature was accepted.'
    )


def test_feature_names_must_be_list():

    print(
        '========== FEATURE NAMES TYPE TEST =========='
    )

    features = create_valid_features()

    invalid_feature_names = (
        tuple(FEATURE_NAMES),
    )

    for feature_names in invalid_feature_names:

        try:

            validate_feature_schema(
                features,
                feature_names,
            )

        except ValueError:

            print(
                'Feature names type validation: PASSED'
            )

            return

    raise AssertionError(
        'Invalid feature_names type was accepted.'
    )


def test_empty_feature_names():

    print(
        '========== EMPTY FEATURE NAMES TEST =========='
    )

    features = create_valid_features()

    try:

        validate_feature_schema(
            features,
            [],
        )

    except ValueError:

        print(
            'Empty feature names handling: PASSED'
        )

        return

    raise AssertionError(
        'Empty feature names were accepted.'
    )


def test_invalid_feature_name_type():

    print(
        '========== INVALID FEATURE NAME TEST =========='
    )

    features = create_valid_features()

    invalid_names = [
        123,
        None,
        True,
    ]

    for invalid_name in invalid_names:

        feature_names = [
            invalid_name,
            'expense_lag_7',
            'expense_rolling_mean_7',
        ]

        try:

            validate_feature_schema(
                features,
                feature_names,
            )

        except ValueError:

            continue

        raise AssertionError(
            'Invalid feature name was accepted.'
        )

    print(
        'Invalid feature name validation: PASSED'
    )


def test_duplicate_feature_names():

    print(
        '========== DUPLICATE FEATURE NAMES TEST =========='
    )

    features = create_valid_features()

    feature_names = [
        'expense_lag_1',
        'expense_lag_7',
        'expense_lag_1',
    ]

    try:

        validate_feature_schema(
            features,
            feature_names,
        )

    except ValueError as exc:

        if 'duplicate' not in str(exc).lower():

            raise AssertionError(
                'Duplicate feature names were rejected '
                'without reporting the duplicate.'
            )

        print(
            'Duplicate feature names handling: PASSED'
        )

        return

    raise AssertionError(
        'Duplicate feature names were accepted.'
    )


def test_empty_feature_name():

    print(
        '========== EMPTY FEATURE NAME TEST =========='
    )

    features = create_valid_features()

    feature_names = [
        '',
        'expense_lag_7',
        'expense_rolling_mean_7',
    ]

    try:

        validate_feature_schema(
            features,
            feature_names,
        )

    except ValueError:

        print(
            'Empty feature name handling: PASSED'
        )

        return

    raise AssertionError(
        'Empty feature name was accepted.'
    )


# ==========================================================
# FEATURE VECTOR
# ==========================================================

def test_feature_vector_order():

    print(
        '========== FEATURE VECTOR ORDER TEST =========='
    )

    features = {
        'expense_rolling_mean_7':
            95.0,

        'expense_lag_7':
            90.0,

        'expense_lag_1':
            100.0,
    }

    vector = build_feature_vector(
        features,
        FEATURE_NAMES,
    )

    expected = [
        [
            100.0,
            90.0,
            95.0,
        ]
    ]

    if vector != expected:

        raise AssertionError(
            'Feature vector order does not match '
            'the registered model schema.'
        )

    print(
        'Feature vector ordering: PASSED'
    )


def test_feature_vector_numeric_conversion():

    print(
        '========== FEATURE VECTOR NUMERIC TEST =========='
    )

    features = {
        'expense_lag_1':
            '100',

        'expense_lag_7':
            '90.5',

        'expense_rolling_mean_7':
            95,
    }

    vector = build_feature_vector(
        features,
        FEATURE_NAMES,
    )

    expected = [
        [
            100.0,
            90.5,
            95.0,
        ]
    ]

    if vector != expected:

        raise AssertionError(
            'Feature vector numeric conversion failed.'
        )

    print(
        'Feature vector numeric conversion: PASSED'
    )


# ==========================================================
# REGISTERED MODEL LOADING
# ==========================================================

def test_load_latest_registered_model_valid():

    print(
        '========== LOAD REGISTERED MODEL TEST =========='
    )

    with patch(
        'ml.prediction.predict.get_latest_model_version',
        return_value=MODEL_VERSION,
    ), patch(
        'ml.prediction.predict.load_registered_model',
        return_value={
            'status':
                REGISTRY_VALID,

            'model':
                SyntheticRegressionModel(),

            'metadata':
                create_valid_metadata(),

            'model_path':
                'models/test/model.pkl',

            'metadata_path':
                'models/test/metadata.json',
        },
    ):

        result = load_latest_registered_model(
            target_name=TARGET_NAME,
        )

    if result[
        'status'
    ] != PREDICTION_VALID:

        raise AssertionError(
            'Valid registered model was not accepted.'
        )

    if result[
        'version'
    ] != MODEL_VERSION:

        raise AssertionError(
            'Registered model version was not preserved.'
        )

    if result[
        'model'
    ] is None:

        raise AssertionError(
            'Registered model was not loaded.'
        )

    print(
        'Registered model loading: PASSED'
    )


def test_load_latest_registered_model_not_found():

    print(
        '========== MODEL NOT FOUND TEST =========='
    )

    with patch(
        'ml.prediction.predict.get_latest_model_version',
        return_value=None,
    ):

        result = load_latest_registered_model(
            target_name=TARGET_NAME,
        )

    if result[
        'status'
    ] != PREDICTION_MODEL_NOT_FOUND:

        raise AssertionError(
            'Missing registered model was not '
            'reported correctly.'
        )

    if result[
        'model'
    ] is not None:

        raise AssertionError(
            'Missing model unexpectedly returned a model.'
        )

    print(
        'Model not found handling: PASSED'
    )


# ==========================================================
# REGISTERED MODEL PREDICTION
# ==========================================================

def test_prediction_success():

    print(
        '========== PREDICTION SUCCESS TEST =========='
    )

    model_info = create_valid_model_info()

    features = create_valid_features()

    with patch(
        'ml.prediction.predict.load_latest_registered_model',
        return_value=model_info,
    ):

        result = predict_from_registered_model(
            features=features,
            target_name=TARGET_NAME,
        )

    if result[
        'status'
    ] != PREDICTION_VALID:

        raise AssertionError(
            'Prediction did not return a valid result.'
        )

    expected_prediction = 106.0

    if result[
        'prediction'
    ] != expected_prediction:

        raise AssertionError(
            'Prediction returned an unexpected value.'
        )

    if not isinstance(
        result[
            'prediction'
        ],
        float,
    ):

        raise AssertionError(
            'Prediction was not normalized to float.'
        )

    print(
        'Prediction success: PASSED'
    )


def test_public_predict_api_initial():

    print(
        '========== PUBLIC PREDICT CALCULATION TEST =========='
    )

    model_info = create_valid_model_info()

    features = create_valid_features()

    model = model_info[
        'model'
    ]

    feature_names = model_info[
        'metadata'
    ][
        'feature_names'
    ]

    vector = [
        features[
            feature_name
        ]
        for feature_name in feature_names
    ]

    expected_prediction = float(
        model.predict(
            [vector]
        )[0]
    )

    with patch(
        'ml.prediction.predict.load_latest_registered_model',
        return_value=model_info,
    ):

        result = predict(
            features=features,
            target_name=TARGET_NAME,
        )

    if result[
        'status'
    ] != PREDICTION_VALID:

        raise AssertionError(
            'Public predict() API did not '
            'return a valid result.'
        )

    if result[
        'prediction'
    ] != expected_prediction:

        raise AssertionError(
            'Public predict() returned a prediction '
            'different from the registered model output.'
        )

    if not isinstance(
        result[
            'prediction'
        ],
        float,
    ):

        raise AssertionError(
            'Public predict() prediction '
            'was not normalized to float.'
        )

    print(
        'Public predict() calculation: PASSED'
    )


def test_prediction_preserves_feature_schema():

    print(
        '========== PREDICTION FEATURE SCHEMA TEST =========='
    )

    model_info = create_valid_model_info()

    features = create_valid_features()

    with patch(
        'ml.prediction.predict.load_latest_registered_model',
        return_value=model_info,
    ):

        result = predict_from_registered_model(
            features=features,
            target_name=TARGET_NAME,
        )

    if result[
        'feature_names'
    ] != FEATURE_NAMES:

        raise AssertionError(
            'Feature names were not preserved.'
        )

    if result[
        'feature_count'
    ] != len(FEATURE_NAMES):

        raise AssertionError(
            'Feature count was not preserved.'
        )

    print(
        'Prediction feature schema: PASSED'
    )


def test_prediction_preserves_metadata():

    print(
        '========== PREDICTION METADATA TEST =========='
    )

    model_info = create_valid_model_info()

    features = create_valid_features()

    with patch(
        'ml.prediction.predict.load_latest_registered_model',
        return_value=model_info,
    ):

        result = predict_from_registered_model(
            features=features,
            target_name=TARGET_NAME,
        )

    if result[
        'metadata'
    ] != model_info[
        'metadata'
    ]:

        raise AssertionError(
            'Prediction metadata was not preserved.'
        )

    if result[
        'model_path'
    ] != model_info[
        'model_path'
    ]:

        raise AssertionError(
            'Model path was not preserved.'
        )

    if result[
        'metadata_path'
    ] != model_info[
        'metadata_path'
    ]:

        raise AssertionError(
            'Metadata path was not preserved.'
        )

    print(
        'Prediction metadata preservation: PASSED'
    )


# ==========================================================
# PREDICTION MODEL NOT FOUND
# ==========================================================

def test_prediction_model_not_found():

    print(
        '========== PREDICTION MODEL NOT FOUND TEST =========='
    )

    features = create_valid_features()

    model_info = {
        'status':
            PREDICTION_MODEL_NOT_FOUND,

        'target_name':
            TARGET_NAME,

        'version':
            None,

        'model':
            None,

        'metadata':
            None,

        'model_path':
            None,

        'metadata_path':
            None,
    }

    with patch(
        'ml.prediction.predict.load_latest_registered_model',
        return_value=model_info,
    ):

        result = predict_from_registered_model(
            features=features,
            target_name=TARGET_NAME,
        )

    if result[
        'status'
    ] != PREDICTION_MODEL_NOT_FOUND:

        raise AssertionError(
            'Model-not-found status was not propagated.'
        )

    if result[
        'prediction'
    ] is not None:

        raise AssertionError(
            'Prediction should be None when model is missing.'
        )

    print(
        'Prediction model-not-found handling: PASSED'
    )


# ==========================================================
# INVALID FEATURE TESTS
# ==========================================================

def test_prediction_missing_feature():

    print(
        '========== PREDICTION MISSING FEATURE TEST =========='
    )

    model_info = create_valid_model_info()

    features = create_valid_features()

    del features[
        'expense_lag_7'
    ]

    with patch(
        'ml.prediction.predict.load_latest_registered_model',
        return_value=model_info,
    ):

        result = predict_from_registered_model(
            features=features,
            target_name=TARGET_NAME,
        )

    if result[
        'status'
    ] != PREDICTION_INVALID:

        raise AssertionError(
            'Missing feature did not produce invalid prediction.'
        )

    if 'expense_lag_7' not in result.get(
        'error',
        '',
    ):

        raise AssertionError(
            'Missing feature name was not included in error.'
        )

    print(
        'Prediction missing feature handling: PASSED'
    )


def test_prediction_unexpected_feature():

    print(
        '========== PREDICTION UNEXPECTED FEATURE TEST =========='
    )

    model_info = create_valid_model_info()

    features = create_valid_features()

    features[
        'unknown_feature'
    ] = 999.0

    with patch(
        'ml.prediction.predict.load_latest_registered_model',
        return_value=model_info,
    ):

        result = predict_from_registered_model(
            features=features,
            target_name=TARGET_NAME,
        )

    if result[
        'status'
    ] != PREDICTION_INVALID:

        raise AssertionError(
            'Unexpected feature did not produce invalid prediction.'
        )

    if 'unknown_feature' not in result.get(
        'error',
        '',
    ):

        raise AssertionError(
            'Unexpected feature name was not included in error.'
        )

    print(
        'Prediction unexpected feature handling: PASSED'
    )


def test_prediction_invalid_numeric_feature():

    print(
        '========== PREDICTION INVALID NUMERIC FEATURE TEST =========='
    )

    model_info = create_valid_model_info()

    features = create_valid_features()

    features[
        'expense_lag_1'
    ] = float('nan')

    with patch(
        'ml.prediction.predict.load_latest_registered_model',
        return_value=model_info,
    ):

        result = predict_from_registered_model(
            features=features,
            target_name=TARGET_NAME,
        )

    if result[
        'status'
    ] != PREDICTION_INVALID:

        raise AssertionError(
            'Invalid numeric feature did not '
            'produce invalid prediction.'
        )

    print(
        'Prediction invalid numeric feature handling: PASSED'
    )


# ==========================================================
# INVALID MODEL TESTS
# ==========================================================

def test_prediction_missing_model_object():

    print(
        '========== MISSING MODEL OBJECT TEST =========='
    )

    model_info = create_valid_model_info()

    model_info[
        'model'
    ] = None

    features = create_valid_features()

    with patch(
        'ml.prediction.predict.load_latest_registered_model',
        return_value=model_info,
    ):

        result = predict_from_registered_model(
            features=features,
            target_name=TARGET_NAME,
        )

    if result[
        'status'
    ] != PREDICTION_INVALID:

        raise AssertionError(
            'Missing model object was not rejected.'
        )

    if result[
        'prediction'
    ] is not None:

        raise AssertionError(
            'Prediction should be None for missing model.'
        )

    print(
        'Missing model object handling: PASSED'
    )


class ModelWithoutPredict:

    pass


def test_prediction_model_without_predict_method():

    print(
        '========== MODEL WITHOUT PREDICT TEST =========='
    )

    model_info = create_valid_model_info()

    model_info[
        'model'
    ] = ModelWithoutPredict()

    features = create_valid_features()

    with patch(
        'ml.prediction.predict.load_latest_registered_model',
        return_value=model_info,
    ):

        result = predict_from_registered_model(
            features=features,
            target_name=TARGET_NAME,
        )

    if result[
        'status'
    ] != PREDICTION_INVALID:

        raise AssertionError(
            'Model without predict() was accepted.'
        )

    if 'predict()' not in result.get(
        'error',
        '',
    ):

        raise AssertionError(
            'Missing predict() error was not reported.'
        )

    print(
        'Model without predict() handling: PASSED'
    )


# ==========================================================
# MODEL PREDICTION FAILURE
# ==========================================================

class FailingModel:

    def predict(
        self,
        X,
    ):

        raise RuntimeError(
            'Synthetic prediction failure'
        )


def test_model_prediction_failure():

    print(
        '========== MODEL PREDICTION FAILURE TEST =========='
    )

    model_info = create_valid_model_info()

    model_info[
        'model'
    ] = FailingModel()

    features = create_valid_features()

    with patch(
        'ml.prediction.predict.load_latest_registered_model',
        return_value=model_info,
    ):

        result = predict_from_registered_model(
            features=features,
            target_name=TARGET_NAME,
        )

    if result[
        'status'
    ] != PREDICTION_INVALID:

        raise AssertionError(
            'Model prediction failure was not handled.'
        )

    if 'prediction failed' not in result.get(
        'error',
        '',
    ).lower():

        raise AssertionError(
            'Prediction failure error was not reported.'
        )

    print(
        'Model prediction failure handling: PASSED'
    )


# ==========================================================
# MODEL OUTPUT TESTS
# ==========================================================

class IntegerOutputModel:

    def predict(
        self,
        X,
    ):

        return np.array([
            123,
        ])


def test_integer_prediction_output():

    print(
        '========== INTEGER PREDICTION OUTPUT TEST =========='
    )

    model_info = create_valid_model_info()

    model_info[
        'model'
    ] = IntegerOutputModel()

    features = create_valid_features()

    with patch(
        'ml.prediction.predict.load_latest_registered_model',
        return_value=model_info,
    ):

        result = predict_from_registered_model(
            features=features,
            target_name=TARGET_NAME,
        )

    if result[
        'status'
    ] != PREDICTION_VALID:

        raise AssertionError(
            'Integer prediction output was rejected.'
        )

    if result[
        'prediction'
    ] != 123.0:

        raise AssertionError(
            'Integer prediction was not normalized to 123.0.'
        )

    if not isinstance(
        result['prediction'],
        float,
    ):

        raise AssertionError(
            'Integer prediction was not converted to float.'
        )

    print(
        'Integer prediction normalization: PASSED'
    )


class MultipleOutputModel:

    def predict(
        self,
        X,
    ):

        return np.array([
            100.0,
            200.0,
        ])


def test_multiple_prediction_outputs():

    print(
        '========== MULTIPLE PREDICTION OUTPUT TEST =========='
    )

    model_info = create_valid_model_info()

    model_info[
        'model'
    ] = MultipleOutputModel()

    features = create_valid_features()

    with patch(
        'ml.prediction.predict.load_latest_registered_model',
        return_value=model_info,
    ):

        result = predict_from_registered_model(
            features=features,
            target_name=TARGET_NAME,
        )

    if result[
        'status'
    ] != PREDICTION_INVALID:

        raise AssertionError(
            'Multiple predictions were accepted.'
        )

    if 'exactly one prediction' not in result.get(
        'error',
        '',
    ):

        raise AssertionError(
            'Multiple prediction error was not reported correctly.'
        )

    print(
        'Multiple prediction output handling: PASSED'
    )


class NoneOutputModel:

    def predict(
        self,
        X,
    ):

        return None


def test_none_prediction_output():

    print(
        '========== NONE PREDICTION OUTPUT TEST =========='
    )

    model_info = create_valid_model_info()

    model_info[
        'model'
    ] = NoneOutputModel()

    features = create_valid_features()

    with patch(
        'ml.prediction.predict.load_latest_registered_model',
        return_value=model_info,
    ):

        result = predict_from_registered_model(
            features=features,
            target_name=TARGET_NAME,
        )

    if result[
        'status'
    ] != PREDICTION_INVALID:

        raise AssertionError(
            'None prediction output was accepted.'
        )

    if 'no prediction' not in result.get(
        'error',
        '',
    ).lower():

        raise AssertionError(
            'None prediction error was not reported.'
        )

    print(
        'None prediction output handling: PASSED'
    )


class NaNOutputModel:

    def predict(
        self,
        X,
    ):

        return np.array([
            float('nan'),
        ])


def test_nan_prediction_output():

    print(
        '========== NAN PREDICTION OUTPUT TEST =========='
    )

    model_info = create_valid_model_info()

    model_info[
        'model'
    ] = NaNOutputModel()

    features = create_valid_features()

    with patch(
        'ml.prediction.predict.load_latest_registered_model',
        return_value=model_info,
    ):

        result = predict_from_registered_model(
            features=features,
            target_name=TARGET_NAME,
        )

    if result[
        'status'
    ] != PREDICTION_INVALID:

        raise AssertionError(
            'NaN prediction was accepted.'
        )

    if 'non-finite' not in result.get(
        'error',
        '',
    ).lower():

        raise AssertionError(
            'Non-finite prediction error was not reported.'
        )

    print(
        'NaN prediction output handling: PASSED'
    )


# ==========================================================
# TARGET NAME
# ==========================================================

def test_target_name_preservation():

    print(
        '========== TARGET NAME TEST =========='
    )

    custom_target = 'Target_Travel_Day_7D'

    model_info = create_valid_model_info()

    model_info[
        'target_name'
    ] = custom_target

    features = create_valid_features()

    with patch(
        'ml.prediction.predict.load_latest_registered_model',
        return_value=model_info,
    ):

        result = predict_from_registered_model(
            features=features,
            target_name=custom_target,
        )

    if result[
        'target_name'
    ] != custom_target:

        raise AssertionError(
            'Target name was not preserved.'
        )

    print(
        'Target name preservation: PASSED'
    )


# ==========================================================
# PUBLIC API
# ==========================================================

def test_public_predict_api():

    print(
        '========== PUBLIC PREDICT API TEST =========='
    )

    model_info = create_valid_model_info()

    features = create_valid_features()

    with patch(
        'ml.prediction.predict.load_latest_registered_model',
        return_value=model_info,
    ):

        result = predict(
            features=features,
            target_name=TARGET_NAME,
        )

    if result[
        'status'
    ] != PREDICTION_VALID:

        raise AssertionError(
            'Public predict() API did not return a valid result.'
        )

    if result[
        'prediction'
    ] != 106.0:

        raise AssertionError(
            'Public predict() returned an unexpected prediction.'
        )

    print(
        'Public predict() API: PASSED'
    )


# ==========================================================
# FEATURE ORDER + PREDICTION INTEGRATION
# ==========================================================

class OrderSensitiveModel:

    def predict(
        self,
        X,
    ):

        row = X[0]

        return np.array([
            (
                row[0] * 1000.0
                + row[1] * 10.0
                + row[2]
            )
        ])


def test_prediction_uses_registered_feature_order():

    print(
        '========== REGISTERED FEATURE ORDER TEST =========='
    )

    model_info = create_valid_model_info()

    model_info[
        'model'
    ] = OrderSensitiveModel()

    features = {
        'expense_rolling_mean_7':
            3.0,

        'expense_lag_7':
            2.0,

        'expense_lag_1':
            1.0,
    }

    with patch(
        'ml.prediction.predict.load_latest_registered_model',
        return_value=model_info,
    ):

        result = predict_from_registered_model(
            features=features,
            target_name=TARGET_NAME,
        )

    expected = 1023.0

    if result[
        'prediction'
    ] != expected:

        raise AssertionError(
            'Prediction did not use the registered '
            'feature order.'
        )

    print(
        'Registered feature order: PASSED'
    )


# ==========================================================
# FULL INTEGRATION
# ==========================================================

def test_full_prediction_integration():

    print(
        '========== FULL PREDICTION INTEGRATION TEST =========='
    )

    model_info = create_valid_model_info()

    features = create_valid_features()

    with patch(
        'ml.prediction.predict.load_latest_registered_model',
        return_value=model_info,
    ):

        result = predict_from_registered_model(
            features=features,
            target_name=TARGET_NAME,
        )

    required_keys = {
        'status',
        'target_name',
        'version',
        'prediction',
        'feature_count',
        'feature_names',
        'metadata',
        'model_path',
        'metadata_path',
    }

    missing = (
        required_keys
        - set(result.keys())
    )

    if missing:

        raise AssertionError(
            'Prediction result is missing '
            f'required fields: {missing}'
        )

    if result[
        'status'
    ] != PREDICTION_VALID:

        raise AssertionError(
            'Integration prediction is not valid.'
        )

    if result[
        'target_name'
    ] != TARGET_NAME:

        raise AssertionError(
            'Integration target name mismatch.'
        )

    if result[
        'version'
    ] != MODEL_VERSION:

        raise AssertionError(
            'Integration model version mismatch.'
        )

    if result[
        'feature_names'
    ] != FEATURE_NAMES:

        raise AssertionError(
            'Integration feature names mismatch.'
        )

    if result[
        'feature_count'
    ] != len(FEATURE_NAMES):

        raise AssertionError(
            'Integration feature count mismatch.'
        )

    if not isinstance(
        result['prediction'],
        float,
    ):

        raise AssertionError(
            'Integration prediction is not a float.'
        )

    if not math.isfinite(
        result['prediction']
    ):

        raise AssertionError(
            'Integration prediction is not finite.'
        )

    print(
        'Full prediction integration: PASSED'
    )


# ==========================================================
# ALL TESTS
# ==========================================================

def run_all_tests():

    print()
    print(
        '=================================================='
    )
    print(
        '       REGISTERED MODEL PREDICTION TEST SUITE'
    )
    print(
        '=================================================='
    )

    # ------------------------------------------------------
    # Numeric feature validation
    # ------------------------------------------------------

    test_numeric_feature_integer()
    test_numeric_feature_float()
    test_numeric_feature_string()
    test_numeric_feature_boolean()
    test_numeric_feature_none()
    test_numeric_feature_invalid_string()
    test_numeric_feature_nan()
    test_numeric_feature_infinite()
    test_numeric_feature_negative()

    # ------------------------------------------------------
    # Feature validation
    # ------------------------------------------------------

    test_valid_features()
    test_features_must_be_dictionary()
    test_empty_features()

    # ------------------------------------------------------
    # Feature schema
    # ------------------------------------------------------

    test_valid_feature_schema()
    test_missing_feature()
    test_unexpected_feature()
    test_feature_names_must_be_list()
    test_empty_feature_names()
    test_invalid_feature_name_type()
    test_empty_feature_name()

    # ------------------------------------------------------
    # Feature vector
    # ------------------------------------------------------

    test_feature_vector_order()
    test_feature_vector_numeric_conversion()

    # ------------------------------------------------------
    # Registry
    # ------------------------------------------------------

    test_load_latest_registered_model_valid()
    test_load_latest_registered_model_not_found()

    # ------------------------------------------------------
    # Prediction
    # ------------------------------------------------------

    test_prediction_success()
    test_public_predict_api_initial()
    test_prediction_preserves_feature_schema()
    test_prediction_preserves_metadata()

    # ------------------------------------------------------
    # Missing / invalid features
    # ------------------------------------------------------

    test_prediction_model_not_found()
    test_prediction_missing_feature()
    test_prediction_unexpected_feature()
    test_prediction_invalid_numeric_feature()

    # ------------------------------------------------------
    # Invalid models
    # ------------------------------------------------------

    test_prediction_missing_model_object()
    test_prediction_model_without_predict_method()
    test_model_prediction_failure()

    # ------------------------------------------------------
    # Model outputs
    # ------------------------------------------------------

    test_integer_prediction_output()
    test_multiple_prediction_outputs()
    test_none_prediction_output()
    test_nan_prediction_output()

    # ------------------------------------------------------
    # Metadata
    # ------------------------------------------------------

    test_target_name_preservation()

    # ------------------------------------------------------
    # Public API
    # ------------------------------------------------------

    test_public_predict_api()

    # ------------------------------------------------------
    # Feature order integration
    # ------------------------------------------------------

    test_prediction_uses_registered_feature_order()

    # ------------------------------------------------------
    # Full integration
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
# PYTEST ENTRY POINT
# ==========================================================

if __name__ == '__main__':

    run_all_tests()