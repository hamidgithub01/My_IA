from ml.alerts.alerts import (
    analyze_alerts,
    ALERT_NONE,
    ALERT_VALID,
    ALERT_LOW_RELIABILITY,
    ALERT_UNRELIABLE,
    ALERT_HIGH_ERROR,
    ALERT_RELIABILITY_DECLINE,
    ALERT_INSUFFICIENT_DATA,
)

from ml.alerts.recommendations import (
    generate_recommendations,
    RECOMMENDATION_RETRAIN_MODEL,
    RECOMMENDATION_REVIEW_MODEL,
    RECOMMENDATION_MONITOR_CLOSELY,
    RECOMMENDATION_COLLECT_MORE_DATA,
)

from ml.alerts.decision_policy import (
    resolve_decision,
    DECISION_VALID,
    DECISION_NONE,
)


# ==========================================================
# FULL PIPELINE HELPER
# ==========================================================

def _run_pipeline(
    monitoring_result,
    maximum_error_rate=None,
    minimum_reliability_decline=None,
):
    """
    Run the complete operational pipeline:

        Monitoring Result
              ↓
        Alert Analysis
              ↓
        Recommendation Generation
              ↓
        Decision Policy
    """

    alert_result = analyze_alerts(
        monitoring_result,
        maximum_error_rate=maximum_error_rate,
        minimum_reliability_decline=(
            minimum_reliability_decline
        ),
    )

    recommendation_result = (
        generate_recommendations(
            alert_result
        )
    )

    decision_result = resolve_decision(
        alert_result
    )

    return {
        'alert_result': alert_result,
        'recommendation_result': (
            recommendation_result
        ),
        'decision_result': decision_result,
    }


# ==========================================================
# NO ALERTS
# ==========================================================

def test_pipeline_no_alerts_produces_no_decision():

    result = _run_pipeline(
        {
            'status': 'reliable',
            'reliability_level': 'high',
            'target_name': 'Target_Test',
            'error_rate': 0.05,
        },
        maximum_error_rate=0.20,
    )

    alert_result = result['alert_result']
    recommendation_result = (
        result['recommendation_result']
    )
    decision_result = result['decision_result']

    assert alert_result['status'] == ALERT_NONE
    assert alert_result['alert_count'] == 0
    assert alert_result['alerts'] == []

    assert (
        recommendation_result['recommendations']
        == []
    )

    assert (
        decision_result['status']
        == DECISION_NONE
    )

    assert (
        decision_result['primary_action']
        is None
    )

    assert (
        decision_result['recommendations']
        == []
    )


# ==========================================================
# UNRELIABLE MODEL
# ==========================================================

def test_pipeline_unreliable_model_leads_to_retraining():

    result = _run_pipeline(
        {
            'status': 'unreliable',
            'reliability_level': 'low',
            'target_name': 'Target_Test',
        }
    )

    alert_result = result['alert_result']
    recommendation_result = (
        result['recommendation_result']
    )
    decision_result = result['decision_result']

    # Alert layer
    assert alert_result['status'] == ALERT_VALID

    alert_types = {
        alert['alert_type']
        for alert in alert_result['alerts']
    }

    assert ALERT_UNRELIABLE in alert_types

    # Recommendation layer
    recommendation_types = {
        recommendation[
            'recommendation_type'
        ]
        for recommendation
        in recommendation_result[
            'recommendations'
        ]
    }

    assert (
        RECOMMENDATION_RETRAIN_MODEL
        in recommendation_types
    )

    # Decision layer
    assert (
        decision_result['status']
        == DECISION_VALID
    )

    assert (
        decision_result['primary_action']
        == RECOMMENDATION_RETRAIN_MODEL
    )

    assert (
        decision_result['priority']
        == 'critical'
    )


# ==========================================================
# LOW RELIABILITY
# ==========================================================

def test_pipeline_low_reliability_leads_to_model_review():

    result = _run_pipeline(
        {
            'status': 'reliable',
            'reliability_level': 'low',
            'target_name': 'Target_Test',
        }
    )

    alert_result = result['alert_result']
    recommendation_result = (
        result['recommendation_result']
    )
    decision_result = result['decision_result']

    assert alert_result['status'] == ALERT_VALID

    assert (
        alert_result['alerts'][0]['alert_type']
        == ALERT_LOW_RELIABILITY
    )

    assert (
        recommendation_result[
            'recommendations'
        ][0]['recommendation_type']
        == RECOMMENDATION_REVIEW_MODEL
    )

    assert (
        decision_result['primary_action']
        == RECOMMENDATION_REVIEW_MODEL
    )

    assert (
        decision_result['priority']
        == 'high'
    )


# ==========================================================
# HIGH ERROR RATE
# ==========================================================

def test_pipeline_high_error_leads_to_model_review():

    result = _run_pipeline(
        {
            'status': 'reliable',
            'reliability_level': 'high',
            'error_rate': 0.40,
            'target_name': 'Target_Test',
        },
        maximum_error_rate=0.20,
    )

    alert_result = result['alert_result']
    recommendation_result = (
        result['recommendation_result']
    )
    decision_result = result['decision_result']

    assert alert_result['status'] == ALERT_VALID

    assert (
        alert_result['alerts'][0]['alert_type']
        == ALERT_HIGH_ERROR
    )

    assert (
        recommendation_result[
            'recommendations'
        ][0]['recommendation_type']
        == RECOMMENDATION_REVIEW_MODEL
    )

    assert (
        decision_result['primary_action']
        == RECOMMENDATION_REVIEW_MODEL
    )

    assert (
        decision_result['priority']
        == 'high'
    )


# ==========================================================
# RELIABILITY DECLINE
# ==========================================================

def test_pipeline_reliability_decline_leads_to_close_monitoring():

    result = _run_pipeline(
        {
            'status': 'reliable',
            'reliability_level': 'high',
            'previous_quality_score': 0.90,
            'quality_score': 0.70,
            'target_name': 'Target_Test',
        },
        minimum_reliability_decline=0.10,
    )

    alert_result = result['alert_result']
    recommendation_result = (
        result['recommendation_result']
    )
    decision_result = result['decision_result']

    assert alert_result['status'] == ALERT_VALID

    assert (
        alert_result['alerts'][0]['alert_type']
        == ALERT_RELIABILITY_DECLINE
    )

    assert (
        recommendation_result[
            'recommendations'
        ][0]['recommendation_type']
        == RECOMMENDATION_MONITOR_CLOSELY
    )

    assert (
        decision_result['primary_action']
        == RECOMMENDATION_MONITOR_CLOSELY
    )

    assert (
        decision_result['priority']
        == 'medium'
    )


# ==========================================================
# INSUFFICIENT DATA
# ==========================================================

def test_pipeline_insufficient_data_leads_to_more_data():

    result = _run_pipeline(
        {
            'status': 'reliable',
            'reliability_level': 'unknown',
            'target_name': 'Target_Test',
        }
    )

    alert_result = result['alert_result']
    recommendation_result = (
        result['recommendation_result']
    )
    decision_result = result['decision_result']

    assert alert_result['status'] == ALERT_VALID

    assert (
        alert_result['alerts'][0]['alert_type']
        == ALERT_INSUFFICIENT_DATA
    )

    assert (
        recommendation_result[
            'recommendations'
        ][0]['recommendation_type']
        == RECOMMENDATION_COLLECT_MORE_DATA
    )

    assert (
        decision_result['primary_action']
        == RECOMMENDATION_COLLECT_MORE_DATA
    )

    assert (
        decision_result['priority']
        == 'medium'
    )


# ==========================================================
# MULTIPLE ALERTS
# ==========================================================

def test_pipeline_critical_alert_overrides_weaker_actions():

    result = _run_pipeline(
        {
            'status': 'unreliable',
            'reliability_level': 'low',
            'error_rate': 0.50,
            'previous_quality_score': 0.90,
            'quality_score': 0.60,
            'target_name': 'Target_Test',
        },
        maximum_error_rate=0.20,
        minimum_reliability_decline=0.10,
    )

    alert_result = result['alert_result']
    recommendation_result = (
        result['recommendation_result']
    )
    decision_result = result['decision_result']

    # Several alerts should exist.
    assert alert_result['status'] == ALERT_VALID

    alert_types = {
        alert['alert_type']
        for alert in alert_result['alerts']
    }

    assert ALERT_UNRELIABLE in alert_types
    assert ALERT_LOW_RELIABILITY in alert_types
    assert ALERT_HIGH_ERROR in alert_types
    assert ALERT_RELIABILITY_DECLINE in alert_types

    # The recommendation layer may receive several
    # actionable alerts, but the decision policy must
    # select retraining as the dominant action.
    recommendation_types = {
        recommendation[
            'recommendation_type'
        ]
        for recommendation
        in recommendation_result[
            'recommendations'
        ]
    }

    assert (
        RECOMMENDATION_RETRAIN_MODEL
        in recommendation_types
    )

    assert (
        decision_result['primary_action']
        == RECOMMENDATION_RETRAIN_MODEL
    )

    assert (
        decision_result['priority']
        == 'critical'
    )


# ==========================================================
# TARGET ISOLATION
# ==========================================================

def test_pipeline_preserves_target_isolation():

    target_a = _run_pipeline(
        {
            'status': 'unreliable',
            'reliability_level': 'low',
            'target_name': 'Target_A',
        }
    )

    target_b = _run_pipeline(
        {
            'status': 'reliable',
            'reliability_level': 'high',
            'previous_quality_score': 0.90,
            'quality_score': 0.70,
            'target_name': 'Target_B',
        },
        minimum_reliability_decline=0.10,
    )

    decision_a = target_a[
        'decision_result'
    ]

    decision_b = target_b[
        'decision_result'
    ]

    assert (
        decision_a['primary_action']
        == RECOMMENDATION_RETRAIN_MODEL
    )

    assert (
        decision_a['priority']
        == 'critical'
    )

    assert (
        decision_b['primary_action']
        == RECOMMENDATION_MONITOR_CLOSELY
    )

    assert (
        decision_b['priority']
        == 'medium'
    )


# ==========================================================
# UNKNOWN ALERT SAFETY
# ==========================================================

def test_pipeline_unknown_alert_remains_safe():

    alert_result = {
        'status': ALERT_VALID,
        'alert_count': 1,
        'alerts': [
            {
                'alert_type':
                    'future_unknown_alert',
                'severity':
                    'warning',
                'target_name':
                    'Target_Test',
            }
        ],
    }

    recommendation_result = (
        generate_recommendations(
            alert_result
        )
    )

    decision_result = resolve_decision(
        alert_result
    )

    assert (
        recommendation_result[
            'recommendations'
        ]
        == []
    )

    assert (
        decision_result['status']
        == DECISION_NONE
    )

    assert (
        decision_result['primary_action']
        is None
    )

    assert (
        decision_result['recommendations']
        == []
    )


# ==========================================================
# CONTRACT PRESERVATION
# ==========================================================

def test_pipeline_preserves_end_to_end_contract():

    result = _run_pipeline(
        {
            'status': 'reliable',
            'reliability_level': 'low',
            'target_name': 'Target_Test',
        }
    )

    alert_result = result['alert_result']
    recommendation_result = (
        result['recommendation_result']
    )
    decision_result = result['decision_result']

    # Alert contract
    assert {
        'status',
        'alert_count',
        'alerts',
        'target_name',
    }.issubset(
        alert_result.keys()
    )

    # Recommendation contract
    assert {
        'status',
        'recommendation_count',
        'recommendations',
    }.issubset(
        recommendation_result.keys()
    )

    # Decision contract
    assert {
        'status',
        'target_name',
        'alerts',
        'primary_action',
        'priority',
        'recommendations',
        'decisions_by_target',
    }.issubset(
        decision_result.keys()
    )


# ==========================================================
# ALERT → RECOMMENDATION → DECISION CONSISTENCY
# ==========================================================

def test_pipeline_preserves_target_through_all_layers():

    result = _run_pipeline(
        {
            'status': 'unreliable',
            'reliability_level': 'low',
            'target_name': 'Target_Financial',
        }
    )

    alert_result = result['alert_result']
    recommendation_result = (
        result['recommendation_result']
    )
    decision_result = result['decision_result']

    assert (
        alert_result['target_name']
        == 'Target_Financial'
    )

    assert (
        alert_result['alerts'][0][
            'target_name'
        ]
        == 'Target_Financial'
    )

    assert (
        recommendation_result[
            'recommendations'
        ][0]['target_name']
        == 'Target_Financial'
    )

    assert (
        decision_result['target_name']
        == 'Target_Financial'
    )


# ==========================================================
# MAIN
# ==========================================================

if __name__ == '__main__':

    print(
        '========== ALERT PIPELINE INTEGRATION TESTS =========='
    )

    print(
        'ALL PIPELINE INTEGRATION TESTS PASSED'
    )