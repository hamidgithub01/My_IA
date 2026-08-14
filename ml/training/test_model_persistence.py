from ml.training.train import (
    train_model,
)

from ml.training.save import (
    save_model_history,
)

from ml.training.load import (
    load_model_by_id,
)


def test_model_persistence():

    print(
        '========== MODEL PERSISTENCE TEST =========='
    )

    # ------------------------------------------------------
    # 1. Train model
    # ------------------------------------------------------

    training_result = train_model()

    model = training_result[
        'model'
    ]

    feature_names = training_result[
        'feature_names'
    ]

    training_rows = training_result[
        'training_rows'
    ]

    if model is None:

        raise AssertionError(
            'Training returned no model.'
        )

    print(
        'Model training: PASSED'
    )

    # ------------------------------------------------------
    # 2. Verify model parameters
    # ------------------------------------------------------

    coefficients = model.coef_

    intercept = model.intercept_

    if len(coefficients) != len(
        feature_names
    ):

        raise AssertionError(
            'Coefficient count does not '
            'match feature count.'
        )

    print(
        'Model parameters: PASSED'
    )

    print(
        f'Features: {len(feature_names)}'
    )

    print(
        f'Training rows: {training_rows}'
    )

    # ------------------------------------------------------
    # 3. Save model
    # ------------------------------------------------------

    model_history_id = save_model_history(
        training_result,
        evaluation_result=None,
        reused_previous_state=False,
    )

    if model_history_id is None:

        raise AssertionError(
            'Model history ID was not returned.'
        )

    print(
        'Model save: PASSED'
    )

    print(
        f'Model history ID: {model_history_id}'
    )

    # ------------------------------------------------------
    # 4. Load saved model
    # ------------------------------------------------------

    loaded_result = load_model_by_id(
        model_history_id
    )

    if loaded_result is None:

        raise AssertionError(
            'Saved model could not be loaded.'
        )

    loaded_model = loaded_result[
        'model'
    ]

    loaded_feature_names = (
        loaded_result[
            'feature_names'
        ]
    )

    if loaded_model is None:

        raise AssertionError(
            'Loaded model is None.'
        )

    print(
        'Model load: PASSED'
    )

    # ------------------------------------------------------
    # 5. Compare feature names
    # ------------------------------------------------------

    if (
        feature_names
        != loaded_feature_names
    ):

        raise AssertionError(
            'Loaded feature names do not '
            'match original feature names.'
        )

    print(
        'Feature names preservation: PASSED'
    )

    # ------------------------------------------------------
    # 6. Compare coefficients
    # ------------------------------------------------------

    loaded_coefficients = (
        loaded_model.coef_
    )

    if len(
        coefficients
    ) != len(
        loaded_coefficients
    ):

        raise AssertionError(
            'Loaded coefficient count '
            'does not match original.'
        )

    for original, loaded in zip(
        coefficients,
        loaded_coefficients,
    ):

        if abs(
            float(original)
            - float(loaded)
        ) > 1e-10:

            raise AssertionError(
                'Loaded coefficients do not '
                'match original coefficients.'
            )

    print(
        'Coefficient preservation: PASSED'
    )

    # ------------------------------------------------------
    # 7. Compare intercept
    # ------------------------------------------------------

    if abs(
        float(intercept)
        - float(
            loaded_model.intercept_
        )
    ) > 1e-10:

        raise AssertionError(
            'Loaded intercept does not '
            'match original intercept.'
        )

    print(
        'Intercept preservation: PASSED'
    )

    # ------------------------------------------------------
    # 8. Verify loaded model can predict
    # ------------------------------------------------------

    X = []

    from ml.training.dataset import (
        prepare_model_dataset,
    )

    dataset = prepare_model_dataset()

    for row in dataset[
        'test_data'
    ]:

        X.append([
            row[name]
            for name in feature_names
        ])

    original_predictions = model.predict(
        X
    )

    loaded_predictions = (
        loaded_model.predict(X)
    )

    if len(
        original_predictions
    ) != len(
        loaded_predictions
    ):

        raise AssertionError(
            'Prediction count mismatch '
            'between original and loaded model.'
        )

    for original, loaded in zip(
        original_predictions,
        loaded_predictions,
    ):

        if abs(
            float(original)
            - float(loaded)
        ) > 1e-10:

            raise AssertionError(
                'Loaded model predictions '
                'do not match original predictions.'
            )

    print(
        'Prediction preservation: PASSED'
    )

    # ------------------------------------------------------
    # Final
    # ------------------------------------------------------

    print()

    print(
        '========== MODEL PERSISTENCE TEST PASSED =========='
    )


if __name__ == '__main__':

    test_model_persistence()