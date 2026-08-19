from ml.alerts.alerts import (
    ALERT_VALID,
    ALERT_NONE,
    ALERT_LOW_RELIABILITY,
    ALERT_RELIABILITY_DECLINE,
    ALERT_HIGH_ERROR,
    ALERT_INSUFFICIENT_DATA,
    ALERT_UNRELIABLE,
    SEVERITY_WARNING,
    SEVERITY_HIGH,
    SEVERITY_CRITICAL,
    analyze_alerts,
    has_alerts,
)

from ml.prediction.reliability_monitoring import (
    evaluate_reliability,
)


# ==========================================================
# NO ALERT
# ==========================================================

def test_no_alert():

    result = analyze_alerts(
        {
            'target_name':
                'Target_Expense_Total_1D',

            'reliability_level':
                'high',

            'quality_score':
                0.95,
        }
    )

    assert (
        result['status']
        == ALERT_NONE
    )

    assert result['alert_count'] == 0

    assert result['alerts'] == []

    assert (
        has_alerts(result)
        is False
    )


# ==========================================================
# LOW RELIABILITY
# ==========================================================

def test_low_reliability_alert():

    result = analyze_alerts(
        {
            'target_name':
                'Target_Expense_Total_1D',

            'reliability_level':
                'low',
        }
    )

    assert (
        result['status']
        == ALERT_VALID
    )

    assert result['alert_count'] == 1

    alert = result['alerts'][0]

    assert (
        alert['alert_type']
        == ALERT_LOW_RELIABILITY
    )

    assert (
        alert['severity']
        == SEVERITY_HIGH
    )

    assert (
        has_alerts(result)
        is True
    )


# ==========================================================
# UNKNOWN RELIABILITY
# ==========================================================

def test_unknown_reliability():

    result = analyze_alerts(
        {
            'target_name':
                'Target_Test',

            'reliability_level':
                'unknown',
        }
    )

    assert (
        result['alert_count']
        == 1
    )

    alert = result['alerts'][0]

    assert (
        alert['alert_type']
        == ALERT_INSUFFICIENT_DATA
    )

    assert (
        alert['severity']
        == SEVERITY_WARNING
    )


# ==========================================================
# UNRELIABLE STATUS
# ==========================================================

def test_unreliable_status():

    result = analyze_alerts(
        {
            'target_name':
                'Target_Test',

            'status':
                'unreliable',

            'reliability_level':
                'low',
        }
    )

    assert result['alert_count'] == 2

    alert_types = {
        alert['alert_type']
        for alert in result['alerts']
    }

    assert (
        ALERT_UNRELIABLE
        in alert_types
    )

    assert (
        ALERT_LOW_RELIABILITY
        in alert_types
    )

    critical_alerts = [
        alert
        for alert in result['alerts']
        if alert['severity']
        == SEVERITY_CRITICAL
    ]

    assert len(
        critical_alerts
    ) == 1


# ==========================================================
# ERROR RATE
# ==========================================================

def test_high_error_rate():

    result = analyze_alerts(
        {
            'target_name':
                'Target_Test',

            'reliability_level':
                'medium',

            'error_rate':
                0.40,
        },
        maximum_error_rate=0.25,
    )

    assert result['alert_count'] == 1

    alert = result['alerts'][0]

    assert (
        alert['alert_type']
        == ALERT_HIGH_ERROR
    )

    assert (
        alert['severity']
        == SEVERITY_HIGH
    )

    assert (
        alert['current_value']
        == 0.40
    )

    assert (
        alert['threshold']
        == 0.25
    )


# ==========================================================
# ACCEPTABLE ERROR RATE
# ==========================================================

def test_acceptable_error_rate():

    result = analyze_alerts(
        {
            'target_name':
                'Target_Test',

            'reliability_level':
                'medium',

            'error_rate':
                0.20,
        },
        maximum_error_rate=0.25,
    )

    assert result['alert_count'] == 0


# ==========================================================
# RELIABILITY DECLINE
# ==========================================================

def test_reliability_decline():

    result = analyze_alerts(
        {
            'target_name':
                'Target_Test',

            'quality_score':
                0.60,

            'previous_quality_score':
                0.85,

            'reliability_level':
                'medium',
        },
        minimum_reliability_decline=0.20,
    )

    assert result['alert_count'] == 1

    alert = result['alerts'][0]

    assert (
        alert['alert_type']
        == ALERT_RELIABILITY_DECLINE
    )

    assert (
        alert['severity']
        == SEVERITY_WARNING
    )


# ==========================================================
# BELOW DECLINE THRESHOLD
# ==========================================================

def test_small_reliability_decline():

    result = analyze_alerts(
        {
            'target_name':
                'Target_Test',

            'quality_score':
                0.80,

            'previous_quality_score':
                0.85,

            'reliability_level':
                'high',
        },
        minimum_reliability_decline=0.20,
    )

    assert result['alert_count'] == 0


# ==========================================================
# MULTIPLE ALERTS
# ==========================================================

def test_multiple_alerts():

    result = analyze_alerts(
        {
            'target_name':
                'Target_Test',

            'status':
                'unreliable',

            'reliability_level':
                'low',

            'error_rate':
                0.50,

            'quality_score':
                0.40,

            'previous_quality_score':
                0.90,
        },
        maximum_error_rate=0.25,
        minimum_reliability_decline=0.20,
    )

    assert (
        result['alert_count']
        == 4
    )

    assert (
        has_alerts(result)
        is True
    )


# ==========================================================
# INVALID INPUT
# ==========================================================

def test_invalid_inputs():

    try:

        analyze_alerts(
            None
        )

        assert False

    except ValueError:

        pass

    try:

        analyze_alerts(
            []
        )

        assert False

    except ValueError:

        pass

    try:

        analyze_alerts(
            {
                'error_rate':
                    0.5,
            },
            maximum_error_rate=1.5,
        )

        assert False

    except ValueError:

        pass

    try:

        analyze_alerts(
            {
                'quality_score':
                    0.5,
            },
            minimum_reliability_decline=-0.1,
        )

        assert False

    except ValueError:

        pass


# ==========================================================
# PREDICTION MONITORING → ALERT CONTRACT
# ==========================================================

def test_prediction_monitoring_result_can_feed_alerts():

    prediction_result = {
        'prediction': 100.0,
        'target_name': 'Target_Test',
        'target_task': 'regression',
    }

    monitoring_result = evaluate_reliability(
        prediction_result,
        actual_value=150.0,
    )

    assert (
        monitoring_result['status']
        == 'evaluated'
    )

    assert (
        monitoring_result[
            'reliability_available'
        ]
        is True
    )

    monitoring_record = (
        monitoring_result[
            'monitoring_record'
        ]
    )

    alert_input = {
        'target_name':
            prediction_result[
                'target_name'
            ],

        'reliability_level':
            monitoring_result[
                'reliability'
            ],
    }

    alert_result = analyze_alerts(
        alert_input
    )

    assert isinstance(
        alert_result,
        dict,
    )

    assert 'status' in alert_result
    assert 'alert_count' in alert_result
    assert 'alerts' in alert_result

    assert (
        alert_result['alert_count']
        == len(alert_result['alerts'])
    )

# ==========================================================
# MAIN
# ==========================================================

if __name__ == '__main__':

    print(
        '========== ALERT TEST SUITE =========='
    )

    test_no_alert()

    test_low_reliability_alert()

    test_unknown_reliability()

    test_unreliable_status()

    test_high_error_rate()

    test_acceptable_error_rate()

    test_reliability_decline()

    test_small_reliability_decline()

    test_multiple_alerts()

    test_invalid_inputs()

    print(
        'ALL ALERT TESTS PASSED'
    )

# ==========================================================
# ALERT RESULT CONTRACT
# ==========================================================

def test_alert_result_contract():

    result = analyze_alerts(
        {
            'target_name':
                'Target_Contract',

            'reliability_level':
                'low',
        }
    )

    assert isinstance(
        result,
        dict,
    )

    assert 'status' in result
    assert 'alert_count' in result
    assert 'alerts' in result

    assert result['alert_count'] == len(
        result['alerts']
    )


# ==========================================================
# ALERT OBJECT CONTRACT
# ==========================================================

def test_alert_object_contract():

    result = analyze_alerts(
        {
            'target_name':
                'Target_Contract',

            'reliability_level':
                'low',
        }
    )

    assert result['alerts']

    alert = result['alerts'][0]

    required_fields = {
        'alert_type',
        'severity',
        'message',
        'reason',
        'target_name',
    }

    assert required_fields.issubset(
        alert.keys()
    )


# ==========================================================
# ALERT TARGET IS PRESERVED
# ==========================================================

def test_alert_target_is_preserved():

    result = analyze_alerts(
        {
            'target_name':
                'Target_Contract',

            'reliability_level':
                'low',
        }
    )

    alert = result['alerts'][0]

    assert (
        alert['target_name']
        == 'Target_Contract'
    )


# ==========================================================
# NO ALERT RESULT CONTRACT
# ==========================================================

def test_no_alert_result_contract():

    result = analyze_alerts(
        {
            'target_name':
                'Target_Contract',

            'reliability_level':
                'high',

            'quality_score':
                0.95,
        }
    )

    assert isinstance(
        result,
        dict,
    )

    assert (
        result['status']
        == ALERT_NONE
    )

    assert (
        result['alert_count']
        == 0
    )

    assert (
        result['alerts']
        == []
    )

    assert (
        result['alert_count']
        == len(result['alerts'])
    )


# ==========================================================
# MULTIPLE ALERTS CONTRACT
# ==========================================================

def test_multiple_alerts_contract():

    result = analyze_alerts(
        {
            'target_name':
                'Target_Contract',

            'status':
                'unreliable',

            'reliability_level':
                'low',

            'error_rate':
                0.50,

            'quality_score':
                0.40,

            'previous_quality_score':
                0.90,
        },
        maximum_error_rate=0.25,
        minimum_reliability_decline=0.20,
    )

    assert (
        result['alert_count']
        == len(result['alerts'])
    )

    for alert in result['alerts']:

        assert isinstance(
            alert,
            dict,
        )

        required_fields = {
            'alert_type',
            'severity',
            'message',
            'reason',
            'target_name',
        }

        assert required_fields.issubset(
            alert.keys()
        )