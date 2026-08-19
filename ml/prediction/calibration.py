# ==========================================================
# PREDICTION CALIBRATION
# ==========================================================

import math


# ==========================================================
# CALIBRATION STATUS
# ==========================================================

CALIBRATION_VALID = 'valid'
CALIBRATION_INSUFFICIENT_DATA = 'insufficient_data'
CALIBRATION_UNCALIBRATED = 'uncalibrated'
CALIBRATION_INVALID = 'invalid'


# ==========================================================
# CALIBRATION LEVELS
# ==========================================================

CALIBRATION_HIGH = 'high'
CALIBRATION_MEDIUM = 'medium'
CALIBRATION_LOW = 'low'


# ==========================================================
# VALIDATION HELPERS
# ==========================================================

def _validate_probability(
    value,
    name='probability',
):
    """
    Validate one probability value.

    Probability must be finite and within [0, 1].
    """

    if isinstance(
        value,
        bool,
    ):
        raise ValueError(
            f'{name} must be numeric.'
        )

    try:
        value = float(value)

    except (
        TypeError,
        ValueError,
    ):
        raise ValueError(
            f'{name} must be numeric.'
        )

    if not math.isfinite(value):
        raise ValueError(
            f'{name} must be finite.'
        )

    if (
        value < 0.0
        or value > 1.0
    ):
        raise ValueError(
            f'{name} must be between 0 and 1.'
        )

    return value


def _validate_binary_outcome(
    value,
    name='actual_value',
):
    """
    Validate one binary outcome.

    Accepted values:

        0
        1
        False
        True
    """

    if isinstance(
        value,
        bool,
    ):
        return int(value)

    if value in (
        0,
        1,
    ):
        return int(value)

    raise ValueError(
        f'{name} must be binary (0 or 1).'
    )


def _validate_prediction_inputs(
    actual_values,
    predicted_probabilities,
):
    """
    Validate actual outcomes and predicted probabilities.
    """

    if actual_values is None:
        raise ValueError(
            'actual_values are required.'
        )

    if predicted_probabilities is None:
        raise ValueError(
            'predicted_probabilities are required.'
        )

    try:
        actual_values = list(actual_values)
        predicted_probabilities = list(
            predicted_probabilities
        )

    except TypeError:
        raise ValueError(
            'Prediction inputs must be iterable.'
        )

    if not actual_values:
        raise ValueError(
            'Prediction values cannot be empty.'
        )

    if len(actual_values) != len(
        predicted_probabilities
    ):
        raise ValueError(
            'Actual values and predicted probabilities '
            'must have equal lengths.'
        )

    validated_actual = []
    validated_probabilities = []

    for index, (
        actual,
        probability,
    ) in enumerate(
        zip(
            actual_values,
            predicted_probabilities,
        )
    ):
        validated_actual.append(
            _validate_binary_outcome(
                actual,
                f'actual_values[{index}]',
            )
        )

        validated_probabilities.append(
            _validate_probability(
                probability,
                f'predicted_probabilities[{index}]',
            )
        )

    return (
        validated_actual,
        validated_probabilities,
    )


# ==========================================================
# BRIER SCORE
# ==========================================================

def calculate_brier_score(
    actual_values,
    predicted_probabilities,
):
    """
    Calculate the binary Brier Score.

    Formula:

        mean((probability - actual)²)

    Lower is better.

    Perfect probabilistic prediction:

        0.0
    """

    (
        actual_values,
        predicted_probabilities,
    ) = _validate_prediction_inputs(
        actual_values,
        predicted_probabilities,
    )

    squared_errors = [
        (
            probability - actual
        ) ** 2
        for actual, probability
        in zip(
            actual_values,
            predicted_probabilities,
        )
    ]

    return sum(
        squared_errors
    ) / len(squared_errors)


# ==========================================================
# ABSOLUTE CALIBRATION ERRORS
# ==========================================================

def calculate_calibration_errors(
    actual_values,
    predicted_probabilities,
):
    """
    Calculate per-observation absolute calibration errors.

    Formula:

        abs(predicted_probability - actual_outcome)
    """

    (
        actual_values,
        predicted_probabilities,
    ) = _validate_prediction_inputs(
        actual_values,
        predicted_probabilities,
    )

    return [
        abs(
            probability - actual
        )
        for actual, probability
        in zip(
            actual_values,
            predicted_probabilities,
        )
    ]


# ==========================================================
# MEAN CALIBRATION ERROR
# ==========================================================

def calculate_mean_calibration_error(
    actual_values,
    predicted_probabilities,
):
    """
    Calculate mean absolute calibration error.

    Lower is better.
    """

    errors = calculate_calibration_errors(
        actual_values,
        predicted_probabilities,
    )

    return sum(errors) / len(errors)


# ==========================================================
# PREDICTION CONFIDENCE
# ==========================================================

def calculate_prediction_confidence(
    predicted_probabilities,
):
    """
    Convert positive-class probabilities into prediction
    confidence.

    For binary classification:

        confidence = max(p, 1 - p)
    """

    if predicted_probabilities is None:
        raise ValueError(
            'predicted_probabilities are required.'
        )

    probabilities = list(
        predicted_probabilities
    )

    if not probabilities:
        raise ValueError(
            'predicted_probabilities cannot be empty.'
        )

    validated_probabilities = [
        _validate_probability(
            probability,
            'predicted_probability',
        )
        for probability
        in probabilities
    ]

    return [
        max(
            probability,
            1.0 - probability,
        )
        for probability
        in validated_probabilities
    ]


# ==========================================================
# EXPECTED CALIBRATION ERROR
# ==========================================================

def calculate_expected_calibration_error(
    actual_values,
    predicted_probabilities,
    bin_count=10,
):
    """
    Calculate Expected Calibration Error (ECE).

    Predictions are divided into confidence bins.

    ECE is the weighted average difference between:

        average confidence

    and:

        empirical accuracy

    Lower is better.
    """

    (
        actual_values,
        predicted_probabilities,
    ) = _validate_prediction_inputs(
        actual_values,
        predicted_probabilities,
    )

    if not isinstance(
        bin_count,
        int,
    ) or isinstance(
        bin_count,
        bool,
    ):
        raise ValueError(
            'bin_count must be an integer.'
        )

    if bin_count <= 0:
        raise ValueError(
            'bin_count must be greater than zero.'
        )

    confidence_values = []
    predicted_classes = []

    for probability in predicted_probabilities:
        confidence = max(
            probability,
            1.0 - probability,
        )

        predicted_class = (
            1
            if probability >= 0.5
            else 0
        )

        confidence_values.append(
            confidence
        )

        predicted_classes.append(
            predicted_class
        )

    total_count = len(actual_values)

    ece = 0.0

    for bin_index in range(bin_count):
        lower = (
            bin_index / bin_count
        )

        upper = (
            (bin_index + 1) / bin_count
        )

        if bin_index == bin_count - 1:
            indices = [
                index
                for index, confidence
                in enumerate(
                    confidence_values
                )
                if (
                    confidence >= lower
                    and confidence <= upper
                )
            ]

        else:
            indices = [
                index
                for index, confidence
                in enumerate(
                    confidence_values
                )
                if (
                    confidence >= lower
                    and confidence < upper
                )
            ]

        if not indices:
            continue

        bin_accuracy = (
            sum(
                1
                for index
                in indices
                if (
                    predicted_classes[index]
                    == actual_values[index]
                )
            )
            / len(indices)
        )

        bin_confidence = (
            sum(
                confidence_values[index]
                for index
                in indices
            )
            / len(indices)
        )

        bin_weight = (
            len(indices)
            / total_count
        )

        ece += (
            bin_weight
            * abs(
                bin_accuracy
                - bin_confidence
            )
        )

    return ece


# ==========================================================
# CALIBRATION LEVEL
# ==========================================================

def determine_calibration_level(
    calibration_error,
):
    """
    Convert calibration error into a qualitative level.

    Thresholds:

        <= 0.10 -> high
        <= 0.20 -> medium
        >  0.20 -> low
    """

    calibration_error = _validate_probability(
        calibration_error,
        'calibration_error',
    )

    if calibration_error <= 0.10:
        return CALIBRATION_HIGH

    if calibration_error <= 0.20:
        return CALIBRATION_MEDIUM

    return CALIBRATION_LOW


# ==========================================================
# CALIBRATION SCORE
# ==========================================================

def calculate_calibration_score(
    calibration_error,
):
    """
    Convert calibration error into a normalized score.

    Score:

        1.0 -> perfect
        0.0 -> maximally poor

    The score is bounded to [0, 1].
    """

    calibration_error = _validate_probability(
        calibration_error,
        'calibration_error',
    )

    score = 1.0 - calibration_error

    return max(
        0.0,
        min(
            1.0,
            score,
        ),
    )


# ==========================================================
# FULL CALIBRATION EVALUATION
# ==========================================================

def evaluate_prediction_calibration(
    actual_values,
    predicted_probabilities,
    minimum_sample_count=10,
    bin_count=10,
):
    """
    Perform complete binary classification calibration
    evaluation.

    Returns:

        status
        calibration_level
        calibration_score
        brier_score
        mean_calibration_error
        expected_calibration_error
        sample_count
    """

    (
        actual_values,
        predicted_probabilities,
    ) = _validate_prediction_inputs(
        actual_values,
        predicted_probabilities,
    )

    if not isinstance(
        minimum_sample_count,
        int,
    ) or isinstance(
        minimum_sample_count,
        bool,
    ):
        raise ValueError(
            'minimum_sample_count must be an integer.'
        )

    if minimum_sample_count <= 0:
        raise ValueError(
            'minimum_sample_count must be greater than zero.'
        )

    sample_count = len(actual_values)

    if sample_count < minimum_sample_count:
        return {
            'status':
                CALIBRATION_INSUFFICIENT_DATA,

            'calibration_level':
                CALIBRATION_LOW,

            'calibration_score':
                0.0,

            'brier_score':
                None,

            'mean_calibration_error':
                None,

            'expected_calibration_error':
                None,

            'sample_count':
                sample_count,
        }

    brier_score = calculate_brier_score(
        actual_values,
        predicted_probabilities,
    )

    mean_calibration_error = (
        calculate_mean_calibration_error(
            actual_values,
            predicted_probabilities,
        )
    )

    expected_calibration_error = (
        calculate_expected_calibration_error(
            actual_values,
            predicted_probabilities,
            bin_count,
        )
    )

    calibration_level = determine_calibration_level(
        expected_calibration_error
    )

    calibration_score = calculate_calibration_score(
        expected_calibration_error
    )

    return {
        'status':
            CALIBRATION_VALID,

        'calibration_level':
            calibration_level,

        'calibration_score':
            calibration_score,

        'brier_score':
            brier_score,

        'mean_calibration_error':
            mean_calibration_error,

        'expected_calibration_error':
            expected_calibration_error,

        'sample_count':
            sample_count,
    }


# ==========================================================
# MANUAL TEST
# ==========================================================

if __name__ == '__main__':

    result = evaluate_prediction_calibration(
        actual_values=[
            0,
            1,
            0,
            1,
            1,
            0,
            1,
            1,
            0,
            1,
        ],
        predicted_probabilities=[
            0.10,
            0.90,
            0.20,
            0.80,
            0.85,
            0.15,
            0.75,
            0.90,
            0.10,
            0.85,
        ],
        minimum_sample_count=5,
    )

    print()
    print(
        '=================================================='
    )

    print(
        '       PREDICTION CALIBRATION TEST'
    )

    print(
        '=================================================='
    )

    print(result)

    print(
        '=================================================='
    )