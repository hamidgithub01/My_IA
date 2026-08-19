"""
Prediction Monitoring
=====================

Prediction-level monitoring after production predictions are created.

Architectural boundary
----------------------
This module tracks individual predictions until their actual outcomes become
available, evaluates their errors, and aggregates those observations.

It deliberately does not calculate model-level baseline-relative reliability;
that responsibility belongs to ``ml.prediction.reliability``.
"""

import math
from datetime import datetime, timezone


# ==========================================================
# MONITORING STATUS
# ==========================================================

MONITORING_VALID = 'valid'
MONITORING_DEGRADED = 'degraded'
MONITORING_STABLE = 'stable'
MONITORING_IMPROVED = 'improved'
MONITORING_DEGRADED_STATE = MONITORING_DEGRADED


# ==========================================================
# RELIABILITY LEVELS
# ==========================================================

RELIABILITY_EXCELLENT = 'excellent'
RELIABILITY_GOOD = 'good'
RELIABILITY_MODERATE = 'moderate'
RELIABILITY_LOW = 'low'
RELIABILITY_UNKNOWN = 'unknown'


# ==========================================================
# MONITORING RECORD STATUS
# ==========================================================

MONITORING_PENDING_ACTUAL = 'pending_actual'
MONITORING_READY = 'ready_for_evaluation'


# ==========================================================
# DEFAULT THRESHOLDS
# ==========================================================

DEFAULT_DEGRADATION_THRESHOLD = 0.10
DEFAULT_IMPROVEMENT_THRESHOLD = 0.05
DEFAULT_EXCELLENT_MAX_ERROR = 0.05
DEFAULT_GOOD_MAX_ERROR = 0.10
DEFAULT_MODERATE_MAX_ERROR = 0.20
DEFAULT_LOW_MAX_ERROR = 0.50


# ==========================================================
# VALIDATION
# ==========================================================

def _validate_finite_number(value, name):
    """Validate one finite numeric value; booleans are rejected."""
    if value is None:
        raise ValueError(f'{name} is required.')
    if isinstance(value, bool):
        raise ValueError(f'{name} must be numeric.')
    try:
        numeric_value = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f'{name} must be numeric.') from exc
    if not math.isfinite(numeric_value):
        raise ValueError(f'{name} must be finite.')
    return numeric_value


def _validate_score(value, name='score'):
    value = _validate_finite_number(value, name)
    if not 0.0 <= value <= 1.0:
        raise ValueError(f'{name} must be between 0 and 1.')
    return value


def _validate_threshold(value, name='threshold'):
    return _validate_score(value, name)


def _validate_sample_count(value, name='sample_count'):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f'{name} must be a non-negative integer.')
    if value < 0:
        raise ValueError(f'{name} cannot be negative.')
    return value


def _current_timestamp():
    """Return a timezone-aware UTC ISO-8601 timestamp."""
    return datetime.now(timezone.utc).isoformat()


# ==========================================================
# SCORE MONITORING
# ==========================================================

def calculate_score_change(current_score, previous_score):
    """Return current - previous, or None when previous is unavailable."""
    current_score = _validate_score(current_score, 'current_score')
    if previous_score is None:
        return None
    previous_score = _validate_score(previous_score, 'previous_score')
    return current_score - previous_score


def detect_degradation(
    current_score,
    previous_score,
    degradation_threshold=DEFAULT_DEGRADATION_THRESHOLD,
):
    """Return True when the score drop reaches the configured threshold."""
    current_score = _validate_score(current_score, 'current_score')
    if previous_score is None:
        return False
    previous_score = _validate_score(previous_score, 'previous_score')
    degradation_threshold = _validate_threshold(
        degradation_threshold, 'degradation_threshold'
    )
    score_drop = previous_score - current_score
    return score_drop >= degradation_threshold - 1e-12


def detect_improvement(
    current_score,
    previous_score,
    improvement_threshold=DEFAULT_IMPROVEMENT_THRESHOLD,
):
    """Return True when the score gain reaches the configured threshold."""
    current_score = _validate_score(current_score, 'current_score')
    if previous_score is None:
        return False
    previous_score = _validate_score(previous_score, 'previous_score')
    improvement_threshold = _validate_threshold(
        improvement_threshold, 'improvement_threshold'
    )
    score_gain = current_score - previous_score
    return score_gain >= improvement_threshold - 1e-12


def determine_monitoring_state(
    current_score,
    previous_score,
    degradation_threshold=DEFAULT_DEGRADATION_THRESHOLD,
    improvement_threshold=DEFAULT_IMPROVEMENT_THRESHOLD,
):
    """Return stable, improved, or degraded."""
    current_score = _validate_score(current_score, 'current_score')
    degradation_threshold = _validate_threshold(
        degradation_threshold, 'degradation_threshold'
    )
    improvement_threshold = _validate_threshold(
        improvement_threshold, 'improvement_threshold'
    )

    if previous_score is None:
        return MONITORING_STABLE

    previous_score = _validate_score(previous_score, 'previous_score')

    if detect_degradation(current_score, previous_score, degradation_threshold):
        return MONITORING_DEGRADED
    if detect_improvement(current_score, previous_score, improvement_threshold):
        return MONITORING_IMPROVED
    return MONITORING_STABLE


def _build_monitoring_result(
    current_result,
    previous_result,
    score_key,
    level_key,
    degradation_threshold,
    improvement_threshold,
):
    """Build a common score-monitoring result."""
    if current_result is None:
        raise ValueError('current_result is required.')
    if not isinstance(current_result, dict):
        raise ValueError('current_result must be a dictionary.')
    if previous_result is not None and not isinstance(previous_result, dict):
        raise ValueError('previous_result must be a dictionary.')

    if score_key not in current_result:
        raise ValueError(f'current_result is missing {score_key}.')
    current_score = _validate_score(current_result[score_key], score_key)

    previous_score = None
    if previous_result is not None:
        if score_key not in previous_result:
            raise ValueError(f'previous_result is missing {score_key}.')
        previous_score = _validate_score(
            previous_result[score_key], f'previous_{score_key}'
        )

    if 'sample_count' not in current_result:
        raise ValueError('sample_count is required.')
    sample_count = _validate_sample_count(current_result['sample_count'])

    previous_sample_count = None
    if previous_result is not None and 'sample_count' in previous_result:
        previous_sample_count = _validate_sample_count(
            previous_result['sample_count'], 'previous_sample_count'
        )

    degradation_threshold = _validate_threshold(
        degradation_threshold, 'degradation_threshold'
    )
    improvement_threshold = _validate_threshold(
        improvement_threshold, 'improvement_threshold'
    )

    degraded = detect_degradation(
        current_score, previous_score, degradation_threshold
    )
    improved = detect_improvement(
        current_score, previous_score, improvement_threshold
    )

    return {
        'status': MONITORING_DEGRADED if degraded else MONITORING_VALID,
        'monitoring_state': determine_monitoring_state(
            current_score,
            previous_score,
            degradation_threshold,
            improvement_threshold,
        ),
        'degraded': degraded,
        'improved': improved,
        f'current_{score_key}': current_score,
        f'previous_{score_key}': previous_score,
        'score_change': calculate_score_change(current_score, previous_score),
        f'current_{level_key}': current_result.get(level_key),
        f'previous_{level_key}': (
            previous_result.get(level_key) if previous_result is not None else None
        ),
        'sample_count': sample_count,
        'previous_sample_count': previous_sample_count,
        'monitored_at': _current_timestamp(),
    }


# ==========================================================
# RELIABILITY / CALIBRATION SCORE MONITORING
# ==========================================================

def monitor_reliability(
    current_result,
    previous_result=None,
    degradation_threshold=DEFAULT_DEGRADATION_THRESHOLD,
    improvement_threshold=DEFAULT_IMPROVEMENT_THRESHOLD,
):
    """Monitor a model-level reliability score supplied by reliability.py."""
    return _build_monitoring_result(
        current_result,
        previous_result,
        'reliability_score',
        'reliability_level',
        degradation_threshold,
        improvement_threshold,
    )


def monitor_calibration(
    current_result,
    previous_result=None,
    degradation_threshold=DEFAULT_DEGRADATION_THRESHOLD,
    improvement_threshold=DEFAULT_IMPROVEMENT_THRESHOLD,
):
    """Monitor a calibration score."""
    return _build_monitoring_result(
        current_result,
        previous_result,
        'calibration_score',
        'calibration_level',
        degradation_threshold,
        improvement_threshold,
    )


def monitor_prediction(
    current_result,
    previous_result=None,
    degradation_threshold=DEFAULT_DEGRADATION_THRESHOLD,
    improvement_threshold=DEFAULT_IMPROVEMENT_THRESHOLD,
):
    """Unified score-monitoring entry point."""
    if current_result is None:
        raise ValueError('current_result is required.')
    if not isinstance(current_result, dict):
        raise ValueError('current_result must be a dictionary.')

    if 'reliability_score' in current_result:
        return monitor_reliability(
            current_result,
            previous_result,
            degradation_threshold,
            improvement_threshold,
        )
    if 'calibration_score' in current_result:
        return monitor_calibration(
            current_result,
            previous_result,
            degradation_threshold,
            improvement_threshold,
        )
    raise ValueError(
        'current_result must contain either reliability_score or calibration_score.'
    )


# ==========================================================
# PREDICTION RECORD VALIDATION
# ==========================================================

def _validate_prediction_result(prediction_result):
    """Validate a production prediction result."""
    if prediction_result is None:
        raise ValueError('prediction_result is required.')
    if not isinstance(prediction_result, dict):
        raise ValueError('prediction_result must be a dictionary.')

    required_fields = ['prediction', 'target_name', 'target_task']
    missing_fields = [
        field for field in required_fields if field not in prediction_result
    ]
    if missing_fields:
        raise ValueError(
            'prediction_result is missing required fields: '
            f'{missing_fields}'
        )

    return _validate_finite_number(prediction_result['prediction'], 'prediction')


def _validate_actual_value(actual_value):
    return _validate_finite_number(actual_value, 'actual_value')


# ==========================================================
# ERROR METRICS
# ==========================================================

def calculate_absolute_error(prediction, actual_value):
    prediction = _validate_finite_number(prediction, 'prediction')
    actual_value = _validate_actual_value(actual_value)
    return abs(prediction - actual_value)


def calculate_signed_error(prediction, actual_value):
    prediction = _validate_finite_number(prediction, 'prediction')
    actual_value = _validate_actual_value(actual_value)
    return prediction - actual_value


def calculate_squared_error(prediction, actual_value):
    signed_error = calculate_signed_error(prediction, actual_value)
    return signed_error ** 2


def calculate_relative_error(prediction, actual_value):
    """Return absolute relative error; None when actual value is zero."""
    prediction = _validate_finite_number(prediction, 'prediction')
    actual_value = _validate_actual_value(actual_value)
    denominator = abs(actual_value)
    if denominator == 0.0:
        return None
    relative_error = abs(prediction - actual_value) / denominator
    if not math.isfinite(relative_error):
        raise ValueError('Calculated relative error is not finite.')
    return relative_error


# ==========================================================
# INDIVIDUAL PREDICTION RELIABILITY
# ==========================================================

def classify_reliability(
    relative_error,
    excellent_max_error=DEFAULT_EXCELLENT_MAX_ERROR,
    good_max_error=DEFAULT_GOOD_MAX_ERROR,
    moderate_max_error=DEFAULT_MODERATE_MAX_ERROR,
    low_max_error=DEFAULT_LOW_MAX_ERROR,
):
    """Classify an individual prediction by relative error."""
    if relative_error is None:
        return RELIABILITY_UNKNOWN

    relative_error = _validate_finite_number(relative_error, 'relative_error')
    if relative_error < 0.0:
        raise ValueError('relative_error cannot be negative.')

    thresholds = [
        ('excellent_max_error', excellent_max_error),
        ('good_max_error', good_max_error),
        ('moderate_max_error', moderate_max_error),
        ('low_max_error', low_max_error),
    ]
    validated = [
        _validate_finite_number(value, name)
        for name, value in thresholds
    ]
    if any(value < 0.0 for value in validated):
        raise ValueError('Reliability thresholds cannot be negative.')
    if not (
        validated[0] <= validated[1] <= validated[2] <= validated[3]
    ):
        raise ValueError('Reliability thresholds must be in ascending order.')

    if relative_error <= validated[0]:
        return RELIABILITY_EXCELLENT
    if relative_error <= validated[1]:
        return RELIABILITY_GOOD
    if relative_error <= validated[2]:
        return RELIABILITY_MODERATE
    return RELIABILITY_LOW


# ==========================================================
# MONITORING RECORDS
# ==========================================================

def create_monitoring_record(prediction_result):
    """Create a pending record; reliability remains unknown."""
    prediction = _validate_prediction_result(prediction_result)
    record = {
        'status': MONITORING_PENDING_ACTUAL,
        'target_name': prediction_result['target_name'],
        'target_task': prediction_result['target_task'],
        'prediction': prediction,
        'actual_value': None,
        'actual_value_available': False,
        'absolute_error': None,
        'signed_error': None,
        'squared_error': None,
        'relative_error': None,
        'reliability_available': False,
        'reliability_level': RELIABILITY_UNKNOWN,
        'reliability_status': 'pending_actual_value',
    }

    for field in ('model_history_id', 'model_version', 'Date'):
        if field in prediction_result:
            record[field] = prediction_result[field]

    return record


def evaluate_prediction(prediction_result, actual_value):
    """Complete a monitoring record after the actual target is available."""
    prediction = _validate_prediction_result(prediction_result)
    actual_value = _validate_actual_value(actual_value)

    relative_error = calculate_relative_error(prediction, actual_value)
    reliability_level = classify_reliability(relative_error)
    record = create_monitoring_record(prediction_result)
    record.update({
        'status': MONITORING_READY,
        'actual_value': actual_value,
        'actual_value_available': True,
        'signed_error': calculate_signed_error(prediction, actual_value),
        'absolute_error': calculate_absolute_error(prediction, actual_value),
        'squared_error': calculate_squared_error(prediction, actual_value),
        'relative_error': relative_error,
        'reliability_available': relative_error is not None,
        'reliability_level': reliability_level,
        'reliability_status': (
            'evaluated' if relative_error is not None else 'actual_value_zero'
        ),
    })
    return record


def evaluate_prediction_batch(prediction_results, actual_values):
    """Evaluate a non-empty batch of predictions against actual values."""
    if prediction_results is None:
        raise ValueError('prediction_results is required.')
    if actual_values is None:
        raise ValueError('actual_values are required.')

    try:
        prediction_results = list(prediction_results)
        actual_values = list(actual_values)
    except TypeError as exc:
        raise ValueError(
            'prediction_results and actual_values must be iterable.'
        ) from exc

    if not prediction_results:
        raise ValueError('prediction_results cannot be empty.')
    if len(prediction_results) != len(actual_values):
        raise ValueError('Prediction and actual-value counts must match.')

    return [
        evaluate_prediction(prediction_result, actual_value)
        for prediction_result, actual_value in zip(prediction_results, actual_values)
    ]


# ==========================================================
# SUMMARY
# ==========================================================

def summarize_monitoring(monitoring_records):
    """Aggregate evaluated prediction-level monitoring records."""
    if monitoring_records is None:
        raise ValueError('monitoring_records is required.')
    try:
        monitoring_records = list(monitoring_records)
    except TypeError as exc:
        raise ValueError('monitoring_records must be iterable.') from exc
    if not monitoring_records:
        raise ValueError('monitoring_records cannot be empty.')

    evaluated_records = [
        record
        for record in monitoring_records
        if isinstance(record, dict)
        and record.get('actual_value_available') is True
    ]

    reliability_counts = {
        RELIABILITY_EXCELLENT: 0,
        RELIABILITY_GOOD: 0,
        RELIABILITY_MODERATE: 0,
        RELIABILITY_LOW: 0,
        RELIABILITY_UNKNOWN: 0,
    }

    if not evaluated_records:
        return {
            'record_count': len(monitoring_records),
            'evaluated_count': 0,
            'reliability_available_count': 0,
            'mean_absolute_error': None,
            'mean_squared_error': None,
            'mean_relative_error': None,
            'reliability_counts': reliability_counts,
        }

    absolute_errors = []
    squared_errors = []
    relative_errors = []

    for index, record in enumerate(evaluated_records):
        absolute_errors.append(
            _validate_finite_number(
                record.get('absolute_error'),
                f'absolute_error[{index}]',
            )
        )
        squared_errors.append(
            _validate_finite_number(
                record.get('squared_error'),
                f'squared_error[{index}]',
            )
        )

        relative_error = record.get('relative_error')
        if relative_error is not None:
            relative_errors.append(
                _validate_finite_number(
                    relative_error,
                    f'relative_error[{index}]',
                )
            )

        reliability_level = record.get(
            'reliability_level', RELIABILITY_UNKNOWN
        )
        if reliability_level not in reliability_counts:
            raise ValueError(f'Unknown reliability level: {reliability_level}')
        reliability_counts[reliability_level] += 1

    return {
        'record_count': len(monitoring_records),
        'evaluated_count': len(evaluated_records),
        'reliability_available_count': len(relative_errors),
        'mean_absolute_error': sum(absolute_errors) / len(absolute_errors),
        'mean_squared_error': sum(squared_errors) / len(squared_errors),
        'mean_relative_error': (
            sum(relative_errors) / len(relative_errors)
            if relative_errors else None
        ),
        'reliability_counts': reliability_counts,
    }
