# ==========================================================
# PREDICTION MONITORING TESTS
# ==========================================================

import pytest


from ml.prediction.monitoring import (
    MONITORING_VALID,
    MONITORING_DEGRADED,
    MONITORING_STABLE,
    MONITORING_IMPROVED,
    MONITORING_DEGRADED_STATE,
    calculate_score_change,
    detect_degradation,
    detect_improvement,
    determine_monitoring_state,
    monitor_reliability,
    monitor_calibration,
    monitor_prediction,
)


# ==========================================================
# SCORE CHANGE
# ==========================================================

def test_calculate_score_change():
    """
    Score change must be current minus previous.
    """

    result = calculate_score_change(
        0.90,
        0.70,
    )

    assert result == pytest.approx(
        0.20
    )


def test_calculate_score_change_without_previous():
    """
    No previous score must produce None.
    """

    result = calculate_score_change(
        0.90,
        None,
    )

    assert result is None


# ==========================================================
# DEGRADATION
# ==========================================================

def test_detect_degradation():
    """
    A score decrease equal to the threshold must be
    considered degradation.
    """

    result = detect_degradation(
        current_score=0.70,
        previous_score=0.80,
        degradation_threshold=0.10,
    )

    assert result is True


def test_no_degradation_on_improvement():
    """
    An increased score must not be degradation.
    """

    result = detect_degradation(
        current_score=0.90,
        previous_score=0.80,
        degradation_threshold=0.10,
    )

    assert result is False


def test_no_degradation_without_previous():
    """
    Without historical data degradation cannot be detected.
    """

    result = detect_degradation(
        current_score=0.50,
        previous_score=None,
    )

    assert result is False


# ==========================================================
# IMPROVEMENT
# ==========================================================

def test_detect_improvement():
    """
    A score increase equal to the threshold must be
    considered improvement.
    """

    result = detect_improvement(
        current_score=0.90,
        previous_score=0.80,
        improvement_threshold=0.10,
    )

    assert result is True


def test_no_improvement_on_degradation():
    """
    A decreased score must not be improvement.
    """

    result = detect_improvement(
        current_score=0.70,
        previous_score=0.80,
        improvement_threshold=0.10,
    )

    assert result is False


def test_no_improvement_without_previous():
    """
    Without historical data improvement cannot be detected.
    """

    result = detect_improvement(
        current_score=0.90,
        previous_score=None,
    )

    assert result is False


# ==========================================================
# MONITORING STATE
# ==========================================================

def test_monitoring_state_stable():
    """
    Small score changes must remain stable.
    """

    result = determine_monitoring_state(
        current_score=0.84,
        previous_score=0.80,
        degradation_threshold=0.10,
        improvement_threshold=0.10,
    )

    assert result == MONITORING_STABLE


def test_monitoring_state_improved():
    """
    A sufficient score increase must produce improved state.
    """

    result = determine_monitoring_state(
        current_score=0.95,
        previous_score=0.80,
        degradation_threshold=0.10,
        improvement_threshold=0.10,
    )

    assert result == MONITORING_IMPROVED


def test_monitoring_state_degraded():
    """
    A sufficient score decrease must produce degraded state.
    """

    result = determine_monitoring_state(
        current_score=0.65,
        previous_score=0.80,
        degradation_threshold=0.10,
        improvement_threshold=0.10,
    )

    assert result == MONITORING_DEGRADED_STATE


def test_monitoring_state_without_previous():
    """
    Without previous data monitoring state must be stable.
    """

    result = determine_monitoring_state(
        current_score=0.50,
        previous_score=None,
    )

    assert result == MONITORING_STABLE


# ==========================================================
# RELIABILITY MONITORING
# ==========================================================

def test_monitor_reliability_without_previous():
    """
    Reliability monitoring without previous data must not
    report degradation or improvement.
    """

    current = {
        'status':
            'valid',

        'reliability_score':
            0.90,

        'reliability_level':
            'high',

        'sample_count':
            100,
    }

    result = monitor_reliability(
        current
    )

    assert result[
        'status'
    ] == MONITORING_VALID

    assert result[
        'monitoring_state'
    ] == MONITORING_STABLE

    assert result[
        'degraded'
    ] is False

    assert result[
        'improved'
    ] is False

    assert result[
        'previous_reliability_score'
    ] is None

    assert result[
        'score_change'
    ] is None


def test_monitor_reliability_detects_improvement():
    """
    Reliability improvement must be detected.
    """

    previous = {
        'status':
            'valid',

        'reliability_score':
            0.70,

        'reliability_level':
            'medium',

        'sample_count':
            100,
    }

    current = {
        'status':
            'valid',

        'reliability_score':
            0.90,

        'reliability_level':
            'high',

        'sample_count':
            120,
    }

    result = monitor_reliability(
        current,
        previous,
    )

    assert result[
        'status'
    ] == MONITORING_VALID

    assert result[
        'monitoring_state'
    ] == MONITORING_IMPROVED

    assert result[
        'degraded'
    ] is False

    assert result[
        'improved'
    ] is True

    assert result[
        'score_change'
    ] == pytest.approx(
        0.20
    )


def test_monitor_reliability_detects_degradation():
    """
    Reliability degradation must be detected.
    """

    previous = {
        'status':
            'valid',

        'reliability_score':
            0.90,

        'reliability_level':
            'high',

        'sample_count':
            100,
    }

    current = {
        'status':
            'valid',

        'reliability_score':
            0.65,

        'reliability_level':
            'medium',

        'sample_count':
            100,
    }

    result = monitor_reliability(
        current,
        previous,
    )

    assert result[
        'status'
    ] == MONITORING_DEGRADED

    assert result[
        'monitoring_state'
    ] == MONITORING_DEGRADED_STATE

    assert result[
        'degraded'
    ] is True

    assert result[
        'improved'
    ] is False

    assert result[
        'previous_reliability_score'
    ] == 0.90

    assert result[
        'score_change'
    ] == pytest.approx(
        -0.25
    )


# ==========================================================
# CALIBRATION MONITORING
# ==========================================================

def test_monitor_calibration_without_previous():
    """
    Calibration monitoring without previous data must remain
    stable.
    """

    current = {
        'status':
            'valid',

        'calibration_score':
            0.95,

        'calibration_level':
            'high',

        'sample_count':
            100,
    }

    result = monitor_calibration(
        current
    )

    assert result[
        'status'
    ] == MONITORING_VALID

    assert result[
        'monitoring_state'
    ] == MONITORING_STABLE

    assert result[
        'degraded'
    ] is False

    assert result[
        'improved'
    ] is False

    assert result[
        'previous_calibration_score'
    ] is None


def test_monitor_calibration_detects_improvement():
    """
    Calibration improvement must be detected.
    """

    previous = {
        'status':
            'valid',

        'calibration_score':
            0.65,

        'calibration_level':
            'medium',

        'sample_count':
            100,
    }

    current = {
        'status':
            'valid',

        'calibration_score':
            0.90,

        'calibration_level':
            'high',

        'sample_count':
            120,
    }

    result = monitor_calibration(
        current,
        previous,
    )

    assert result[
        'status'
    ] == MONITORING_VALID

    assert result[
        'monitoring_state'
    ] == MONITORING_IMPROVED

    assert result[
        'improved'
    ] is True

    assert result[
        'degraded'
    ] is False

    assert result[
        'score_change'
    ] == pytest.approx(
        0.25
    )


def test_monitor_calibration_detects_degradation():
    """
    Calibration degradation must be detected.
    """

    previous = {
        'status':
            'valid',

        'calibration_score':
            0.90,

        'calibration_level':
            'high',

        'sample_count':
            100,
    }

    current = {
        'status':
            'valid',

        'calibration_score':
            0.65,

        'calibration_level':
            'medium',

        'sample_count':
            100,
    }

    result = monitor_calibration(
        current,
        previous,
    )

    assert result[
        'status'
    ] == MONITORING_DEGRADED

    assert result[
        'monitoring_state'
    ] == MONITORING_DEGRADED_STATE

    assert result[
        'degraded'
    ] is True

    assert result[
        'improved'
    ] is False

    assert result[
        'score_change'
    ] == pytest.approx(
        -0.25
    )


# ==========================================================
# UNIFIED MONITORING
# ==========================================================

def test_monitor_prediction_routes_reliability():
    """
    Unified monitoring must route reliability results to
    reliability monitoring.
    """

    current = {
        'status':
            'valid',

        'reliability_score':
            0.90,

        'reliability_level':
            'high',

        'sample_count':
            100,
    }

    result = monitor_prediction(
        current
    )

    assert result[
        'status'
    ] == MONITORING_VALID

    assert (
        'current_reliability_score'
        in result
    )


def test_monitor_prediction_routes_calibration():
    """
    Unified monitoring must route calibration results to
    calibration monitoring.
    """

    current = {
        'status':
            'valid',

        'calibration_score':
            0.90,

        'calibration_level':
            'high',

        'sample_count':
            100,
    }

    result = monitor_prediction(
        current
    )

    assert result[
        'status'
    ] == MONITORING_VALID

    assert (
        'current_calibration_score'
        in result
    )


# ==========================================================
# VALIDATION TESTS
# ==========================================================

def test_rejects_missing_current_result():
    """
    Current result is required.
    """

    with pytest.raises(
        ValueError
    ):
        monitor_prediction(
            None
        )


def test_rejects_non_dictionary_result():
    """
    Monitoring results must be dictionaries.
    """

    with pytest.raises(
        ValueError
    ):
        monitor_prediction(
            []
        )


def test_rejects_missing_reliability_score():
    """
    Reliability monitoring requires a reliability score.
    """

    current = {
        'status':
            'valid',

        'reliability_level':
            'high',
    }

    with pytest.raises(
        ValueError
    ):
        monitor_reliability(
            current
        )


def test_rejects_missing_calibration_score():
    """
    Calibration monitoring requires a calibration score.
    """

    current = {
        'status':
            'valid',

        'calibration_level':
            'high',
    }

    with pytest.raises(
        ValueError
    ):
        monitor_calibration(
            current
        )


def test_rejects_invalid_score():
    """
    Scores must remain inside [0, 1].
    """

    with pytest.raises(
        ValueError
    ):
        calculate_score_change(
            1.5,
            0.5,
        )


def test_rejects_nan_score():
    """
    NaN scores must be rejected.
    """

    with pytest.raises(
        ValueError
    ):
        calculate_score_change(
            float('nan'),
            0.5,
        )


def test_rejects_infinite_score():
    """
    Infinite scores must be rejected.
    """

    with pytest.raises(
        ValueError
    ):
        calculate_score_change(
            float('inf'),
            0.5,
        )


def test_rejects_invalid_threshold():
    """
    Thresholds must remain inside [0, 1].
    """

    with pytest.raises(
        ValueError
    ):
        detect_degradation(
            current_score=0.5,
            previous_score=0.8,
            degradation_threshold=1.5,
        )


def test_rejects_negative_sample_count():
    """
    Sample count cannot be negative.
    """

    current = {
        'status':
            'valid',

        'reliability_score':
            0.90,

        'reliability_level':
            'high',

        'sample_count':
            -1,
    }

    with pytest.raises(
        ValueError
    ):
        monitor_reliability(
            current
        )


# ==========================================================
# RESULT STRUCTURE
# ==========================================================

def test_reliability_monitoring_result_structure():
    """
    Reliability monitoring must return the core monitoring
    fields required by the prediction layer.
    """

    current = {
        'status':
            'valid',

        'reliability_score':
            0.90,

        'reliability_level':
            'high',

        'sample_count':
            100,
    }

    result = monitor_reliability(
        current
    )

    required_fields = {
        'status',
        'monitoring_state',
        'degraded',
        'improved',
        'current_reliability_score',
        'previous_reliability_score',
        'score_change',
        'current_reliability_level',
        'previous_reliability_level',
        'sample_count',
        'monitored_at',
    }

    assert required_fields.issubset(
        result.keys()
    )


def test_calibration_monitoring_result_structure():
    """
    Calibration monitoring must return the core monitoring
    fields required by the prediction layer.
    """

    current = {
        'status':
            'valid',

        'calibration_score':
            0.90,

        'calibration_level':
            'high',

        'sample_count':
            100,
    }

    result = monitor_calibration(
        current
    )

    required_fields = {
        'status',
        'monitoring_state',
        'degraded',
        'improved',
        'current_calibration_score',
        'previous_calibration_score',
        'score_change',
        'current_calibration_level',
        'previous_calibration_level',
        'sample_count',
        'monitored_at',
    }

    assert required_fields.issubset(
        result.keys()
    )


# ==========================================================
# THRESHOLD BEHAVIOR
# ==========================================================

def test_exact_improvement_threshold():
    """
    Improvement exactly at the threshold must be detected.
    """

    result = detect_improvement(
        current_score=0.80,
        previous_score=0.70,
        improvement_threshold=0.10,
    )

    assert result is True


def test_exact_degradation_threshold():
    """
    Degradation exactly at the threshold must be detected.
    """

    result = detect_degradation(
        current_score=0.70,
        previous_score=0.80,
        degradation_threshold=0.10,
    )

    assert result is True