"""
Alerts & Recommendations Pipeline
=================================

High-level facade for the complete operational pipeline:

    Monitoring Result
            ↓
        Alert Analysis
            ↓
     Recommendation Generation
            ↓
       Decision Policy
            ↓
    Unified Operational Result

This module intentionally contains orchestration only.
Business rules remain in:
    - ml.alerts.alerts
    - ml.alerts.recommendations
    - ml.alerts.decision_policy
"""


from ml.alerts.alerts import (
    analyze_alerts,
)

from ml.alerts.recommendations import (
    generate_recommendations,
)

from ml.alerts.decision_policy import (
    resolve_decision,
)


# ==========================================================
# PIPELINE STATUS
# ==========================================================

PIPELINE_VALID = 'valid'
PIPELINE_NONE = 'none'


# ==========================================================
# VALIDATION
# ==========================================================

def _validate_monitoring_result(
    monitoring_result,
):
    """
    Validate the monitoring result supplied to the pipeline.
    """

    if monitoring_result is None:
        raise ValueError(
            'monitoring_result is required.'
        )

    if not isinstance(
        monitoring_result,
        dict,
    ):
        raise ValueError(
            'monitoring_result must be a dictionary.'
        )


# ==========================================================
# PUBLIC PIPELINE
# ==========================================================

def run_alert_pipeline(
    monitoring_result,
    maximum_error_rate=None,
    minimum_reliability_decline=None,
):
    """
    Run the complete Alerts & Recommendations pipeline.

    Pipeline:

        monitoring_result
            ↓
        analyze_alerts()
            ↓
        generate_recommendations()
            ↓
        resolve_decision()

    The function does not implement business rules itself.
    It only composes the existing layers.
    """

    _validate_monitoring_result(
        monitoring_result
    )

    # ------------------------------------------------------
    # STEP 1: ALERT ANALYSIS
    # ------------------------------------------------------

    alert_result = analyze_alerts(
        monitoring_result,
        maximum_error_rate=(
            maximum_error_rate
        ),
        minimum_reliability_decline=(
            minimum_reliability_decline
        ),
    )

    # ------------------------------------------------------
    # STEP 2: RECOMMENDATIONS
    # ------------------------------------------------------

    recommendation_result = (
        generate_recommendations(
            alert_result
        )
    )

    # ------------------------------------------------------
    # STEP 3: DECISION POLICY
    # ------------------------------------------------------

    decision_result = resolve_decision(
        alert_result
    )

    # ------------------------------------------------------
    # PIPELINE STATUS
    # ------------------------------------------------------

    if (
        alert_result['alert_count'] > 0
        or recommendation_result[
            'recommendation_count'
        ] > 0
    ):
        status = PIPELINE_VALID
    else:
        status = PIPELINE_NONE

    # ------------------------------------------------------
    # UNIFIED RESULT
    # ------------------------------------------------------

    return {

        'status':
            status,

        'target_name':
            monitoring_result.get(
                'target_name'
            ),

        'monitoring_result':
            monitoring_result,

        'alerts':
            alert_result,

        'recommendations':
            recommendation_result,

        'decision':
            decision_result,
    }


# ==========================================================
# CONVENIENCE HELPERS
# ==========================================================

def has_operational_action(
    pipeline_result,
):
    """
    Return True when the pipeline produced
    at least one actionable recommendation.
    """

    if pipeline_result is None:
        raise ValueError(
            'pipeline_result is required.'
        )

    if not isinstance(
        pipeline_result,
        dict,
    ):
        raise ValueError(
            'pipeline_result must be a dictionary.'
        )

    recommendations = (
        pipeline_result
        .get(
            'recommendations',
            {},
        )
        .get(
            'recommendations',
            [],
        )
    )

    return bool(
        recommendations
    )


def has_alerts(
    pipeline_result,
):
    """
    Return True when the pipeline produced
    at least one alert.
    """

    if pipeline_result is None:
        raise ValueError(
            'pipeline_result is required.'
        )

    if not isinstance(
        pipeline_result,
        dict,
    ):
        raise ValueError(
            'pipeline_result must be a dictionary.'
        )

    alert_result = (
        pipeline_result.get(
            'alerts',
            {},
        )
    )

    return (
        alert_result.get(
            'alert_count',
            0,
        )
        > 0
    )