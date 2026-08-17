import math


# ==========================================================
# MONITORING STATUS
# ==========================================================

MONITORING_VALID = 'valid'

MONITORING_INSUFFICIENT_DATA = (
    'insufficient_data'
)

MONITORING_STABLE = 'stable'

MONITORING_IMPROVING = 'improving'

MONITORING_DEGRADING = 'degrading'

MONITORING_CRITICAL = 'critical'


# ==========================================================
# MONITORING HELPERS
# ==========================================================

def _to_float(
    value,
):
    """
    Convert a value to a finite float.
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


def _validate_snapshot(
    snapshot,
):
    """
    Validate a monitoring snapshot.
    """

    if snapshot is None:

        raise ValueError(
            'snapshot is required.'
        )

    if not isinstance(
        snapshot,
        dict,
    ):

        raise ValueError(
            'snapshot must be a dictionary.'
        )

    if 'quality_score' not in snapshot:

        raise ValueError(
            'snapshot must contain quality_score.'
        )

    quality_score = snapshot[
        'quality_score'
    ]

    if quality_score is not None:

        quality_score = _to_float(
            quality_score
        )

        if not (
            0.0
            <= quality_score
            <= 1.0
        ):

            raise ValueError(
                'quality_score must be between '
                '0 and 1.'
            )


def _validate_snapshots(
    snapshots,
):
    """
    Validate a chronological sequence of snapshots.
    """

    if snapshots is None:

        raise ValueError(
            'snapshots are required.'
        )

    if not isinstance(
        snapshots,
        (list, tuple),
    ):

        raise ValueError(
            'snapshots must be a list or tuple.'
        )

    if len(snapshots) == 0:

        raise ValueError(
            'At least one snapshot is required.'
        )

    for snapshot in snapshots:

        _validate_snapshot(
            snapshot
        )


def _get_quality_score(
    snapshot,
):
    """
    Return the quality score from a snapshot.
    """

    value = snapshot.get(
        'quality_score'
    )

    if value is None:

        return None

    return _to_float(
        value
    )


def _get_reliability_level(
    snapshot,
):
    """
    Return reliability level safely.
    """

    return snapshot.get(
        'reliability_level'
    )


# ==========================================================
# SINGLE SNAPSHOT COMPARISON
# ==========================================================

def compare_reliability_snapshots(
    previous_snapshot,
    current_snapshot,
    degradation_threshold=0.05,
    critical_threshold=0.20,
):
    """
    Compare two reliability snapshots.

    Positive quality change:
        improvement

    Negative quality change:
        degradation

    The thresholds prevent insignificant fluctuations from
    being treated as meaningful changes.
    """

    _validate_snapshot(
        previous_snapshot
    )

    _validate_snapshot(
        current_snapshot
    )

    degradation_threshold = _to_float(
        degradation_threshold
    )

    critical_threshold = _to_float(
        critical_threshold
    )

    if degradation_threshold < 0:

        raise ValueError(
            'degradation_threshold cannot be negative.'
        )

    if critical_threshold <= 0:

        raise ValueError(
            'critical_threshold must be greater than zero.'
        )

    if critical_threshold < degradation_threshold:

        raise ValueError(
            'critical_threshold must be greater than '
            'or equal to degradation_threshold.'
        )

    previous_quality = _get_quality_score(
        previous_snapshot
    )

    current_quality = _get_quality_score(
        current_snapshot
    )

    if (
        previous_quality is None
        or current_quality is None
    ):

        return {

            'status':
                MONITORING_INSUFFICIENT_DATA,

            'quality_change':
                None,

            'previous_quality_score':
                previous_quality,

            'current_quality_score':
                current_quality,

            'previous_reliability_level':
                _get_reliability_level(
                    previous_snapshot
                ),

            'current_reliability_level':
                _get_reliability_level(
                    current_snapshot
                ),
        }

    quality_change = (
        current_quality
        - previous_quality
    )

    # ------------------------------------------------------
    # Critical degradation
    # ------------------------------------------------------

    if (
        quality_change
        <= -critical_threshold
    ):

        status = MONITORING_CRITICAL

    # ------------------------------------------------------
    # Normal degradation
    # ------------------------------------------------------

    elif (
        quality_change
        <= -degradation_threshold
    ):

        status = MONITORING_DEGRADING

    # ------------------------------------------------------
    # Improvement
    # ------------------------------------------------------

    elif (
        quality_change
        >= degradation_threshold
    ):

        status = MONITORING_IMPROVING

    # ------------------------------------------------------
    # Stable
    # ------------------------------------------------------

    else:

        status = MONITORING_STABLE

    return {

        'status':
            status,

        'quality_change':
            float(quality_change),

        'previous_quality_score':
            float(previous_quality),

        'current_quality_score':
            float(current_quality),

        'previous_reliability_level':
            _get_reliability_level(
                previous_snapshot
            ),

        'current_reliability_level':
            _get_reliability_level(
                current_snapshot
            ),

        'reliability_level_changed':
            (
                _get_reliability_level(
                    previous_snapshot
                )
                !=
                _get_reliability_level(
                    current_snapshot
                )
            ),
    }


# ==========================================================
# ERROR CHANGE
# ==========================================================

def calculate_error_change(
    previous_snapshot,
    current_snapshot,
    metric='mae',
):
    """
    Calculate relative error change.

    Supported metrics:

        mae
        rmse

    Positive value:
        error increased.

    Negative value:
        error decreased.
    """

    _validate_snapshot(
        previous_snapshot
    )

    _validate_snapshot(
        current_snapshot
    )

    if metric not in {
        'mae',
        'rmse',
    }:

        raise ValueError(
            'Unsupported error metric: '
            f'{metric}'
        )

    previous_value = previous_snapshot.get(
        metric
    )

    current_value = current_snapshot.get(
        metric
    )

    if (
        previous_value is None
        or current_value is None
    ):

        return None

    previous_value = _to_float(
        previous_value
    )

    current_value = _to_float(
        current_value
    )

    if previous_value == 0:

        if current_value == 0:

            return 0.0

        return math.inf

    return (
        current_value
        - previous_value
    ) / previous_value


# ==========================================================
# CONTINUOUS DEGRADATION DETECTION
# ==========================================================

def detect_continuous_degradation(
    snapshots,
    minimum_degrading_periods=2,
    degradation_threshold=0.05,
):
    """
    Detect repeated reliability degradation.

    Snapshots must be ordered chronologically from oldest
    to newest.

    Example:

        [high, high, medium, low]

    may indicate continuous degradation.
    """

    _validate_snapshots(
        snapshots
    )

    if minimum_degrading_periods <= 0:

        raise ValueError(
            'minimum_degrading_periods must be greater '
            'than zero.'
        )

    degradation_threshold = _to_float(
        degradation_threshold
    )

    if degradation_threshold < 0:

        raise ValueError(
            'degradation_threshold cannot be negative.'
        )

    if len(snapshots) < 2:

        return {

            'status':
                MONITORING_INSUFFICIENT_DATA,

            'continuous_degradation':
                False,

            'degrading_periods':
                0,

            'comparisons':
                [],
        }

    comparisons = []

    degrading_periods = 0

    for index in range(
        1,
        len(snapshots)
    ):

        comparison = (
            compare_reliability_snapshots(
                snapshots[index - 1],
                snapshots[index],
                degradation_threshold=(
                    degradation_threshold
                ),
            )
        )

        comparisons.append(
            comparison
        )

        if comparison[
            'status'
        ] in {
            MONITORING_DEGRADING,
            MONITORING_CRITICAL,
        }:

            degrading_periods += 1

        else:

            degrading_periods = 0

    continuous = (
        degrading_periods
        >= minimum_degrading_periods
    )

    if continuous:

        status = MONITORING_DEGRADING

    else:

        status = MONITORING_STABLE

    return {

        'status':
            status,

        'continuous_degradation':
            continuous,

        'degrading_periods':
            degrading_periods,

        'minimum_degrading_periods':
            minimum_degrading_periods,

        'comparisons':
            comparisons,
    }


# ==========================================================
# MONITORING HISTORY
# ==========================================================

def monitor_reliability_history(
    snapshots,
    degradation_threshold=0.05,
    critical_threshold=0.20,
    minimum_degrading_periods=2,
):
    """
    Analyze the complete reliability history.

    The snapshots must be chronological.
    """

    _validate_snapshots(
        snapshots
    )

    if len(snapshots) < 2:

        return {

            'status':
                MONITORING_INSUFFICIENT_DATA,

            'snapshot_count':
                len(snapshots),

            'current_snapshot':
                snapshots[-1],

            'previous_snapshot':
                None,

            'current_status':
                MONITORING_INSUFFICIENT_DATA,

            'continuous_degradation':
                False,

            'degrading_periods':
                0,

            'latest_comparison':
                None,
        }

    latest_comparison = (
        compare_reliability_snapshots(
            snapshots[-2],
            snapshots[-1],
            degradation_threshold=(
                degradation_threshold
            ),
            critical_threshold=(
                critical_threshold
            ),
        )
    )

    continuous_result = (
        detect_continuous_degradation(
            snapshots,
            minimum_degrading_periods=(
                minimum_degrading_periods
            ),
            degradation_threshold=(
                degradation_threshold
            ),
        )
    )

    # ------------------------------------------------------
    # Critical takes priority.
    # ------------------------------------------------------

    if (
        latest_comparison['status']
        == MONITORING_CRITICAL
    ):

        current_status = (
            MONITORING_CRITICAL
        )

    elif (
        continuous_result[
            'continuous_degradation'
        ]
    ):

        current_status = (
            MONITORING_DEGRADING
        )

    else:

        current_status = (
            latest_comparison['status']
        )

    return {

        'status':
            MONITORING_VALID,

        'snapshot_count':
            len(snapshots),

        'current_snapshot':
            snapshots[-1],

        'previous_snapshot':
            snapshots[-2],

        'current_status':
            current_status,

        'continuous_degradation':
            continuous_result[
                'continuous_degradation'
            ],

        'degrading_periods':
            continuous_result[
                'degrading_periods'
            ],

        'latest_comparison':
            latest_comparison,

        'history_analysis':
            continuous_result,
    }


# ==========================================================
# EVALUATION RESULT MONITORING
# ==========================================================

def create_monitoring_snapshot(
    reliability_result,
    period=None,
    target_name=None,
):
    """
    Convert a reliability result into a normalized
    monitoring snapshot.

    This keeps monitoring independent from the exact
    structure of the prediction pipeline.
    """

    if reliability_result is None:

        raise ValueError(
            'reliability_result is required.'
        )

    if not isinstance(
        reliability_result,
        dict,
    ):

        raise ValueError(
            'reliability_result must be a dictionary.'
        )

    return {

        'period':
            period,

        'target_name':
            target_name,

        'sample_count':
            reliability_result.get(
                'sample_count'
            ),

        'quality_score':
            reliability_result.get(
                'quality_score'
            ),

        'reliability_level':
            reliability_result.get(
                'reliability_level'
            ),

        'mae':
            reliability_result.get(
                'mae'
            ),

        'rmse':
            reliability_result.get(
                'rmse'
            ),

        'accuracy':
            reliability_result.get(
                'accuracy'
            ),

        'error_rate':
            reliability_result.get(
                'error_rate'
            ),

        'expected_calibration_error':
            reliability_result.get(
                'expected_calibration_error'
            ),
    }


def monitor_evaluation_history(
    reliability_results,
    periods=None,
    target_name=None,
    degradation_threshold=0.05,
    critical_threshold=0.20,
    minimum_degrading_periods=2,
):
    """
    Build monitoring snapshots from reliability results
    and analyze their chronological history.
    """

    if reliability_results is None:

        raise ValueError(
            'reliability_results are required.'
        )

    if not isinstance(
        reliability_results,
        (list, tuple),
    ):

        raise ValueError(
            'reliability_results must be a list or tuple.'
        )

    if len(reliability_results) == 0:

        raise ValueError(
            'At least one reliability result is required.'
        )

    if periods is not None:

        if len(periods) != len(
            reliability_results
        ):

            raise ValueError(
                'periods must have the same length as '
                'reliability_results.'
            )

    snapshots = []

    for index, reliability_result in enumerate(
        reliability_results
    ):

        period = None

        if periods is not None:

            period = periods[index]

        snapshot = create_monitoring_snapshot(
            reliability_result,
            period=period,
            target_name=target_name,
        )

        snapshots.append(
            snapshot
        )

    return monitor_reliability_history(
        snapshots,
        degradation_threshold=(
            degradation_threshold
        ),
        critical_threshold=(
            critical_threshold
        ),
        minimum_degrading_periods=(
            minimum_degrading_periods
        ),
    )


# ==========================================================
# SIMPLE MANUAL TEST
# ==========================================================

if __name__ == '__main__':

    snapshots = [

        {
            'period': '2026-08-01',
            'quality_score': 0.90,
            'reliability_level': 'high',
            'mae': 10.0,
            'rmse': 15.0,
        },

        {
            'period': '2026-08-08',
            'quality_score': 0.84,
            'reliability_level': 'high',
            'mae': 12.0,
            'rmse': 17.0,
        },

        {
            'period': '2026-08-15',
            'quality_score': 0.72,
            'reliability_level': 'medium',
            'mae': 18.0,
            'rmse': 25.0,
        },

    ]

    result = monitor_reliability_history(
        snapshots
    )

    print()
    print(
        '========== PREDICTION RELIABILITY MONITORING =========='
    )

    print()
    print(result)

    print()
    print(
        '========== MONITORING TEST PASSED =========='
    )