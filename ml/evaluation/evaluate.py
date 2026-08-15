
from sklearn.linear_model import LinearRegression

from ml.features.build import (
    build_training_dataset,
)

from ml.evaluation.metrics import (
    calculate_metrics,
)


# ==========================================================
# EVALUATION STATUS
# ==========================================================

EVALUATION_VALID = 'valid'
EVALUATION_INSUFFICIENT_TRAINING_VARIATION = (
    'insufficient_training_variation'
)


# ==========================================================
# MODEL EVALUATION
# ==========================================================

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

    Important:

        A target value of 0.0 is a valid real observation.

        Zero is NEVER treated as missing.

        If the training target contains only one unique value,
        the model may legitimately learn a constant prediction.
        In that case, the evaluation is reported as having
        insufficient target variation rather than treating the
        resulting R² as a normal model-quality score.
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
    # Training target analysis
    # ------------------------------------------------------

    training_target_values = [
        float(
            row['Target_Expense_Total']
        )
        for row in train_data
    ]

    unique_training_targets = sorted(
        set(training_target_values)
    )

    training_target_unique_count = len(
        unique_training_targets
    )

    training_target_has_variation = (
        training_target_unique_count > 1
    )

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

    y_pred_raw = model.predict(
        X_test
    )

    y_pred = [
        max(
            0.0,
            float(value),
        )
        for value in y_pred_raw
    ]

    # ------------------------------------------------------
    # Metrics
    # ------------------------------------------------------

    metrics = calculate_metrics(
        y_true,
        y_pred,
    )

    # ------------------------------------------------------
    # Evaluation status
    # ------------------------------------------------------

    if not training_target_has_variation:

        evaluation_status = (
            EVALUATION_INSUFFICIENT_TRAINING_VARIATION
        )

        # R² is not a meaningful model-quality indicator
        # when the training period contains only one unique
        # target value.
        metrics['r_squared'] = None

    else:

        evaluation_status = EVALUATION_VALID

    # ------------------------------------------------------
    # Results
    # ------------------------------------------------------

    return {
        'metrics': metrics,

        'evaluation_status':
            evaluation_status,

        'evaluation_valid':
            evaluation_status == EVALUATION_VALID,

        'training_target_values':
            training_target_values,

        'training_target_unique_values':
            unique_training_targets,

        'training_target_unique_count':
            training_target_unique_count,

        'training_target_has_variation':
            training_target_has_variation,

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

        'predicted_values':
            y_pred,
    }
