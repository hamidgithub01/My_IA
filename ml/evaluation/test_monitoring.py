from ml.evaluation.monitoring import (
    MONITORING_VALID,
    MONITORING_INSUFFICIENT_DATA,
    MONITORING_STABLE,
    MONITORING_IMPROVING,
    MONITORING_DEGRADING,
    MONITORING_CRITICAL,
    compare_reliability_snapshots,
    calculate_error_change,
    detect_continuous_degradation,
    monitor_reliability_history,
    create_monitoring_snapshot,
    monitor_evaluation_history,
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
    Assert approximate numeric equality.
    """

    assert abs(
        actual - expected
    ) < tolerance, (
        f'Expected {expected}, got {actual}'
    )


# ==========================================================
# SNAPSHOT COMPARISON
# ==========================================================

def test_stable_snapshots():
    """
    Small quality changes must be considered stable.
    """

    previous = {
        'quality_score': 0.80,
        'reliability_level': 'high',
    }

    current = {
        'quality_score': 0.78,
        'reliability_level': 'high',
    }

    result = compare_reliability_snapshots(
        previous,
        current,
        degradation_threshold=0.05,
    )

    assert (
        result['status']
        == MONITORING_STABLE
    )

    assert_close(
        result['quality_change'],
        -0.02,
    )


def test_improving_snapshots():
    """
    Significant quality improvement must be detected.
    """

    previous = {
        'quality_score': 0.60,
        'reliability_level': 'medium',
    }

    current = {
        'quality_score': 0.75,
        'reliability_level': 'medium',
    }

    result = compare_reliability_snapshots(
        previous,
        current,
    )

    assert (
        result['status']
        == MONITORING_IMPROVING
    )

    assert_close(
        result['quality_change'],
        0.15,
    )


def test_degrading_snapshots():
    """
    Significant quality degradation must be detected.
    """

    previous = {
        'quality_score': 0.85,
        'reliability_level': 'high',
    }

    current = {
        'quality_score': 0.75,
        'reliability_level': 'medium',
    }

    result = compare_reliability_snapshots(
        previous,
        current,
    )

    assert (
        result['status']
        == MONITORING_DEGRADING
    )

    assert (
        result['reliability_level_changed']
        is True
    )


def test_critical_degradation():
    """
    Large quality degradation must be critical.
    """

    previous = {
        'quality_score': 0.90,
        'reliability_level': 'high',
    }

    current = {
        'quality_score': 0.60,
        'reliability_level': 'low',
    }

    result = compare_reliability_snapshots(
        previous,
        current,
    )

    assert (
        result['status']
        == MONITORING_CRITICAL
    )

    assert_close(
        result['quality_change'],
        -0.30,
    )


# ==========================================================
# ERROR CHANGE
# ==========================================================

def test_error_change():
    """
    Test relative MAE and RMSE changes.
    """

    previous = {
        'quality_score': 0.80,
        'mae': 10.0,
        'rmse': 20.0,
    }

    current = {
        'quality_score': 0.70,
        'mae': 15.0,
        'rmse': 30.0,
    }

    mae_change = calculate_error_change(
        previous,
        current,
        metric='mae',
    )

    rmse_change = calculate_error_change(
        previous,
        current,
        metric='rmse',
    )

    assert_close(
        mae_change,
        0.50,
    )

    assert_close(
        rmse_change,
        0.50,
    )


def test_zero_previous_error():
    """
    Moving from zero error to non-zero error must be
    represented safely.
    """

    previous = {
        'quality_score': 1.0,
        'mae': 0.0,
    }

    current = {
        'quality_score': 0.80,
        'mae': 10.0,
    }

    result = calculate_error_change(
        previous,
        current,
        metric='mae',
    )

    assert result == float('inf')


# ==========================================================
# CONTINUOUS DEGRADATION
# ==========================================================

def test_continuous_degradation():
    """
    Multiple consecutive degrading periods must be detected.
    """

    snapshots = [

        {
            'quality_score': 0.95,
            'reliability_level': 'high',
        },

        {
            'quality_score': 0.85,
            'reliability_level': 'high',
        },

        {
            'quality_score': 0.75,
            'reliability_level': 'medium',
        },

        {
            'quality_score': 0.60,
            'reliability_level': 'low',
        },

    ]

    result = detect_continuous_degradation(
        snapshots,
        minimum_degrading_periods=2,
    )

    assert (
        result['status']
        == MONITORING_DEGRADING
    )

    assert (
        result['continuous_degradation']
        is True
    )

    assert (
        result['degrading_periods']
        == 3
    )


def test_degradation_resets_after_improvement():
    """
    A non-degrading period resets the consecutive
    degradation counter.
    """

    snapshots = [

        {
            'quality_score': 0.90,
            'reliability_level': 'high',
        },

        {
            'quality_score': 0.80,
            'reliability_level': 'high',
        },

        {
            'quality_score': 0.70,
            'reliability_level': 'medium',
        },

        {
            'quality_score': 0.85,
            'reliability_level': 'high',
        },

        {
            'quality_score': 0.75,
            'reliability_level': 'medium',
        },

    ]

    result = detect_continuous_degradation(
        snapshots,
        minimum_degrading_periods=2,
    )

    assert (
        result['continuous_degradation']
        is False
    )

    assert (
        result['degrading_periods']
        == 1
    )


# ==========================================================
# HISTORY MONITORING
# ==========================================================

def test_monitor_history():
    """
    Test complete reliability history monitoring.
    """

    snapshots = [

        {
            'period': '2026-08-01',
            'quality_score': 0.90,
            'reliability_level': 'high',
            'mae': 10.0,
        },

        {
            'period': '2026-08-08',
            'quality_score': 0.82,
            'reliability_level': 'high',
            'mae': 12.0,
        },

        {
            'period': '2026-08-15',
            'quality_score': 0.70,
            'reliability_level': 'medium',
            'mae': 18.0,
        },

    ]

    result = monitor_reliability_history(
        snapshots
    )

    assert (
        result['status']
        == MONITORING_VALID
    )

    assert (
        result['snapshot_count']
        == 3
    )

    assert (
        result['current_status']
        == MONITORING_DEGRADING
    )

    assert (
        result['continuous_degradation']
        is True
    )


def test_history_with_single_snapshot():
    """
    One snapshot is not enough to detect a trend.
    """

    snapshots = [

        {
            'quality_score': 0.90,
            'reliability_level': 'high',
        },

    ]

    result = monitor_reliability_history(
        snapshots
    )

    assert (
        result['status']
        == MONITORING_INSUFFICIENT_DATA
    )

    assert (
        result['current_status']
        == MONITORING_INSUFFICIENT_DATA
    )


# ==========================================================
# SNAPSHOT CREATION
# ==========================================================

def test_create_monitoring_snapshot():
    """
    Test normalization of reliability results.
    """

    reliability_result = {

        'sample_count':
            100,

        'quality_score':
            0.85,

        'reliability_level':
            'high',

        'mae':
            10.0,

        'rmse':
            15.0,

        'accuracy':
            None,

        'error_rate':
            None,

        'expected_calibration_error':
            None,
    }

    snapshot = create_monitoring_snapshot(
        reliability_result,
        period='2026-08-17',
        target_name='Target_Expense_Total_1D',
    )

    assert (
        snapshot['period']
        == '2026-08-17'
    )

    assert (
        snapshot['target_name']
        == 'Target_Expense_Total_1D'
    )

    assert (
        snapshot['sample_count']
        == 100
    )

    assert_close(
        snapshot['quality_score'],
        0.85,
    )

    assert (
        snapshot['reliability_level']
        == 'high'
    )


# ==========================================================
# EVALUATION HISTORY
# ==========================================================

def test_monitor_evaluation_history():
    """
    Test monitoring directly from reliability results.
    """

    results = [

        {
            'sample_count': 100,
            'quality_score': 0.90,
            'reliability_level': 'high',
            'mae': 10.0,
        },

        {
            'sample_count': 100,
            'quality_score': 0.80,
            'reliability_level': 'high',
            'mae': 12.0,
        },

        {
            'sample_count': 100,
            'quality_score': 0.65,
            'reliability_level': 'medium',
            'mae': 20.0,
        },

    ]

    result = monitor_evaluation_history(
        results,
        periods=[
            '2026-08-01',
            '2026-08-08',
            '2026-08-15',
        ],
        target_name='Target_Expense_Total_1D',
    )

    assert (
        result['status']
        == MONITORING_VALID
    )

    assert (
        result['snapshot_count']
        == 3
    )

    assert (
        result['current_status']
        == MONITORING_DEGRADING
    )


# ==========================================================
# INSUFFICIENT QUALITY DATA
# ==========================================================

def test_missing_quality_score():
    """
    Missing quality scores must not produce a false
    reliability trend.
    """

    previous = {
        'quality_score': None,
        'reliability_level': 'unknown',
    }

    current = {
        'quality_score': 0.80,
        'reliability_level': 'high',
    }

    result = compare_reliability_snapshots(
        previous,
        current,
    )

    assert (
        result['status']
        == MONITORING_INSUFFICIENT_DATA
    )

    assert (
        result['quality_change']
        is None
    )


# ==========================================================
# INVALID INPUTS
# ==========================================================

def test_invalid_inputs():
    """
    Verify safe validation.
    """

    # Missing snapshot.

    try:

        compare_reliability_snapshots(
            None,
            {
                'quality_score': 0.8,
            },
        )

        assert False

    except ValueError:

        pass

    # Invalid quality score.

    try:

        compare_reliability_snapshots(
            {
                'quality_score': 1.2,
            },
            {
                'quality_score': 0.8,
            },
        )

        assert False

    except ValueError:

        pass

    # Invalid threshold.

    try:

        compare_reliability_snapshots(
            {
                'quality_score': 0.8,
            },
            {
                'quality_score': 0.7,
            },
            degradation_threshold=-0.1,
        )

        assert False

    except ValueError:

        pass

    # Invalid metric.

    try:

        calculate_error_change(
            {
                'quality_score': 0.8,
                'mae': 10,
            },
            {
                'quality_score': 0.7,
                'mae': 12,
            },
            metric='unsupported',
        )

        assert False

    except ValueError:

        pass

    # Empty history.

    try:

        monitor_reliability_history(
            []
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
        '       PREDICTION RELIABILITY MONITORING TEST'
    )

    print(
        '=================================================='
    )

    test_stable_snapshots()

    test_improving_snapshots()

    test_degrading_snapshots()

    test_critical_degradation()

    test_error_change()

    test_zero_previous_error()

    test_continuous_degradation()

    test_degradation_resets_after_improvement()

    test_monitor_history()

    test_history_with_single_snapshot()

    test_create_monitoring_snapshot()

    test_monitor_evaluation_history()

    test_missing_quality_score()

    test_invalid_inputs()

    print()
    print(
        '=================================================='
    )

    print(
        '       ALL MONITORING TESTS PASSED'
    )

    print(
        '=================================================='
    )