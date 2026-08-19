from ml.analysis.analyzer import (
    ANALYSIS_VALID,
    analyze_predictions,
    analyze_errors,
    analyze_reliability,
    analyze_monitoring,
    analyze_alerts,
    analyze_recommendations,
    build_executive_summary,
    analyze_system,
)


# ==========================================================
# PREDICTION ANALYSIS
# ==========================================================

def test_prediction_analysis():

    result = analyze_predictions(
        {
            'target_name':
                'Target_Expense_Total_1D',

            'target_task':
                'regression',

            'predictions':
                [100, 200, 300],

            'confidence':
                0.85,
        }
    )

    assert (
        result['prediction_count']
        == 3
    )

    assert (
        result['has_predictions']
        is True
    )

    assert (
        result['numeric_predictions']
        is True
    )

    assert (
        result['minimum_prediction']
        == 100.0
    )

    assert (
        result['maximum_prediction']
        == 300.0
    )

    assert (
        result['mean_prediction']
        == 200.0
    )

    assert (
        result['confidence']
        == 0.85
    )


# ==========================================================
# EMPTY PREDICTIONS
# ==========================================================

def test_empty_predictions():

    result = analyze_predictions(
        {
            'target_name':
                'Target_Test',

            'target_task':
                'regression',

            'predictions':
                [],
        }
    )

    assert (
        result['prediction_count']
        == 0
    )

    assert (
        result['has_predictions']
        is False
    )


# ==========================================================
# REGRESSION ERROR ANALYSIS
# ==========================================================

def test_regression_error_analysis():

    result = analyze_errors(
        {
            'target_task':
                'regression',

            'actual_values':
                [100, 200, 300],

            'predicted_values':
                [110, 180, 300],

            'metrics':
                {
                    'mae':
                        10.0,
                },
        }
    )

    assert (
        result['sample_count']
        == 3
    )

    assert (
        result['mean_error']
        == -10.0 / 3.0
    )

    assert (
        result['mean_absolute_error']
        == 10.0
    )

    assert (
        result['over_predictions']
        == 1
    )

    assert (
        result['under_predictions']
        == 1
    )

    assert (
        result['exact_predictions']
        == 1
    )


# ==========================================================
# BINARY CLASSIFICATION ERROR
# ==========================================================

def test_binary_classification_error_analysis():

    result = analyze_errors(
        {
            'target_task':
                'classification',

            'actual_values':
                [0, 1, 1, 0],

            'predicted_values':
                [0, 1, 0, 0],
        }
    )

    assert (
        result['sample_count']
        == 4
    )

    assert (
        result['correct_predictions']
        == 3
    )

    assert (
        result['incorrect_predictions']
        == 1
    )

    assert (
        result['accuracy']
        == 0.75
    )

    assert (
        result['error_rate']
        == 0.25
    )


# ==========================================================
# MULTICLASS ERROR
# ==========================================================

def test_multiclass_error_analysis():

    result = analyze_errors(
        {
            'target_task':
                'categorical',

            'actual_values':
                [0, 1, 2, 0, 1, 2],

            'predicted_values':
                [0, 1, 1, 0, 2, 2],
        }
    )

    assert (
        result['correct_predictions']
        == 4
    )

    assert (
        result['incorrect_predictions']
        == 2
    )

    assert (
        result['accuracy']
        == 4.0 / 6.0
    )


# ==========================================================
# RELIABILITY
# ==========================================================

def test_reliability_analysis():

    result = analyze_reliability(
        {
            'status':
                'valid',

            'reliability_level':
                'high',

            'quality_score':
                0.91,

            'sample_count':
                50,
        }
    )

    assert (
        result['available']
        is True
    )

    assert (
        result['reliability_level']
        == 'high'
    )

    assert (
        result['quality_score']
        == 0.91
    )

    assert (
        result['sample_count']
        == 50
    )


# ==========================================================
# MISSING RELIABILITY
# ==========================================================

def test_missing_reliability():

    result = analyze_reliability(
        None
    )

    assert (
        result['available']
        is False
    )

    assert (
        result['reliability_level']
        is None
    )


# ==========================================================
# MONITORING
# ==========================================================

def test_monitoring_analysis():

    result = analyze_monitoring(
        {
            'status':
                'valid',

            'alert_count':
                2,

            'alerts':
                [
                    {
                        'alert_type':
                            'high_error',
                    },
                    {
                        'alert_type':
                            'low_reliability',
                    },
                ],
        }
    )

    assert (
        result['available']
        is True
    )

    assert (
        result['alert_count']
        == 2
    )

    assert (
        len(result['alerts'])
        == 2
    )


# ==========================================================
# ALERT ANALYSIS
# ==========================================================

def test_alert_analysis():

    result = analyze_alerts(
        {
            'alerts':
                [
                    {
                        'severity':
                            'critical',
                    },
                    {
                        'severity':
                            'high',
                    },
                    {
                        'severity':
                            'high',
                    },
                    {
                        'severity':
                            'low',
                    },
                ],
        }
    )

    assert (
        result['alert_count']
        == 4
    )

    assert (
        result['critical_count']
        == 1
    )

    assert (
        result['high_count']
        == 2
    )

    assert (
        result['low_count']
        == 1
    )


# ==========================================================
# RECOMMENDATION ANALYSIS
# ==========================================================

def test_recommendation_analysis():

    result = analyze_recommendations(
        {
            'status':
                'valid',

            'recommendation_count':
                1,

            'recommendations':
                [
                    {
                        'recommendation_type':
                            'review_model',
                    }
                ],
        }
    )

    assert (
        result['available']
        is True
    )

    assert (
        result['recommendation_count']
        == 1
    )

    assert (
        len(result['recommendations'])
        == 1
    )


# ==========================================================
# EXECUTIVE SUMMARY
# ==========================================================

def test_executive_summary():

    summary = build_executive_summary(
        {
            'has_predictions':
                True,

            'prediction_count':
                3,
        },

        {
            'target_task':
                'regression',

            'mean_absolute_error':
                10.0,
        },

        {
            'reliability_level':
                'high',
        },

        {
            'alert_count':
                1,
        },

        {
            'recommendation_count':
                1,
        },
    )

    assert (
        len(summary)
        > 0
    )

    combined = ' '.join(
        summary
    )

    assert (
        '3 prediction'
        in combined
    )

    assert (
        'high'
        in combined
    )

    assert (
        '10.000000'
        in combined
    )


# ==========================================================
# UNIFIED SYSTEM ANALYSIS
# ==========================================================

def test_unified_system_analysis():

    result = analyze_system(

        {
            'target_name':
                'Target_Expense_Total_1D',

            'target_task':
                'regression',

            'predictions':
                [100, 120, 140],

            'confidence':
                0.85,
        },

        {
            'target_task':
                'regression',

            'actual_values':
                [90, 130, 140],

            'predicted_values':
                [100, 120, 140],

            'metrics':
                {
                    'mae':
                        6.6666666667,
                },
        },

        {
            'status':
                'valid',

            'reliability_level':
                'high',

            'quality_score':
                0.90,

            'sample_count':
                30,
        },

        {
            'status':
                'valid',

            'alert_count':
                1,

            'alerts':
                [
                    {
                        'alert_type':
                            'high_error',
                    }
                ],
        },

        {
            'status':
                'valid',

            'alert_count':
                1,

            'alerts':
                [
                    {
                        'severity':
                            'high',

                        'alert_type':
                            'high_error',
                    }
                ],
        },

        {
            'status':
                'valid',

            'recommendation_count':
                1,

            'recommendations':
                [
                    {
                        'recommendation_type':
                            'review_model',
                    }
                ],
        },
    )

    assert (
        result['status']
        == ANALYSIS_VALID
    )

    assert (
        result[
            'prediction_analysis'
        ][
            'prediction_count'
        ]
        == 3
    )

    assert (
        result[
            'error_analysis'
        ][
            'mean_absolute_error'
        ]
        == 20.0 / 3.0
    )

    assert (
        result[
            'reliability_analysis'
        ][
            'reliability_level'
        ]
        == 'high'
    )

    assert (
        result[
            'alert_analysis'
        ][
            'high_count'
        ]
        == 1
    )

    assert (
        result[
            'recommendation_analysis'
        ][
            'recommendation_count'
        ]
        == 1
    )

    assert (
        len(
            result[
                'executive_summary'
            ]
        )
        > 0
    )


# ==========================================================
# INVALID PREDICTION RESULT
# ==========================================================

def test_invalid_prediction_result():

    try:

        analyze_predictions(
            None
        )

        assert False

    except ValueError:

        pass


# ==========================================================
# INVALID CONFIDENCE
# ==========================================================

def test_invalid_confidence():

    try:

        analyze_predictions(
            {
                'predictions':
                    [100],

                'confidence':
                    1.5,
            }
        )

        assert False

    except ValueError:

        pass


# ==========================================================
# MISMATCHED ERROR ARRAYS
# ==========================================================

def test_mismatched_error_arrays():

    try:

        analyze_errors(
            {
                'target_task':
                    'regression',

                'actual_values':
                    [1, 2, 3],

                'predicted_values':
                    [1, 2],
            }
        )

        assert False

    except ValueError:

        pass


# ==========================================================
# UNSUPPORTED TASK
# ==========================================================

def test_unsupported_task():

    try:

        analyze_errors(
            {
                'target_task':
                    'unknown',

                'actual_values':
                    [1],

                'predicted_values':
                    [1],
            }
        )

        assert False

    except ValueError:

        pass


# ==========================================================
# INVALID OPTIONAL COMPONENT
# ==========================================================

def test_invalid_optional_component():

    try:

        analyze_system(
            {
                'predictions':
                    [100],
            },

            reliability_result=[
                'invalid'
            ],
        )

        assert False

    except ValueError:

        pass


# ==========================================================
# MAIN
# ==========================================================

if __name__ == '__main__':

    print()
    print(
        '========== ANALYZER TEST SUITE =========='
    )

    test_prediction_analysis()

    test_empty_predictions()

    test_regression_error_analysis()

    test_binary_classification_error_analysis()

    test_multiclass_error_analysis()

    test_reliability_analysis()

    test_missing_reliability()

    test_monitoring_analysis()

    test_alert_analysis()

    test_recommendation_analysis()

    test_executive_summary()

    test_unified_system_analysis()

    test_invalid_prediction_result()

    test_invalid_confidence()

    test_mismatched_error_arrays()

    test_unsupported_task()

    test_invalid_optional_component()

    print()
    print(
        'ALL ANALYZER TESTS PASSED'
    )