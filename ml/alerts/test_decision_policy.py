
from ml.alerts.decision_policy import (
    DECISION_VALID,
    DECISION_NONE,
    resolve_decision,
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

def test_no_alerts_produce_no_decision():

    result = resolve_decision(
        {
            'status': 'none',
            'alert_count': 0,
            'alerts': [],
        }
    )

    assert result['status'] == DECISION_NONE

    assert result['primary_action'] is None

    assert result['priority'] is None

    assert result['recommendations'] == []


# ==========================================================
# UNRELIABLE MODEL
# ==========================================================

def test_unreliable_model_has_critical_retrain_decision():

    result = resolve_decision(
        {
            'status': 'valid',
            'alert_count': 1,
            'alerts': [
                {
                    'alert_type': 'unreliable',
                    'severity': 'critical',
                    'target_name': 'Target_Test',
                }
            ],
        }
    )

    assert result['status'] == DECISION_VALID

    assert result['target_name'] == 'Target_Test'

    assert (
        result['primary_action']
        == RECOMMENDATION_RETRAIN_MODEL
    )

    assert (
        result['priority']
        == PRIORITY_CRITICAL
    )


# ==========================================================
# UNRELIABLE OVERRIDES WEAKER ACTIONS
# ==========================================================

def test_critical_retrain_suppresses_weaker_actions():

    result = resolve_decision(
        {
            'status': 'valid',
            'alert_count': 4,
            'alerts': [

                {
                    'alert_type': 'unreliable',
                    'severity': 'critical',
                    'target_name': 'Target_Test',
                },

                {
                    'alert_type': 'low_reliability',
                    'severity': 'high',
                    'target_name': 'Target_Test',
                },

                {
                    'alert_type': 'high_error',
                    'severity': 'high',
                    'target_name': 'Target_Test',
                },

                {
                    'alert_type': 'reliability_decline',
                    'severity': 'warning',
                    'target_name': 'Target_Test',
                },

            ],
        }
    )

    assert (
        result['primary_action']
        == RECOMMENDATION_RETRAIN_MODEL
    )

    assert (
        result['priority']
        == PRIORITY_CRITICAL
    )

    actions = {
        recommendation['recommendation_type']
        for recommendation
        in result['recommendations']
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
# REVIEW MODEL
# ==========================================================

def test_review_model_is_selected_for_high_risk_review_alerts():

    result = resolve_decision(
        {
            'status': 'valid',
            'alert_count': 2,
            'alerts': [

                {
                    'alert_type': 'low_reliability',
                    'severity': 'high',
                    'target_name': 'Target_Test',
                },

                {
                    'alert_type': 'high_error',
                    'severity': 'high',
                    'target_name': 'Target_Test',
                },

            ],
        }
    )

    assert (
        result['primary_action']
        == RECOMMENDATION_REVIEW_MODEL
    )

    assert (
        result['priority']
        == PRIORITY_HIGH
    )

    assert (
        len(result['recommendations'])
        == 1
    )


# ==========================================================
# MONITOR CLOSELY
# ==========================================================

def test_reliability_decline_selects_monitor_closely():

    result = resolve_decision(
        {
            'status': 'valid',
            'alert_count': 1,
            'alerts': [
                {
                    'alert_type': 'reliability_decline',
                    'severity': 'warning',
                    'target_name': 'Target_Test',
                }
            ],
        }
    )

    assert (
        result['primary_action']
        == RECOMMENDATION_MONITOR_CLOSELY
    )

    assert (
        result['priority']
        == PRIORITY_MEDIUM
    )


# ==========================================================
# COLLECT MORE DATA
# ==========================================================

def test_insufficient_data_selects_collect_more_data():

    result = resolve_decision(
        {
            'status': 'valid',
            'alert_count': 1,
            'alerts': [
                {
                    'alert_type': 'insufficient_data',
                    'severity': 'warning',
                    'target_name': 'Target_Test',
                }
            ],
        }
    )

    assert (
        result['primary_action']
        == RECOMMENDATION_COLLECT_MORE_DATA
    )

    assert (
        result['priority']
        == PRIORITY_MEDIUM
    )


# ==========================================================
# TARGET ISOLATION
# ==========================================================

def test_different_targets_have_independent_decisions():

    result = resolve_decision(
        {
            'status': 'valid',
            'alert_count': 2,
            'alerts': [

                {
                    'alert_type': 'unreliable',
                    'severity': 'critical',
                    'target_name': 'Target_A',
                },

                {
                    'alert_type': 'reliability_decline',
                    'severity': 'warning',
                    'target_name': 'Target_B',
                },

            ],
        }
    )

    decisions = result['decisions_by_target']

    assert (
        decisions['Target_A']['primary_action']
        == RECOMMENDATION_RETRAIN_MODEL
    )

    assert (
        decisions['Target_A']['priority']
        == PRIORITY_CRITICAL
    )

    assert (
        decisions['Target_B']['primary_action']
        == RECOMMENDATION_MONITOR_CLOSELY
    )

    assert (
        decisions['Target_B']['priority']
        == PRIORITY_MEDIUM
    )


# ==========================================================
# UNKNOWN ALERT
# ==========================================================

def test_unknown_alert_does_not_break_decision_contract():

    result = resolve_decision(
        {
            'status': 'valid',
            'alert_count': 1,
            'alerts': [
                {
                    'alert_type': 'future_unknown_alert',
                    'severity': 'warning',
                    'target_name': 'Target_Test',
                }
            ],
        }
    )

    assert result['status'] == DECISION_NONE

    assert result['primary_action'] is None

    assert result['priority'] is None

    assert result['recommendations'] == []


# ==========================================================
# ALERTS ARE PRESERVED
# ==========================================================

def test_decision_preserves_original_alerts():

    alerts = [
        {
            'alert_type': 'low_reliability',
            'severity': 'high',
            'target_name': 'Target_Test',
        },
        {
            'alert_type': 'high_error',
            'severity': 'high',
            'target_name': 'Target_Test',
        },
    ]

    result = resolve_decision(
        {
            'status': 'valid',
            'alert_count': 2,
            'alerts': alerts,
        }
    )

    assert result['alerts'] == alerts


# ==========================================================
# NO AUTOMATIC CONTINUE MONITORING
# ==========================================================

def test_no_alert_does_not_create_continue_monitoring():

    result = resolve_decision(
        {
            'status': 'none',
            'alert_count': 0,
            'alerts': [],
        }
    )

    actions = {
        recommendation['recommendation_type']
        for recommendation
        in result['recommendations']
    }

    assert actions == set()


# ==========================================================
# CONTRACT
# ==========================================================

def test_decision_result_contract():

    result = resolve_decision(
        {
            'status': 'valid',
            'alert_count': 1,
            'alerts': [
                {
                    'alert_type': 'low_reliability',
                    'severity': 'high',
                    'target_name': 'Target_Test',
                }
            ],
        }
    )

    required_fields = {
        'status',
        'target_name',
        'alerts',
        'primary_action',
        'priority',
        'recommendations',
        'decisions_by_target',
    }

    assert required_fields.issubset(
        result.keys()
    )


# ==========================================================
# MAIN
# ==========================================================

if __name__ == '__main__':

    print(
        '========== DECISION POLICY TEST SUITE =========='
    )

    test_no_alerts_produce_no_decision()

    test_unreliable_model_has_critical_retrain_decision()

    test_critical_retrain_suppresses_weaker_actions()

    test_review_model_is_selected_for_high_risk_review_alerts()

    test_reliability_decline_selects_monitor_closely()

    test_insufficient_data_selects_collect_more_data()

    test_different_targets_have_independent_decisions()

    test_unknown_alert_does_not_break_decision_contract()

    test_decision_preserves_original_alerts()

    test_no_alert_does_not_create_continue_monitoring()

    test_decision_result_contract()

    print(
        'ALL DECISION POLICY TESTS PASSED'
    )