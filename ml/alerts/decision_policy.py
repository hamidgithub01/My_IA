from ml.alerts.recommendations import (
    RECOMMENDATION_RETRAIN_MODEL,
    RECOMMENDATION_REVIEW_MODEL,
    RECOMMENDATION_MONITOR_CLOSELY,
    RECOMMENDATION_COLLECT_MORE_DATA,
    PRIORITY_MEDIUM,
    PRIORITY_HIGH,
    PRIORITY_CRITICAL,
    _recommend_for_alert,
)


# ==========================================================
# DECISION STATUS
# ==========================================================

DECISION_VALID = 'valid'
DECISION_NONE = 'none'


# ==========================================================
# DECISION RESOLUTION
# ==========================================================

def _resolve_recommendations(recommendations):
    """
    Resolve recommendations into one primary decision and
    one effective recommendation set.

    Stronger decisions suppress weaker actions.

    Policy:

        critical retrain
            > high review
            > medium monitor
            > medium collect data
    """

    if not recommendations:
        return {
            'primary_action': None,
            'priority': None,
            'recommendations': [],
        }

    # ------------------------------------------------------
    # CRITICAL: RETRAIN
    # ------------------------------------------------------

    retrain = [
        recommendation
        for recommendation in recommendations
        if recommendation['recommendation_type']
        == RECOMMENDATION_RETRAIN_MODEL
    ]

    if retrain:
        return {
            'primary_action':
                RECOMMENDATION_RETRAIN_MODEL,

            'priority':
                PRIORITY_CRITICAL,

            'recommendations':
                [retrain[0]],
        }

    # ------------------------------------------------------
    # HIGH: REVIEW
    # ------------------------------------------------------

    review = [
        recommendation
        for recommendation in recommendations
        if recommendation['recommendation_type']
        == RECOMMENDATION_REVIEW_MODEL
    ]

    if review:
        return {
            'primary_action':
                RECOMMENDATION_REVIEW_MODEL,

            'priority':
                PRIORITY_HIGH,

            'recommendations':
                [review[0]],
        }

    # ------------------------------------------------------
    # MEDIUM: MONITOR
    # ------------------------------------------------------

    monitor = [
        recommendation
        for recommendation in recommendations
        if recommendation['recommendation_type']
        == RECOMMENDATION_MONITOR_CLOSELY
    ]

    if monitor:
        return {
            'primary_action':
                RECOMMENDATION_MONITOR_CLOSELY,

            'priority':
                PRIORITY_MEDIUM,

            'recommendations':
                [monitor[0]],
        }

    # ------------------------------------------------------
    # MEDIUM: COLLECT MORE DATA
    # ------------------------------------------------------

    collect = [
        recommendation
        for recommendation in recommendations
        if recommendation['recommendation_type']
        == RECOMMENDATION_COLLECT_MORE_DATA
    ]

    if collect:
        return {
            'primary_action':
                RECOMMENDATION_COLLECT_MORE_DATA,

            'priority':
                PRIORITY_MEDIUM,

            'recommendations':
                [collect[0]],
        }

    return {
        'primary_action': None,
        'priority': None,
        'recommendations': [],
    }

# ==========================================================
# ALERT → RECOMMENDATION
# ==========================================================

def _build_recommendations(alerts):
    """
    Convert actionable alerts into recommendations.

    Unknown alerts are intentionally ignored.
    """

    recommendations = []

    for alert in alerts:

        recommendation = (
            _recommend_for_alert(
                alert
            )
        )

        if recommendation is None:
            continue

        recommendations.append(
            recommendation
        )

    return recommendations


# ==========================================================
# TARGET GROUPING
# ==========================================================

def _group_by_target(recommendations):
    """
    Group recommendations by target_name.
    """

    grouped = {}

    for recommendation in recommendations:

        target_name = recommendation.get(
            'target_name'
        )

        if target_name not in grouped:

            grouped[target_name] = []

        grouped[target_name].append(
            recommendation
        )

    return grouped


# ==========================================================
# TARGET DECISION
# ==========================================================

def _resolve_target_decision(
    target_name,
    recommendations,
):
    """
    Resolve the final decision for one target.
    """

    resolved = _resolve_recommendations(
        recommendations
    )

    return {
        'target_name':
            target_name,

        'primary_action':
            resolved['primary_action'],

        'priority':
            resolved['priority'],

        'recommendations':
            resolved['recommendations'],
    }


# ==========================================================
# PUBLIC DECISION API
# ==========================================================

def resolve_decision(alert_result):
    """
    Resolve alerts into final operational decisions.

    This layer does not perform prediction, reliability
    calculation, or alert detection.

    It only translates actionable alerts into decisions.
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

    # ------------------------------------------------------
    # No alerts
    # ------------------------------------------------------

    if not alerts:

        return {

            'status':
                DECISION_NONE,

            'target_name':
                None,

            'alerts':
                alerts,

            'primary_action':
                None,

            'priority':
                None,

            'recommendations':
                [],

            'decisions_by_target':
                {},
        }

    # ------------------------------------------------------
    # Build recommendations
    # ------------------------------------------------------

    recommendations = _build_recommendations(
        alerts
    )

    # ------------------------------------------------------
    # No actionable alerts
    # ------------------------------------------------------

    if not recommendations:

        return {

            'status':
                DECISION_NONE,

            'target_name':
                None,

            'alerts':
                alerts,

            'primary_action':
                None,

            'priority':
                None,

            'recommendations':
                [],

            'decisions_by_target':
                {},
        }

    # ------------------------------------------------------
    # Group by target
    # ------------------------------------------------------

    grouped = _group_by_target(
        recommendations
    )

    decisions_by_target = {}

    for target_name, target_recommendations in grouped.items():

        decisions_by_target[target_name] = (
            _resolve_target_decision(
                target_name,
                target_recommendations,
            )
        )

    # ------------------------------------------------------
    # Determine top-level decision
    # ------------------------------------------------------

    all_resolved = []

    for decision in decisions_by_target.values():

        if decision['primary_action'] is not None:

            all_resolved.append(
                decision
            )

    if not all_resolved:

        return {

            'status':
                DECISION_NONE,

            'target_name':
                None,

            'alerts':
                alerts,

            'primary_action':
                None,

            'priority':
                None,

            'recommendations':
                [],

            'decisions_by_target':
                decisions_by_target,
        }

    # ------------------------------------------------------
    # Global priority
    # ------------------------------------------------------

    priority_order = {
        PRIORITY_CRITICAL: 3,
        PRIORITY_HIGH: 2,
        PRIORITY_MEDIUM: 1,
    }

    top_decision = max(
        all_resolved,
        key=lambda decision:
            priority_order.get(
                decision['priority'],
                0,
            ),
    )

    return {

        'status':
            DECISION_VALID,

        'target_name':
            top_decision['target_name'],

        'alerts':
            alerts,

        'primary_action':
            top_decision['primary_action'],

        'priority':
            top_decision['priority'],

        'recommendations':
            top_decision['recommendations'],

        'decisions_by_target':
            decisions_by_target,
    }