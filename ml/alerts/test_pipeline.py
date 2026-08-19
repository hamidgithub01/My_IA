from ml.alerts.pipeline import (
    PIPELINE_VALID,
    PIPELINE_NONE,
    run_alert_pipeline,
    has_alerts,
    has_operational_action,
)

from ml.alerts.recommendations import (
    RECOMMENDATION_RETRAIN_MODEL,
    RECOMMENDATION_REVIEW_MODEL,
    RECOMMENDATION_MONITOR_CLOSELY,
    RECOMMENDATION_COLLECT_MORE_DATA,
    PRIORITY_CRITICAL,
    PRIORITY_HIGH,
    PRIORITY_MEDIUM,
)


# ==========================================================
# NO ALERTS
# ==========================================================

def test_pipeline_no_alerts():

    result = run_alert_pipeline(
        {
            'status': 'reliable',
            'reliability_level': 'high',
            'target_name': 'Target_Test',
        }
    )

    assert result['status'] == PIPELINE_NONE

    assert result['target_name'] == 'Target_Test'

    assert result['alerts']['alert_count'] == 0

    assert result['alerts']['alerts'] == []

    assert (
        result['recommendations']['recommendations']
        == []
    )

    assert (
        result['decision']['primary_action']
        is None
    )

    assert (
        result['decision']['priority']
        is None
    )


# ==========================================================
# UNRELIABLE MODEL
# ==========================================================

def test_pipeline_unreliable_model():

    result = run_alert_pipeline(
        {
            'status': 'unreliable',
            'reliability_level': 'low',
            'target_name': 'Target_Test',
        }
    )

    assert result['status'] == PIPELINE_VALID

    assert (
        result['alerts']['alert_count']
        >= 1
    )

    assert (
        result['recommendations']
        ['recommendation_count']
        >= 1
    )

    assert (
        result['decision']
        ['primary_action']
        == RECOMMENDATION_RETRAIN_MODEL
    )

    assert (
        result['decision']['priority']
        == PRIORITY_CRITICAL
    )


# ==========================================================
# LOW RELIABILITY
# ==========================================================

def test_pipeline_low_reliability():

    result = run_alert_pipeline(
        {
            'status': 'reliable',
            'reliability_level': 'low',
            'target_name': 'Target_Test',
        }
    )

    assert result['status'] == PIPELINE_VALID

    assert (
        result['decision']
        ['primary_action']
        == RECOMMENDATION_REVIEW_MODEL
    )

    assert (
        result['decision']['priority']
        == PRIORITY_HIGH
    )


# ==========================================================
# HIGH ERROR RATE
# ==========================================================

def test_pipeline_high_error():

    result = run_alert_pipeline(
        {
            'status': 'reliable',
            'reliability_level': 'high',
            'error_rate': 0.40,
            'target_name': 'Target_Test',
        },
        maximum_error_rate=0.20,
    )

    assert result['status'] == PIPELINE_VALID

    assert (
        result['decision']
        ['primary_action']
        == RECOMMENDATION_REVIEW_MODEL
    )

    assert (
        result['decision']['priority']
        == PRIORITY_HIGH
    )


# ==========================================================
# RELIABILITY DECLINE
# ==========================================================

def test_pipeline_reliability_decline():

    result = run_alert_pipeline(
        {
            'status': 'reliable',
            'reliability_level': 'high',
            'previous_quality_score': 0.90,
            'quality_score': 0.70,
            'target_name': 'Target_Test',
        },
        minimum_reliability_decline=0.10,
    )

    assert result['status'] == PIPELINE_VALID

    assert (
        result['decision']
        ['primary_action']
        == RECOMMENDATION_MONITOR_CLOSELY
    )

    assert (
        result['decision']['priority']
        == PRIORITY_MEDIUM
    )


# ==========================================================
# INSUFFICIENT DATA
# ==========================================================

def test_pipeline_insufficient_data():

    result = run_alert_pipeline(
        {
            'status': 'reliable',
            'reliability_level': 'unknown',
            'target_name': 'Target_Test',
        }
    )

    assert result['status'] == PIPELINE_VALID

    assert (
        result['decision']
        ['primary_action']
        == RECOMMENDATION_COLLECT_MORE_DATA
    )

    assert (
        result['decision']['priority']
        == PRIORITY_MEDIUM
    )


# ==========================================================
# CRITICAL OVERRIDE
# ==========================================================

def test_pipeline_critical_alert_overrides_weaker_actions():

    result = run_alert_pipeline(
        {
            'status': 'unreliable',
            'reliability_level': 'low',
            'error_rate': 0.40,
            'previous_quality_score': 0.90,
            'quality_score': 0.70,
            'target_name': 'Target_Test',
        },
        maximum_error_rate=0.20,
        minimum_reliability_decline=0.10,
    )

    assert (
        result['decision']
        ['primary_action']
        == RECOMMENDATION_RETRAIN_MODEL
    )

    assert (
        result['decision']['priority']
        == PRIORITY_CRITICAL
    )

    actions = {
        recommendation[
            'recommendation_type'
        ]
        for recommendation
        in result['decision']
        ['recommendations']
    }

    assert (
        RECOMMENDATION_RETRAIN_MODEL
        in actions
    )

    assert (
        RECOMMENDATION_REVIEW_MODEL
        not in actions
    )

    assert (
        RECOMMENDATION_MONITOR_CLOSELY
        not in actions
    )


# ==========================================================
# TARGET PRESERVATION
# ==========================================================

def test_pipeline_preserves_target():

    result = run_alert_pipeline(
        {
            'status': 'unreliable',
            'reliability_level': 'low',
            'target_name': 'Financial_Target',
        }
    )

    assert (
        result['target_name']
        == 'Financial_Target'
    )

    assert (
        result['alerts']['target_name']
        == 'Financial_Target'
    )

    assert (
        result['decision']['target_name']
        == 'Financial_Target'
    )


# ==========================================================
# TARGET ISOLATION
# ==========================================================

def test_pipeline_preserves_target_isolation():

    result = run_alert_pipeline(
        {
            'status': 'unreliable',
            'reliability_level': 'low',
            'target_name': 'Target_A',
        }
    )

    assert (
        result['decision']
        ['decisions_by_target']
        ['Target_A']
        ['primary_action']
        == RECOMMENDATION_RETRAIN_MODEL
    )


# ==========================================================
# UNKNOWN ALERT SAFETY
# ==========================================================

def test_pipeline_unknown_conditions_remain_safe():

    result = run_alert_pipeline(
        {
            'status': 'reliable',
            'reliability_level': 'high',
            'target_name': 'Target_Test',
        }
    )

    assert result['status'] == PIPELINE_NONE

    assert (
        result['decision']
        ['primary_action']
        is None
    )

    assert (
        result['decision']
        ['recommendations']
        == []
    )


# ==========================================================
# END-TO-END CONTRACT
# ==========================================================

def test_pipeline_result_contract():

    result = run_alert_pipeline(
        {
            'status': 'unreliable',
            'reliability_level': 'low',
            'target_name': 'Target_Test',
        }
    )

    required_fields = {
        'status',
        'target_name',
        'monitoring_result',
        'alerts',
        'recommendations',
        'decision',
    }

    assert required_fields.issubset(
        result.keys()
    )


# ==========================================================
# NESTED CONTRACT
# ==========================================================

def test_pipeline_preserves_nested_layer_contracts():

    result = run_alert_pipeline(
        {
            'status': 'unreliable',
            'reliability_level': 'low',
            'target_name': 'Target_Test',
        }
    )

    alert_fields = {
        'status',
        'alert_count',
        'alerts',
        'target_name',
    }

    recommendation_fields = {
        'status',
        'recommendation_count',
        'recommendations',
    }

    decision_fields = {
        'status',
        'target_name',
        'alerts',
        'primary_action',
        'priority',
        'recommendations',
        'decisions_by_target',
    }

    assert alert_fields.issubset(
        result['alerts'].keys()
    )

    assert recommendation_fields.issubset(
        result['recommendations'].keys()
    )

    assert decision_fields.issubset(
        result['decision'].keys()
    )


# ==========================================================
# HELPER: HAS ALERTS
# ==========================================================

def test_has_alerts_helper():

    result = run_alert_pipeline(
        {
            'status': 'unreliable',
            'reliability_level': 'low',
            'target_name': 'Target_Test',
        }
    )

    assert has_alerts(result) is True


def test_has_alerts_returns_false_when_no_alerts():

    result = run_alert_pipeline(
        {
            'status': 'reliable',
            'reliability_level': 'high',
            'target_name': 'Target_Test',
        }
    )

    assert has_alerts(result) is False


# ==========================================================
# HELPER: HAS OPERATIONAL ACTION
# ==========================================================

def test_has_operational_action():

    result = run_alert_pipeline(
        {
            'status': 'unreliable',
            'reliability_level': 'low',
            'target_name': 'Target_Test',
        }
    )

    assert (
        has_operational_action(result)
        is True
    )


def test_has_operational_action_returns_false_when_none():

    result = run_alert_pipeline(
        {
            'status': 'reliable',
            'reliability_level': 'high',
            'target_name': 'Target_Test',
        }
    )

    assert (
        has_operational_action(result)
        is False
    )


# ==========================================================
# VALIDATION
# ==========================================================

def test_pipeline_requires_monitoring_result():

    try:
        run_alert_pipeline(None)
        assert False
    except ValueError:
        assert True


def test_pipeline_rejects_non_dictionary_input():

    try:
        run_alert_pipeline([])
        assert False
    except ValueError:
        assert True


# ==========================================================
# MAIN
# ==========================================================

if __name__ == '__main__':

    print(
        '========== ALERT PIPELINE TEST SUITE =========='
    )

    test_pipeline_no_alerts()

    test_pipeline_unreliable_model()

    test_pipeline_low_reliability()

    test_pipeline_high_error()

    test_pipeline_reliability_decline()

    test_pipeline_insufficient_data()

    test_pipeline_critical_alert_overrides_weaker_actions()

    test_pipeline_preserves_target()

    test_pipeline_preserves_target_isolation()

    test_pipeline_unknown_conditions_remain_safe()

    test_pipeline_result_contract()

    test_pipeline_preserves_nested_layer_contracts()

    test_has_alerts_helper()

    test_has_alerts_returns_false_when_no_alerts()

    test_has_operational_action()

    test_has_operational_action_returns_false_when_none()

    test_pipeline_requires_monitoring_result()

    test_pipeline_rejects_non_dictionary_input()

    print(
        'ALL ALERT PIPELINE TESTS PASSED'
    )