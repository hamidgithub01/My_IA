import math


# ==========================================================
# ERROR ANALYSIS STATUS
# ==========================================================

ERROR_ANALYSIS_EVALUATED = 'evaluated'
ERROR_ANALYSIS_UNKNOWN = 'unknown'


# ==========================================================
# VALIDATION
# ==========================================================

def _validate_numeric_value(
    value,
    name,
):
    """
    Validate one numeric finite value.
    """

    if value is None:

        raise ValueError(
            f'{name} cannot be None.'
        )

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

    if not math.isfinite(
        numeric_value
    ):

        raise ValueError(
            f'{name} must be finite.'
        )

    return numeric_value


def _validate_prediction_pairs(
    predictions,
    actual_values,
):
    """
    Validate prediction / actual pairs.
    """

    if predictions is None:

        raise ValueError(
            'predictions are required.'
        )

    if actual_values is None:

        raise ValueError(
            'actual_values are required.'
        )

    try:

        predictions = list(
            predictions
        )

    except TypeError as exc:

        raise ValueError(
            'predictions must be iterable.'
        ) from exc

    try:

        actual_values = list(
            actual_values
        )

    except TypeError as exc:

        raise ValueError(
            'actual_values must be iterable.'
        ) from exc

    if not predictions:

        raise ValueError(
            'predictions cannot be empty.'
        )

    if len(predictions) != len(
        actual_values
    ):

        raise ValueError(
            'predictions and actual_values '
            'must contain the same number of observations.'
        )

    validated_predictions = []
    validated_actual_values = []

    for index, (
        prediction,
        actual,
    ) in enumerate(
        zip(
            predictions,
            actual_values,
        )
    ):

        validated_predictions.append(
            _validate_numeric_value(
                prediction,
                f'prediction[{index}]',
            )
        )

        validated_actual_values.append(
            _validate_numeric_value(
                actual,
                f'actual_values[{index}]',
            )
        )

    return (
        validated_predictions,
        validated_actual_values,
    )


# ==========================================================
# ERROR CALCULATION
# ==========================================================

def calculate_errors(
    predictions,
    actual_values,
):
    """
    Calculate detailed error information for every
    prediction / actual pair.

    Error convention:

        signed_error = prediction - actual

    Therefore:

        positive -> overprediction
        negative -> underprediction

    Returns a list of dictionaries.
    """

    (
        predictions,
        actual_values,
    ) = _validate_prediction_pairs(
        predictions,
        actual_values,
    )

    errors = []

    for index, (
        prediction,
        actual,
    ) in enumerate(
        zip(
            predictions,
            actual_values,
        )
    ):

        signed_error = (
            prediction
            - actual
        )

        absolute_error = abs(
            signed_error
        )

        squared_error = (
            signed_error
            ** 2
        )

        if actual != 0:

            relative_error = (
                absolute_error
                / abs(actual)
            )

        else:

            relative_error = None

        errors.append({

            'index':
                index,

            'prediction':
                prediction,

            'actual':
                actual,

            'signed_error':
                signed_error,

            'absolute_error':
                absolute_error,

            'squared_error':
                squared_error,

            'relative_error':
                relative_error,
        })

    return errors


# ==========================================================
# ERROR DIRECTION
# ==========================================================

def classify_error_direction(
    signed_error,
):
    """
    Classify the direction of one prediction error.
    """

    signed_error = _validate_numeric_value(
        signed_error,
        'signed_error',
    )

    if signed_error > 0:

        return 'overprediction'

    if signed_error < 0:

        return 'underprediction'

    return 'exact'


# ==========================================================
# ERROR SUMMARY
# ==========================================================

def summarize_errors(
    predictions,
    actual_values,
):
    """
    Calculate aggregate error statistics.

    This function focuses exclusively on error behavior.

    It does not calculate reliability or calibration.
    """

    errors = calculate_errors(
        predictions,
        actual_values,
    )

    evaluated_count = len(
        errors
    )

    absolute_errors = [
        item[
            'absolute_error'
        ]
        for item in errors
    ]

    squared_errors = [
        item[
            'squared_error'
        ]
        for item in errors
    ]

    signed_errors = [
        item[
            'signed_error'
        ]
        for item in errors
    ]

    relative_errors = [
        item[
            'relative_error'
        ]
        for item in errors
        if item[
            'relative_error'
        ] is not None
    ]

    mae = (
        sum(absolute_errors)
        / evaluated_count
    )

    mse = (
        sum(squared_errors)
        / evaluated_count
    )

    rmse = math.sqrt(
        mse
    )

    mean_error = (
        sum(signed_errors)
        / evaluated_count
    )

    if relative_errors:

        mean_relative_error = (
            sum(relative_errors)
            / len(relative_errors)
        )

    else:

        mean_relative_error = None

    maximum_error = max(
        errors,
        key=lambda item:
            item['absolute_error'],
    )

    minimum_error = min(
        errors,
        key=lambda item:
            item['absolute_error'],
    )

    overprediction_count = sum(
        1
        for error in errors
        if error[
            'signed_error'
        ] > 0
    )

    underprediction_count = sum(
        1
        for error in errors
        if error[
            'signed_error'
        ] < 0
    )

    exact_prediction_count = sum(
        1
        for error in errors
        if error[
            'signed_error'
        ] == 0
    )

    return {

        'status':
            ERROR_ANALYSIS_EVALUATED,

        'evaluated_count':
            evaluated_count,

        'mae':
            mae,

        'mse':
            mse,

        'rmse':
            rmse,

        'mean_error':
            mean_error,

        'mean_relative_error':
            mean_relative_error,

        'maximum_error':
            dict(
                maximum_error
            ),

        'minimum_error':
            dict(
                minimum_error
            ),

        'overprediction_count':
            overprediction_count,

        'underprediction_count':
            underprediction_count,

        'exact_prediction_count':
            exact_prediction_count,

        'errors':
            errors,
    }


# ==========================================================
# ERROR DISTRIBUTION
# ==========================================================

def analyze_error_distribution(
    predictions,
    actual_values,
):
    """
    Analyze the distribution of signed and absolute errors.
    """

    errors = calculate_errors(
        predictions,
        actual_values,
    )

    absolute_errors = sorted(
        [
            item[
                'absolute_error'
            ]
            for item in errors
        ]
    )

    signed_errors = [
        item[
            'signed_error'
        ]
        for item in errors
    ]

    count = len(
        absolute_errors
    )

    def percentile(
        values,
        percentage,
    ):
        """
        Calculate a simple linear percentile.
        """

        if not values:

            return None

        if len(values) == 1:

            return values[0]

        position = (
            (len(values) - 1)
            * percentage
        )

        lower_index = int(
            math.floor(position)
        )

        upper_index = int(
            math.ceil(position)
        )

        if lower_index == upper_index:

            return values[
                lower_index
            ]

        lower_value = values[
            lower_index
        ]

        upper_value = values[
            upper_index
        ]

        weight = (
            position
            - lower_index
        )

        return (
            lower_value
            + (
                upper_value
                - lower_value
            )
            * weight
        )

    return {

        'evaluated_count':
            count,

        'absolute_error_min':
            min(
                absolute_errors
            ),

        'absolute_error_max':
            max(
                absolute_errors
            ),

        'absolute_error_p50':
            percentile(
                absolute_errors,
                0.50,
            ),

        'absolute_error_p75':
            percentile(
                absolute_errors,
                0.75,
            ),

        'absolute_error_p90':
            percentile(
                absolute_errors,
                0.90,
            ),

        'absolute_error_p95':
            percentile(
                absolute_errors,
                0.95,
            ),

        'absolute_error_p99':
            percentile(
                absolute_errors,
                0.99,
            ),

        'signed_error_min':
            min(
                signed_errors
            ),

        'signed_error_max':
            max(
                signed_errors
            ),
    }


# ==========================================================
# LARGE ERROR DETECTION
# ==========================================================

def detect_large_errors(
    predictions,
    actual_values,
    threshold,
):
    """
    Detect observations whose absolute error is greater than
    or equal to the supplied threshold.
    """

    threshold = _validate_numeric_value(
        threshold,
        'threshold',
    )

    if threshold < 0:

        raise ValueError(
            'threshold cannot be negative.'
        )

    errors = calculate_errors(
        predictions,
        actual_values,
    )

    large_errors = [
        item
        for item in errors
        if item[
            'absolute_error'
        ] >= threshold
    ]

    return {

        'threshold':
            threshold,

        'count':
            len(
                large_errors
            ),

        'errors':
            large_errors,
    }


# ==========================================================
# ERROR BIAS ANALYSIS
# ==========================================================

def analyze_error_bias(
    predictions,
    actual_values,
):
    """
    Analyze whether errors systematically move in one
    direction.
    """

    errors = calculate_errors(
        predictions,
        actual_values,
    )

    overprediction_count = sum(
        1
        for item in errors
        if item[
            'signed_error'
        ] > 0
    )

    underprediction_count = sum(
        1
        for item in errors
        if item[
            'signed_error'
        ] < 0
    )

    exact_prediction_count = sum(
        1
        for item in errors
        if item[
            'signed_error'
        ] == 0
    )

    mean_error = (
        sum(
            item[
                'signed_error'
            ]
            for item in errors
        )
        / len(errors)
    )

    if mean_error > 0:

        direction = (
            'overprediction'
        )

    elif mean_error < 0:

        direction = (
            'underprediction'
        )

    else:

        direction = 'balanced'

    return {

        'mean_error':
            mean_error,

        'direction':
            direction,

        'overprediction_count':
            overprediction_count,

        'underprediction_count':
            underprediction_count,

        'exact_prediction_count':
            exact_prediction_count,
    }


# ==========================================================
# COMPLETE ERROR ANALYSIS
# ==========================================================

def analyze_regression_errors(
    predictions,
    actual_values,
    large_error_threshold=None,
):
    """
    Perform complete regression error analysis.

    This function combines:

        - individual errors
        - aggregate metrics
        - error distribution
        - bias analysis
        - optional large-error detection

    It intentionally does NOT calculate:

        - reliability
        - calibration
        - model training
        - model selection
    """

    summary = summarize_errors(
        predictions,
        actual_values,
    )

    distribution = (
        analyze_error_distribution(
            predictions,
            actual_values,
        )
    )

    bias = analyze_error_bias(
        predictions,
        actual_values,
    )

    result = {

        'status':
            ERROR_ANALYSIS_EVALUATED,

        'summary':
            summary,

        'distribution':
            distribution,

        'bias':
            bias,
    }

    if large_error_threshold is not None:

        result[
            'large_errors'
        ] = detect_large_errors(
            predictions,
            actual_values,
            large_error_threshold,
        )

    else:

        result[
            'large_errors'
        ] = None

    return result


# ==========================================================
# SIMPLE MANUAL TEST
# ==========================================================

if __name__ == '__main__':

    predictions = [
        100.0,
        200.0,
        300.0,
        400.0,
        500.0,
        600.0,
        700.0,
        800.0,
        900.0,
        1000.0,
    ]

    actual_values = [
        110.0,
        190.0,
        315.0,
        380.0,
        510.0,
        570.0,
        735.0,
        760.0,
        945.0,
        980.0,
    ]

    result = analyze_regression_errors(
        predictions,
        actual_values,
        large_error_threshold=50.0,
    )

    summary = result[
        'summary'
    ]

    distribution = result[
        'distribution'
    ]

    bias = result[
        'bias'
    ]

    large_errors = result[
        'large_errors'
    ]

    print()
    print(
        '=================================================='
    )

    print(
        '       REGRESSION ERROR ANALYSIS TEST'
    )

    print(
        '=================================================='
    )

    print()
    print(
        'Evaluated count:',
        summary[
            'evaluated_count'
        ]
    )

    print(
        'MAE:',
        summary[
            'mae'
        ]
    )

    print(
        'MSE:',
        summary[
            'mse'
        ]
    )

    print(
        'RMSE:',
        summary[
            'rmse'
        ]
    )

    print(
        'Mean error:',
        summary[
            'mean_error'
        ]
    )

    print(
        'Mean relative error:',
        summary[
            'mean_relative_error'
        ]
    )

    print()
    print(
        'Maximum error:',
        summary[
            'maximum_error'
        ]
    )

    print(
        'Minimum error:',
        summary[
            'minimum_error'
        ]
    )

    print()
    print(
        'P90 absolute error:',
        distribution[
            'absolute_error_p90'
        ]
    )

    print(
        'P95 absolute error:',
        distribution[
            'absolute_error_p95'
        ]
    )

    print(
        'P99 absolute error:',
        distribution[
            'absolute_error_p99'
        ]
    )

    print()
    print(
        'Overprediction count:',
        bias[
            'overprediction_count'
        ]
    )

    print(
        'Underprediction count:',
        bias[
            'underprediction_count'
        ]
    )

    print(
        'Exact prediction count:',
        bias[
            'exact_prediction_count'
        ]
    )

    print(
        'Error direction:',
        bias[
            'direction'
        ]
    )

    print()
    print(
        'Large error threshold:',
        large_errors[
            'threshold'
        ]
    )

    print(
        'Large error count:',
        large_errors[
            'count'
        ]
    )

    print()
    print(
        '=================================================='
    )

    print(
        '   REGRESSION ERROR ANALYSIS TEST PASSED'
    )

    print(
        '=================================================='
    )