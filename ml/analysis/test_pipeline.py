# ==========================================================
# ANALYSIS PIPELINE TESTS
# ==========================================================

import pytest

from ml.analysis.pipeline import (
    run_analysis_pipeline,
    analyze_pipeline,
    is_analysis_available,
    has_analysis_data,
)

from ml.analysis.analyzer import (
    ANALYSIS_VALID,
    ANALYSIS_INSUFFICIENT_DATA,
)


# ==========================================================
# BASIC PIPELINE
# ==========================================================

def test_pipeline_with_predictions():

    result = run_analysis_pipeline(
        {
            'target_name':
                'Target_Expense_Total_1D',

            'target_task':
                'regression',

            'predictions':
                [100, 120, 140],
        }
    )

    assert isinstance(
        result,
        dict,
    )

    assert (
        result['status']
        == ANALYSIS_VALID
    )

    assert (
        'analysis'
        in result
    )

    assert (
        result['analysis']
        ['prediction_analysis']
        ['prediction_count']
        == 3
    )


# ==========================================================
# RESULT CONTRACT
# ==========================================================

def test_pipeline_result_contract():

    result = run_analysis_pipeline(
        {
            'target_name':
                'Target_Test',

            'target_task':
                'regression',

            'predictions':
                [1, 2, 3],
        }
    )

    required_keys = {
        'status',
        'analysis',
        'target_name',
        'target_task',
    }

    assert required_keys.issubset(
        result.keys()
    )

    assert isinstance(
        result['status'],
        str,
    )

    assert isinstance(
        result['analysis'],
        dict,
    )


# ==========================================================
# TARGET PRESERVATION
# ==========================================================

def test_pipeline_preserves_target():

    result = run_analysis_pipeline(
        {
            'target_name':
                'Target_Income_Total_1D',

            'target_task':
                'regression',

            'predictions':
                [500, 600],
        }
    )

    assert (
        result['target_name']
        == 'Target_Income_Total_1D'
    )

    assert (
        result['target_task']
        == 'regression'
    )

    assert (
        result['analysis']
        ['prediction_analysis']
        ['target_name']
        == 'Target_Income_Total_1D'
    )


# ==========================================================
# FULL PIPELINE
# ==========================================================

def test_pipeline_full_analysis():

    result = run_analysis_pipeline(

        prediction_result={
            'target_name':
                'Target_Expense_Total_1D',

            'target_task':
                'regression',

            'predictions':
                [100, 120, 140],
        },

        evaluation_result={

            'target_task':
                'regression',

            'actual_values':
                [110, 115, 150],

            'predicted_values':
                [100, 120, 140],

            'metrics': {

                'mae':
                    11.666666,
            },
        },

        reliability_result={

            'status':
                'reliable',

            'reliability_level':
                'high',

            'quality_score':
                0.92,

            'sample_count':
                100,
        },

        monitoring_result={

            'status':
                'valid',

            'target_name':
                'Target_Expense_Total_1D',

            'reliability_level':
                'high',

            'quality_score':
                0.92,

            'alert_count':
                0,

            'alerts':
                [],
        },

        alert_result={

            'status':
                'none',

            'alert_count':
                0,

            'alerts':
                [],
        },

        recommendation_result={

            'status':
                'none',

            'recommendation_count':
                0,

            'recommendations':
                [],
        },
    )

    assert (
        result['status']
        == ANALYSIS_VALID
    )

    assert (
        result['target_name']
        == 'Target_Expense_Total_1D'
    )

    assert (
        result['target_task']
        == 'regression'
    )

    analysis = result[
        'analysis'
    ]

    assert (
        analysis[
            'prediction_analysis'
        ][
            'has_predictions'
        ]
        is True
    )

    assert (
        analysis[
            'error_analysis'
        ] is not None
    )

    assert (
        analysis[
            'reliability_analysis'
        ][
            'available'
        ]
        is True
    )

    assert (
        analysis[
            'monitoring_analysis'
        ][
            'available'
        ]
        is True
    )

    assert (
        analysis[
            'alert_analysis'
        ][
            'available'
        ]
        is True
    )

    assert (
        analysis[
            'recommendation_analysis'
        ][
            'available'
        ]
        is True
    )


# ==========================================================
# OPTIONAL COMPONENTS
# ==========================================================

def test_pipeline_accepts_missing_optional_layers():

    result = run_analysis_pipeline(
        {
            'target_name':
                'Target_Test',

            'target_task':
                'regression',

            'predictions':
                [10, 20, 30],
        }
    )

    assert (
        result['status']
        == ANALYSIS_VALID
    )

    analysis = result[
        'analysis'
    ]

    assert (
        analysis[
            'error_analysis'
        ] is None
    )

    assert (
        analysis[
            'reliability_analysis'
        ][
            'available'
        ]
        is False
    )

    assert (
        analysis[
            'monitoring_analysis'
        ][
            'available'
        ]
        is False
    )

    assert (
        analysis[
            'alert_analysis'
        ][
            'available'
        ]
        is False
    )

    assert (
        analysis[
            'recommendation_analysis'
        ][
            'available'
        ]
        is False
    )


# ==========================================================
# EMPTY PREDICTIONS
# ==========================================================

def test_pipeline_handles_empty_predictions():

    result = run_analysis_pipeline(
        {
            'target_name':
                'Target_Test',

            'target_task':
                'regression',

            'predictions':
                [],
        }
    )

    assert isinstance(
        result,
        dict,
    )

    assert (
        result['analysis']
        ['prediction_analysis']
        ['has_predictions']
        is False
    )


# ==========================================================
# RELIABILITY FLOW
# ==========================================================

def test_pipeline_preserves_reliability_information():

    result = run_analysis_pipeline(

        prediction_result={

            'target_name':
                'Target_Test',

            'target_task':
                'regression',

            'predictions':
                [10, 20],
        },

        reliability_result={

            'status':
                'reliable',

            'reliability_level':
                'high',

            'quality_score':
                0.95,

            'sample_count':
                200,
        },
    )

    reliability = (
        result[
            'analysis'
        ][
            'reliability_analysis'
        ]
    )

    assert (
        reliability['available']
        is True
    )

    assert (
        reliability['status']
        == 'reliable'
    )

    assert (
        reliability['reliability_level']
        == 'high'
    )

    assert (
        reliability['quality_score']
        == 0.95
    )

    assert (
        reliability['sample_count']
        == 200
    )


# ==========================================================
# MONITORING FLOW
# ==========================================================

def test_pipeline_preserves_monitoring_information():

    result = run_analysis_pipeline(

        prediction_result={

            'target_name':
                'Target_Test',

            'target_task':
                'regression',

            'predictions':
                [10, 20],
        },

        monitoring_result={

            'status':
                'valid',

            'alert_count':
                1,

            'alerts': [

                {
                    'alert_type':
                        'reliability_decline',

                    'severity':
                        'warning',
                },
            ],
        },
    )

    monitoring = (
        result[
            'analysis'
        ][
            'monitoring_analysis'
        ]
    )

    assert (
        monitoring[
            'available'
        ]
        is True
    )

    assert (
        monitoring[
            'status'
        ]
        == 'valid'
    )

    assert (
        monitoring[
            'alert_count'
        ]
        == 1
    )

    assert (
        len(
            monitoring['alerts']
        )
        == 1
    )


# ==========================================================
# ALERT FLOW
# ==========================================================

def test_pipeline_preserves_alert_information():

    result = run_analysis_pipeline(

        prediction_result={

            'target_name':
                'Target_Test',

            'target_task':
                'regression',

            'predictions':
                [10, 20],
        },

        alert_result={

            'status':
                'valid',

            'alert_count':
                1,

            'alerts': [

                {
                    'alert_type':
                        'high_error',

                    'severity':
                        'high',
                },
            ],
        },
    )

    alerts = (
        result[
            'analysis'
        ][
            'alert_analysis'
        ]
    )

    assert (
        alerts[
            'available'
        ]
        is True
    )

    assert (
        alerts[
            'alert_count'
        ]
        == 1
    )

    assert (
        alerts[
            'high_count'
        ]
        == 1
    )


# ==========================================================
# RECOMMENDATION FLOW
# ==========================================================

def test_pipeline_preserves_recommendations():

    result = run_analysis_pipeline(

        prediction_result={

            'target_name':
                'Target_Test',

            'target_task':
                'regression',

            'predictions':
                [10, 20],
        },

        recommendation_result={

            'status':
                'valid',

            'recommendation_count':
                1,

            'recommendations': [

                {
                    'recommendation_type':
                        'review_model',

                    'priority':
                        'high',
                },
            ],
        },
    )

    recommendations = (
        result[
            'analysis'
        ][
            'recommendation_analysis'
        ]
    )

    assert (
        recommendations[
            'available'
        ]
        is True
    )

    assert (
        recommendations[
            'recommendation_count'
        ]
        == 1
    )

    assert (
        recommendations[
            'recommendations'
        ][0][
            'recommendation_type'
        ]
        == 'review_model'
    )


# ==========================================================
# EXECUTIVE SUMMARY
# ==========================================================

def test_pipeline_contains_executive_summary():

    result = run_analysis_pipeline(

        {
            'target_name':
                'Target_Test',

            'target_task':
                'regression',

            'predictions':
                [100, 200, 300],
        }
    )

    summary = (
        result[
            'analysis'
        ][
            'executive_summary'
        ]
    )

    assert isinstance(
        summary,
        list,
    )

    assert len(summary) > 0


# ==========================================================
# STATUS HELPERS
# ==========================================================

def test_is_analysis_available():

    result = run_analysis_pipeline(

        {
            'target_name':
                'Target_Test',

            'target_task':
                'regression',

            'predictions':
                [1, 2, 3],
        }
    )

    assert (
        is_analysis_available(
            result
        )
        is True
    )


def test_has_analysis_data():

    result = run_analysis_pipeline(

        {
            'target_name':
                'Target_Test',

            'target_task':
                'regression',

            'predictions':
                [1, 2, 3],
        }
    )

    assert (
        has_analysis_data(
            result
        )
        is True
    )


def test_is_analysis_available_rejects_invalid_input():

    with pytest.raises(
        ValueError
    ):

        is_analysis_available(
            None
        )


def test_has_analysis_data_rejects_invalid_input():

    with pytest.raises(
        ValueError
    ):

        has_analysis_data(
            None
        )


# ==========================================================
# BACKWARD COMPATIBILITY
# ==========================================================

def test_analyze_pipeline_wrapper():

    prediction_result = {

        'target_name':
            'Target_Test',

        'target_task':
            'regression',

        'predictions':
            [10, 20, 30],
    }

    direct_result = (
        run_analysis_pipeline(
            prediction_result
        )
    )

    wrapper_result = (
        analyze_pipeline(
            prediction_result
        )
    )

    assert (
        wrapper_result
        == direct_result
    )


# ==========================================================
# INPUT VALIDATION
# ==========================================================

def test_pipeline_requires_prediction_result():

    with pytest.raises(
        ValueError
    ):

        run_analysis_pipeline(
            None
        )


def test_pipeline_rejects_non_dictionary_prediction_result():

    with pytest.raises(
        ValueError
    ):

        run_analysis_pipeline(
            ['invalid']
        )


def test_pipeline_rejects_invalid_evaluation_result():

    with pytest.raises(
        ValueError
    ):

        run_analysis_pipeline(

            prediction_result={

                'target_name':
                    'Target_Test',

                'target_task':
                    'regression',

                'predictions':
                    [1, 2, 3],
            },

            evaluation_result=[
                'invalid'
            ],
        )


def test_pipeline_rejects_invalid_reliability_result():

    with pytest.raises(
        ValueError
    ):

        run_analysis_pipeline(

            prediction_result={

                'target_name':
                    'Target_Test',

                'target_task':
                    'regression',

                'predictions':
                    [1, 2, 3],
            },

            reliability_result=[
                'invalid'
            ],
        )


def test_pipeline_rejects_invalid_monitoring_result():

    with pytest.raises(
        ValueError
    ):

        run_analysis_pipeline(

            prediction_result={

                'target_name':
                    'Target_Test',

                'target_task':
                    'regression',

                'predictions':
                    [1, 2, 3],
            },

            monitoring_result=[
                'invalid'
            ],
        )


def test_pipeline_rejects_invalid_alert_result():

    with pytest.raises(
        ValueError
    ):

        run_analysis_pipeline(

            prediction_result={

                'target_name':
                    'Target_Test',

                'target_task':
                    'regression',

                'predictions':
                    [1, 2, 3],
            },

            alert_result=[
                'invalid'
            ],
        )


def test_pipeline_rejects_invalid_recommendation_result():

    with pytest.raises(
        ValueError
    ):

        run_analysis_pipeline(

            prediction_result={

                'target_name':
                    'Target_Test',

                'target_task':
                    'regression',

                'predictions':
                    [1, 2, 3],
            },

            recommendation_result=[
                'invalid'
            ],
        )


# ==========================================================
# INPUT IMMUTABILITY
# ==========================================================

def test_pipeline_does_not_modify_prediction_input():

    prediction_result = {

        'target_name':
            'Target_Test',

        'target_task':
            'regression',

        'predictions':
            [10, 20, 30],
    }

    original_predictions = list(
        prediction_result[
            'predictions'
        ]
    )

    run_analysis_pipeline(
        prediction_result
    )

    assert (
        prediction_result[
            'predictions'
        ]
        == original_predictions
    )


# ==========================================================
# TARGET ISOLATION
# ==========================================================

def test_pipeline_keeps_targets_isolated():

    first = run_analysis_pipeline(

        {
            'target_name':
                'Target_A',

            'target_task':
                'regression',

            'predictions':
                [1, 2],
        }
    )

    second = run_analysis_pipeline(

        {
            'target_name':
                'Target_B',

            'target_task':
                'regression',

            'predictions':
                [100, 200],
        }
    )

    assert (
        first['target_name']
        == 'Target_A'
    )

    assert (
        second['target_name']
        == 'Target_B'
    )

    assert (
        first['analysis']
        ['prediction_analysis']
        ['target_name']
        == 'Target_A'
    )

    assert (
        second['analysis']
        ['prediction_analysis']
        ['target_name']
        == 'Target_B'
    )