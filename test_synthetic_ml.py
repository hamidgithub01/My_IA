from datetime import date, timedelta
from unittest.mock import patch

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
                'Date': current_date,

                # --------------------------------------------------
                # Feature intentionally correlated with target.
                # The model should learn:
                #
                # expense = 100 + 10 * Synthetic_Expense_Signal
                # --------------------------------------------------

                'Synthetic_Expense_Signal':
                    float(index),

                # --------------------------------------------------
                # Additional feature
                # --------------------------------------------------

                'Day_of_Week':
                    float(current_date.weekday()),

                # --------------------------------------------------
                # Real target
                # --------------------------------------------------

                'Target_Expense_Total':
                    expense,
            }
        )

    return rows


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

    assert len(synthetic_dataset) == 10

    target_values = [
        row['Target_Expense_Total']
        for row in synthetic_dataset
    ]

    unique_targets = set(
        target_values
    )

    assert len(unique_targets) > 1

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

    assert dates == sorted(dates)

    print()
    print(
        'Chronological ordering: PASSED'
    )

    # ------------------------------------------------------
    # Replace the real database-backed dataset
    # temporarily.
    #
    # The actual evaluate_model() implementation is still
    # being executed.
    # ------------------------------------------------------

    with patch(
        'ml.evaluation.evaluate.build_training_dataset',
        return_value=synthetic_dataset,
    ):

        result = evaluate_model(
            training_result=None,
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

    assert result[
        'evaluation_valid'
    ] is True

    print(
        'Evaluation status: VALID'
    )

    # ------------------------------------------------------
    # Training target variation
    # ------------------------------------------------------

    assert result[
        'training_target_has_variation'
    ] is True

    assert result[
        'training_target_unique_count'
    ] > 1

    print(
        'Training target variation: PASSED'
    )

    # ------------------------------------------------------
    # Dataset split
    # ------------------------------------------------------

    assert result[
        'training_rows'
    ] == 8

    assert result[
        'testing_rows'
    ] == 2

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

    print(
        'Temporal separation: PASSED'
    )

    # ------------------------------------------------------
    # Metrics
    # ------------------------------------------------------

    metrics = result['metrics']

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
    # R² must now be a real value.
    #
    # Unlike the real empty database, the synthetic
    # training data contains target variation.
    # ------------------------------------------------------

    assert metrics[
        'r_squared'
    ] is not None

    # The synthetic relationship is intentionally simple,
    # so the model should achieve an excellent score.
    assert metrics[
        'r_squared'
    ] > 0.90

    # ------------------------------------------------------
    # Predictions
    # ------------------------------------------------------

    actual_values = result[
        'actual_values'
    ]

    predicted_values = result[
        'predicted_values'
    ]

    assert len(actual_values) == 2

    assert len(predicted_values) == 2

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

        assert predicted >= 0.0

        # Predictions should be reasonably close to
        # the known synthetic target values.
        assert abs(
            actual - predicted
        ) < 25.0

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