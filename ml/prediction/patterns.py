"""
Prediction Pattern Detection
=============================

Detect recurring or directional patterns across prediction-level
monitoring records.

Architectural boundary
----------------------

This module does not:

- calculate prediction errors;
- calculate reliability levels;
- generate alerts;
- generate recommendations.

Those responsibilities belong to the monitoring, reliability, alerts,
and recommendations layers respectively.

This module only detects patterns across already evaluated monitoring
records.
"""

from ml.prediction.monitoring import (
    RELIABILITY_LOW,
    RELIABILITY_UNKNOWN,
)


# ==========================================================
# PATTERN STATUS
# ==========================================================

PATTERN_DETECTED = 'patterns_detected'
PATTERN_NONE = 'no_patterns'
PATTERN_INSUFFICIENT_DATA = 'insufficient_data'
PATTERN_INVALID = 'invalid'


# ==========================================================
# PATTERN TYPES
# ==========================================================

PATTERN_PERSISTENT_LOW_RELIABILITY = (
    'persistent_low_reliability'
)

PATTERN_PERSISTENT_HIGH_ERROR = (
    'persistent_high_error'
)

PATTERN_RELIABILITY_DECLINE = (
    'reliability_decline'
)

PATTERN_INCREASING_ERROR = (
    'increasing_error'
)

PATTERN_INSUFFICIENT_DATA = (
    'insufficient_data'
)


# ==========================================================
# SEVERITY
# ==========================================================

PATTERN_SEVERITY_INFO = 'info'
PATTERN_SEVERITY_WARNING = 'warning'
PATTERN_SEVERITY_HIGH = 'high'
PATTERN_SEVERITY_CRITICAL = 'critical'


# ==========================================================
# VALIDATION
# ==========================================================

def _validate_records(
    monitoring_records,
):
    """
    Validate monitoring records.

    The records must be supplied in chronological order.
    This function intentionally does not reorder them.
    """

    if monitoring_records is None:

        raise ValueError(
            'monitoring_records is required.'
        )

    try:

        records = list(
            monitoring_records
        )

    except TypeError as exc:

        raise ValueError(
            'monitoring_records must be iterable.'
        ) from exc

    if not records:

        raise ValueError(
            'monitoring_records cannot be empty.'
        )

    for index, record in enumerate(records):

        if not isinstance(
            record,
            dict,
        ):

            raise ValueError(
                f'monitoring_records[{index}] '
                'must be a dictionary.'
            )

    return records


def _validate_minimum_occurrences(
    value,
):
    """
    Validate a minimum occurrence count.
    """

    if isinstance(
        value,
        bool,
    ) or not isinstance(
        value,
        int,
    ):

        raise ValueError(
            'minimum_occurrences must be '
            'a positive integer.'
        )

    if value <= 0:

        raise ValueError(
            'minimum_occurrences must be '
            'greater than zero.'
        )

    return value


def _to_float(
    value,
    name,
):
    """
    Convert a value to a finite float.
    """

    if isinstance(
        value,
        bool,
    ):

        raise ValueError(
            f'{name} must be numeric.'
        )

    try:

        numeric_value = float(
            value
        )

    except (
        TypeError,
        ValueError,
    ) as exc:

        raise ValueError(
            f'{name} must be numeric.'
        ) from exc

    if numeric_value != numeric_value:

        raise ValueError(
            f'{name} must be finite.'
        )

    if numeric_value in (
        float('inf'),
        float('-inf'),
    ):

        raise ValueError(
            f'{name} must be finite.'
        )

    return numeric_value


def _validate_non_negative(
    value,
    name,
):
    """
    Validate a non-negative numeric threshold.
    """

    value = _to_float(
        value,
        name,
    )

    if value < 0:

        raise ValueError(
            f'{name} cannot be negative.'
        )

    return value


# ==========================================================
# BASIC HELPERS
# ==========================================================

def _target_name(
    records,
):
    """
    Return the target name when available.

    A pattern result should preserve the monitored target.
    """

    for record in records:

        if record.get(
            'target_name'
        ) is not None:

            return record.get(
                'target_name'
            )

    return None


def _evaluated_records(
    records,
):
    """
    Return records whose actual values are available.
    """

    return [
        record
        for record in records
        if record.get(
            'actual_value_available'
        ) is True
    ]


def _create_pattern(
    pattern_type,
    severity,
    message,
    reason,
    target_name=None,
    occurrences=0,
    metric=None,
    current_value=None,
    threshold=None,
):
    """
    Create a standardized pattern dictionary.
    """

    return {

        'pattern_type':
            pattern_type,

        'severity':
            severity,

        'message':
            message,

        'reason':
            reason,

        'target_name':
            target_name,

        'occurrences':
            occurrences,

        'metric':
            metric,

        'current_value':
            current_value,

        'threshold':
            threshold,
    }


# ==========================================================
# PERSISTENT LOW RELIABILITY
# ==========================================================

def _detect_persistent_low_reliability(
    records,
    minimum_occurrences,
):
    """
    Detect repeated low-reliability observations.
    """

    low_records = [
        record
        for record in records
        if record.get(
            'reliability_level'
        ) == RELIABILITY_LOW
    ]

    occurrences = len(
        low_records
    )

    if occurrences < minimum_occurrences:

        return None

    return _create_pattern(
        pattern_type=(
            PATTERN_PERSISTENT_LOW_RELIABILITY
        ),
        severity=PATTERN_SEVERITY_HIGH,
        message=(
            'Low prediction reliability is '
            'occurring repeatedly.'
        ),
        reason=(
            'Multiple monitored predictions '
            'were classified as low reliability.'
        ),
        target_name=_target_name(
            records
        ),
        occurrences=occurrences,
        metric='reliability_level',
        current_value=RELIABILITY_LOW,
        threshold=minimum_occurrences,
    )


# ==========================================================
# PERSISTENT HIGH ERROR
# ==========================================================

def _detect_persistent_high_error(
    records,
    maximum_relative_error,
    minimum_occurrences,
):
    """
    Detect repeated relative errors above a configured threshold.
    """

    high_error_records = []

    for record in records:

        relative_error = record.get(
            'relative_error'
        )

        if relative_error is None:

            continue

        relative_error = _to_float(
            relative_error,
            'relative_error',
        )

        if relative_error > maximum_relative_error:

            high_error_records.append(
                record
            )

    occurrences = len(
        high_error_records
    )

    if occurrences < minimum_occurrences:

        return None

    current_value = max(
        _to_float(
            record['relative_error'],
            'relative_error',
        )
        for record in high_error_records
    )

    return _create_pattern(
        pattern_type=(
            PATTERN_PERSISTENT_HIGH_ERROR
        ),
        severity=PATTERN_SEVERITY_HIGH,
        message=(
            'High prediction error is '
            'occurring repeatedly.'
        ),
        reason=(
            'Multiple monitored predictions '
            'exceeded the configured relative '
            'error threshold.'
        ),
        target_name=_target_name(
            records
        ),
        occurrences=occurrences,
        metric='relative_error',
        current_value=current_value,
        threshold=maximum_relative_error,
    )


# ==========================================================
# RELIABILITY DECLINE
# ==========================================================

def _detect_reliability_decline(
    records,
    minimum_decline,
):
    """
    Detect a directional decline in relative-error-based reliability.

    Reliability levels are ordered:

        excellent
        good
        moderate
        low

    The detection is based on transitions between these levels.
    """

    level_order = {
        'excellent': 0,
        'good': 1,
        'moderate': 2,
        'low': 3,
    }

    evaluated = [
        record
        for record in records
        if record.get(
            'reliability_level'
        ) in level_order
    ]

    if len(
        evaluated
    ) < 2:

        return None

    first_level = evaluated[0].get(
        'reliability_level'
    )

    last_level = evaluated[-1].get(
        'reliability_level'
    )

    decline = (
        level_order[last_level]
        - level_order[first_level]
    )

    if decline < minimum_decline:

        return None

    return _create_pattern(
        pattern_type=(
            PATTERN_RELIABILITY_DECLINE
        ),
        severity=PATTERN_SEVERITY_WARNING,
        message=(
            'Prediction reliability has '
            'declined across monitored observations.'
        ),
        reason=(
            'The final reliability level is '
            'lower than the initial monitored '
            'reliability level.'
        ),
        target_name=_target_name(
            records
        ),
        occurrences=decline,
        metric='reliability_level',
        current_value=last_level,
        threshold=minimum_decline,
    )


# ==========================================================
# INCREASING ERROR
# ==========================================================

def _detect_increasing_error(
    records,
    minimum_error_increase,
):
    """
    Detect a meaningful increase in relative error.

    The comparison is between the first and last
    available relative-error observations.
    """

    errors = []

    for record in records:

        relative_error = record.get(
            'relative_error'
        )

        if relative_error is None:

            continue

        errors.append(
            _to_float(
                relative_error,
                'relative_error',
            )
        )

    if len(errors) < 2:

        return None

    increase = (
        errors[-1]
        - errors[0]
    )

    if increase < minimum_error_increase:

        return None

    return _create_pattern(
        pattern_type=(
            PATTERN_INCREASING_ERROR
        ),
        severity=PATTERN_SEVERITY_WARNING,
        message=(
            'Prediction error is increasing '
            'across monitored observations.'
        ),
        reason=(
            'The latest relative error is '
            'higher than the earliest monitored '
            'relative error by at least the '
            'configured threshold.'
        ),
        target_name=_target_name(
            records
        ),
        occurrences=len(errors),
        metric='relative_error',
        current_value=errors[-1],
        threshold=(
            errors[0]
            + minimum_error_increase
        ),
    )


# ==========================================================
# INSUFFICIENT DATA
# ==========================================================

def _detect_insufficient_data(
    records,
    minimum_occurrences,
):
    """
    Detect a lack of evaluated reliability data.
    """

    evaluated = _evaluated_records(
        records
    )

    if len(
        evaluated
    ) >= minimum_occurrences:

        return None

    return _create_pattern(
        pattern_type=(
            PATTERN_INSUFFICIENT_DATA
        ),
        severity=PATTERN_SEVERITY_INFO,
        message=(
            'There is not enough evaluated '
            'monitoring data to detect reliable patterns.'
        ),
        reason=(
            'The number of evaluated monitoring '
            'records is below the configured '
            'minimum required for pattern detection.'
        ),
        target_name=_target_name(
            records
        ),
        occurrences=len(
            evaluated
        ),
        metric='evaluated_count',
        current_value=len(
            evaluated
        ),
        threshold=minimum_occurrences,
    )


# ==========================================================
# PUBLIC PATTERN ANALYSIS
# ==========================================================

def detect_patterns(
    monitoring_records,
    minimum_occurrences=3,
    maximum_relative_error=None,
    minimum_reliability_decline=None,
    minimum_error_increase=None,
):
    """
    Detect recurring or directional patterns.

    Parameters
    ----------

    monitoring_records:
        Monitoring records produced by monitoring.py.

    minimum_occurrences:
        Minimum number of observations required for
        recurring-pattern detection.

    maximum_relative_error:
        Optional explicit threshold for persistent
        high-error detection.

    minimum_reliability_decline:
        Optional number of reliability levels that
        must be lost between the earliest and latest
        observations.

    minimum_error_increase:
        Optional absolute increase in relative error
        required for increasing-error detection.

    Important
    ---------

    No threshold-based pattern is generated when its
    threshold has not been explicitly supplied.
    """

    records = _validate_records(
        monitoring_records
    )

    minimum_occurrences = (
        _validate_minimum_occurrences(
            minimum_occurrences
        )
    )

    if maximum_relative_error is not None:

        maximum_relative_error = (
            _validate_non_negative(
                maximum_relative_error,
                'maximum_relative_error',
            )
        )

    if minimum_reliability_decline is not None:

        minimum_reliability_decline = (
            _validate_non_negative(
                minimum_reliability_decline,
                'minimum_reliability_decline',
            )
        )

    if minimum_error_increase is not None:

        minimum_error_increase = (
            _validate_non_negative(
                minimum_error_increase,
                'minimum_error_increase',
            )
        )

    patterns = []

    insufficient_pattern = (
        _detect_insufficient_data(
            records,
            minimum_occurrences,
        )
    )

    if insufficient_pattern is not None:

        patterns.append(
            insufficient_pattern
        )

        return {
            'status':
                PATTERN_INSUFFICIENT_DATA,

            'pattern_count':
                len(patterns),

            'patterns':
                patterns,

            'target_name':
                _target_name(records),
        }

    persistent_low = (
        _detect_persistent_low_reliability(
            records,
            minimum_occurrences,
        )
    )

    if persistent_low is not None:

        patterns.append(
            persistent_low
        )

    if maximum_relative_error is not None:

        persistent_error = (
            _detect_persistent_high_error(
                records,
                maximum_relative_error,
                minimum_occurrences,
            )
        )

        if persistent_error is not None:

            patterns.append(
                persistent_error
            )

    if minimum_reliability_decline is not None:

        decline_pattern = (
            _detect_reliability_decline(
                records,
                minimum_reliability_decline,
            )
        )

        if decline_pattern is not None:

            patterns.append(
                decline_pattern
            )

    if minimum_error_increase is not None:

        increasing_error = (
            _detect_increasing_error(
                records,
                minimum_error_increase,
            )
        )

        if increasing_error is not None:

            patterns.append(
                increasing_error
            )

    return {

        'status': (
            PATTERN_DETECTED
            if patterns
            else PATTERN_NONE
        ),

        'pattern_count':
            len(patterns),

        'patterns':
            patterns,

        'target_name':
            _target_name(records),
    }


# ==========================================================
# CONVENIENCE FUNCTION
# ==========================================================

def has_patterns(
    pattern_result,
):
    """
    Return True when at least one pattern exists.
    """

    if pattern_result is None:

        raise ValueError(
            'pattern_result is required.'
        )

    if not isinstance(
        pattern_result,
        dict,
    ):

        raise ValueError(
            'pattern_result must be a dictionary.'
        )

    return (
        pattern_result.get(
            'pattern_count',
            0,
        )
        > 0
    )