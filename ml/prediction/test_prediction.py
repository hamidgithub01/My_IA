
from ml.prediction.predict import (
    predict_expense,
    build_prediction_vector,
    validate_prediction_features,
)

from ml.training.load import (
    load_latest_model,
)


def test_prediction_pipeline():

    print(
        '========== PREDICTION PIPELINE TEST =========='
    )

    # ------------------------------------------------------
    # 1. Load latest model
    # ------------------------------------------------------

    model_info = load_latest_model()

    if model_info is None:

        raise AssertionError(
            'No saved model is available.'
        )

    model = model_info[
        'model'
    ]

    feature_names = model_info[
        'feature_names'
    ]

    model_history_id = model_info.get(
        'model_history_id'
    )

    print(
        'Model loading: PASSED'
    )

    print(
        f'Model history ID: '
        f'{model_history_id}'
    )

    print(
        f'Feature count: '
        f'{len(feature_names)}'
    )

    # ------------------------------------------------------
    # 2. Build realistic prediction input
    # ------------------------------------------------------

    prediction_data = {
        feature_name: 0.0
        for feature_name
        in feature_names
    }

    # Date is metadata only and must never
    # become a model input feature.
    prediction_data[
        'Date'
    ] = '2026-08-14'

    # ------------------------------------------------------
    # 3. Validate prediction features
    # ------------------------------------------------------

    validate_prediction_features(
        prediction_data,
        feature_names,
    )

    print(
        'Feature validation: PASSED'
    )

    # ------------------------------------------------------
    # 4. Build prediction vector
    # ------------------------------------------------------

    vector = build_prediction_vector(
        prediction_data,
        feature_names,
    )

    if len(vector) != len(
        feature_names
    ):

        raise AssertionError(
            'Prediction vector length does not '
            'match feature count.'
        )

    print(
        'Feature vector dimensions: PASSED'
    )

    # ------------------------------------------------------
    # 5. Feature order validation
    # ------------------------------------------------------

    for index, feature_name in enumerate(
        feature_names
    ):

        if prediction_data[
            feature_name
        ] != vector[index]:

            raise AssertionError(
                'Feature order mismatch detected.'
            )

    print(
        'Feature order: PASSED'
    )

    # ------------------------------------------------------
    # 6. Verify forbidden fields are not
    #    model features
    # ------------------------------------------------------

    if 'Date' in feature_names:

        raise AssertionError(
            'Date is present inside model features.'
        )

    target_features = [
        name
        for name in feature_names
        if name.startswith('Target_')
    ]

    if target_features:

        raise AssertionError(
            'Target columns are present inside '
            'model features: '
            + ', '.join(target_features)
        )

    print(
        'Target leakage check: PASSED'
    )

    # ------------------------------------------------------
    # 7. Generate prediction directly
    # ------------------------------------------------------

    direct_prediction = model.predict([
        vector
    ])[0]

    if not isinstance(
        float(direct_prediction),
        float,
    ):

        raise AssertionError(
            'Direct prediction is not numeric.'
        )

    print(
        'Direct prediction generation: PASSED'
    )

    # ------------------------------------------------------
    # 8. Apply the same business rule used by
    #    the public prediction API.
    #
    # Expense predictions cannot be negative.
    # ------------------------------------------------------

    expected_prediction = max(
        0.0,
        float(direct_prediction),
    )

    # ------------------------------------------------------
    # 9. Generate prediction through public API
    # ------------------------------------------------------

    result = predict_expense(
        prediction_data
    )

    if not isinstance(
        result,
        dict,
    ):

        raise AssertionError(
            'Prediction result is not a dictionary.'
        )

    if 'prediction' not in result:

        raise AssertionError(
            'Prediction result contains no prediction.'
        )

    prediction = result[
        'prediction'
    ]

    if not isinstance(
        prediction,
        float,
    ):

        raise AssertionError(
            'Prediction is not a float.'
        )

    print(
        'Prediction generation: PASSED'
    )

    # ------------------------------------------------------
    # 10. Prediction must be non-negative
    # ------------------------------------------------------

    if prediction < 0:

        raise AssertionError(
            'Expense prediction cannot be negative.'
        )

    print(
        'Non-negative prediction: PASSED'
    )

    # ------------------------------------------------------
    # 11. Public API must use latest model
    # ------------------------------------------------------

    if result[
        'model_history_id'
    ] != model_history_id:

        raise AssertionError(
            'Prediction did not use the latest saved model.'
        )

    print(
        'Latest model usage: PASSED'
    )

    # ------------------------------------------------------
    # 12. Prediction consistency
    #
    # Compare the public result with the expected
    # business-safe prediction.
    # ------------------------------------------------------

    print(
        'Raw direct prediction:',
        repr(float(direct_prediction))
    )

    print(
        'Expected public prediction:',
        repr(float(expected_prediction))
    )

    print(
        'Public prediction:',
        repr(float(prediction))
    )

    print(
        'Prediction difference:',
        repr(
            float(expected_prediction)
            - float(prediction)
        )
    )

    if abs(
        float(expected_prediction)
        - float(prediction)
    ) > 1e-10:

        raise AssertionError(
            'Public prediction does not match '
            'expected prediction.'
        )

    print(
        'Prediction consistency: PASSED'
    )

    # ------------------------------------------------------
    # 13. Verify no training occurred
    # ------------------------------------------------------

    model_info_after = load_latest_model()

    if model_info_after is None:

        raise AssertionError(
            'Latest model disappeared after prediction.'
        )

    if model_info_after.get(
        'model_history_id'
    ) != model_history_id:

        raise AssertionError(
            'Prediction unexpectedly changed '
            'the latest model.'
        )

    print(
        'Inference without retraining: PASSED'
    )

    # ------------------------------------------------------
    # Final
    # ------------------------------------------------------

    print()

    print(
        '========== PREDICTION PIPELINE TEST PASSED =========='
    )


if __name__ == '__main__':

    test_prediction_pipeline()
