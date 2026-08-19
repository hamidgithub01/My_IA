# ==========================================================
# PREDICTION CALIBRATION TESTS
# ==========================================================

import pytest


from ml.prediction.calibration import (
    CALIBRATION_VALID,
    CALIBRATION_INSUFFICIENT_DATA,
    CALIBRATION_HIGH,
    CALIBRATION_MEDIUM,
    CALIBRATION_LOW,
    calculate_brier_score,
    calculate_calibration_errors,
    calculate_mean_calibration_error,
    calculate_prediction_confidence,
    calculate_expected_calibration_error,
    determine_calibration_level,
    calculate_calibration_score,
    evaluate_prediction_calibration,
)


# ==========================================================
# BRIER SCORE
# ==========================================================

def test_calculate_brier_score():
    """
    Brier Score must be calculated correctly.
    """

    result = calculate_brier_score(
        [
            0,
            1,
            0,
            1,
        ],
        [
            0.1,
            0.8,
            0.2,
            0.9,
        ],
    )

    expected = (
        (
            (0.1 - 0) ** 2
            + (0.8 - 1) ** 2
            + (0.2 - 0) ** 2
            + (0.9 - 1) ** 2
        )
        / 4
    )

    assert result == pytest.approx(
        expected
    )


# ==========================================================
# PERFECT BRIER SCORE
# ==========================================================

def test_perfect_brier_score():
    """
    Perfect probabilistic predictions must have a Brier
    Score of zero.
    """

    result = calculate_brier_score(
        [
            0,
            1,
            0,
            1,
        ],
        [
            0.0,
            1.0,
            0.0,
            1.0,
        ],
    )

    assert result == 0.0


# ==========================================================
# CALIBRATION ERRORS
# ==========================================================

def test_calculate_calibration_errors():
    """
    Per-observation calibration errors must be calculated
    correctly.
    """

    result = calculate_calibration_errors(
        [
            0,
            1,
            0,
        ],
        [
            0.2,
            0.8,
            0.4,
        ],
    )

    assert result == pytest.approx(
        [
            0.2,
            0.2,
            0.4,
        ]
    )


# ==========================================================
# MEAN CALIBRATION ERROR
# ==========================================================

def test_calculate_mean_calibration_error():
    """
    Mean calibration error must be calculated correctly.
    """

    result = calculate_mean_calibration_error(
        [
            0,
            1,
            0,
        ],
        [
            0.2,
            0.8,
            0.4,
        ],
    )

    assert result == pytest.approx(
        (
            0.2
            + 0.2
            + 0.4
        ) / 3
    )


# ==========================================================
# PREDICTION CONFIDENCE
# ==========================================================

def test_calculate_prediction_confidence():
    """
    Confidence must equal max(p, 1-p).
    """

    result = calculate_prediction_confidence(
        [
            0.1,
            0.8,
            0.5,
            0.9,
        ]
    )

    assert result == pytest.approx(
        [
            0.9,
            0.8,
            0.5,
            0.9,
        ]
    )


# ==========================================================
# PERFECT ECE
# ==========================================================

def test_perfect_expected_calibration_error():
    """
    Perfect predictions with confidence 1.0 must have zero
    Expected Calibration Error.
    """

    result = calculate_expected_calibration_error(
        [
            0,
            1,
            0,
            1,
        ],
        [
            0.0,
            1.0,
            0.0,
            1.0,
        ],
    )

    assert result == 0.0


# ==========================================================
# ECE
# ==========================================================

def test_expected_calibration_error():
    """
    ECE must detect the difference between confidence and
    empirical accuracy.
    """

    result = calculate_expected_calibration_error(
        [
            0,
            0,
            1,
            1,
        ],
        [
            0.9,
            0.9,
            0.9,
            0.9,
        ],
        bin_count=10,
    )

    assert result == pytest.approx(
        0.4
    )


# ==========================================================
# CALIBRATION LEVEL
# ==========================================================

def test_high_calibration_level():
    """
    Small calibration error must produce high calibration.
    """

    assert determine_calibration_level(
        0.05
    ) == CALIBRATION_HIGH


def test_medium_calibration_level():
    """
    Moderate calibration error must produce medium
    calibration.
    """

    assert determine_calibration_level(
        0.15
    ) == CALIBRATION_MEDIUM


def test_low_calibration_level():
    """
    Large calibration error must produce low calibration.
    """

    assert determine_calibration_level(
        0.30
    ) == CALIBRATION_LOW


# ==========================================================
# CALIBRATION SCORE
# ==========================================================

def test_calibration_score():
    """
    Calibration score must be one minus calibration error.
    """

    result = calculate_calibration_score(
        0.20
    )

    assert result == pytest.approx(
        0.80
    )


def test_perfect_calibration_score():
    """
    Perfect calibration must have a score of one.
    """

    assert calculate_calibration_score(
        0.0
    ) == 1.0


# ==========================================================
# FULL HIGH CALIBRATION
# ==========================================================

def test_high_prediction_calibration():
    """
    Perfect probability predictions must produce high
    calibration.
    """

    result = evaluate_prediction_calibration(
        actual_values=[
            0,
            1,
            0,
            1,
            0,
            1,
            0,
            1,
            0,
            1,
        ],
        predicted_probabilities=[
            0.0,
            1.0,
            0.0,
            1.0,
            0.0,
            1.0,
            0.0,
            1.0,
            0.0,
            1.0,
        ],
        minimum_sample_count=5,
    )

    assert result[
        'status'
    ] == CALIBRATION_VALID

    assert result[
        'calibration_level'
    ] == CALIBRATION_HIGH

    assert result[
        'calibration_score'
    ] == 1.0

    assert result[
        'brier_score'
    ] == 0.0

    assert result[
        'expected_calibration_error'
    ] == 0.0

    assert result[
        'sample_count'
    ] == 10


# ==========================================================
# INSUFFICIENT DATA
# ==========================================================

def test_calibration_insufficient_data():
    """
    Calibration must not be considered valid when the number
    of observations is below the configured minimum.
    """

    result = evaluate_prediction_calibration(
        actual_values=[
            0,
            1,
        ],
        predicted_probabilities=[
            0.2,
            0.8,
        ],
        minimum_sample_count=10,
    )

    assert result[
        'status'
    ] == CALIBRATION_INSUFFICIENT_DATA

    assert result[
        'calibration_level'
    ] == CALIBRATION_LOW

    assert result[
        'calibration_score'
    ] == 0.0

    assert result[
        'brier_score'
    ] is None

    assert result[
        'sample_count'
    ] == 2


# ==========================================================
# EMPTY VALUES
# ==========================================================

def test_rejects_empty_values():
    """
    Empty prediction datasets must be rejected.
    """

    with pytest.raises(
        ValueError
    ):
        calculate_brier_score(
            [],
            [],
        )


# ==========================================================
# MISMATCHED LENGTHS
# ==========================================================

def test_rejects_mismatched_lengths():
    """
    Actual values and probabilities must have equal lengths.
    """

    with pytest.raises(
        ValueError
    ):
        calculate_brier_score(
            [
                0,
                1,
            ],
            [
                0.2,
            ],
        )


# ==========================================================
# INVALID PROBABILITY
# ==========================================================

def test_rejects_probability_above_one():
    """
    Probabilities above one must be rejected.
    """

    with pytest.raises(
        ValueError
    ):
        calculate_brier_score(
            [
                0,
            ],
            [
                1.2,
            ],
        )


def test_rejects_probability_below_zero():
    """
    Probabilities below zero must be rejected.
    """

    with pytest.raises(
        ValueError
    ):
        calculate_brier_score(
            [
                0,
            ],
            [
                -0.1,
            ],
        )


# ==========================================================
# NON-FINITE PROBABILITY
# ==========================================================

def test_rejects_nan_probability():
    """
    NaN probabilities must never enter calibration metrics.
    """

    with pytest.raises(
        ValueError
    ):
        calculate_brier_score(
            [
                0,
            ],
            [
                float('nan'),
            ],
        )


def test_rejects_infinite_probability():
    """
    Infinite probabilities must never enter calibration
    metrics.
    """

    with pytest.raises(
        ValueError
    ):
        calculate_brier_score(
            [
                0,
            ],
            [
                float('inf'),
            ],
        )


# ==========================================================
# INVALID ACTUAL CLASS
# ==========================================================

def test_rejects_non_binary_actual_value():
    """
    Calibration currently supports binary classification only.
    """

    with pytest.raises(
        ValueError
    ):
        calculate_brier_score(
            [
                0,
                2,
            ],
            [
                0.2,
                0.8,
            ],
        )


# ==========================================================
# INVALID BIN COUNT
# ==========================================================

def test_rejects_invalid_bin_count():
    """
    Bin count must be a positive integer.
    """

    with pytest.raises(
        ValueError
    ):
        calculate_expected_calibration_error(
            [
                0,
                1,
            ],
            [
                0.2,
                0.8,
            ],
            bin_count=0,
        )


# ==========================================================
# INVALID MINIMUM SAMPLE COUNT
# ==========================================================

def test_rejects_invalid_minimum_sample_count():
    """
    Minimum sample count must be a positive integer.
    """

    with pytest.raises(
        ValueError
    ):
        evaluate_prediction_calibration(
            actual_values=[
                0,
                1,
            ],
            predicted_probabilities=[
                0.2,
                0.8,
            ],
            minimum_sample_count=0,
        )


# ==========================================================
# RESULT STRUCTURE
# ==========================================================

def test_calibration_result_structure():
    """
    Calibration result must expose all core fields required
    by the prediction monitoring layer.
    """

    result = evaluate_prediction_calibration(
        actual_values=[
            0,
            1,
            0,
            1,
            0,
            1,
            0,
            1,
            0,
            1,
        ],
        predicted_probabilities=[
            0.1,
            0.9,
            0.2,
            0.8,
            0.1,
            0.9,
            0.2,
            0.8,
            0.1,
            0.9,
        ],
        minimum_sample_count=5,
    )

    required_fields = {
        'status',
        'calibration_level',
        'calibration_score',
        'brier_score',
        'mean_calibration_error',
        'expected_calibration_error',
        'sample_count',
    }

    assert required_fields.issubset(
        result.keys()
    )