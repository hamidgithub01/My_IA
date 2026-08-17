from ml.evaluation.error_analysis import (
    ERROR_ANALYSIS_VALID,
    analyze_regression_errors,
    analyze_classification_errors,
    analyze_errors,
    analyze_evaluation_result,
)


# ==========================================================
# TEST HELPERS
# ==========================================================

def assert_close(
    actual,
    expected,
    tolerance=1e-9,
):
    """
    Assert that two numeric values are approximately equal.
    """

    assert abs(
        actual - expected
    ) < tolerance, (
        f'Expected {expected}, got {actual}'
    )


# ==========================================================
# REGRESSION TEST
# ==========================================================

def test_regression_error_analysis():
    """
    Test standard regression error analysis.
    """

    print()
    print(
        '========== REGRESSION ERROR ANALYSIS TEST =========='
    )

    actual = [
        100.0,
        200.0,
        300.0,
    ]

    predicted = [
        110.0,
        180.0,
        300.0,
    ]

    result = analyze_regression_errors(
        actual,
        predicted,
    )

    print()
    print(
        'Regression result:'
    )

    print(
        result
    )

    # ------------------------------------------------------
    # Basic result
    # ------------------------------------------------------

    assert result['status'] == (
        ERROR_ANALYSIS_VALID
    )

    assert result['observation_count'] == 3

    # ------------------------------------------------------
    # Individual errors
    # ------------------------------------------------------

    assert_close(
        result['observations'][0]['error'],
        10.0,
    )

    assert_close(
        result['observations'][1]['error'],
        -20.0,
    )

    assert_close(
        result['observations'][2]['error'],
        0.0,
    )

    # ------------------------------------------------------
    # Absolute errors
    # ------------------------------------------------------

    assert_close(
        result['observations'][0]['absolute_error'],
        10.0,
    )

    assert_close(
        result['observations'][1]['absolute_error'],
        20.0,
    )

    assert_close(
        result['observations'][2]['absolute_error'],
        0.0,
    )

    # ------------------------------------------------------
    # Aggregate statistics
    # ------------------------------------------------------

    assert_close(
        result['mean_error'],
        -10.0 / 3.0,
    )

    assert_close(
        result['mean_absolute_error'],
        10.0,
    )

    assert_close(
        result['max_absolute_error'],
        20.0,
    )

    assert_close(
        result['min_absolute_error'],
        0.0,
    )

    # ------------------------------------------------------
    # Percentage error
    # ------------------------------------------------------

    expected_mean_percentage = (
        (
            10.0
            + 10.0
            + 0.0
        )
        / 3.0
    )

    assert_close(
        result['mean_percentage_error'],
        expected_mean_percentage,
    )

    assert_close(
        result['max_percentage_error'],
        10.0,
    )

    # ------------------------------------------------------
    # Direction of errors
    # ------------------------------------------------------

    assert result['over_predictions'] == 1

    assert result['under_predictions'] == 1

    assert result['exact_predictions'] == 1

    # ------------------------------------------------------
    # Largest / smallest errors
    # ------------------------------------------------------

    assert (
        result['largest_error']['index']
        == 1
    )

    assert (
        result['smallest_error']['index']
        == 2
    )

    print()
    print(
        'Regression error analysis: PASSED'
    )


# ==========================================================
# ZERO TARGET TEST
# ==========================================================

def test_regression_zero_targets():
    """
    Verify that zero is treated as a valid actual value.

    Percentage error is undefined when actual == 0,
    therefore percentage_error must be None.
    """

    print()
    print(
        '========== ZERO TARGET TEST =========='
    )

    actual = [
        0.0,
        100.0,
        0.0,
    ]

    predicted = [
        20.0,
        110.0,
        0.0,
    ]

    result = analyze_regression_errors(
        actual,
        predicted,
    )

    print()
    print(
        'Zero-target result:'
    )

    print(
        result
    )

    # Zero must remain a valid observation.
    assert result['observation_count'] == 3

    # First observation:
    # actual = 0
    # predicted = 20
    assert_close(
        result['observations'][0]['error'],
        20.0,
    )

    assert_close(
        result['observations'][0]['absolute_error'],
        20.0,
    )

    assert (
        result['observations'][0]['percentage_error']
        is None
    )

    # Third observation:
    # actual = 0
    # predicted = 0
    assert (
        result['observations'][2]['percentage_error']
        is None
    )

    # Only the non-zero actual value contributes to
    # percentage-error statistics.
    assert_close(
        result['mean_percentage_error'],
        10.0,
    )

    print()
    print(
        'Zero-target handling: PASSED'
    )


# ==========================================================
# OVER / UNDER PREDICTION TEST
# ==========================================================

def test_over_under_predictions():
    """
    Verify that the system correctly counts over-predictions,
    under-predictions, and exact predictions.
    """

    print()
    print(
        '========== OVER / UNDER PREDICTION TEST =========='
    )

    actual = [
        100.0,
        100.0,
        100.0,
        100.0,
    ]

    predicted = [
        120.0,
        80.0,
        100.0,
        130.0,
    ]

    result = analyze_regression_errors(
        actual,
        predicted,
    )

    print()
    print(
        'Direction result:'
    )

    print(
        result
    )

    assert result['over_predictions'] == 2

    assert result['under_predictions'] == 1

    assert result['exact_predictions'] == 1

    print()
    print(
        'Over/under prediction handling: PASSED'
    )


# ==========================================================
# PERFECT REGRESSION TEST
# ==========================================================

def test_perfect_regression():
    """
    Verify behavior when every prediction is exact.
    """

    print()
    print(
        '========== PERFECT REGRESSION TEST =========='
    )

    actual = [
        10.0,
        20.0,
        30.0,
    ]

    predicted = [
        10.0,
        20.0,
        30.0,
    ]

    result = analyze_regression_errors(
        actual,
        predicted,
    )

    print()
    print(
        'Perfect regression result:'
    )

    print(
        result
    )

    assert_close(
        result['mean_error'],
        0.0,
    )

    assert_close(
        result['mean_absolute_error'],
        0.0,
    )

    assert_close(
        result['max_absolute_error'],
        0.0,
    )

    assert_close(
        result['min_absolute_error'],
        0.0,
    )

    assert_close(
        result['mean_percentage_error'],
        0.0,
    )

    assert_close(
        result['max_percentage_error'],
        0.0,
    )

    assert result['over_predictions'] == 0

    assert result['under_predictions'] == 0

    assert result['exact_predictions'] == 3

    print()
    print(
        'Perfect regression handling: PASSED'
    )


# ==========================================================
# BINARY CLASSIFICATION TEST
# ==========================================================

def test_binary_classification_error_analysis():
    """
    Test binary classification error analysis.
    """

    print()
    print(
        '========== BINARY CLASSIFICATION TEST =========='
    )

    actual = [
        0,
        1,
        1,
        0,
    ]

    predicted = [
        0,
        1,
        0,
        0,
    ]

    result = analyze_classification_errors(
        actual,
        predicted,
    )

    print()
    print(
        'Binary classification result:'
    )

    print(
        result
    )

    assert result['status'] == (
        ERROR_ANALYSIS_VALID
    )

    assert result['observation_count'] == 4

    assert result['correct_predictions'] == 3

    assert result['incorrect_predictions'] == 1

    assert_close(
        result['accuracy'],
        0.75,
    )

    assert_close(
        result['error_rate'],
        0.25,
    )

    # Individual observations
    assert (
        result['observations'][0]['correct']
        is True
    )

    assert (
        result['observations'][2]['correct']
        is False
    )

    print()
    print(
        'Binary classification error analysis: PASSED'
    )


# ==========================================================
# MULTICLASS TEST
# ==========================================================

def test_multiclass_classification_error_analysis():
    """
    Test multiclass classification error analysis.
    """

    print()
    print(
        '========== MULTICLASS CLASSIFICATION TEST =========='
    )

    actual = [
        0,
        1,
        2,
        0,
        1,
        2,
    ]

    predicted = [
        0,
        1,
        1,
        0,
        2,
        2,
    ]

    result = analyze_classification_errors(
        actual,
        predicted,
    )

    print()
    print(
        'Multiclass result:'
    )

    print(
        result
    )

    assert result['observation_count'] == 6

    assert result['correct_predictions'] == 4

    assert result['incorrect_predictions'] == 2

    assert_close(
        result['accuracy'],
        4.0 / 6.0,
    )

    assert_close(
        result['error_rate'],
        2.0 / 6.0,
    )

    print()
    print(
        'Multiclass error analysis: PASSED'
    )


# ==========================================================
# UNIFIED ANALYSIS TEST
# ==========================================================

def test_unified_error_analysis():
    """
    Verify that analyze_errors correctly selects the
    appropriate analysis based on target task.
    """

    print()
    print(
        '========== UNIFIED ERROR ANALYSIS TEST =========='
    )

    regression_result = analyze_errors(
        [100.0, 200.0],
        [110.0, 190.0],
        'regression',
    )

    assert (
        regression_result['status']
        == ERROR_ANALYSIS_VALID
    )

    assert (
        'mean_absolute_error'
        in regression_result
    )

    classification_result = analyze_errors(
        [0, 1, 1],
        [0, 1, 0],
        'classification',
    )

    assert (
        classification_result['status']
        == ERROR_ANALYSIS_VALID
    )

    assert (
        'accuracy'
        in classification_result
    )

    categorical_result = analyze_errors(
        [0, 1, 2],
        [0, 2, 2],
        'categorical',
    )

    assert (
        categorical_result['status']
        == ERROR_ANALYSIS_VALID
    )

    assert (
        'accuracy'
        in categorical_result
    )

    print()
    print(
        'Unified error analysis: PASSED'
    )


# ==========================================================
# EVALUATION RESULT INTEGRATION TEST
# ==========================================================

def test_evaluation_result_integration():
    """
    Verify integration with evaluate_model() output.
    """

    print()
    print(
        '========== EVALUATION RESULT INTEGRATION TEST =========='
    )

    evaluation_result = {

        'target_name':
            'Target_Expense_Total_1D',

        'target_task':
            'regression',

        'target_type':
            'numeric',

        'actual_values': [
            100.0,
            200.0,
            300.0,
        ],

        'predicted_values': [
            110.0,
            180.0,
            300.0,
        ],
    }

    result = analyze_evaluation_result(
        evaluation_result
    )

    print()
    print(
        'Integration result:'
    )

    print(
        result
    )

    assert result['status'] == (
        ERROR_ANALYSIS_VALID
    )

    assert result['observation_count'] == 3

    assert_close(
        result['mean_absolute_error'],
        10.0,
    )

    print()
    print(
        'Evaluation result integration: PASSED'
    )


# ==========================================================
# INVALID INPUT TEST
# ==========================================================

def test_invalid_inputs():
    """
    Verify that invalid input is rejected safely.
    """

    print()
    print(
        '========== INVALID INPUT TEST =========='
    )

    # ------------------------------------------------------
    # Missing actual values
    # ------------------------------------------------------

    try:

        analyze_regression_errors(
            None,
            [1, 2],
        )

        assert False, (
            'Expected ValueError for missing actual values.'
        )

    except ValueError:

        pass

    # ------------------------------------------------------
    # Missing predicted values
    # ------------------------------------------------------

    try:

        analyze_regression_errors(
            [1, 2],
            None,
        )

        assert False, (
            'Expected ValueError for missing predictions.'
        )

    except ValueError:

        pass

    # ------------------------------------------------------
    # Different lengths
    # ------------------------------------------------------

    try:

        analyze_regression_errors(
            [1, 2, 3],
            [1, 2],
        )

        assert False, (
            'Expected ValueError for different lengths.'
        )

    except ValueError:

        pass

    # ------------------------------------------------------
    # Empty input
    # ------------------------------------------------------

    try:

        analyze_regression_errors(
            [],
            [],
        )

        assert False, (
            'Expected ValueError for empty input.'
        )

    except ValueError:

        pass

    # ------------------------------------------------------
    # Non-numeric regression value
    # ------------------------------------------------------

    try:

        analyze_regression_errors(
            [100, 'invalid'],
            [100, 110],
        )

        assert False, (
            'Expected ValueError for non-numeric value.'
        )

    except ValueError:

        pass

    # ------------------------------------------------------
    # Unsupported target task
    # ------------------------------------------------------

    try:

        analyze_errors(
            [1, 2],
            [1, 2],
            'unsupported_task',
        )

        assert False, (
            'Expected ValueError for unsupported task.'
        )

    except ValueError:

        pass

    # ------------------------------------------------------
    # Missing evaluation result
    # ------------------------------------------------------

    try:

        analyze_evaluation_result(
            None
        )

        assert False, (
            'Expected ValueError for missing evaluation result.'
        )

    except ValueError:

        pass

    print()
    print(
        'Invalid input handling: PASSED'
    )


# ==========================================================
# MAIN TEST SUITE
# ==========================================================

if __name__ == '__main__':

    print()
    print(
        '=================================================='
    )

    print(
        '          ERROR ANALYSIS MODULE TEST SUITE'
    )

    print(
        '=================================================='
    )

    test_regression_error_analysis()

    test_regression_zero_targets()

    test_over_under_predictions()

    test_perfect_regression()

    test_binary_classification_error_analysis()

    test_multiclass_classification_error_analysis()

    test_unified_error_analysis()

    test_evaluation_result_integration()

    test_invalid_inputs()

    print()
    print(
        '=================================================='
    )

    print(
        '       ALL ERROR ANALYSIS TESTS PASSED'
    )

    print(
        '=================================================='
    )