
import pytest


from ml.models.prediction import (
    PREDICTION_VALID,
    build_feature_vector,
    predict_with_model,
    generate_prediction,
    generate_batch_predictions,
    generate_prediction_from_training_result,
)


# ==========================================================
# DEMO MODEL
# ==========================================================

class DummyRegressionModel:

    def predict(
        self,
        values,
    ):

        return [
            sum(values[0])
        ]


class DummyClassificationModel:

    def predict(
        self,
        values,
    ):

        if sum(values[0]) >= 10:

            return [1]

        return [0]


class EmptyPredictionModel:

    def predict(
        self,
        values,
    ):

        return []


class BrokenModel:

    def predict(
        self,
        values,
    ):

        raise RuntimeError(
            'prediction failure'
        )


# ==========================================================
# FEATURE VECTOR TEST
# ==========================================================

def test_build_feature_vector():

    feature_names = [
        'a',
        'b',
        'c',
    ]

    feature_data = {

        'c': 30,

        'a': 10,

        'b': 20,
    }

    vector = build_feature_vector(
        feature_names,
        feature_data,
    )

    assert vector == [
        10,
        20,
        30,
    ]


# ==========================================================
# MISSING FEATURE TEST
# ==========================================================

def test_missing_feature():

    with pytest.raises(
        ValueError
    ):

        build_feature_vector(
            ['a', 'b'],
            {
                'a': 10,
            },
        )


# ==========================================================
# INVALID FEATURE VALUE TEST
# ==========================================================

def test_invalid_feature_value():

    with pytest.raises(
        ValueError
    ):

        build_feature_vector(
            ['a', 'b'],
            {
                'a': 10,
                'b': 'invalid',
            },
        )


# ==========================================================
# FEATURE COUNT TEST
# ==========================================================

def test_feature_count():

    with pytest.raises(
        ValueError
    ):

        predict_with_model(
            DummyRegressionModel(),
            [10],
            ['a', 'b'],
        )


# ==========================================================
# REGRESSION PREDICTION
# ==========================================================

def test_regression_prediction():

    result = generate_prediction(
        DummyRegressionModel(),
        ['a', 'b'],
        {
            'a': 10,
            'b': 20,
        },
        'Target_Expense_Total_1D',
        'regression',
        'v1.0.0',
    )

    assert (
        result['status']
        == PREDICTION_VALID
    )

    assert (
        result['prediction']
        == 30
    )

    assert (
        result['target_name']
        == 'Target_Expense_Total_1D'
    )

    assert (
        result['model_version']
        == 'v1.0.0'
    )


# ==========================================================
# CLASSIFICATION PREDICTION
# ==========================================================

def test_classification_prediction():

    result = generate_prediction(
        DummyClassificationModel(),
        ['a', 'b'],
        {
            'a': 7,
            'b': 5,
        },
        'Target_Behavior',
        'classification',
        'v1.0.0',
    )

    assert (
        result['status']
        == PREDICTION_VALID
    )

    assert (
        result['prediction']
        == 1
    )


# ==========================================================
# BATCH PREDICTION
# ==========================================================

def test_batch_predictions():

    result = generate_batch_predictions(
        DummyRegressionModel(),
        ['a', 'b'],
        [
            {
                'a': 10,
                'b': 20,
            },
            {
                'a': 30,
                'b': 40,
            },
        ],
        'Target_Expense_Total_1D',
        'regression',
        'v1.0.0',
    )

    assert (
        result['status']
        == PREDICTION_VALID
    )

    assert (
        result['prediction_count']
        == 2
    )

    assert (
        result['predictions'][0][
            'prediction'
        ]
        == 30
    )

    assert (
        result['predictions'][1][
            'prediction'
        ]
        == 70
    )


# ==========================================================
# TRAINING RESULT INTEGRATION
# ==========================================================

def test_training_result_integration():

    training_result = {

        'model':
            DummyRegressionModel(),

        'feature_names':
            [
                'a',
                'b',
            ],

        'target_name':
            'Target_Expense_Total_1D',

        'target_task':
            'regression',

        'model_version':
            'v1.0.0',
    }

    result = (
        generate_prediction_from_training_result(
            training_result,
            {
                'a': 5,
                'b': 15,
            },
        )
    )

    assert (
        result['status']
        == PREDICTION_VALID
    )

    assert (
        result['prediction']
        == 20
    )


# ==========================================================
# EMPTY MODEL OUTPUT
# ==========================================================

def test_empty_prediction_output():

    with pytest.raises(
        ValueError
    ):

        predict_with_model(
            EmptyPredictionModel(),
            [1, 2],
            ['a', 'b'],
        )


# ==========================================================
# MODEL FAILURE
# ==========================================================

def test_model_prediction_failure():

    with pytest.raises(
        ValueError
    ):

        predict_with_model(
            BrokenModel(),
            [1, 2],
            ['a', 'b'],
        )


# ==========================================================
# INVALID MODEL
# ==========================================================

def test_invalid_model():

    with pytest.raises(
        ValueError
    ):

        predict_with_model(
            None,
            [1, 2],
            ['a', 'b'],
        )


# ==========================================================
# EMPTY FEATURE DATA
# ==========================================================

def test_empty_feature_data():

    with pytest.raises(
        ValueError
    ):

        generate_prediction(
            DummyRegressionModel(),
            ['a', 'b'],
            {},
            'Target_Test',
            'regression',
        )


# ==========================================================
# INVALID TRAINING RESULT
# ==========================================================

def test_invalid_training_result():

    with pytest.raises(
        ValueError
    ):

        generate_prediction_from_training_result(
            None,
            {
                'a': 1,
            },
        )


# ==========================================================
# MISSING TRAINING RESULT FIELD
# ==========================================================

def test_missing_training_result_field():

    with pytest.raises(
        ValueError
    ):

        generate_prediction_from_training_result(
            {
                'model':
                    DummyRegressionModel(),

                'feature_names':
                    ['a'],
            },
            {
                'a': 10,
            },
        )


# ==========================================================
# EMPTY BATCH
# ==========================================================

def test_empty_batch():

    with pytest.raises(
        ValueError
    ):

        generate_batch_predictions(
            DummyRegressionModel(),
            ['a'],
            [],
            'Target_Test',
            'regression',
        )


# ==========================================================
# MAIN
# ==========================================================

if __name__ == '__main__':

    print()
    print(
        '=================================================='
    )

    print(
        '       PRODUCTION PREDICTION TEST SUITE'
    )

    print(
        '=================================================='
    )

    print(
        'Run with pytest.'
    )

    print(
        '=================================================='
    )
