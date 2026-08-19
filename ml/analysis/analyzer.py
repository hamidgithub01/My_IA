# ==========================================================
# ANALYSIS STATUS
# ==========================================================

ANALYSIS_VALID = 'valid'
ANALYSIS_INSUFFICIENT_DATA = 'insufficient_data'


# ==========================================================
# BASIC HELPERS
# ==========================================================

def _to_float(value):
    """
    Convert a value to float safely.

    Raises:
        ValueError when the value is not numeric.
    """

    try:
        return float(value)

    except (TypeError, ValueError):

        raise ValueError(
            f'Value must be numeric: {value!r}'
        )


def _safe_list(value):
    """
    Return a list from a possibly missing value.
    """

    if value is None:
        return []

    if isinstance(value, list):
        return value

    try:
        return list(value)

    except TypeError:

        raise ValueError(
            'Expected a list-like value.'
        )


# ==========================================================
# INPUT VALIDATION
# ==========================================================

def _validate_prediction_result(
    prediction_result,
):
    """
    Validate a production prediction result.

    The analyzer intentionally accepts a flexible dictionary
    because prediction results may evolve as the system grows.
    """

    if prediction_result is None:

        raise ValueError(
            'prediction_result is required.'
        )

    if not isinstance(
        prediction_result,
        dict,
    ):

        raise ValueError(
            'prediction_result must be a dictionary.'
        )


def _validate_reliability_result(
    reliability_result,
):
    """
    Validate reliability information when supplied.
    """

    if reliability_result is None:
        return

    if not isinstance(
        reliability_result,
        dict,
    ):

        raise ValueError(
            'reliability_result must be a dictionary.'
        )


def _validate_monitoring_result(
    monitoring_result,
):
    """
    Validate monitoring information when supplied.
    """

    if monitoring_result is None:
        return

    if not isinstance(
        monitoring_result,
        dict,
    ):

        raise ValueError(
            'monitoring_result must be a dictionary.'
        )


def _validate_alert_result(
    alert_result,
):
    """
    Validate alert information when supplied.
    """

    if alert_result is None:
        return

    if not isinstance(
        alert_result,
        dict,
    ):

        raise ValueError(
            'alert_result must be a dictionary.'
        )


def _validate_recommendation_result(
    recommendation_result,
):
    """
    Validate recommendation information when supplied.
    """

    if recommendation_result is None:
        return

    if not isinstance(
        recommendation_result,
        dict,
    ):

        raise ValueError(
            'recommendation_result must be a dictionary.'
        )


# ==========================================================
# PREDICTION ANALYSIS
# ==========================================================

def analyze_predictions(
    prediction_result,
):
    """
    Analyze production prediction output.

    Supported information may include:

        predictions
        predicted_values
        prediction_count
        target_name
        target_task
        confidence
        reliability_level
    """

    _validate_prediction_result(
        prediction_result
    )

    predictions = prediction_result.get(
        'predictions'
    )

    if predictions is None:

        predictions = prediction_result.get(
            'predicted_values'
        )

    predictions = _safe_list(
        predictions
    )

    prediction_count = len(
        predictions
    )

    target_name = prediction_result.get(
        'target_name'
    )

    target_task = prediction_result.get(
        'target_task'
    )

    result = {

        'prediction_count':
            prediction_count,

        'target_name':
            target_name,

        'target_task':
            target_task,

        'has_predictions':
            prediction_count > 0,

        'prediction_values':
            predictions,
    }

    # ------------------------------------------------------
    # Numeric prediction statistics
    # ------------------------------------------------------

    if predictions:

        numeric_predictions = []

        numeric = True

        for value in predictions:

            try:

                numeric_predictions.append(
                    _to_float(value)
                )

            except ValueError:

                numeric = False
                break

        if numeric:

            result.update(
                {
                    'numeric_predictions':
                        True,

                    'minimum_prediction':
                        min(
                            numeric_predictions
                        ),

                    'maximum_prediction':
                        max(
                            numeric_predictions
                        ),

                    'mean_prediction':
                        sum(
                            numeric_predictions
                        )
                        / len(
                            numeric_predictions
                        ),
                }
            )

        else:

            result[
                'numeric_predictions'
            ] = False

    else:

        result[
            'numeric_predictions'
        ] = False

    # ------------------------------------------------------
    # Confidence
    # ------------------------------------------------------

    confidence = prediction_result.get(
        'confidence'
    )

    if confidence is not None:

        confidence = _to_float(
            confidence
        )

        if not (
            0.0
            <= confidence
            <= 1.0
        ):

            raise ValueError(
                'confidence must be between 0 and 1.'
            )

    result[
        'confidence'
    ] = confidence

    return result


# ==========================================================
# ERROR ANALYSIS
# ==========================================================

def analyze_errors(
    evaluation_result,
):
    """
    Analyze model evaluation errors.

    The function works with both regression and
    classification evaluation results.
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

    metrics = evaluation_result.get(
        'metrics'
    ) or {}

    target_task = evaluation_result.get(
        'target_task'
    )

    actual_values = _safe_list(
        evaluation_result.get(
            'actual_values'
        )
    )

    predicted_values = _safe_list(
        evaluation_result.get(
            'predicted_values'
        )
    )

    if len(actual_values) != len(
        predicted_values
    ):

        raise ValueError(
            'actual_values and predicted_values '
            'must have the same length.'
        )

    result = {

        'target_task':
            target_task,

        'sample_count':
            len(actual_values),

        'metrics':
            dict(metrics),
    }

    # ------------------------------------------------------
    # Regression
    # ------------------------------------------------------

    if target_task == 'regression':

        if actual_values:

            errors = []

            absolute_errors = []

            for actual, predicted in zip(
                actual_values,
                predicted_values,
            ):

                actual = _to_float(
                    actual
                )

                predicted = _to_float(
                    predicted
                )

                error = (
                    predicted
                    - actual
                )

                errors.append(
                    error
                )

                absolute_errors.append(
                    abs(error)
                )

            mean_error = (
                sum(errors)
                / len(errors)
            )

            mean_absolute_error = (
                sum(
                    absolute_errors
                )
                / len(
                    absolute_errors
                )
            )

            result.update(
                {
                    'mean_error':
                        mean_error,

                    'mean_absolute_error':
                        mean_absolute_error,

                    'over_predictions':
                        sum(
                            error > 0
                            for error in errors
                        ),

                    'under_predictions':
                        sum(
                            error < 0
                            for error in errors
                        ),

                    'exact_predictions':
                        sum(
                            error == 0
                            for error in errors
                        ),
                }
            )

        else:

            result.update(
                {
                    'mean_error':
                        None,

                    'mean_absolute_error':
                        None,

                    'over_predictions':
                        0,

                    'under_predictions':
                        0,

                    'exact_predictions':
                        0,
                }
            )

        return result

    # ------------------------------------------------------
    # Classification / categorical
    # ------------------------------------------------------

    if target_task in {
        'classification',
        'categorical',
    }:

        correct = sum(
            actual == predicted
            for actual, predicted
            in zip(
                actual_values,
                predicted_values,
            )
        )

        incorrect = (
            len(actual_values)
            - correct
        )

        accuracy = (
            correct
            / len(actual_values)
            if actual_values
            else None
        )

        result.update(
            {
                'correct_predictions':
                    correct,

                'incorrect_predictions':
                    incorrect,

                'accuracy':
                    accuracy,

                'error_rate':
                    (
                        incorrect
                        / len(actual_values)
                        if actual_values
                        else None
                    ),
            }
        )

        return result

    # ------------------------------------------------------
    # Unknown task
    # ------------------------------------------------------

    raise ValueError(
        'Unsupported target task: '
        f'{target_task}'
    )


# ==========================================================
# RELIABILITY ANALYSIS
# ==========================================================

def analyze_reliability(
    reliability_result,
):
    """
    Extract operational reliability information.
    """

    _validate_reliability_result(
        reliability_result
    )

    if reliability_result is None:

        return {

            'available':
                False,

            'status':
                None,

            'reliability_level':
                None,

            'quality_score':
                None,
        }

    return {

        'available':
            True,

        'status':
            reliability_result.get(
                'status'
            ),

        'reliability_level':
            reliability_result.get(
                'reliability_level'
            ),

        'quality_score':
            reliability_result.get(
                'quality_score'
            ),

        'sample_count':
            reliability_result.get(
                'sample_count'
            ),

        'expected_calibration_error':
            reliability_result.get(
                'expected_calibration_error'
            ),
    }


# ==========================================================
# MONITORING ANALYSIS
# ==========================================================

def analyze_monitoring(
    monitoring_result,
):
    """
    Extract monitoring status and detected changes.
    """

    _validate_monitoring_result(
        monitoring_result
    )

    if monitoring_result is None:

        return {

            'available':
                False,

            'status':
                None,

            'alert_count':
                0,
        }

    alerts = monitoring_result.get(
        'alerts',
        []
    )

    alerts = _safe_list(
        alerts
    )

    return {

        'available':
            True,

        'status':
            monitoring_result.get(
                'status'
            ),

        'alert_count':
            monitoring_result.get(
                'alert_count',
                len(alerts),
            ),

        'alerts':
            alerts,
    }


# ==========================================================
# ALERT ANALYSIS
# ==========================================================

def analyze_alerts(
    alert_result,
):
    """
    Summarize alerts by severity.
    """

    _validate_alert_result(
        alert_result
    )

    if alert_result is None:

        return {

            'available':
                False,

            'alert_count':
                0,

            'critical_count':
                0,

            'high_count':
                0,

            'medium_count':
                0,

            'low_count':
                0,
        }

    alerts = _safe_list(
        alert_result.get(
            'alerts',
            []
        )
    )

    severity_counts = {

        'critical':
            0,

        'high':
            0,

        'medium':
            0,

        'low':
            0,
    }

    for alert in alerts:

        if not isinstance(
            alert,
            dict,
        ):

            continue

        severity = alert.get(
            'severity'
        )

        if severity in severity_counts:

            severity_counts[
                severity
            ] += 1

    return {

        'available':
            True,

        'alert_count':
            len(alerts),

        'critical_count':
            severity_counts[
                'critical'
            ],

        'high_count':
            severity_counts[
                'high'
            ],

        'medium_count':
            severity_counts[
                'medium'
            ],

        'low_count':
            severity_counts[
                'low'
            ],

        'alerts':
            alerts,
    }


# ==========================================================
# RECOMMENDATION ANALYSIS
# ==========================================================

def analyze_recommendations(
    recommendation_result,
):
    """
    Summarize generated recommendations.
    """

    _validate_recommendation_result(
        recommendation_result
    )

    if recommendation_result is None:

        return {

            'available':
                False,

            'recommendation_count':
                0,

            'recommendations':
                [],
        }

    recommendations = _safe_list(
        recommendation_result.get(
            'recommendations',
            []
        )
    )

    return {

        'available':
            True,

        'status':
            recommendation_result.get(
                'status'
            ),

        'recommendation_count':
            recommendation_result.get(
                'recommendation_count',
                len(recommendations),
            ),

        'recommendations':
            recommendations,
    }


# ==========================================================
# EXECUTIVE SUMMARY
# ==========================================================

def build_executive_summary(
    prediction_analysis,
    error_analysis=None,
    reliability_analysis=None,
    alert_analysis=None,
    recommendation_analysis=None,
):
    """
    Build a deterministic executive summary.

    No unsupported conclusions are invented.
    """

    statements = []

    # ------------------------------------------------------
    # Prediction
    # ------------------------------------------------------

    if prediction_analysis.get(
        'has_predictions'
    ):

        count = prediction_analysis[
            'prediction_count'
        ]

        statements.append(
            f'{count} prediction(s) are available.'
        )

    else:

        statements.append(
            'No predictions are available.'
        )

    # ------------------------------------------------------
    # Reliability
    # ------------------------------------------------------

    if reliability_analysis:

        level = reliability_analysis.get(
            'reliability_level'
        )

        if level is not None:

            statements.append(
                'Reliability level: '
                f'{level}.'
            )

    # ------------------------------------------------------
    # Errors
    # ------------------------------------------------------

    if error_analysis:

        task = error_analysis.get(
            'target_task'
        )

        if task == 'regression':

            mae = error_analysis.get(
                'mean_absolute_error'
            )

            if mae is not None:

                statements.append(
                    'Mean absolute error: '
                    f'{mae:.6f}.'
                )

        elif task in {
            'classification',
            'categorical',
        }:

            accuracy = error_analysis.get(
                'accuracy'
            )

            if accuracy is not None:

                statements.append(
                    'Classification accuracy: '
                    f'{accuracy:.6f}.'
                )

    # ------------------------------------------------------
    # Alerts
    # ------------------------------------------------------

    if alert_analysis:

        alert_count = alert_analysis.get(
            'alert_count',
            0,
        )

        if alert_count > 0:

            statements.append(
                f'{alert_count} alert(s) '
                'require attention.'
            )

        else:

            statements.append(
                'No active alerts were detected.'
            )

    # ------------------------------------------------------
    # Recommendations
    # ------------------------------------------------------

    if recommendation_analysis:

        recommendation_count = (
            recommendation_analysis.get(
                'recommendation_count',
                0,
            )
        )

        if recommendation_count > 0:

            statements.append(
                f'{recommendation_count} '
                'recommendation(s) are available.'
            )

    return statements


# ==========================================================
# UNIFIED AI ANALYSIS
# ==========================================================

def analyze_system(
    prediction_result,
    evaluation_result=None,
    reliability_result=None,
    monitoring_result=None,
    alert_result=None,
    recommendation_result=None,
):
    """
    Perform unified system analysis.

    This is the main entry point for the AI Analysis layer.

    Every supplied subsystem result is analyzed independently,
    then combined into one structured result.
    """

    _validate_prediction_result(
        prediction_result
    )

    prediction_analysis = (
        analyze_predictions(
            prediction_result
        )
    )

    error_analysis = None

    if evaluation_result is not None:

        error_analysis = analyze_errors(
            evaluation_result
        )

    reliability_analysis = (
        analyze_reliability(
            reliability_result
        )
    )

    monitoring_analysis = (
        analyze_monitoring(
            monitoring_result
        )
    )

    alert_analysis = (
        analyze_alerts(
            alert_result
        )
    )

    recommendation_analysis = (
        analyze_recommendations(
            recommendation_result
        )
    )

    summary = build_executive_summary(
        prediction_analysis,
        error_analysis,
        reliability_analysis,
        alert_analysis,
        recommendation_analysis,
    )

    available_components = [

        prediction_analysis[
            'has_predictions'
        ],

        error_analysis is not None,

        reliability_analysis[
            'available'
        ],

        monitoring_analysis[
            'available'
        ],

        alert_analysis[
            'available'
        ],

        recommendation_analysis[
            'available'
        ],
    ]

    if not any(
        available_components
    ):

        status = (
            ANALYSIS_INSUFFICIENT_DATA
        )

    else:

        status = ANALYSIS_VALID

    return {

        'status':
            status,

        'prediction_analysis':
            prediction_analysis,

        'error_analysis':
            error_analysis,

        'reliability_analysis':
            reliability_analysis,

        'monitoring_analysis':
            monitoring_analysis,

        'alert_analysis':
            alert_analysis,

        'recommendation_analysis':
            recommendation_analysis,

        'executive_summary':
            summary,
    }


# ==========================================================
# SIMPLE TEST
# ==========================================================

if __name__ == '__main__':

    result = analyze_system(
        {
            'target_name':
                'Target_Expense_Total_1D',

            'target_task':
                'regression',

            'predictions':
                [100, 120, 140],
        }
    )

    print()
    print(
        '========== AI ANALYSIS =========='
    )

    print(
        result
    )

# ==========================================================
# BACKWARD COMPATIBILITY
# ==========================================================

def analyze_prediction(
    prediction_result,
):
    """
    Compatibility wrapper for the integration layer.

    The main API uses analyze_predictions().

    This singular form is retained as a compatibility
    entry point for the integration layer.
    """

    return analyze_predictions(
        prediction_result
    )

def analyze_prediction(prediction_result):
    return analyze_predictions(prediction_result)