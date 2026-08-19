import math

import pytest

from ml.prediction.error_analysis import (
    calculate_errors,
    classify_error_direction,
    summarize_errors,
    analyze_error_distribution,
    detect_large_errors,
    analyze_error_bias,
    analyze_regression_errors,
)


# ==========================================================
# BASIC ERROR CALCULATION
# ==========================================================

def test_calculate_errors():

    predictions = [
        100.0,
        200.0,
        300.0,
    ]

    actual_values = [
        110.0,
        190.0,
        300.0,
    ]

    errors = calculate_errors(
        predictions,
        actual_values,
    )

    assert len(errors) == 3

    assert errors[0]['signed_error'] == -10.0
    assert errors[0]['absolute_error'] == 10.0
    assert errors[0]['squared_error'] == 100.0

    assert errors[1]['signed_error'] == 10.0
    assert errors[1]['absolute_error'] == 10.0
    assert errors[1]['squared_error'] == 100.0

    assert errors[2]['signed_error'] == 0.0
    assert errors[2]['absolute_error'] == 0.0
    assert errors[2]['squared_error'] == 0.0


# ==========================================================
# ERROR DIRECTION
# ==========================================================

def test_classify_error_direction():

    assert (
        classify_error_direction(10.0)
        == 'overprediction'
    )

    assert (
        classify_error_direction(-10.0)
        == 'underprediction'
    )

    assert (
        classify_error_direction(0.0)
        == 'exact'
    )


# ==========================================================
# SUMMARY
# ==========================================================

def test_summarize_errors():

    predictions = [
        100.0,
        200.0,
        300.0,
    ]

    actual_values = [
        110.0,
        190.0,
        300.0,
    ]

    result = summarize_errors(
        predictions,
        actual_values,
    )

    assert result[
        'evaluated_count'
    ] == 3

    assert math.isclose(
        result['mae'],
        20.0 / 3.0,
        rel_tol=1e-12,
    )

    assert math.isclose(
        result['mse'],
        200.0 / 3.0,
        rel_tol=1e-12,
    )

    assert math.isclose(
        result['rmse'],
        math.sqrt(
            200.0 / 3.0
        ),
        rel_tol=1e-12,
    )

    assert result[
        'overprediction_count'
    ] == 1

    assert result[
        'underprediction_count'
    ] == 1

    assert result[
        'exact_prediction_count'
    ] == 1


# ==========================================================
# ZERO ACTUAL VALUE
# ==========================================================

def test_zero_actual_relative_error():

    predictions = [
        10.0,
    ]

    actual_values = [
        0.0,
    ]

    errors = calculate_errors(
        predictions,
        actual_values,
    )

    assert errors[0][
        'relative_error'
    ] is None


# ==========================================================
# ERROR DISTRIBUTION
# ==========================================================

def test_error_distribution():

    predictions = [
        100.0,
        200.0,
        300.0,
        400.0,
        500.0,
    ]

    actual_values = [
        110.0,
        190.0,
        300.0,
        380.0,
        510.0,
    ]

    result = analyze_error_distribution(
        predictions,
        actual_values,
    )

    assert result[
        'evaluated_count'
    ] == 5

    assert result[
        'absolute_error_min'
    ] == 0.0

    assert result[
        'absolute_error_max'
    ] == 20.0

    assert result[
        'absolute_error_p50'
    ] == 10.0


# ==========================================================
# LARGE ERRORS
# ==========================================================

def test_large_error_detection():

    predictions = [
        100.0,
        200.0,
        300.0,
    ]

    actual_values = [
        110.0,
        200.0,
        350.0,
    ]

    result = detect_large_errors(
        predictions,
        actual_values,
        threshold=40.0,
    )

    assert result[
        'threshold'
    ] == 40.0

    assert result[
        'count'
    ] == 1

    assert result[
        'errors'
    ][0][
        'absolute_error'
    ] == 50.0


# ==========================================================
# BIAS ANALYSIS
# ==========================================================

def test_error_bias():

    predictions = [
        110.0,
        220.0,
        330.0,
    ]

    actual_values = [
        100.0,
        200.0,
        300.0,
    ]

    result = analyze_error_bias(
        predictions,
        actual_values,
    )

    assert result[
        'overprediction_count'
    ] == 3

    assert result[
        'underprediction_count'
    ] == 0

    assert result[
        'exact_prediction_count'
    ] == 0

    assert result[
        'direction'
    ] == 'overprediction'

    assert result[
        'mean_error'
    ] == 20.0


# ==========================================================
# COMPLETE ANALYSIS
# ==========================================================

def test_complete_error_analysis():

    predictions = [
        100.0,
        200.0,
        300.0,
        400.0,
    ]

    actual_values = [
        110.0,
        190.0,
        310.0,
        400.0,
    ]

    result = analyze_regression_errors(
        predictions,
        actual_values,
        large_error_threshold=50.0,
    )

    assert result[
        'status'
    ] == 'evaluated'

    assert result[
        'summary'
    ][
        'evaluated_count'
    ] == 4

    assert result[
        'distribution'
    ][
        'evaluated_count'
    ] == 4

    assert result[
        'bias'
    ][
        'overprediction_count'
    ] == 1

    assert result[
        'bias'
    ][
        'underprediction_count'
    ] == 2

    assert result[
        'bias'
    ][
        'exact_prediction_count'
    ] == 1

    assert result[
        'large_errors'
    ][
        'count'
    ] == 0


# ==========================================================
# INVALID INPUT
# ==========================================================

def test_empty_predictions_rejected():

    with pytest.raises(
        ValueError
    ):

        calculate_errors(
            [],
            [],
        )


def test_different_lengths_rejected():

    with pytest.raises(
        ValueError
    ):

        calculate_errors(
            [100.0, 200.0],
            [100.0],
        )


def test_nan_rejected():

    with pytest.raises(
        ValueError
    ):

        calculate_errors(
            [math.nan],
            [100.0],
        )


def test_infinity_rejected():

    with pytest.raises(
        ValueError
    ):

        calculate_errors(
            [math.inf],
            [100.0],
        )


def test_negative_threshold_rejected():

    with pytest.raises(
        ValueError
    ):

        detect_large_errors(
            [100.0],
            [100.0],
            -1.0,
        )