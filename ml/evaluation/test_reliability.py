from ml.evaluation.reliability import (
    RELIABILITY_VALID,
    RELIABILITY_HIGH,
    RELIABILITY_MEDIUM,
    RELIABILITY_LOW,
    RELIABILITY_UNKNOWN,
    analyze_regression_reliability,
    analyze_classification_reliability,
    calculate_calibration_error,
    analyze_reliability,
    analyze_evaluation_reliability,
    determine_reliability_level,
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
# RELIABILITY LEVEL TEST
# ==========================================================

def test_reliability_levels():
    """
    Test reliability level classification.
    """

    assert (
        determine_reliability_level(
            20,
            0.90,
        )
        == RELIABILITY_HIGH
    )

    assert (
        determine_reliability_level(
            20,
            0.70,
        )
        == RELIABILITY_MEDIUM
    )

    assert (
        determine_reliability_level(
            20,
            0.40,
        )
        == RELIABILITY_LOW
    )

    # Too few observations.
    assert (
        determine_reliability_level(
            5,
            0.99,
        )
        == RELIABILITY_UNKNOWN
    )


# ==========================================================
# REGRESSION RELIABILITY
# ==========================================================

def test_regression_reliability():
    """
    Test basic regression reliability analysis.
    """

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

    result = analyze_regression_reliability(
        actual,
        predicted,
        minimum_sample_count=2,
    )

    assert (
        result['status']
        == RELIABILITY_VALID
    )

    assert result['sample_count'] == 3

    assert_close(
        result['mae'],
        10.0,
    )

    expected_rmse = (
        (
            100.0
            + 400.0
            + 0.0
        )
        / 3.0
    ) ** 0.5

    assert_close(
        result['rmse'],
        expected_rmse,
    )

    assert_close(
        result['mean_error'],
        -10.0 / 3.0,
    )


# ==========================================================
# REGRESSION WITHOUT THRESHOLDS
# ==========================================================

def test_regression_without_thresholds():
    """
    Regression reliability must not invent an arbitrary
    business threshold.
    """

    result = analyze_regression_reliability(
        [100, 200, 300],
        [100, 200, 300],
        minimum_sample_count=2,
    )

    assert (
        result['quality_score']
        is None
    )

    assert (
        result['reliability_level']
        == RELIABILITY_UNKNOWN
    )


# ==========================================================
# REGRESSION WITH THRESHOLDS
# ==========================================================

def test_regression_with_thresholds():
    """
    Test threshold-based regression reliability.
    """

    result = analyze_regression_reliability(
        [100, 100, 100, 100],
        [100, 100, 100, 100],
        maximum_acceptable_mae=20,
        maximum_acceptable_rmse=20,
        minimum_sample_count=2,
    )

    assert_close(
        result['quality_score'],
        1.0,
    )

    assert (
        result['reliability_level']
        == RELIABILITY_HIGH
    )


# ==========================================================
# BINARY CLASSIFICATION
# ==========================================================

def test_binary_classification_reliability():
    """
    Test binary classification reliability.
    """

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

    result = analyze_classification_reliability(
        actual,
        predicted,
        minimum_sample_count=2,
    )

    assert (
        result['status']
        == RELIABILITY_VALID
    )

    assert result['sample_count'] == 4

    assert_close(
        result['accuracy'],
        0.75,
    )

    assert_close(
        result['error_rate'],
        0.25,
    )

    assert_close(
        result['quality_score'],
        0.75,
    )

    assert (
        result['reliability_level']
        == RELIABILITY_MEDIUM
    )

    assert (
        result['calibration_available']
        is False
    )


# ==========================================================
# MULTICLASS CLASSIFICATION
# ==========================================================

def test_multiclass_classification_reliability():
    """
    Classification reliability must work for multiclass
    targets as well.
    """

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

    result = analyze_classification_reliability(
        actual,
        predicted,
        minimum_sample_count=2,
    )

    assert (
        result['status']
        == RELIABILITY_VALID
    )

    assert result['sample_count'] == 6

    assert_close(
        result['accuracy'],
        4.0 / 6.0,
    )

    assert_close(
        result['error_rate'],
        2.0 / 6.0,
    )


# ==========================================================
# CALIBRATION ERROR
# ==========================================================

def test_calibration_error():
    """
    Test Expected Calibration Error calculation.
    """

    actual = [
        1,
        1,
        0,
        0,
    ]

    predicted_probabilities = [
        0.9,
        0.8,
        0.2,
        0.1,
    ]

    result = calculate_calibration_error(
        actual,
        predicted_probabilities,
        number_of_bins=2,
    )

    assert result['sample_count'] == 4

    assert result['number_of_bins'] == 2

    assert result['ece'] >= 0.0

    assert result['ece'] <= 1.0

    assert len(
        result['bins']
    ) > 0


# ==========================================================
# CALIBRATED CLASSIFICATION
# ==========================================================

def test_classification_with_calibration():
    """
    Test classification reliability when probability
    information is available.
    """

    actual = [
        1,
        1,
        0,
        0,
    ]

    predicted = [
        1,
        1,
        0,
        0,
    ]

    probabilities = [
        0.9,
        0.8,
        0.8,
        0.9,
    ]

    result = analyze_classification_reliability(
        actual,
        predicted,
        predicted_probabilities=probabilities,
        minimum_sample_count=2,
    )

    assert (
        result['calibration_available']
        is True
    )

    assert (
        result['expected_calibration_error']
        is not None
    )

    assert (
        result['calibration_quality_score']
        >= 0.0
    )

    assert (
        result['calibration_quality_score']
        <= 1.0
    )


# ==========================================================
# UNIFIED RELIABILITY
# ==========================================================

def test_unified_reliability():
    """
    Verify unified reliability dispatch.
    """

    regression_result = analyze_reliability(
        [100, 200, 300],
        [110, 180, 300],
        'regression',
        minimum_sample_count=2,
    )

    assert (
        regression_result['status']
        == RELIABILITY_VALID
    )

    classification_result = analyze_reliability(
        [0, 1, 1, 0],
        [0, 1, 0, 0],
        'classification',
        minimum_sample_count=2,
    )

    assert (
        classification_result['status']
        == RELIABILITY_VALID
    )

    categorical_result = analyze_reliability(
        [0, 1, 2],
        [0, 2, 2],
        'categorical',
        minimum_sample_count=2,
    )

    assert (
        categorical_result['status']
        == RELIABILITY_VALID
    )


# ==========================================================
# EVALUATION RESULT INTEGRATION
# ==========================================================

def test_evaluation_result_integration():
    """
    Verify integration with evaluate_model() output.
    """

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

    result = analyze_evaluation_reliability(
        evaluation_result,
        minimum_sample_count=2,
    )

    assert (
        result['status']
        == RELIABILITY_VALID
    )

    assert result['sample_count'] == 3

    assert_close(
        result['mae'],
        10.0,
    )


# ==========================================================
# INSUFFICIENT SAMPLE TEST
# ==========================================================

def test_insufficient_sample_reliability():
    """
    A very small test set must not automatically receive
    a strong reliability classification.
    """

    result = analyze_classification_reliability(
        [0, 1],
        [0, 1],
        minimum_sample_count=10,
    )

    assert (
        result['reliability_level']
        == RELIABILITY_UNKNOWN
    )


# ==========================================================
# INVALID INPUT TEST
# ==========================================================

def test_invalid_inputs():
    """
    Verify that invalid inputs are rejected safely.
    """

    # ------------------------------------------------------
    # Missing actual values
    # ------------------------------------------------------

    try:

        analyze_regression_reliability(
            None,
            [1, 2],
        )

        assert False

    except ValueError:

        pass

    # ------------------------------------------------------
    # Different lengths
    # ------------------------------------------------------

    try:

        analyze_regression_reliability(
            [1, 2, 3],
            [1, 2],
        )

        assert False

    except ValueError:

        pass

    # ------------------------------------------------------
    # Invalid probability
    # ------------------------------------------------------

    try:

        calculate_calibration_error(
            [0, 1],
            [0.2, 1.5],
        )

        assert False

    except ValueError:

        pass

    # ------------------------------------------------------
    # Invalid target task
    # ------------------------------------------------------

    try:

        analyze_reliability(
            [1, 2],
            [1, 2],
            'unsupported_task',
        )

        assert False

    except ValueError:

        pass

    # ------------------------------------------------------
    # Missing evaluation result
    # ------------------------------------------------------

    try:

        analyze_evaluation_reliability(
            None
        )

        assert False

    except ValueError:

        pass


# ==========================================================
# MAIN TEST SUITE
# ==========================================================

if __name__ == '__main__':

    print()
    print(
        '=================================================='
    )

    print(
        '       RELIABILITY MODULE TEST SUITE'
    )

    print(
        '=================================================='
    )

    test_reliability_levels()

    test_regression_reliability()

    test_regression_without_thresholds()

    test_regression_with_thresholds()

    test_binary_classification_reliability()

    test_multiclass_classification_reliability()

    test_calibration_error()

    test_classification_with_calibration()

    test_unified_reliability()

    test_evaluation_result_integration()

    test_insufficient_sample_reliability()

    test_invalid_inputs()

    print()
    print(
        '=================================================='
    )

    print(
        '       ALL RELIABILITY TESTS PASSED'
    )

    print(
        '=================================================='
    )