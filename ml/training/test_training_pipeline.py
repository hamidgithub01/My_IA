from ml.training.dataset import (
    prepare_model_dataset,
)

from ml.training.train import (
    train_model,
)

from ml.evaluation.evaluate import (
    evaluate_model,
)

from ml.evaluation.metrics import (
    calculate_metrics,
)


def test_training_pipeline():

    print(
        '========== TRAINING PIPELINE TEST =========='
    )

    # ------------------------------------------------------
    # 1. Prepare model dataset
    # ------------------------------------------------------

    dataset = prepare_model_dataset()

    X_train = dataset['X_train']
    y_train = dataset['y_train']

    X_test = dataset['X_test']
    y_test = dataset['y_test']

    feature_names = dataset[
        'feature_names'
    ]

    print(
        f'Features: {len(feature_names)}'
    )

    print(
        f'Training rows: {len(X_train)}'
    )

    print(
        f'Test rows: {len(X_test)}'
    )

    # ------------------------------------------------------
    # 2. Verify dataset dimensions
    # ------------------------------------------------------

    if not X_train:

        raise AssertionError(
            'Training dataset is empty.'
        )

    if not X_test:

        raise AssertionError(
            'Test dataset is empty.'
        )

    if len(X_train) != len(y_train):

        raise AssertionError(
            'X_train/y_train mismatch.'
        )

    if len(X_test) != len(y_test):

        raise AssertionError(
            'X_test/y_test mismatch.'
        )

    if len(X_train[0]) != len(
        feature_names
    ):

        raise AssertionError(
            'Training feature dimension mismatch.'
        )

    if len(X_test[0]) != len(
        feature_names
    ):

        raise AssertionError(
            'Test feature dimension mismatch.'
        )

    print(
        'Dataset dimensions: PASSED'
    )

    # ------------------------------------------------------
    # 3. Train model
    # ------------------------------------------------------

    training_result = train_model()

    model = training_result[
        'model'
    ]

    trained_feature_names = (
        training_result[
            'feature_names'
        ]
    )

    if model is None:

        raise AssertionError(
            'Training returned no model.'
        )

    if len(
        trained_feature_names
    ) != len(feature_names):

        raise AssertionError(
            'Training feature count '
            'does not match prepared dataset.'
        )

    print(
        'Model training: PASSED'
    )

    # ------------------------------------------------------
    # 4. Verify model can predict
    # ------------------------------------------------------

    predictions = model.predict(
        X_test
    )

    if len(predictions) != len(
        y_test
    ):

        raise AssertionError(
            'Prediction count does not '
            'match test target count.'
        )

    print(
        'Prediction generation: PASSED'
    )

    # ------------------------------------------------------
    # 5. Calculate metrics
    # ------------------------------------------------------

    metrics = calculate_metrics(
        y_test,
        predictions,
    )

    required_metrics = {
        'mae',
        'rmse',
        'r_squared',
    }

    missing_metrics = (
        required_metrics
        - set(metrics.keys())
    )

    if missing_metrics:

        raise AssertionError(
            'Missing evaluation metrics: '
            f'{missing_metrics}'
        )

    print(
        'Evaluation metrics: PASSED'
    )

    print(
        f"MAE: {metrics['mae']}"
    )

    print(
        f"RMSE: {metrics['rmse']}"
    )

    print(
        f"R²: {metrics['r_squared']}"
    )

    # ------------------------------------------------------
    # 6. Verify chronological evaluation
    # ------------------------------------------------------

    evaluation_result = evaluate_model(
        training_result=training_result,
        test_ratio=0.2,
        min_test_rows=2,
    )

    if evaluation_result is None:

        raise AssertionError(
            'Evaluation returned no result.'
        )

    if not evaluation_result.get(
        'testing_rows'
    ):

        raise AssertionError(
            'Evaluation contains no test rows.'
        )

    if not evaluation_result.get(
        'testing_dates'
    ):

        raise AssertionError(
            'Evaluation contains no test dates.'
        )

    print(
        'Chronological evaluation: PASSED'
    )

    # ------------------------------------------------------
    # 7. Verify training/test date separation
    # ------------------------------------------------------

    training_dates = (
        evaluation_result.get(
            'training_dates',
            [],
        )
    )

    testing_dates = (
        evaluation_result.get(
            'testing_dates',
            [],
        )
    )

    if training_dates and testing_dates:

        if max(training_dates) >= min(
            testing_dates
        ):

            raise AssertionError(
                'Training/test temporal '
                'separation failed.'
            )

    print(
        'Temporal separation: PASSED'
    )

    # ------------------------------------------------------
    # Final
    # ------------------------------------------------------

    print()

    print(
        '========== TRAINING PIPELINE TEST PASSED =========='
    )


if __name__ == '__main__':

    test_training_pipeline()
    