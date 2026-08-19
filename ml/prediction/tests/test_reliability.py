
import pytest


from ml.prediction.reliability import (
    RELIABILITY_VALID,
    RELIABILITY_INSUFFICIENT_DATA,
    RELIABILITY_UNRELIABLE,
    RELIABILITY_HIGH,
    RELIABILITY_MEDIUM,
    RELIABILITY_LOW,
    calculate_absolute_errors,
    calculate_prediction_error,
    calculate_regression_reliability,
    calculate_classification_reliability,
    evaluate_prediction_reliability,
    monitor_prediction_reliability,
)


# ==========================================================
# ABSOLUTE ERRORS
# ==========================================================

def test_calculate_absolute_errors():
    """
    Absolute errors must be calculated correctly.
    """

    result = calculate_absolute_errors(
        [10.0, 20.0, 30.0],
        [8.0, 25.0, 30.0],
    )

    assert result == [
        2.0,
        5.0,
        0.0,
    ]


# ==========================================================
# REGRESSION ERROR
# ==========================================================

def test_calculate_prediction_error():
    """
    Regression error statistics must be correct.
    """

    result = calculate_prediction_error(
        [10.0, 20.0, 30.0],
        [8.0, 25.0, 30.0],
    )

    assert result[
        'mae'
    ] == pytest.approx(
        7.0 / 3.0
    )

    assert result[
        'max_absolute_error'
    ] == 5.0

    assert result[
        'mean_error'
    ] == pytest.approx(
        1.0
    )

    assert result[
        'sample_count'
    ] == 3


# ==========================================================
# HIGH REGRESSION RELIABILITY
# ==========================================================

def test_high_regression_reliability():
    """
    A large improvement over the baseline should produce
    high reliability.
    """

    result = calculate_regression_reliability(
        actual_values=[
            10.0,
            20.0,
            30.0,
            40.0,
        ],
        predicted_values=[
            10.5,
            19.5,
            30.5,
            39.5,
        ],
        baseline_mae=5.0,
    )

    assert result[
        'status'
    ] == RELIABILITY_VALID

    assert result[
        'reliability_level'
    ] == RELIABILITY_HIGH

    assert result[
        'reliability_score'
    ] > 0.80

    assert result[
        'mae'
    ] == pytest.approx(
        0.5
    )


# ==========================================================
# LOW REGRESSION RELIABILITY
# ==========================================================

def test_low_regression_reliability():
    """
    A model that is worse than the baseline must receive
    low reliability.
    """

    result = calculate_regression_reliability(
        actual_values=[
            10.0,
            20.0,
            30.0,
        ],
        predicted_values=[
            20.0,
            30.0,
            40.0,
        ],
        baseline_mae=5.0,
    )

    assert result[
        'status'
    ] == RELIABILITY_VALID

    assert result[
        'reliability_level'
    ] == RELIABILITY_LOW

    assert result[
        'reliability_score'
    ] < 0.60


# ==========================================================
# INSUFFICIENT REGRESSION DATA
# ==========================================================

def test_regression_insufficient_data():
    """
    Reliability must not be considered valid when the number
    of observations is below the configured minimum.
    """

    result = calculate_regression_reliability(
        actual_values=[
            10.0,
        ],
        predicted_values=[
            10.0,
        ],
        baseline_mae=5.0,
        minimum_sample_count=2,
    )

    assert result[
        'status'
    ] == RELIABILITY_INSUFFICIENT_DATA

    assert result[
        'reliability_level'
    ] == RELIABILITY_LOW


# ==========================================================
# CLASSIFICATION HIGH RELIABILITY
# ==========================================================

def test_classification_high_reliability():
    """
    Perfect classification predictions should produce
    high reliability.
    """

    result = calculate_classification_reliability(
        actual_values=[
            0,
            1,
            0,
            1,
            1,
        ],
        predicted_values=[
            0,
            1,
            0,
            1,
            1,
        ],
    )

    assert result[
        'status'
    ] == RELIABILITY_VALID

    assert result[
        'reliability_level'
    ] == RELIABILITY_HIGH

    assert result[
        'accuracy'
    ] == 1.0

    assert result[
        'reliability_score'
    ] == 1.0


# ==========================================================
# CLASSIFICATION MEDIUM RELIABILITY
# ==========================================================

def test_classification_medium_reliability():
    """
    Classification accuracy between 0.60 and 0.80 should
    produce medium reliability.
    """

    result = calculate_classification_reliability(
        actual_values=[
            0,
            1,
            0,
            1,
            1,
        ],
        predicted_values=[
            0,
            1,
            1,
            0,
            1,
        ],
    )

    assert result[
        'status'
    ] == RELIABILITY_VALID

    assert result[
        'reliability_level'
    ] == RELIABILITY_MEDIUM

    assert result[
        'accuracy'
    ] == pytest.approx(
        0.60
    )


# ==========================================================
# CLASSIFICATION LOW RELIABILITY
# ==========================================================

def test_classification_low_reliability():
    """
    Low classification accuracy should produce low
    reliability.
    """

    result = calculate_classification_reliability(
        actual_values=[
            0,
            1,
            0,
            1,
            1,
        ],
        predicted_values=[
            1,
            0,
            1,
            0,
            1,
        ],
    )

    assert result[
        'status'
    ] == RELIABILITY_VALID

    assert result[
        'reliability_level'
    ] == RELIABILITY_LOW

    assert result[
        'accuracy'
    ] == pytest.approx(
        0.20
    )


# ==========================================================
# UNIFIED REGRESSION EVALUATION
# ==========================================================

def test_unified_regression_reliability():
    """
    The unified reliability API must route regression models
    to regression reliability evaluation.
    """

    result = evaluate_prediction_reliability(
        model_type='regression',
        actual_values=[
            10.0,
            20.0,
            30.0,
        ],
        predicted_values=[
            10.0,
            20.0,
            30.0,
        ],
        baseline_mae=5.0,
    )

    assert result[
        'status'
    ] == RELIABILITY_VALID

    assert result[
        'reliability_level'
    ] == RELIABILITY_HIGH

    assert result[
        'mae'
    ] == 0.0


# ==========================================================
# UNIFIED CLASSIFICATION EVALUATION
# ==========================================================

def test_unified_classification_reliability():
    """
    The unified reliability API must route classification
    models to classification reliability evaluation.
    """

    result = evaluate_prediction_reliability(
        model_type='classification',
        actual_values=[
            0,
            1,
            0,
            1,
        ],
        predicted_values=[
            0,
            1,
            0,
            1,
        ],
    )

    assert result[
        'status'
    ] == RELIABILITY_VALID

    assert result[
        'reliability_level'
    ] == RELIABILITY_HIGH

    assert result[
        'accuracy'
    ] == 1.0


# ==========================================================
# MONITORING WITHOUT PREVIOUS RESULT
# ==========================================================

def test_monitor_without_previous_result():
    """
    Monitoring without historical data must not report
    degradation.
    """

    current = {

        'status':
            RELIABILITY_VALID,

        'reliability_level':
            RELIABILITY_HIGH,

        'reliability_score':
            0.90,
    }

    result = monitor_prediction_reliability(
        current
    )

    assert result[
        'degraded'
    ] is False

    assert result[
        'previous_reliability_score'
    ] is None

    assert result[
        'score_change'
    ] is None


# ==========================================================
# MONITORING IMPROVEMENT
# ==========================================================

def test_monitor_detects_improvement():
    """
    An increased reliability score must not be marked as
    degradation.
    """

    previous = {

        'status':
            RELIABILITY_VALID,

        'reliability_level':
            RELIABILITY_MEDIUM,

        'reliability_score':
            0.70,
    }

    current = {

        'status':
            RELIABILITY_VALID,

        'reliability_level':
            RELIABILITY_HIGH,

        'reliability_score':
            0.90,
    }

    result = monitor_prediction_reliability(
        current,
        previous,
    )

    assert result[
        'degraded'
    ] is False

    assert result[
        'previous_reliability_score'
    ] == 0.70

    assert result[
        'score_change'
    ] == pytest.approx(
        0.20
    )

    assert result[
        'status'
    ] == RELIABILITY_VALID


# ==========================================================
# MONITORING DEGRADATION
# ==========================================================

def test_monitor_detects_degradation():
    """
    A decrease in reliability must be detected.
    """

    previous = {

        'status':
            RELIABILITY_VALID,

        'reliability_level':
            RELIABILITY_HIGH,

        'reliability_score':
            0.90,
    }

    current = {

        'status':
            RELIABILITY_VALID,

        'reliability_level':
            RELIABILITY_MEDIUM,

        'reliability_score':
            0.65,
    }

    result = monitor_prediction_reliability(
        current,
        previous,
    )

    assert result[
        'degraded'
    ] is True

    assert result[
        'previous_reliability_score'
    ] == 0.90

    assert result[
        'score_change'
    ] == pytest.approx(
        -0.25
    )

    assert result[
        'status'
    ] == RELIABILITY_UNRELIABLE


# ==========================================================
# VALIDATION TESTS
# ==========================================================

def test_rejects_empty_values():
    """
    Empty prediction datasets must be rejected.
    """

    with pytest.raises(
        ValueError
    ):

        calculate_prediction_error(
            [],
            [],
        )


def test_rejects_mismatched_lengths():
    """
    Actual and predicted values must have equal lengths.
    """

    with pytest.raises(
        ValueError
    ):

        calculate_prediction_error(
            [1.0, 2.0],
            [1.0],
        )


def test_rejects_invalid_model_type():
    """
    Unsupported model types must be rejected.
    """

    with pytest.raises(
        ValueError
    ):

        evaluate_prediction_reliability(
            model_type='unknown',
            actual_values=[
                1.0,
                2.0,
            ],
            predicted_values=[
                1.0,
                2.0,
            ],
        )


def test_rejects_invalid_baseline():
    """
    A zero baseline MAE cannot be used for comparative
    reliability scoring.
    """

    with pytest.raises(
        ValueError
    ):

        calculate_regression_reliability(
            actual_values=[
                1.0,
                2.0,
            ],
            predicted_values=[
                1.0,
                2.0,
            ],
            baseline_mae=0.0,
        )


def test_rejects_non_finite_prediction():
    """
    NaN and infinity must never enter reliability metrics.
    """

    with pytest.raises(
        ValueError
    ):

        calculate_prediction_error(
            [1.0],
            [float('nan')],
        )


# ==========================================================
# TEST SUMMARY
# ==========================================================

def test_reliability_module_returns_expected_structure():
    """
    Verify that the reliability result contains the core
    monitoring fields required by the prediction layer.
    """

    result = calculate_regression_reliability(
        actual_values=[
            10.0,
            20.0,
            30.0,
        ],
        predicted_values=[
            10.0,
            20.0,
            30.0,
        ],
        baseline_mae=5.0,
    )

    required_fields = {
        'status',
        'reliability_level',
        'reliability_score',
        'mae',
        'max_absolute_error',
        'mean_error',
        'sample_count',
        'baseline_mae',
        'improvement',
    }

    assert required_fields.issubset(
        result.keys()
    )
