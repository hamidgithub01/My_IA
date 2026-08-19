# ==========================================================
# RECOMMENDATION STATUS
# ==========================================================

RECOMMENDATION_VALID = 'valid'
RECOMMENDATION_NONE = 'none'


# ==========================================================
# RECOMMENDATION TYPES
# ==========================================================

RECOMMENDATION_RETRAIN_MODEL = (
    'retrain_model'
)

RECOMMENDATION_COLLECT_MORE_DATA = (
    'collect_more_data'
)

RECOMMENDATION_REVIEW_MODEL = (
    'review_model'
)

RECOMMENDATION_MONITOR_CLOSELY = (
    'monitor_closely'
)

RECOMMENDATION_CONTINUE_MONITORING = (
    'continue_monitoring'
)


# ==========================================================
# PRIORITY
# ==========================================================

PRIORITY_LOW = 'low'
PRIORITY_MEDIUM = 'medium'
PRIORITY_HIGH = 'high'
PRIORITY_CRITICAL = 'critical'


# ==========================================================
# BASIC VALIDATION
# ==========================================================

def _validate_alert_result(
    alert_result,
):
    """
    Validate the alert-analysis result.
    """

    if alert_result is None:

        raise ValueError(
            'alert_result is required.'
        )

    if not isinstance(
        alert_result,
        dict,
    ):

        raise ValueError(
            'alert_result must be a dictionary.'
        )

    alerts = alert_result.get(
        'alerts'
    )

    if alerts is None:

        raise ValueError(
            'alert_result must contain alerts.'
        )

    if not isinstance(
        alerts,
        list,
    ):

        raise ValueError(
            'alert_result alerts must be a list.'
        )


# ==========================================================
# RECOMMENDATION CREATION
# ==========================================================

def _create_recommendation(
    recommendation_type,
    priority,
    message,
    reason=None,
    target_name=None,
    source_alert_type=None,
):
    """
    Create a standardized recommendation.
    """

    return {

        'recommendation_type':
            recommendation_type,

        'priority':
            priority,

        'message':
            message,

        'reason':
            reason,

        'target_name':
            target_name,

        'source_alert_type':
            source_alert_type,
    }


# ==========================================================
# ALERT → RECOMMENDATION
# ==========================================================

def _recommend_for_alert(
    alert,
):
    """
    Convert one alert into an actionable recommendation.
    """

    if not isinstance(
        alert,
        dict,
    ):

        raise ValueError(
            'Each alert must be a dictionary.'
        )

    alert_type = alert.get(
        'alert_type'
    )

    severity = alert.get(
        'severity'
    )

    target_name = alert.get(
        'target_name'
    )

    # ------------------------------------------------------
    # Critical unreliable system
    # ------------------------------------------------------

    if alert_type == 'unreliable':

        return _create_recommendation(
            recommendation_type=(
                RECOMMENDATION_RETRAIN_MODEL
            ),
            priority=PRIORITY_CRITICAL,
            message=(
                'Retrain the model before relying '
                'on further predictions.'
            ),
            reason=(
                'The monitoring system explicitly '
                'marked the prediction system as '
                'unreliable.'
            ),
            target_name=target_name,
            source_alert_type=alert_type,
        )

    # ------------------------------------------------------
    # Low reliability
    # ------------------------------------------------------

    if alert_type == 'low_reliability':

        return _create_recommendation(
            recommendation_type=(
                RECOMMENDATION_REVIEW_MODEL
            ),
            priority=PRIORITY_HIGH,
            message=(
                'Review the model performance and '
                'consider retraining with recent data.'
            ),
            reason=(
                'Prediction reliability is below '
                'the acceptable operational level.'
            ),
            target_name=target_name,
            source_alert_type=alert_type,
        )

    # ------------------------------------------------------
    # High error rate
    # ------------------------------------------------------

    if alert_type == 'high_error':

        return _create_recommendation(
            recommendation_type=(
                RECOMMENDATION_REVIEW_MODEL
            ),
            priority=PRIORITY_HIGH,
            message=(
                'Investigate the recent prediction '
                'errors and review model performance.'
            ),
            reason=(
                'The observed prediction error rate '
                'exceeds the configured threshold.'
            ),
            target_name=target_name,
            source_alert_type=alert_type,
        )

    # ------------------------------------------------------
    # Reliability decline
    # ------------------------------------------------------

    if alert_type == 'reliability_decline':

        return _create_recommendation(
            recommendation_type=(
                RECOMMENDATION_MONITOR_CLOSELY
            ),
            priority=PRIORITY_MEDIUM,
            message=(
                'Monitor the model closely for '
                'continued performance degradation.'
            ),
            reason=(
                'Prediction quality has declined '
                'relative to the previous monitoring '
                'period.'
            ),
            target_name=target_name,
            source_alert_type=alert_type,
        )

    # ------------------------------------------------------
    # Insufficient data
    # ------------------------------------------------------

    if alert_type == 'insufficient_data':

        return _create_recommendation(
            recommendation_type=(
                RECOMMENDATION_COLLECT_MORE_DATA
            ),
            priority=PRIORITY_MEDIUM,
            message=(
                'Collect more observations before '
                'making a strong reliability decision.'
            ),
            reason=(
                'There is insufficient monitoring '
                'data to establish reliable model '
                'performance.'
            ),
            target_name=target_name,
            source_alert_type=alert_type,
        )

    # ------------------------------------------------------
    # Unknown alert
    # ------------------------------------------------------

    return None


# ==========================================================
# DEDUPLICATION
# ==========================================================

def _deduplicate_recommendations(
    recommendations,
):
    """
    Remove duplicate recommendations while preserving
    their original order.
    """

    unique = []

    seen = set()

    for recommendation in recommendations:

        key = (
            recommendation[
                'recommendation_type'
            ],
            recommendation.get(
                'target_name'
            ),
        )

        if key in seen:

            continue

        seen.add(key)

        unique.append(
            recommendation
        )

    return unique


# ==========================================================
# PUBLIC RECOMMENDATION ANALYSIS
# ==========================================================

def generate_recommendations(
    alert_result,
):
    """
    Generate actionable recommendations from alerts.

    The function does not create recommendations when
    no actionable alert exists.
    """

    _validate_alert_result(
        alert_result
    )

    alerts = alert_result[
        'alerts'
    ]

    recommendations = []

    for alert in alerts:

        recommendation = (
            _recommend_for_alert(
                alert
            )
        )

        if recommendation is not None:

            recommendations.append(
                recommendation
            )

    recommendations = (
        _deduplicate_recommendations(
            recommendations
        )
    )

    if recommendations:

        status = (
            RECOMMENDATION_VALID
        )

    else:

        status = (
            RECOMMENDATION_NONE
        )

    return {

        'status':
            status,

        'recommendation_count':
            len(recommendations),

        'recommendations':
            recommendations,
    }


# ==========================================================
# UNIFIED ALERT + RECOMMENDATION RESULT
# ==========================================================

def analyze_alerts_and_recommendations(
    alert_result,
):
    """
    Produce a unified decision result containing both
    alerts and recommendations.
    """

    _validate_alert_result(
        alert_result
    )

    recommendation_result = (
        generate_recommendations(
            alert_result
        )
    )

    return {

        'alert_status':
            alert_result.get(
                'status'
            ),

        'alert_count':
            alert_result.get(
                'alert_count',
                len(
                    alert_result[
                        'alerts'
                    ]
                ),
            ),

        'alerts':
            alert_result[
                'alerts'
            ],

        'recommendation_status':
            recommendation_result[
                'status'
            ],

        'recommendation_count':
            recommendation_result[
                'recommendation_count'
            ],

        'recommendations':
            recommendation_result[
                'recommendations'
            ],
    }