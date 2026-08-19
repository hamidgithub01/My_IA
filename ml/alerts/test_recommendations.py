from ml.alerts.recommendations import (
    RECOMMENDATION_VALID,
    RECOMMENDATION_NONE,
    RECOMMENDATION_RETRAIN_MODEL,
    RECOMMENDATION_COLLECT_MORE_DATA,
    RECOMMENDATION_REVIEW_MODEL,
    RECOMMENDATION_MONITOR_CLOSELY,
    PRIORITY_CRITICAL,
    PRIORITY_HIGH,
    PRIORITY_MEDIUM,
    generate_recommendations,
    analyze_alerts_and_recommendations,
)

from ml.prediction.reliability_monitoring import (
    evaluate_reliability,
)

from ml.alerts.alerts import (
    analyze_alerts,
)



# ==========================================================
# NO RECOMMENDATIONS
# ==========================================================

def test_no_recommendations():

    result = generate_recommendations(
        {
            'status': 'none',
            'alert_count': 0,
            'alerts': [],
        }
    )

    assert (
        result['status']
        == RECOMMENDATION_NONE
    )

    assert (
        result['recommendation_count']
        == 0
    )

    assert (
        result['recommendations']
        == []
    )


# ==========================================================
# UNRELIABLE MODEL
# ==========================================================

def test_unreliable_model():

    result = generate_recommendations(
        {
            'status': 'valid',
            'alert_count': 1,
            'alerts': [
                {
                    'alert_type':
                        'unreliable',

                    'severity':
                        'critical',

                    'target_name':
                        'Target_Test',
                }
            ],
        }
    )

    assert (
        result['status']
        == RECOMMENDATION_VALID
    )

    assert (
        result['recommendation_count']
        == 1
    )

    recommendation = (
        result['recommendations'][0]
    )

    assert (
        recommendation[
            'recommendation_type'
        ]
        == RECOMMENDATION_RETRAIN_MODEL
    )

    assert (
        recommendation['priority']
        == PRIORITY_CRITICAL
    )


# ==========================================================
# LOW RELIABILITY
# ==========================================================

def test_low_reliability():

    result = generate_recommendations(
        {
            'status': 'valid',
            'alert_count': 1,
            'alerts': [
                {
                    'alert_type':
                        'low_reliability',

                    'severity':
                        'high',

                    'target_name':
                        'Target_Test',
                }
            ],
        }
    )

    recommendation = (
        result['recommendations'][0]
    )

    assert (
        recommendation[
            'recommendation_type'
        ]
        == RECOMMENDATION_REVIEW_MODEL
    )

    assert (
        recommendation['priority']
        == PRIORITY_HIGH
    )


# ==========================================================
# HIGH ERROR
# ==========================================================

def test_high_error():

    result = generate_recommendations(
        {
            'status': 'valid',
            'alert_count': 1,
            'alerts': [
                {
                    'alert_type':
                        'high_error',

                    'severity':
                        'high',

                    'target_name':
                        'Target_Test',
                }
            ],
        }
    )

    recommendation = (
        result['recommendations'][0]
    )

    assert (
        recommendation[
            'recommendation_type'
        ]
        == RECOMMENDATION_REVIEW_MODEL
    )

    assert (
        recommendation['priority']
        == PRIORITY_HIGH
    )


# ==========================================================
# RELIABILITY DECLINE
# ==========================================================

def test_reliability_decline():

    result = generate_recommendations(
        {
            'status': 'valid',
            'alert_count': 1,
            'alerts': [
                {
                    'alert_type':
                        'reliability_decline',

                    'severity':
                        'warning',

                    'target_name':
                        'Target_Test',
                }
            ],
        }
    )

    recommendation = (
        result['recommendations'][0]
    )

    assert (
        recommendation[
            'recommendation_type'
        ]
        == RECOMMENDATION_MONITOR_CLOSELY
    )

    assert (
        recommendation['priority']
        == PRIORITY_MEDIUM
    )


# ==========================================================
# INSUFFICIENT DATA
# ==========================================================

def test_insufficient_data():

    result = generate_recommendations(
        {
            'status': 'valid',
            'alert_count': 1,
            'alerts': [
                {
                    'alert_type':
                        'insufficient_data',

                    'severity':
                        'warning',

                    'target_name':
                        'Target_Test',
                }
            ],
        }
    )

    recommendation = (
        result['recommendations'][0]
    )

    assert (
        recommendation[
            'recommendation_type'
        ]
        == RECOMMENDATION_COLLECT_MORE_DATA
    )

    assert (
        recommendation['priority']
        == PRIORITY_MEDIUM
    )


# ==========================================================
# UNKNOWN ALERT
# ==========================================================

def test_unknown_alert_is_ignored():

    result = generate_recommendations(
        {
            'status': 'valid',
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
    )

    assert (
        result['status']
        == RECOMMENDATION_NONE
    )

    assert (
        result['recommendation_count']
        == 0
    )


# ==========================================================
# DEDUPLICATION
# ==========================================================

def test_recommendation_deduplication():

    result = generate_recommendations(
        {
            'status': 'valid',
            'alert_count': 2,
            'alerts': [

                {
                    'alert_type':
                        'low_reliability',

                    'severity':
                        'high',

                    'target_name':
                        'Target_Test',
                },

                {
                    'alert_type':
                        'low_reliability',

                    'severity':
                        'high',

                    'target_name':
                        'Target_Test',
                },

            ],
        }
    )

    assert (
        result['recommendation_count']
        == 1
    )


# ==========================================================
# DIFFERENT TARGETS
# ==========================================================

def test_same_recommendation_different_targets():

    result = generate_recommendations(
        {
            'status': 'valid',
            'alert_count': 2,
            'alerts': [

                {
                    'alert_type':
                        'low_reliability',

                    'severity':
                        'high',

                    'target_name':
                        'Target_A',
                },

                {
                    'alert_type':
                        'low_reliability',

                    'severity':
                        'high',

                    'target_name':
                        'Target_B',
                },

            ],
        }
    )

    assert (
        result['recommendation_count']
        == 2
    )


# ==========================================================
# UNIFIED RESULT
# ==========================================================

def test_unified_alert_recommendation_result():

    result = (
        analyze_alerts_and_recommendations(
            {
                'status': 'valid',

                'alert_count': 2,

                'alerts': [

                    {
                        'alert_type':
                            'low_reliability',

                        'severity':
                            'high',

                        'target_name':
                            'Target_Test',
                    },

                    {
                        'alert_type':
                            'high_error',

                        'severity':
                            'high',

                        'target_name':
                            'Target_Test',
                    },

                ],
            }
        )
    )

    assert (
        result['alert_count']
        == 2
    )

    assert (
        len(result['alerts'])
        == 2
    )

    assert (
        result['recommendation_count']
        == 1
    )

    assert (
        len(
            result['recommendations']
        )
        == 1
    )


# ==========================================================
# INVALID INPUT
# ==========================================================

def test_invalid_inputs():

    try:

        generate_recommendations(
            None
        )

        assert False

    except ValueError:

        pass

    try:

        generate_recommendations(
            []
        )

        assert False

    except ValueError:

        pass

    try:

        generate_recommendations(
            {
                'status':
                    'valid',
            }
        )

        assert False

    except ValueError:

        pass


# ==========================================================
# PREDICTION → ALERT → RECOMMENDATION CONTRACT
# ==========================================================

def test_prediction_monitoring_alert_recommendation_flow():

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

    alert_result = analyze_alerts(
        {
            'target_name':
                prediction_result[
                    'target_name'
                ],

            'reliability_level':
                monitoring_result[
                    'reliability'
                ],
        }
    )

    assert isinstance(
        alert_result,
        dict,
    )

    recommendation_result = (
        generate_recommendations(
            alert_result
        )
    )

    assert isinstance(
        recommendation_result,
        dict,
    )

    assert 'status' in (
        recommendation_result
    )

    assert 'recommendation_count' in (
        recommendation_result
    )

    assert 'recommendations' in (
        recommendation_result
    )

    assert (
        recommendation_result[
            'recommendation_count'
        ]
        == len(
            recommendation_result[
                'recommendations'
            ]
        )
    )


# ==========================================================
# MAIN
# ==========================================================

if __name__ == '__main__':

    print(
        '========== RECOMMENDATION TEST SUITE =========='
    )

    test_no_recommendations()

    test_unreliable_model()

    test_low_reliability()

    test_high_error()

    test_reliability_decline()

    test_insufficient_data()

    test_unknown_alert_is_ignored()

    test_recommendation_deduplication()

    test_same_recommendation_different_targets()

    test_unified_alert_recommendation_result()

    test_invalid_inputs()

    print(
        'ALL RECOMMENDATION TESTS PASSED'
    )

# ==========================================================
# RECOMMENDATION RESULT CONTRACT
# ==========================================================

def test_recommendation_result_contract():

    result = generate_recommendations(
        {
            'status': 'valid',

            'alert_count': 1,

            'alerts': [
                {
                    'alert_type':
                        'low_reliability',

                    'severity':
                        'high',

                    'target_name':
                        'Target_Contract',
                }
            ],
        }
    )

    assert isinstance(
        result,
        dict,
    )

    assert 'status' in result
    assert 'recommendation_count' in result
    assert 'recommendations' in result

    assert (
        result['recommendation_count']
        == len(
            result['recommendations']
        )
    )


# ==========================================================
# RECOMMENDATION OBJECT CONTRACT
# ==========================================================

def test_recommendation_object_contract():

    result = generate_recommendations(
        {
            'status': 'valid',

            'alert_count': 1,

            'alerts': [
                {
                    'alert_type':
                        'low_reliability',

                    'severity':
                        'high',

                    'target_name':
                        'Target_Contract',
                }
            ],
        }
    )

    assert result['recommendations']

    recommendation = (
        result['recommendations'][0]
    )

    required_fields = {
        'recommendation_type',
        'priority',
        'message',
        'reason',
        'target_name',
        'source_alert_type',
    }

    assert required_fields.issubset(
        recommendation.keys()
    )


# ==========================================================
# RECOMMENDATION TARGET IS PRESERVED
# ==========================================================

def test_recommendation_target_is_preserved():

    result = generate_recommendations(
        {
            'status': 'valid',

            'alert_count': 1,

            'alerts': [
                {
                    'alert_type':
                        'low_reliability',

                    'severity':
                        'high',

                    'target_name':
                        'Target_Contract',
                }
            ],
        }
    )

    recommendation = (
        result['recommendations'][0]
    )

    assert (
        recommendation['target_name']
        == 'Target_Contract'
    )


# ==========================================================
# SOURCE ALERT TYPE IS PRESERVED
# ==========================================================

def test_recommendation_source_alert_is_preserved():

    result = generate_recommendations(
        {
            'status': 'valid',

            'alert_count': 1,

            'alerts': [
                {
                    'alert_type':
                        'low_reliability',

                    'severity':
                        'high',

                    'target_name':
                        'Target_Contract',
                }
            ],
        }
    )

    recommendation = (
        result['recommendations'][0]
    )

    assert (
        recommendation[
            'source_alert_type'
        ]
        == 'low_reliability'
    )


# ==========================================================
# RECOMMENDATION METADATA CONTRACT
# ==========================================================

def test_all_recommendations_have_required_fields():

    result = generate_recommendations(
        {
            'status': 'valid',

            'alert_count': 4,

            'alerts': [

                {
                    'alert_type':
                        'unreliable',

                    'severity':
                        'critical',

                    'target_name':
                        'Target_Contract',
                },

                {
                    'alert_type':
                        'low_reliability',

                    'severity':
                        'high',

                    'target_name':
                        'Target_Contract',
                },

                {
                    'alert_type':
                        'reliability_decline',

                    'severity':
                        'warning',

                    'target_name':
                        'Target_Contract',
                },

                {
                    'alert_type':
                        'insufficient_data',

                    'severity':
                        'warning',

                    'target_name':
                        'Target_Contract',
                },
            ],
        }
    )

    required_fields = {
        'recommendation_type',
        'priority',
        'message',
        'reason',
        'target_name',
        'source_alert_type',
    }

    for recommendation in (
        result['recommendations']
    ):

        assert required_fields.issubset(
            recommendation.keys()
        )

    assert (
        result['recommendation_count']
        == len(
            result['recommendations']
        )
    )


# ==========================================================
# UNIFIED RESULT CONTRACT
# ==========================================================

def test_unified_result_contract():

    result = (
        analyze_alerts_and_recommendations(
            {
                'status':
                    'valid',

                'alert_count':
                    2,

                'alerts': [

                    {
                        'alert_type':
                            'low_reliability',

                        'severity':
                            'high',

                        'target_name':
                            'Target_Contract',
                    },

                    {
                        'alert_type':
                            'high_error',

                        'severity':
                            'high',

                        'target_name':
                            'Target_Contract',
                    },
                ],
            }
        )
    )

    required_fields = {
        'alert_status',
        'alert_count',
        'alerts',
        'recommendation_status',
        'recommendation_count',
        'recommendations',
    }

    assert required_fields.issubset(
        result.keys()
    )

    assert (
        result['alert_count']
        == len(result['alerts'])
    )

    assert (
        result['recommendation_count']
        == len(
            result['recommendations']
        )
    )


# ==========================================================
# TARGET ISOLATION
# ==========================================================

def test_recommendations_are_isolated_by_target():

    result = generate_recommendations(
        {
            'status': 'valid',

            'alert_count': 2,

            'alerts': [

                {
                    'alert_type':
                        'low_reliability',

                    'severity':
                        'high',

                    'target_name':
                        'Target_A',
                },

                {
                    'alert_type':
                        'low_reliability',

                    'severity':
                        'high',

                    'target_name':
                        'Target_B',
                },
            ],
        }
    )

    assert (
        result['recommendation_count']
        == 2
    )

    targets = {
        recommendation[
            'target_name'
        ]
        for recommendation in
        result['recommendations']
    }

    assert targets == {
        'Target_A',
        'Target_B',
    }


# ==========================================================
# UNKNOWN ALERT CONTRACT
# ==========================================================

def test_unknown_alert_does_not_break_contract():

    result = generate_recommendations(
        {
            'status': 'valid',

            'alert_count': 1,

            'alerts': [
                {
                    'alert_type':
                        'future_unknown_alert',

                    'severity':
                        'warning',

                    'target_name':
                        'Target_Contract',
                }
            ],
        }
    )

    assert (
        result['status']
        == RECOMMENDATION_NONE
    )

    assert (
        result['recommendation_count']
        == 0
    )

    assert (
        result['recommendations']
        == []
    )