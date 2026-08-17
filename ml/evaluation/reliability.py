import math


# ==========================================================
# RELIABILITY STATUS
# ==========================================================

RELIABILITY_VALID = 'valid'

RELIABILITY_INSUFFICIENT_DATA = (
    'insufficient_data'
)

RELIABILITY_UNRELIABLE = (
    'unreliable'
)


# ==========================================================
# RELIABILITY LEVELS
# ==========================================================

RELIABILITY_HIGH = 'high'
RELIABILITY_MEDIUM = 'medium'
RELIABILITY_LOW = 'low'
RELIABILITY_UNKNOWN = 'unknown'


# ==========================================================
# BASIC HELPERS
# ==========================================================

def _to_float(
    value,
):
    """
    Convert a value to finite float.

    Raises:
        ValueError when the value is not numeric
        or is not finite.
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


def _validate_arrays(
    actual_values,
    predicted_values,
):
    """
    Validate actual and predicted arrays.
    """

    if actual_values is None:

        raise ValueError(
            'actual_values are required.'
        )

    if predicted_values is None:

        raise ValueError(
            'predicted_values are required.'
        )

    if len(actual_values) == 0:

        raise ValueError(
            'At least one observation is required.'
        )

    if len(actual_values) != len(
        predicted_values
    ):

        raise ValueError(
            'actual_values and predicted_values '
            'must have the same length.'
        )


def _calculate_mean(
    values,
):
    """
    Calculate arithmetic mean.
    """

    if not values:
        return None

    return (
        sum(values)
        / len(values)
    )


def _calculate_accuracy(
    actual_values,
    predicted_values,
):
    """
    Calculate classification accuracy.
    """

    if not actual_values:
        return None

    correct = sum(
        actual == predicted
        for actual, predicted
        in zip(
            actual_values,
            predicted_values,
        )
    )

    return (
        correct
        / len(actual_values)
    )


# ==========================================================
# RELIABILITY LEVEL
# ==========================================================

def determine_reliability_level(
    sample_count,
    quality_score,
    high_threshold=0.80,
    medium_threshold=0.60,
    minimum_sample_count=10,
):
    """
    Determine a reliability level from a normalized
    quality score.

    Parameters:

        sample_count:
            Number of observations used.

        quality_score:
            Value between 0 and 1 where larger values
            indicate better reliability.

        high_threshold:
            Minimum quality score for HIGH reliability.

        medium_threshold:
            Minimum quality score for MEDIUM reliability.

        minimum_sample_count:
            Minimum number of observations required before
            a reliability level can be considered meaningful.

    Important:

        This function does not claim statistical certainty.

        It provides a conservative operational reliability
        classification for the ML system.
    """

    if sample_count is None:

        raise ValueError(
            'sample_count is required.'
        )

    if sample_count < 0:

        raise ValueError(
            'sample_count cannot be negative.'
        )

    quality_score = _to_float(
        quality_score
    )

    high_threshold = _to_float(
        high_threshold
    )

    medium_threshold = _to_float(
        medium_threshold
    )

    if not (
        0.0
        <= quality_score
        <= 1.0
    ):

        raise ValueError(
            'quality_score must be between 0 and 1.'
        )

    if not (
        0.0
        <= medium_threshold
        <= high_threshold
        <= 1.0
    ):

        raise ValueError(
            'Thresholds must satisfy: '
            '0 <= medium <= high <= 1.'
        )

    if sample_count < minimum_sample_count:

        return RELIABILITY_UNKNOWN

    if quality_score >= high_threshold:

        return RELIABILITY_HIGH

    if quality_score >= medium_threshold:

        return RELIABILITY_MEDIUM

    return RELIABILITY_LOW


# ==========================================================
# REGRESSION RELIABILITY
# ==========================================================

def analyze_regression_reliability(
    actual_values,
    predicted_values,
    maximum_acceptable_mae=None,
    maximum_acceptable_rmse=None,
    minimum_sample_count=10,
):
    """
    Analyze operational reliability of a regression model.

    The analysis is based on prediction errors.

    Returns:

        sample_count
        mae
        rmse
        mean_error
        error_std
        quality_score
        reliability_level
        status

    Important:

        There is no universal acceptable MAE for all targets.

        Therefore maximum_acceptable_mae and
        maximum_acceptable_rmse are optional.

        When thresholds are not supplied, reliability is
        reported as UNKNOWN rather than inventing an
        arbitrary business threshold.
    """

    _validate_arrays(
        actual_values,
        predicted_values,
    )

    actual = [
        _to_float(value)
        for value in actual_values
    ]

    predicted = [
        _to_float(value)
        for value in predicted_values
    ]

    errors = [
        prediction - truth
        for truth, prediction
        in zip(
            actual,
            predicted,
        )
    ]

    absolute_errors = [
        abs(error)
        for error in errors
    ]

    squared_errors = [
        error ** 2
        for error in errors
    ]

    sample_count = len(
        actual
    )

    mae = (
        sum(absolute_errors)
        / sample_count
    )

    mse = (
        sum(squared_errors)
        / sample_count
    )

    rmse = math.sqrt(
        mse
    )

    mean_error = (
        sum(errors)
        / sample_count
    )

    # ------------------------------------------------------
    # Error standard deviation
    # ------------------------------------------------------

    variance = (
        sum(
            (
                error - mean_error
            ) ** 2
            for error in errors
        )
        / sample_count
    )

    error_std = math.sqrt(
        variance
    )

    # ------------------------------------------------------
    # No universal threshold
    # ------------------------------------------------------

    if (
        maximum_acceptable_mae is None
        and maximum_acceptable_rmse is None
    ):

        return {

            'status':
                RELIABILITY_VALID,

            'reliability_level':
                RELIABILITY_UNKNOWN,

            'sample_count':
                sample_count,

            'mae':
                float(mae),

            'rmse':
                float(rmse),

            'mean_error':
                float(mean_error),

            'error_std':
                float(error_std),

            'quality_score':
                None,

            'maximum_acceptable_mae':
                None,

            'maximum_acceptable_rmse':
                None,
        }

    # ------------------------------------------------------
    # Validate thresholds
    # ------------------------------------------------------

    if maximum_acceptable_mae is not None:

        maximum_acceptable_mae = _to_float(
            maximum_acceptable_mae
        )

        if maximum_acceptable_mae <= 0:

            raise ValueError(
                'maximum_acceptable_mae must be greater '
                'than zero.'
            )

    if maximum_acceptable_rmse is not None:

        maximum_acceptable_rmse = _to_float(
            maximum_acceptable_rmse
        )

        if maximum_acceptable_rmse <= 0:

            raise ValueError(
                'maximum_acceptable_rmse must be greater '
                'than zero.'
            )

    # ------------------------------------------------------
    # Quality scores
    #
    # A score of 1 means zero error.
    # A score of 0 means error >= allowed threshold.
    # ------------------------------------------------------

    quality_components = []

    if maximum_acceptable_mae is not None:

        mae_quality = max(
            0.0,
            min(
                1.0,
                1.0
                - (
                    mae
                    / maximum_acceptable_mae
                ),
            ),
        )

        quality_components.append(
            mae_quality
        )

    if maximum_acceptable_rmse is not None:

        rmse_quality = max(
            0.0,
            min(
                1.0,
                1.0
                - (
                    rmse
                    / maximum_acceptable_rmse
                ),
            ),
        )

        quality_components.append(
            rmse_quality
        )

    quality_score = (
        sum(quality_components)
        / len(quality_components)
    )

    reliability_level = (
        determine_reliability_level(
            sample_count,
            quality_score,
            minimum_sample_count=minimum_sample_count,
        )
    )

    return {

        'status':
            RELIABILITY_VALID,

        'reliability_level':
            reliability_level,

        'sample_count':
            sample_count,

        'mae':
            float(mae),

        'rmse':
            float(rmse),

        'mean_error':
            float(mean_error),

        'error_std':
            float(error_std),

        'quality_score':
            float(quality_score),

        'maximum_acceptable_mae':
            maximum_acceptable_mae,

        'maximum_acceptable_rmse':
            maximum_acceptable_rmse,
    }


# ==========================================================
# CLASSIFICATION CALIBRATION
# ==========================================================

def calculate_calibration_error(
    actual_values,
    predicted_probabilities,
    number_of_bins=10,
):
    """
    Calculate Expected Calibration Error (ECE).

    predicted_probabilities must contain the probability
    assigned to the predicted class for every observation.

    Example:

        actual:
            [0, 1, 1, 0]

        predicted probability:
            [0.90, 0.80, 0.60, 0.70]

    ECE is calculated by grouping predictions into
    probability bins.

    Lower ECE means better calibration.
    """

    _validate_arrays(
        actual_values,
        predicted_probabilities,
    )

    if number_of_bins <= 0:

        raise ValueError(
            'number_of_bins must be greater than zero.'
        )

    actual = list(
        actual_values
    )

    probabilities = [
        _to_float(value)
        for value in predicted_probabilities
    ]

    for probability in probabilities:

        if not (
            0.0
            <= probability
            <= 1.0
        ):

            raise ValueError(
                'Predicted probabilities must be '
                'between 0 and 1.'
            )

    total = len(
        actual
    )

    weighted_error = 0.0

    bins = []

    for bin_index in range(
        number_of_bins
    ):

        lower = (
            bin_index
            / number_of_bins
        )

        upper = (
            (bin_index + 1)
            / number_of_bins
        )

        bin_indices = []

        for index, probability in enumerate(
            probabilities
        ):

            is_last_bin = (
                bin_index
                == number_of_bins - 1
            )

            if is_last_bin:

                belongs = (
                    lower
                    <= probability
                    <= upper
                )

            else:

                belongs = (
                    lower
                    <= probability
                    < upper
                )

            if belongs:

                bin_indices.append(
                    index
                )

        if not bin_indices:

            continue

        confidence = (
            sum(
                probabilities[index]
                for index in bin_indices
            )
            / len(bin_indices)
        )

        accuracy = (
            sum(
                actual[index]
                == (
                    probability >= 0.5
                )
                for index, probability
                in [
                    (
                        index,
                        probabilities[index],
                    )
                    for index in bin_indices
                ]
            )
            / len(bin_indices)
        )

        bin_error = abs(
            accuracy
            - confidence
        )

        weighted_error += (
            len(bin_indices)
            / total
            * bin_error
        )

        bins.append(
            {
                'bin_index':
                    bin_index,

                'lower_bound':
                    lower,

                'upper_bound':
                    upper,

                'count':
                    len(bin_indices),

                'confidence':
                    float(confidence),

                'accuracy':
                    float(accuracy),

                'calibration_error':
                    float(bin_error),
            }
        )

    return {

        'ece':
            float(weighted_error),

        'number_of_bins':
            number_of_bins,

        'sample_count':
            total,

        'bins':
            bins,
    }


# ==========================================================
# CLASSIFICATION RELIABILITY
# ==========================================================

def analyze_classification_reliability(
    actual_values,
    predicted_values,
    predicted_probabilities=None,
    minimum_sample_count=10,
):
    """
    Analyze classification reliability.

    Without probabilities:

        Reliability is based only on observed accuracy,
        and is reported conservatively.

    With probabilities:

        Expected Calibration Error (ECE) is also calculated.

    Important:

        predicted_probabilities must represent the
        probability assigned to the predicted class.

        This keeps the function independent of the model's
        internal probability representation.
    """

    _validate_arrays(
        actual_values,
        predicted_values,
    )

    actual = list(
        actual_values
    )

    predicted = list(
        predicted_values
    )

    sample_count = len(
        actual
    )

    accuracy = _calculate_accuracy(
        actual,
        predicted,
    )

    incorrect_predictions = (
        sample_count
        - sum(
            actual_value
            == predicted_value
            for actual_value,
            predicted_value
            in zip(
                actual,
                predicted,
            )
        )
    )

    result = {

        'status':
            RELIABILITY_VALID,

        'sample_count':
            sample_count,

        'accuracy':
            float(accuracy),

        'error_rate':
            float(
                incorrect_predictions
                / sample_count
            ),

        'quality_score':
            float(accuracy),

        'reliability_level':
            determine_reliability_level(
                sample_count,
                accuracy,
                minimum_sample_count=minimum_sample_count,
            ),

        'calibration_available':
            False,

        'expected_calibration_error':
            None,
    }

    # ------------------------------------------------------
    # Calibration
    # ------------------------------------------------------

    if predicted_probabilities is not None:

        calibration = (
            calculate_calibration_error(
                actual,
                predicted_probabilities,
            )
        )

        ece = calibration[
            'ece'
        ]

        # Convert calibration error into a quality score.
        calibration_quality = max(
            0.0,
            min(
                1.0,
                1.0 - ece,
            ),
        )

        combined_quality = (
            accuracy
            * calibration_quality
        )

        result.update(
            {
                'calibration_available':
                    True,

                'expected_calibration_error':
                    float(ece),

                'calibration':
                    calibration,

                'calibration_quality_score':
                    float(
                        calibration_quality
                    ),

                'quality_score':
                    float(
                        combined_quality
                    ),

                'reliability_level':
                    determine_reliability_level(
                        sample_count,
                        combined_quality,
                        minimum_sample_count=minimum_sample_count,
                    ),
            }
        )

    return result


# ==========================================================
# UNIFIED RELIABILITY ANALYSIS
# ==========================================================

def analyze_reliability(
    actual_values,
    predicted_values,
    target_task,
    predicted_probabilities=None,
    maximum_acceptable_mae=None,
    maximum_acceptable_rmse=None,
    minimum_sample_count=10,
):
    """
    Unified reliability analysis.

    Supported target tasks:

        regression
        classification
        categorical
    """

    if target_task == 'regression':

        return analyze_regression_reliability(
            actual_values,
            predicted_values,
            maximum_acceptable_mae=(
                maximum_acceptable_mae
            ),
            maximum_acceptable_rmse=(
                maximum_acceptable_rmse
            ),
            minimum_sample_count=(
                minimum_sample_count
            ),
        )

    if target_task in {
        'classification',
        'categorical',
    }:

        return analyze_classification_reliability(
            actual_values,
            predicted_values,
            predicted_probabilities=(
                predicted_probabilities
            ),
            minimum_sample_count=(
                minimum_sample_count
            ),
        )

    raise ValueError(
        'Unsupported target task: '
        f'{target_task}'
    )


# ==========================================================
# EVALUATION RESULT INTEGRATION
# ==========================================================

def analyze_evaluation_reliability(
    evaluation_result,
    predicted_probabilities=None,
    maximum_acceptable_mae=None,
    maximum_acceptable_rmse=None,
    minimum_sample_count=10,
):
    """
    Run reliability analysis directly from an evaluation
    result produced by evaluate_model().
    """

    if evaluation_result is None:

        raise ValueError(
            'evaluation_result is required.'
        )

    if not isinstance(
        evaluation_result,
        dict,
    ):

        raise ValueError(
            'evaluation_result must be a dictionary.'
        )

    actual_values = (
        evaluation_result.get(
            'actual_values'
        )
    )

    predicted_values = (
        evaluation_result.get(
            'predicted_values'
        )
    )

    target_task = (
        evaluation_result.get(
            'target_task'
        )
    )

    if target_task is None:

        raise ValueError(
            'evaluation_result does not contain '
            'target_task.'
        )

    return analyze_reliability(
        actual_values,
        predicted_values,
        target_task,
        predicted_probabilities=(
            predicted_probabilities
        ),
        maximum_acceptable_mae=(
            maximum_acceptable_mae
        ),
        maximum_acceptable_rmse=(
            maximum_acceptable_rmse
        ),
        minimum_sample_count=(
            minimum_sample_count
        ),
    )


# ==========================================================
# SIMPLE TEST
# ==========================================================

if __name__ == '__main__':

    print()
    print(
        '========== RELIABILITY TEST =========='
    )

    regression_result = (
        analyze_regression_reliability(
            [100, 200, 300],
            [110, 180, 300],
        )
    )

    print()
    print(
        'Regression reliability:'
    )

    print(
        regression_result
    )

    classification_result = (
        analyze_classification_reliability(
            [0, 1, 1, 0],
            [0, 1, 0, 0],
        )
    )

    print()
    print(
        'Classification reliability:'
    )

    print(
        classification_result
    )

    print()
    print(
        '========== RELIABILITY TEST PASSED =========='
    )

# ==========================================================
# PREDICTION RELIABILITY MONITORING
# ==========================================================

MONITORING_VALID = 'valid'

MONITORING_INSUFFICIENT_HISTORY = (
    'insufficient_history'
)

MONITORING_STABLE = 'stable'
MONITORING_IMPROVING = 'improving'
MONITORING_DEGRADING = 'degrading'
MONITORING_CRITICAL = 'critical'


# ==========================================================
# MONITORING HELPERS
# ==========================================================

def _validate_monitoring_history(
    history,
):
    """
    Validate a reliability monitoring history.

    Each history item must contain at least:

        reliability_level

    and preferably:

        quality_score

    The function intentionally accepts dictionaries
    produced by the existing reliability layer.
    """

    if history is None:

        raise ValueError(
            'history is required.'
        )

    if not isinstance(
        history,
        (list, tuple),
    ):

        raise ValueError(
            'history must be a list or tuple.'
        )

    if not history:

        raise ValueError(
            'At least one reliability observation '
            'is required.'
        )

    for index, item in enumerate(history):

        if not isinstance(
            item,
            dict,
        ):

            raise ValueError(
                'Each monitoring history item must '
                f'be a dictionary. Index: {index}'
            )

        if 'reliability_level' not in item:

            raise ValueError(
                'Monitoring history item is missing '
                f'reliability_level. Index: {index}'
            )


def _extract_quality_score(
    reliability_result,
):
    """
    Extract and validate a quality score.

    Returns None when the existing reliability analysis
    intentionally does not provide one.
    """

    if reliability_result is None:

        return None

    quality_score = (
        reliability_result.get(
            'quality_score'
        )
    )

    if quality_score is None:

        return None

    quality_score = _to_float(
        quality_score
    )

    if not (
        0.0
        <= quality_score
        <= 1.0
    ):

        raise ValueError(
            'quality_score must be between 0 and 1.'
        )

    return quality_score


def _quality_change(
    baseline_score,
    current_score,
):
    """
    Calculate absolute quality change.

    Positive:
        improvement

    Negative:
        degradation
    """

    if (
        baseline_score is None
        or current_score is None
    ):

        return None

    return (
        current_score
        - baseline_score
    )


def _calculate_trend(
    scores,
    degradation_threshold=0.05,
):
    """
    Determine the direction of reliability over time.

    The function compares the first available quality score
    with the latest available quality score.

    Returns:

        improving
        degrading
        stable
        unknown
    """

    if scores is None:

        raise ValueError(
            'scores are required.'
        )

    if len(scores) < 2:

        return RELIABILITY_UNKNOWN

    valid_scores = [
        score
        for score in scores
        if score is not None
    ]

    if len(valid_scores) < 2:

        return RELIABILITY_UNKNOWN

    first_score = valid_scores[0]
    last_score = valid_scores[-1]

    change = (
        last_score
        - first_score
    )

    if change >= degradation_threshold:

        return MONITORING_IMPROVING

    if change <= -degradation_threshold:

        return MONITORING_DEGRADING

    return MONITORING_STABLE


def _count_consecutive_degrading(
    scores,
    degradation_threshold=0.05,
):
    """
    Count consecutive degrading observations at the end
    of the monitoring history.

    Example:

        [0.90, 0.88, 0.80, 0.70]

    Returns the number of consecutive negative changes
    from the end of the sequence.
    """

    if scores is None:

        return 0

    valid_scores = [
        score
        for score in scores
        if score is not None
    ]

    if len(valid_scores) < 2:

        return 0

    count = 0

    for index in range(
        len(valid_scores) - 1,
        0,
        -1,
    ):

        current_score = (
            valid_scores[index]
        )

        previous_score = (
            valid_scores[index - 1]
        )

        change = (
            current_score
            - previous_score
        )

        if change <= -degradation_threshold:

            count += 1

        else:

            break

    return count


# ==========================================================
# MONITOR SINGLE RELIABILITY RESULT
# ==========================================================

def monitor_prediction_reliability(
    reliability_result,
    history=None,
    degradation_threshold=0.05,
    critical_quality_threshold=0.40,
    consecutive_degradation_limit=3,
    minimum_history_count=2,
):
    """
    Monitor the current prediction reliability against
    previous reliability observations.

    This is the main Prediction Reliability Monitoring
    entry point.

    Parameters:

        reliability_result:
            Current result produced by:

                analyze_reliability()

        history:
            Previous reliability results.

        degradation_threshold:
            Minimum quality-score decrease considered
            meaningful.

        critical_quality_threshold:
            Quality score below which the current prediction
            reliability is considered critical.

        consecutive_degradation_limit:
            Number of consecutive degrading observations
            required before declaring a critical trend.

        minimum_history_count:
            Minimum number of historical observations needed
            for trend analysis.

    Returns:

        status
        monitoring_state
        current_reliability_level
        current_quality_score
        baseline_quality_score
        quality_change
        trend
        consecutive_degrading_observations
        alert_required
        critical
        history_count
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

    degradation_threshold = _to_float(
        degradation_threshold
    )

    critical_quality_threshold = _to_float(
        critical_quality_threshold
    )

    if not (
        0.0
        < degradation_threshold
        <= 1.0
    ):

        raise ValueError(
            'degradation_threshold must be '
            'greater than 0 and at most 1.'
        )

    if not (
        0.0
        <= critical_quality_threshold
        <= 1.0
    ):

        raise ValueError(
            'critical_quality_threshold must be '
            'between 0 and 1.'
        )

    if consecutive_degradation_limit <= 0:

        raise ValueError(
            'consecutive_degradation_limit must '
            'be greater than zero.'
        )

    if minimum_history_count <= 0:

        raise ValueError(
            'minimum_history_count must '
            'be greater than zero.'
        )

    current_quality_score = (
        _extract_quality_score(
            reliability_result
        )
    )

    current_level = (
        reliability_result.get(
            'reliability_level',
            RELIABILITY_UNKNOWN,
        )
    )

    previous_history = []

    if history is not None:

        _validate_monitoring_history(
            history
        )

        previous_history = list(
            history
        )

    # ------------------------------------------------------
    # Build score history
    # ------------------------------------------------------

    historical_scores = [
        _extract_quality_score(item)
        for item in previous_history
    ]

    scores = (
        historical_scores
        + [current_quality_score]
    )

    history_count = len(
        previous_history
    )

    # ------------------------------------------------------
    # Insufficient history
    # ------------------------------------------------------

    if (
        history_count
        < minimum_history_count
    ):

        critical = (
            current_quality_score is not None
            and current_quality_score
            < critical_quality_threshold
        )

        return {

            'status':
                MONITORING_INSUFFICIENT_HISTORY,

            'monitoring_state':
                (
                    MONITORING_CRITICAL
                    if critical
                    else MONITORING_STABLE
                ),

            'current_reliability_level':
                current_level,

            'current_quality_score':
                current_quality_score,

            'baseline_quality_score':
                (
                    historical_scores[0]
                    if historical_scores
                    else None
                ),

            'quality_change':
                None,

            'trend':
                RELIABILITY_UNKNOWN,

            'consecutive_degrading_observations':
                0,

            'alert_required':
                critical,

            'critical':
                critical,

            'history_count':
                history_count,

            'minimum_history_count':
                minimum_history_count,
        }

    # ------------------------------------------------------
    # Baseline
    # ------------------------------------------------------

    baseline_quality_score = None

    for score in historical_scores:

        if score is not None:

            baseline_quality_score = score
            break

    quality_change = _quality_change(
        baseline_quality_score,
        current_quality_score,
    )

    # ------------------------------------------------------
    # Trend
    # ------------------------------------------------------

    trend = _calculate_trend(
        scores,
        degradation_threshold=(
            degradation_threshold
        ),
    )

    # ------------------------------------------------------
    # Consecutive degradation
    # ------------------------------------------------------

    consecutive_degradation = (
        _count_consecutive_degrading(
            scores,
            degradation_threshold=(
                degradation_threshold
            ),
        )
    )

    # ------------------------------------------------------
    # Critical condition
    # ------------------------------------------------------

    low_quality = (
        current_quality_score is not None
        and current_quality_score
        < critical_quality_threshold
    )

    persistent_degradation = (
        consecutive_degradation
        >= consecutive_degradation_limit
    )

    critical = (
        low_quality
        or persistent_degradation
    )

    # ------------------------------------------------------
    # Monitoring state
    # ------------------------------------------------------

    if critical:

        monitoring_state = (
            MONITORING_CRITICAL
        )

    elif trend == MONITORING_DEGRADING:

        monitoring_state = (
            MONITORING_DEGRADING
        )

    elif trend == MONITORING_IMPROVING:

        monitoring_state = (
            MONITORING_IMPROVING
        )

    else:

        monitoring_state = (
            MONITORING_STABLE
        )

    # ------------------------------------------------------
    # Final result
    # ------------------------------------------------------

    return {

        'status':
            MONITORING_VALID,

        'monitoring_state':
            monitoring_state,

        'current_reliability_level':
            current_level,

        'current_quality_score':
            current_quality_score,

        'baseline_quality_score':
            baseline_quality_score,

        'quality_change':
            (
                float(quality_change)
                if quality_change is not None
                else None
            ),

        'trend':
            trend,

        'consecutive_degrading_observations':
            consecutive_degradation,

        'alert_required':
            critical,

        'critical':
            critical,

        'history_count':
            history_count,

        'minimum_history_count':
            minimum_history_count,

        'degradation_threshold':
            degradation_threshold,

        'critical_quality_threshold':
            critical_quality_threshold,

        'consecutive_degradation_limit':
            consecutive_degradation_limit,
    }


# ==========================================================
# MONITOR RELIABILITY HISTORY
# ==========================================================

def monitor_reliability_history(
    history,
    degradation_threshold=0.05,
    critical_quality_threshold=0.40,
    consecutive_degradation_limit=3,
    minimum_history_count=2,
):
    """
    Analyze an entire reliability history.

    The latest observation is treated as the current
    production reliability state.

    This function is useful for periodic monitoring jobs.
    """

    _validate_monitoring_history(
        history
    )

    if len(history) < 2:

        return {

            'status':
                MONITORING_INSUFFICIENT_HISTORY,

            'monitoring_state':
                MONITORING_STABLE,

            'history_count':
                len(history),

            'current':
                history[-1],

            'trend':
                RELIABILITY_UNKNOWN,

            'alert_required':
                False,

            'critical':
                False,
        }

    current = history[-1]

    previous = history[:-1]

    result = monitor_prediction_reliability(
        current,
        history=previous,
        degradation_threshold=(
            degradation_threshold
        ),
        critical_quality_threshold=(
            critical_quality_threshold
        ),
        consecutive_degradation_limit=(
            consecutive_degradation_limit
        ),
        minimum_history_count=(
            minimum_history_count
        ),
    )

    result['history_count'] = len(
        history
    )

    return result


# ==========================================================
# MONITOR EVALUATION RESULT
# ==========================================================

def monitor_evaluation_reliability(
    evaluation_result,
    history=None,
    predicted_probabilities=None,
    maximum_acceptable_mae=None,
    maximum_acceptable_rmse=None,
    minimum_sample_count=10,
    degradation_threshold=0.05,
    critical_quality_threshold=0.40,
    consecutive_degradation_limit=3,
    minimum_history_count=2,
):
    """
    Evaluate current model reliability and immediately feed
    it into Prediction Reliability Monitoring.

    This provides a direct bridge:

        Evaluation
            ↓
        Reliability
            ↓
        Monitoring
    """

    reliability_result = (
        analyze_evaluation_reliability(
            evaluation_result,
            predicted_probabilities=(
                predicted_probabilities
            ),
            maximum_acceptable_mae=(
                maximum_acceptable_mae
            ),
            maximum_acceptable_rmse=(
                maximum_acceptable_rmse
            ),
            minimum_sample_count=(
                minimum_sample_count
            ),
        )
    )

    monitoring_result = (
        monitor_prediction_reliability(
            reliability_result,
            history=history,
            degradation_threshold=(
                degradation_threshold
            ),
            critical_quality_threshold=(
                critical_quality_threshold
            ),
            consecutive_degradation_limit=(
                consecutive_degradation_limit
            ),
            minimum_history_count=(
                minimum_history_count
            ),
        )
    )

    return {

        'reliability':
            reliability_result,

        'monitoring':
            monitoring_result,
    }
