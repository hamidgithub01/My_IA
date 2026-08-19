"""
Prediction Reliability
======================

Model-level reliability evaluation.

Responsibilities
----------------
1. Calculate prediction errors.
2. Evaluate regression reliability relative to a baseline.
3. Evaluate numeric classification reliability using accuracy.
4. Produce a unified reliability result.
5. Monitor model-level reliability changes over time.

Architectural boundary
----------------------
This module evaluates model performance. It does not create production
prediction-monitoring records and it never modifies, trains, or activates a
model.

Note
----
Classification labels are intentionally required to be numeric in this
version because the project targets are represented as numeric ML targets.
"""

import math


# ==========================================================
# RELIABILITY STATUS
# ==========================================================

RELIABILITY_VALID = 'valid'
RELIABILITY_INSUFFICIENT_DATA = 'insufficient_data'
RELIABILITY_UNRELIABLE = 'unreliable'


# ==========================================================
# RELIABILITY LEVELS
# ==========================================================

RELIABILITY_HIGH = 'high'
RELIABILITY_MEDIUM = 'medium'
RELIABILITY_LOW = 'low'


# ==========================================================
# DEFAULT CONFIGURATION
# ==========================================================

DEFAULT_MINIMUM_SAMPLE_COUNT = 2
HIGH_RELIABILITY_THRESHOLD = 0.80
MEDIUM_RELIABILITY_THRESHOLD = 0.60
DEFAULT_DEGRADATION_THRESHOLD = 0.0


# ==========================================================
# BASIC VALIDATION
# ==========================================================

def _validate_numeric_value(value, name):
    """Validate one finite numeric value; booleans are rejected."""
    if isinstance(value, bool):
        raise ValueError(f'{name} must be numeric.')

    try:
        numeric_value = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f'{name} must be numeric.') from exc

    if not math.isfinite(numeric_value):
        raise ValueError(f'{name} must be finite.')

    return numeric_value


def _validate_score(value, name='reliability_score'):
    """Validate a score in [0, 1]."""
    value = _validate_numeric_value(value, name)
    if not 0.0 <= value <= 1.0:
        raise ValueError(f'{name} must be between 0.0 and 1.0.')
    return value


def _validate_prediction_values(actual_values, predicted_values):
    """Validate paired numeric actual and predicted values."""
    if actual_values is None:
        raise ValueError('actual_values are required.')
    if predicted_values is None:
        raise ValueError('predicted_values are required.')

    try:
        actual = list(actual_values)
        predicted = list(predicted_values)
    except TypeError as exc:
        raise ValueError(
            'actual_values and predicted_values must be iterable.'
        ) from exc

    if not actual:
        raise ValueError('prediction values cannot be empty.')

    if len(actual) != len(predicted):
        raise ValueError(
            'actual_values and predicted_values must have equal lengths.'
        )

    validated_actual = [
        _validate_numeric_value(value, f'actual_values[{index}]')
        for index, value in enumerate(actual)
    ]
    validated_predicted = [
        _validate_numeric_value(value, f'predicted_values[{index}]')
        for index, value in enumerate(predicted)
    ]

    return validated_actual, validated_predicted


def _validate_minimum_sample_count(minimum_sample_count):
    """Validate a positive integer minimum sample count."""
    if isinstance(minimum_sample_count, bool):
        raise ValueError('minimum_sample_count must be an integer.')
    if not isinstance(minimum_sample_count, int):
        raise ValueError('minimum_sample_count must be an integer.')
    if minimum_sample_count < 1:
        raise ValueError('minimum_sample_count must be at least 1.')
    return minimum_sample_count


def _validate_baseline_mae(baseline_mae):
    """Validate a strictly positive baseline MAE."""
    baseline_mae = _validate_numeric_value(baseline_mae, 'baseline_mae')
    if baseline_mae <= 0.0:
        raise ValueError('baseline_mae must be greater than zero.')
    return baseline_mae


# ==========================================================
# ABSOLUTE ERRORS
# ==========================================================

def calculate_absolute_errors(actual_values, predicted_values):
    """Return absolute errors |actual - predicted|."""
    actual, predicted = _validate_prediction_values(actual_values, predicted_values)
    return [
        abs(actual_value - predicted_value)
        for actual_value, predicted_value in zip(actual, predicted)
    ]


# ==========================================================
# PREDICTION ERROR
# ==========================================================

def calculate_prediction_error(actual_values, predicted_values):
    """Return MAE, maximum absolute error, signed mean error and sample count."""
    actual, predicted = _validate_prediction_values(actual_values, predicted_values)
    absolute_errors = [
        abs(actual_value - predicted_value)
        for actual_value, predicted_value in zip(actual, predicted)
    ]
    errors = [
        predicted_value - actual_value
        for actual_value, predicted_value in zip(actual, predicted)
    ]
    sample_count = len(actual)

    return {
        'mae': sum(absolute_errors) / sample_count,
        'max_absolute_error': max(absolute_errors),
        'mean_error': sum(errors) / sample_count,
        'sample_count': sample_count,
    }


# ==========================================================
# RELIABILITY SCORE
# ==========================================================

def _calculate_regression_reliability_score(mae, baseline_mae):
    """Calculate bounded improvement over the baseline MAE."""
    mae = _validate_numeric_value(mae, 'mae')
    baseline_mae = _validate_baseline_mae(baseline_mae)

    improvement = (baseline_mae - mae) / baseline_mae
    reliability_score = max(0.0, min(1.0, improvement))
    return reliability_score, improvement


def _reliability_level_from_score(reliability_score):
    """Map a validated score to high/medium/low."""
    reliability_score = _validate_score(reliability_score)
    if reliability_score >= HIGH_RELIABILITY_THRESHOLD:
        return RELIABILITY_HIGH
    if reliability_score >= MEDIUM_RELIABILITY_THRESHOLD:
        return RELIABILITY_MEDIUM
    return RELIABILITY_LOW


# ==========================================================
# REGRESSION RELIABILITY
# ==========================================================

def calculate_regression_reliability(
    actual_values,
    predicted_values,
    baseline_mae,
    minimum_sample_count=DEFAULT_MINIMUM_SAMPLE_COUNT,
):
    """Evaluate regression reliability relative to baseline MAE."""
    baseline_mae = _validate_baseline_mae(baseline_mae)
    minimum_sample_count = _validate_minimum_sample_count(minimum_sample_count)
    error_result = calculate_prediction_error(actual_values, predicted_values)
    sample_count = error_result['sample_count']

    if sample_count < minimum_sample_count:
        return {
            'status': RELIABILITY_INSUFFICIENT_DATA,
            'reliability_level': RELIABILITY_LOW,
            'reliability_score': 0.0,
            'mae': error_result['mae'],
            'max_absolute_error': error_result['max_absolute_error'],
            'mean_error': error_result['mean_error'],
            'sample_count': sample_count,
            'baseline_mae': baseline_mae,
            'improvement': None,
        }

    reliability_score, improvement = _calculate_regression_reliability_score(
        error_result['mae'], baseline_mae
    )

    return {
        'status': RELIABILITY_VALID,
        'reliability_level': _reliability_level_from_score(reliability_score),
        'reliability_score': reliability_score,
        'mae': error_result['mae'],
        'max_absolute_error': error_result['max_absolute_error'],
        'mean_error': error_result['mean_error'],
        'sample_count': sample_count,
        'baseline_mae': baseline_mae,
        'improvement': improvement,
    }


# ==========================================================
# CLASSIFICATION RELIABILITY
# ==========================================================

def calculate_classification_reliability(
    actual_values,
    predicted_values,
    minimum_sample_count=DEFAULT_MINIMUM_SAMPLE_COUNT,
):
    """Evaluate numeric classification reliability using exact-match accuracy."""
    minimum_sample_count = _validate_minimum_sample_count(minimum_sample_count)
    actual, predicted = _validate_prediction_values(actual_values, predicted_values)
    sample_count = len(actual)
    correct_count = sum(
        actual_value == predicted_value
        for actual_value, predicted_value in zip(actual, predicted)
    )
    accuracy = correct_count / sample_count

    result = {
        'status': RELIABILITY_VALID,
        'reliability_level': _reliability_level_from_score(accuracy),
        'reliability_score': accuracy,
        'accuracy': accuracy,
        'sample_count': sample_count,
    }

    if sample_count < minimum_sample_count:
        result['status'] = RELIABILITY_INSUFFICIENT_DATA
        result['reliability_level'] = RELIABILITY_LOW

    return result


# ==========================================================
# UNIFIED RELIABILITY EVALUATION
# ==========================================================

def evaluate_prediction_reliability(
    model_type,
    actual_values,
    predicted_values,
    baseline_mae=None,
    minimum_sample_count=DEFAULT_MINIMUM_SAMPLE_COUNT,
):
    """Unified reliability API for regression and classification."""
    if not isinstance(model_type, str):
        raise ValueError('model_type must be a string.')

    model_type = model_type.strip().lower()

    if model_type == 'regression':
        if baseline_mae is None:
            raise ValueError(
                'baseline_mae is required for regression reliability.'
            )
        return calculate_regression_reliability(
            actual_values=actual_values,
            predicted_values=predicted_values,
            baseline_mae=baseline_mae,
            minimum_sample_count=minimum_sample_count,
        )

    if model_type == 'classification':
        return calculate_classification_reliability(
            actual_values=actual_values,
            predicted_values=predicted_values,
            minimum_sample_count=minimum_sample_count,
        )

    raise ValueError(
        "Unsupported model_type. Expected 'regression' or 'classification'."
    )


# ==========================================================
# MODEL-LEVEL RELIABILITY MONITORING
# ==========================================================

def monitor_prediction_reliability(
    current_result,
    previous_result=None,
    degradation_threshold=DEFAULT_DEGRADATION_THRESHOLD,
):
    """Monitor changes in model-level reliability score."""
    if not isinstance(current_result, dict):
        raise ValueError('current_result must be a dictionary.')
    if previous_result is not None and not isinstance(previous_result, dict):
        raise ValueError('previous_result must be a dictionary.')

    degradation_threshold = _validate_numeric_value(
        degradation_threshold, 'degradation_threshold'
    )
    if degradation_threshold < 0.0:
        raise ValueError('degradation_threshold cannot be negative.')

    current_score = current_result.get('reliability_score')
    if current_score is None:
        raise ValueError('current_result must contain reliability_score.')
    current_score = _validate_score(current_score, 'current reliability_score')

    if previous_result is None:
        return {
            'status': current_result.get('status', RELIABILITY_VALID),
            'degraded': False,
            'previous_reliability_score': None,
            'current_reliability_score': current_score,
            'score_change': None,
            'current_reliability_level': current_result.get('reliability_level'),
            'previous_reliability_level': None,
        }

    previous_score = previous_result.get('reliability_score')
    if previous_score is None:
        raise ValueError('previous_result must contain reliability_score.')
    previous_score = _validate_score(previous_score, 'previous reliability_score')

    score_change = current_score - previous_score
    degraded = score_change <= -degradation_threshold

    # A threshold of zero means any strictly negative change is degradation;
    # with a positive threshold, the configured boundary is inclusive.
    if degradation_threshold == 0.0:
        degraded = score_change < 0.0

    return {
        'status': RELIABILITY_UNRELIABLE if degraded else current_result.get(
            'status', RELIABILITY_VALID
        ),
        'degraded': degraded,
        'previous_reliability_score': previous_score,
        'current_reliability_score': current_score,
        'score_change': score_change,
        'current_reliability_level': current_result.get('reliability_level'),
        'previous_reliability_level': previous_result.get('reliability_level'),
    }
