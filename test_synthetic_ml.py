from datetime import date, timedelta

from sklearn.linear_model import LinearRegression

from ml.evaluation.evaluate import (
    evaluate_model,
    EVALUATION_VALID,
)


# ==========================================================
# SYNTHETIC DATASET
# ==========================================================

def build_synthetic_dataset():

    rows = []

    start_date = date(2026, 1, 1)

    # ------------------------------------------------------
    # Synthetic relationship:
    #
    # Expense = 100 + (day_index * 10)
    #
    # This creates real target variation.
    # ------------------------------------------------------

    for index in range(10):

        current_date = (
            start_date
            + timedelta(days=index)
        )

        expense = 100.0 + (
            index * 10.0
        )

        rows.append(
            {
                'Date':
                    current_date,

                'Synthetic_Expense_Signal':
                    float(index),

                'Day_of_Week':
                    float(
                        current_date.weekday()
                    ),

                'Target_Expense_Total':
                    expense,
            }
        )

    return rows


# ==========================================================
# BUILD SYNTHETIC TRAINING RESULT
# ==========================================================

def build_synthetic_training_result():

    dataset = build_synthetic_dataset()

    # ------------------------------------------------------
    # Chronological split
    #
    # 10 rows:
    #
    # Training = first 8
    # Testing  = last 2
    # ------------------------------------------------------

    training_data = dataset[:8]

    test_data = dataset[8:]

    feature_names = [
        'Synthetic_Expense_Signal',
        'Day_of_Week',
    ]

    X_train = [
        [
            row['Synthetic_Expense_Signal'],
            row['Day_of_Week'],
        ]
        for row in training_data
    ]

    y_train = [
        row['Target_Expense_Total']
        for row in training_data
    ]

    X_test = [
        [
            row['Synthetic_Expense_Signal'],
            row['Day_of_Week'],
        ]
        for row in test_data
    ]

    y_test = [
        row['Target_Expense_Total']
        for row in test_data
    ]

    # ------------------------------------------------------
    # Use the same regression model family used by the
    # project.
    # ------------------------------------------------------

    model = LinearRegression()

    model.fit(
        X_train,
        y_train,
    )

    # ------------------------------------------------------
    # Construct the same contract produced by
    # train_target_model().
    # ------------------------------------------------------

    return {

        'model':
            model,

        'target_name':
            'Target_Expense_Total',

        'target_task':
            'regression',

        'target_type':
            'numeric',

        'model_type':
            'regression',

        'algorithm':
            model.__class__.__name__,

        'class_count':
            None,

        'classes':
            None,

        'feature_names':
            feature_names,

        'training_rows':
            len(X_train),

        'test_rows':
            len(X_test),

        'training_data':
            training_data,

        'test_data':
            test_data,

        'X_train':
            X_train,

        'y_train':
            y_train,

        'X_test':
            X_test,

        'y_test':
            y_test,

        'validation_report':
            {},
    }


# ==========================================================
# TEST
# ==========================================================

def test_synthetic_training_and_evaluation():

    print()
    print(
        '================================================='
    )
    print(
        '       SYNTHETIC ML TRAINING VALIDATION'
    )
    print(
        '================================================='
    )
    print()

    synthetic_dataset = (
        build_synthetic_dataset()
    )

    # ------------------------------------------------------
    # Dataset validation
    # ------------------------------------------------------

    assert len(
        synthetic_dataset
    ) == 10

    target_values = [
        row['Target_Expense_Total']
        for row in synthetic_dataset
    ]

    unique_targets = set(
        target_values
    )

    assert len(
        unique_targets
    ) > 1

    print(
        f'Synthetic rows: '
        f'{len(synthetic_dataset)}'
    )

    print(
        f'Unique target values: '
        f'{len(unique_targets)}'
    )

    print(
        f'Target values: '
        f'{target_values}'
    )

    # ------------------------------------------------------
    # Chronological validation
    # ------------------------------------------------------

    dates = [
        row['Date']
        for row in synthetic_dataset
    ]

    assert dates == sorted(
        dates
    )

    print()
    print(
        'Chronological ordering: PASSED'
    )

    # ------------------------------------------------------
    # Build synthetic training result
    # ------------------------------------------------------

    training_result = (
        build_synthetic_training_result()
    )

    assert (
        training_result['training_rows']
        == 8
    )

    assert (
        training_result['test_rows']
        == 2
    )

    # ------------------------------------------------------
    # Actual Evaluation layer
    #
    # No database.
    # No dataset rebuilding.
    # No retraining inside evaluate_model().
    # ------------------------------------------------------

    result = evaluate_model(
        training_result=training_result,
        test_ratio=0.2,
        min_test_rows=2,
    )

    # ------------------------------------------------------
    # Evaluation status
    # ------------------------------------------------------

    assert (
        result['evaluation_status']
        == EVALUATION_VALID
    )

    assert (
        result['evaluation_valid']
        is True
    )

    print(
        'Evaluation status: VALID'
    )

    # ------------------------------------------------------
    # Training target variation
    # ------------------------------------------------------

    assert (
        result[
            'training_target_has_variation'
        ]
        is True
    )

    assert (
        result[
            'training_target_unique_count'
        ]
        > 1
    )

    print(
        'Training target variation: PASSED'
    )

    # ------------------------------------------------------
    # Dataset split
    # ------------------------------------------------------

    assert (
        result['training_rows']
        == 8
    )

    assert (
        result['testing_rows']
        == 2
    )

    print()
    print(
        f"Training rows: "
        f"{result['training_rows']}"
    )

    print(
        f"Testing rows: "
        f"{result['testing_rows']}"
    )

    # ------------------------------------------------------
    # Temporal separation
    # ------------------------------------------------------

    last_training_date = (
        result['training_dates'][-1]
    )

    first_testing_date = (
        result['testing_dates'][0]
    )

    assert (
        first_testing_date
        > last_training_date
    )

    assert (
        result[
            'chronological_boundary_valid'
        ]
        is True
    )

    print(
        'Temporal separation: PASSED'
    )

    # ------------------------------------------------------
    # Metrics
    # ------------------------------------------------------

    metrics = result[
        'metrics'
    ]

    print()
    print(
        f"MAE: "
        f"{metrics['mae']:.4f}"
    )

    print(
        f"RMSE: "
        f"{metrics['rmse']:.4f}"
    )

    print(
        f"R²: "
        f"{metrics['r_squared']:.4f}"
    )

    # ------------------------------------------------------
    # R² must be a real value.
    # ------------------------------------------------------

    assert (
        metrics['r_squared']
        is not None
    )

    assert (
        metrics['r_squared']
        > 0.90
    )

    # ------------------------------------------------------
    # Predictions
    # ------------------------------------------------------

    actual_values = result[
        'actual_values'
    ]

    predicted_values = result[
        'predicted_values'
    ]

    assert len(
        actual_values
    ) == 2

    assert len(
        predicted_values
    ) == 2

    print()
    print(
        '========== ACTUAL vs PREDICTED =========='
    )

    for actual, predicted in zip(
        actual_values,
        predicted_values,
    ):

        print(
            f'Actual: {actual:.2f} | '
            f'Predicted: {predicted:.2f}'
        )

    # ------------------------------------------------------
    # Prediction quality
    # ------------------------------------------------------

    for actual, predicted in zip(
        actual_values,
        predicted_values,
    ):

        assert (
            predicted >= 0.0
        )

        assert (
            abs(
                actual - predicted
            )
            < 25.0
        )

    print()
    print(
        'Prediction quality: PASSED'
    )

    # ------------------------------------------------------
    # Final result
    # ------------------------------------------------------

    print()
    print(
        '================================================='
    )

    print(
        'SYNTHETIC ML TEST: PASSED'
    )

    print(
        'The evaluation pipeline successfully learned '
        'from variable target values.'
    )

    print(
        'The real database was not used.'
    )

    print(
        '================================================='
    )

    print()


# ==========================================================
# DIRECT EXECUTION
# ==========================================================

if __name__ == '__main__':

    test_synthetic_training_and_evaluation()