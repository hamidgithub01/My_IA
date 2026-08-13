from sklearn.linear_model import LinearRegression

from ml.features.build import (
    build_training_dataset,
)

from ml.evaluation.metrics import (
    calculate_metrics,
)


def evaluate_model(
    training_result=None,
    test_ratio=0.2,
    min_test_rows=2,
):
    """
    Evaluate the forecasting model using chronological data.

    Older records are used for training.
    Newer records are used only for testing.

    The data is never shuffled.

    A valid R² evaluation requires at least two test rows.
    """

    data = build_training_dataset()

    if len(data) < 4:
        raise ValueError(
            'At least four training records are required '
            'for chronological evaluation.'
        )

    # ------------------------------------------------------
    # Sort chronologically
    # ------------------------------------------------------

    data = sorted(
        data,
        key=lambda row: row['Date'],
    )

    # ------------------------------------------------------
    # Determine test size
    # ------------------------------------------------------

    calculated_test_size = int(
        len(data) * test_ratio
    )

    test_size = max(
        min_test_rows,
        calculated_test_size,
    )

    # Keep at least two rows for training.
    if len(data) - test_size < 2:
        test_size = len(data) - 2

    if test_size < min_test_rows:
        raise ValueError(
            'Not enough data for a valid chronological '
            'train/test evaluation.'
        )

    train_size = len(data) - test_size

    train_data = data[:train_size]
    test_data = data[train_size:]

    # ------------------------------------------------------
    # Train model only on the historical training period
    # ------------------------------------------------------

    if training_result is None:

        feature_names = [
            key
            for key in train_data[0].keys()
            if key not in {
                'Date',
                'Target_Expense_Total',
            }
        ]

        X_train = []

        y_train = []

        for row in train_data:

            X_train.append([
                float(
                    row.get(feature, 0.0)
                    or 0.0
                )
                for feature in feature_names
            ])

            y_train.append(
                float(
                    row['Target_Expense_Total']
                )
            )

        model = LinearRegression()

        model.fit(
            X_train,
            y_train,
        )

        training_result = {
            'model': model,
            'feature_names': feature_names,
            'training_rows': len(train_data),
            'target_name': 'Target_Expense_Total',
        }

    model = training_result['model']

    feature_names = training_result[
        'feature_names'
    ]

    # ------------------------------------------------------
    # Test on unseen future records
    # ------------------------------------------------------

    X_test = []

    y_true = []

    dates = []

    for row in test_data:

        X_test.append([
            float(
                row.get(feature, 0.0)
                or 0.0
            )
            for feature in feature_names
        ])

        y_true.append(
            float(
                row['Target_Expense_Total']
            )
        )

        dates.append(
            row['Date']
        )

    y_pred = model.predict(
        X_test
    )

    # ------------------------------------------------------
    # Metrics
    # ------------------------------------------------------

    metrics = calculate_metrics(
        y_true,
        y_pred,
    )

    # ------------------------------------------------------
    # Results
    # ------------------------------------------------------

    return {
        'metrics': metrics,

        'training_rows':
            len(train_data),

        'testing_rows':
            len(test_data),

        'feature_names':
            feature_names,

        'training_dates': [
            row['Date']
            for row in train_data
        ],

        'testing_dates':
            dates,

        'actual_values':
            y_true,

        'predicted_values': [
            max(
                0.0,
                float(value),
            )
            for value in y_pred
        ],
    }