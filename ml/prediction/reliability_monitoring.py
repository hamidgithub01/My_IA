"""
Prediction Reliability Monitoring
=================================

High-level facade for prediction-level reliability monitoring.

This layer composes ``ml.prediction.monitoring`` and deliberately keeps the
pending -> actual -> evaluated lifecycle explicit.
"""

from ml.prediction.monitoring import (
    MONITORING_READY,
    MONITORING_PENDING_ACTUAL,
    RELIABILITY_UNKNOWN,
    create_monitoring_record,
    evaluate_prediction,
    evaluate_prediction_batch,
    summarize_monitoring,
)


# ==========================================================
# HIGH-LEVEL STATUS
# ==========================================================

RELIABILITY_MONITORING_VALID = 'valid'
RELIABILITY_MONITORING_PENDING = 'pending'
RELIABILITY_MONITORING_EVALUATED = 'evaluated'
RELIABILITY_MONITORING_INVALID = 'invalid'


# ==========================================================
# VALIDATION
# ==========================================================

def _validate_prediction_result(prediction_result):
    """Validate the minimum fields required by production monitoring."""
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
    return True


# ==========================================================
# PENDING RECORD
# ==========================================================

def create_reliability_monitoring_record(prediction_result):
    """Create a pending high-level monitoring response."""
    _validate_prediction_result(prediction_result)
    record = create_monitoring_record(prediction_result)

    return {
        'status': RELIABILITY_MONITORING_PENDING,
        'monitoring_record': record,
        'reliability_available': False,
        'reliability': RELIABILITY_UNKNOWN,
    }


# ==========================================================
# SINGLE EVALUATION
# ==========================================================

def evaluate_reliability(prediction_result, actual_value):
    """Evaluate one prediction after its actual value becomes available."""
    _validate_prediction_result(prediction_result)
    monitoring_record = evaluate_prediction(prediction_result, actual_value)

    evaluated = monitoring_record['status'] == MONITORING_READY
    return {
        'status': (
            RELIABILITY_MONITORING_EVALUATED
            if evaluated else RELIABILITY_MONITORING_INVALID
        ),
        'monitoring_record': monitoring_record,
        'reliability_available': monitoring_record['reliability_available'],
        'reliability': monitoring_record['reliability_level'],
    }


# ==========================================================
# COMPLETE FLOW
# ==========================================================

def monitor_prediction(prediction_result, actual_value=None):
    """Create a pending record or evaluate it when an actual value is supplied."""
    if actual_value is None:
        return create_reliability_monitoring_record(prediction_result)
    return evaluate_reliability(prediction_result, actual_value)


# ==========================================================
# BATCH
# ==========================================================

def monitor_prediction_batch(prediction_results, actual_values):
    """Evaluate a batch and return both records and aggregate summary."""
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

    records = evaluate_prediction_batch(prediction_results, actual_values)
    summary = summarize_monitoring(records)

    return {
        'status': RELIABILITY_MONITORING_EVALUATED,
        'records': records,
        'summary': summary,
        'evaluated_count': summary['evaluated_count'],
        'reliability_counts': summary['reliability_counts'],
    }


# ==========================================================
# READ EXISTING STATUS
# ==========================================================

def get_reliability_status(monitoring_record):
    """Read status without recalculating prediction reliability."""
    if not isinstance(monitoring_record, dict):
        raise ValueError('monitoring_record must be a dictionary.')

    if not monitoring_record.get('actual_value_available', False):
        return {
            'status': RELIABILITY_MONITORING_PENDING,
            'reliability_available': False,
            'reliability': RELIABILITY_UNKNOWN,
        }

    return {
        'status': RELIABILITY_MONITORING_EVALUATED,
        'reliability_available': monitoring_record.get(
            'reliability_available', False
        ),
        'reliability': monitoring_record.get(
            'reliability_level', RELIABILITY_UNKNOWN
        ),
    }
