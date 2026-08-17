# ==========================================================
# ERROR ANALYSIS
# ==========================================================

import math


# ==========================================================
# CONSTANTS
# ==========================================================

ERROR_ANALYSIS_VALID = 'valid'
ERROR_ANALYSIS_INSUFFICIENT_DATA = (
    'insufficient_data'
)


# ==========================================================
# BASIC HELPERS
# ==========================================================

def _to_float(value):
    """
    Convert a numeric value to float.

    Raises:
        ValueError when the value is not finite numeric.
    """

    try:
        converted = float(value)

    except (
        TypeError,
        ValueError,
    ):

        raise ValueError(
            f'Value must be numeric: {value!r}'
        )

    if not math.isfinite(
        converted
    ):

        raise ValueError(
            f'Value must be finite: {value!r}'
        )

    return converted


def _validate_prediction_arrays(
    actual_values,
    predicted_values,
):
    """
    Validate actual and predicted value arrays.
    """

    if actual_values is None:

        raise ValueError(
            'actual_values are required.'
        )

    if predicted_values is None:

        raise ValueError(
            'predicted_values are required.'
        )

    if len(actual_values) == 0:

        raise ValueError(
            'At least one observation is required.'
        )

    if len(actual_values) != len(
        predicted_values
    ):

        raise ValueError(
            'actual_values and predicted_values '
            'must have the same length.'
        )


# ==========================================================
# REGRESSION ERROR ANALYSIS
# ==========================================================

def analyze_regression_errors(
    actual_values,
    predicted_values,
):
    """
    Analyze prediction errors for regression.

    For every observation the analysis calculates:

        actual
        predicted
        error
        absolute_error
        percentage_error

    Important:

        Zero is a valid actual value.

        Percentage error cannot be calculated when the
        actual value is zero. In that case percentage_error
        is returned as None.

    Returns:
        dict containing detailed error analysis.
    """

    _validate_prediction_arrays(
        actual_values,
        predicted_values,
    )

    observations = []

    errors = []
    absolute_errors = []
    percentage_errors = []

    for index, (
        actual,
        predicted,
    ) in enumerate(
        zip(
            actual_values,
            predicted_values,
        )
    ):

        actual = _to_float(
            actual
        )

        predicted = _to_float(
            predicted
        )

        error = (
            predicted - actual
        )

        absolute_error = abs(
            error
        )

        if actual != 0.0:

            percentage_error = (
                absolute_error
                / abs(actual)
                * 100.0
            )

            percentage_errors.append(
                percentage_error
            )

        else:

            percentage_error = None

        errors.append(
            error
        )

        absolute_errors.append(
            absolute_error
        )

        observations.append(
            {
                'index':
                    index,

                'actual':
                    actual,

                'predicted':
                    predicted,

                'error':
                    error,

                'absolute_error':
                    absolute_error,

                'percentage_error':
                    percentage_error,
            }
        )

    # ------------------------------------------------------
    # Aggregate error statistics
    # ------------------------------------------------------

    mean_error = (
        sum(errors)
        / len(errors)
    )

    mean_absolute_error = (
        sum(absolute_errors)
        / len(absolute_errors)
    )

    max_absolute_error = max(
        absolute_errors
    )

    min_absolute_error = min(
        absolute_errors
    )

    if percentage_errors:

        mean_percentage_error = (
            sum(percentage_errors)
            / len(percentage_errors)
        )

        max_percentage_error = max(
            percentage_errors
        )

    else:

        mean_percentage_error = None
        max_percentage_error = None

    # ------------------------------------------------------
    # Over / under prediction
    # ------------------------------------------------------

    over_predictions = sum(
        error > 0
        for error in errors
    )

    under_predictions = sum(
        error < 0
        for error in errors
    )

    exact_predictions = sum(
        error == 0
        for error in errors
    )

    # ------------------------------------------------------
    # Largest errors
    # ------------------------------------------------------

    largest_error_index = max(
        range(
            len(
                absolute_errors
            )
        ),
        key=lambda index:
            absolute_errors[index],
    )

    smallest_error_index = min(
        range(
            len(
                absolute_errors
            )
        ),
        key=lambda index:
            absolute_errors[index],
    )

    # ------------------------------------------------------
    # Final result
    # ------------------------------------------------------

    return {

        'status':
            ERROR_ANALYSIS_VALID,

        'observation_count':
            len(observations),

        'observations':
            observations,

        'mean_error':
            float(mean_error),

        'mean_absolute_error':
            float(mean_absolute_error),

        'max_absolute_error':
            float(max_absolute_error),

        'min_absolute_error':
            float(min_absolute_error),

        'mean_percentage_error':
            (
                float(
                    mean_percentage_error
                )
                if mean_percentage_error
                is not None
                else None
            ),

        'max_percentage_error':
            (
                float(
                    max_percentage_error
                )
                if max_percentage_error
                is not None
                else None
            ),

        'over_predictions':
            over_predictions,

        'under_predictions':
            under_predictions,

        'exact_predictions':
            exact_predictions,

        'largest_error':
            observations[
                largest_error_index
            ],

        'smallest_error':
            observations[
                smallest_error_index
            ],
    }


# ==========================================================
# CLASSIFICATION ERROR ANALYSIS
# ==========================================================

def analyze_classification_errors(
    actual_values,
    predicted_values,
):
    """
    Analyze prediction errors for classification.

    Classification errors are based on whether the predicted
    class matches the actual class.

    Returns:

        accuracy
        correct_predictions
        incorrect_predictions
        error_rate
        observations
    """

    _validate_prediction_arrays(
        actual_values,
        predicted_values,
    )

    observations = []

    correct_predictions = 0
    incorrect_predictions = 0

    for index, (
        actual,
        predicted,
    ) in enumerate(
        zip(
            actual_values,
            predicted_values,
        )
    ):

        correct = (
            actual == predicted
        )

        if correct:

            correct_predictions += 1

        else:

            incorrect_predictions += 1

        observations.append(
            {
                'index':
                    index,

                'actual':
                    actual,

                'predicted':
                    predicted,

                'correct':
                    correct,
            }
        )

    total = len(
        observations
    )

    accuracy = (
        correct_predictions
        / total
    )

    error_rate = (
        incorrect_predictions
        / total
    )

    return {

        'status':
            ERROR_ANALYSIS_VALID,

        'observation_count':
            total,

        'observations':
            observations,

        'correct_predictions':
            correct_predictions,

        'incorrect_predictions':
            incorrect_predictions,

        'accuracy':
            float(accuracy),

        'error_rate':
            float(error_rate),
    }


# ==========================================================
# UNIFIED ERROR ANALYSIS
# ==========================================================

def analyze_errors(
    actual_values,
    predicted_values,
    target_task,
):
    """
    Analyze prediction errors according to target task.

    Supported tasks:

        regression
        classification
        categorical

    Categorical targets are treated as classification
    for error-analysis purposes.
    """

    if target_task == 'regression':

        return analyze_regression_errors(
            actual_values,
            predicted_values,
        )

    if target_task in {
        'classification',
        'categorical',
    }:

        return analyze_classification_errors(
            actual_values,
            predicted_values,
        )

    raise ValueError(
        f'Unsupported target task: '
        f'{target_task}'
    )


# ==========================================================
# MODEL RESULT INTEGRATION
# ==========================================================

def analyze_evaluation_result(
    evaluation_result,
):
    """
    Run error analysis directly from an evaluation result.

    Expected evaluation_result fields:

        actual_values
        predicted_values
        target_task

    This keeps Error Analysis independent from the model
    training and evaluation implementation.
    """

    if evaluation_result is None:

        raise ValueError(
            'evaluation_result is required.'
        )

    actual_values = (
        evaluation_result.get(
            'actual_values'
        )
    )

    predicted_values = (
        evaluation_result.get(
            'predicted_values'
        )
    )

    target_task = (
        evaluation_result.get(
            'target_task'
        )
    )

    if target_task is None:

        raise ValueError(
            'evaluation_result does not contain '
            'target_task.'
        )

    return analyze_errors(
        actual_values,
        predicted_values,
        target_task,
    )


# ==========================================================
# SIMPLE TEST
# ==========================================================

if __name__ == '__main__':

    print()
    print(
        '========== ERROR ANALYSIS TEST =========='
    )

    regression_result = (
        analyze_regression_errors(
            [100, 200, 300],
            [110, 180, 300],
        )
    )

    print()
    print(
        'Regression analysis:'
    )

    print(
        regression_result
    )

    classification_result = (
        analyze_classification_errors(
            [0, 1, 1, 0],
            [0, 1, 0, 0],
        )
    )

    print()
    print(
        'Classification analysis:'
    )

    print(
        classification_result
    )

    print()
    print(
        '========== ERROR ANALYSIS TEST PASSED =========='
    )