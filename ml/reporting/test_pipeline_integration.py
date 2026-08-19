# ==========================================================
# REPORTING PIPELINE INTEGRATION TESTS
# ==========================================================

from copy import deepcopy

from ml.reporting.pipeline import (
    run_reporting_pipeline,
    is_report_available,
    has_report_data,
)

from ml.reporting.reporter import (
    REPORT_VALID,
)


# ==========================================================
# TEST DATA
# ==========================================================

def _analysis_result(
    target_name='Target_Expense_Total_1D',
    target_task='regression',
):

    return {

        'status':
            'valid',

        'prediction_analysis': {

            'has_predictions':
                True,

            'prediction_count':
                3,

            'target_name':
                target_name,

            'target_task':
                target_task,

            'prediction_values':
                [100, 120, 140],
        },

        'error_analysis': {

            'target_task':
                target_task,

            'sample_count':
                3,

            'mean_absolute_error':
                5.0,
        },

        'reliability_analysis': {

            'available':
                True,

            'status':
                'reliable',

            'reliability_level':
                'high',

            'quality_score':
                0.95,
        },

        'monitoring_analysis': {

            'available':
                True,

            'status':
                'stable',

            'alert_count':
                0,

            'alerts':
                [],
        },

        'alert_analysis': {

            'available':
                True,

            'alert_count':
                0,

            'alerts':
                [],
        },

        'recommendation_analysis': {

            'available':
                True,

            'recommendation_count':
                0,

            'recommendations':
                [],
        },

        'executive_summary': [

            '3 prediction(s) are available.',

            'Reliability level: high.',

            'Mean absolute error: 5.000000.',

            'No active alerts were detected.',
        ],
    }


# ==========================================================
# BASIC INTEGRATION
# ==========================================================

def test_reporting_pipeline_accepts_analysis_result():

    result = run_reporting_pipeline(
        _analysis_result()
    )

    assert isinstance(
        result,
        dict,
    )

    assert result[
        'status'
    ] == REPORT_VALID


def test_reporting_pipeline_produces_report():

    result = run_reporting_pipeline(
        _analysis_result()
    )

    assert 'report' in result

    assert isinstance(
        result[
            'report'
        ],
        dict,
    )


# ==========================================================
# ANALYSIS → REPORTING
# ==========================================================

def test_analysis_status_reaches_reporting():

    result = run_reporting_pipeline(
        _analysis_result()
    )

    report = result[
        'report'
    ]

    assert report[
        'analysis_status'
    ] == 'valid'


def test_prediction_analysis_reaches_reporting():

    result = run_reporting_pipeline(
        _analysis_result()
    )

    sections = result[
        'report'
    ][
        'sections'
    ]

    prediction = sections[
        'predictions'
    ]

    assert prediction[
        'prediction_count'
    ] == 3

    assert prediction[
        'prediction_values'
    ] == [100, 120, 140]


def test_error_analysis_reaches_reporting():

    result = run_reporting_pipeline(
        _analysis_result()
    )

    sections = result[
        'report'
    ][
        'sections'
    ]

    errors = sections[
        'errors'
    ]

    assert errors[
        'target_task'
    ] == 'regression'

    assert errors[
        'mean_absolute_error'
    ] == 5.0


def test_reliability_analysis_reaches_reporting():

    result = run_reporting_pipeline(
        _analysis_result()
    )

    sections = result[
        'report'
    ][
        'sections'
    ]

    reliability = sections[
        'reliability'
    ]

    assert reliability[
        'available'
    ] is True

    assert reliability[
        'reliability_level'
    ] == 'high'

    assert reliability[
        'quality_score'
    ] == 0.95


def test_monitoring_analysis_reaches_reporting():

    result = run_reporting_pipeline(
        _analysis_result()
    )

    sections = result[
        'report'
    ][
        'sections'
    ]

    monitoring = sections[
        'monitoring'
    ]

    assert monitoring[
        'available'
    ] is True

    assert monitoring[
        'status'
    ] == 'stable'


def test_alert_analysis_reaches_reporting():

    result = run_reporting_pipeline(
        _analysis_result()
    )

    sections = result[
        'report'
    ][
        'sections'
    ]

    alerts = sections[
        'alerts'
    ]

    assert alerts[
        'available'
    ] is True

    assert alerts[
        'alert_count'
    ] == 0

    assert alerts[
        'alerts'
    ] == []


def test_recommendation_analysis_reaches_reporting():

    result = run_reporting_pipeline(
        _analysis_result()
    )

    sections = result[
        'report'
    ][
        'sections'
    ]

    recommendations = sections[
        'recommendations'
    ]

    assert recommendations[
        'available'
    ] is True

    assert recommendations[
        'recommendation_count'
    ] == 0

    assert recommendations[
        'recommendations'
    ] == []


# ==========================================================
# EXECUTIVE SUMMARY
# ==========================================================

def test_executive_summary_reaches_reporting():

    result = run_reporting_pipeline(
        _analysis_result()
    )

    summary = result[
        'report'
    ][
        'executive_summary'
    ]

    assert isinstance(
        summary,
        list,
    )

    assert len(
        summary
    ) > 0


# ==========================================================
# TARGET IDENTITY
# ==========================================================

def test_reporting_pipeline_preserves_target_identity():

    target_name = (
        'Target_Expense_Total_1D'
    )

    result = run_reporting_pipeline(
        _analysis_result(
            target_name=target_name
        )
    )

    assert result[
        'target_name'
    ] == target_name

    prediction = result[
        'report'
    ][
        'sections'
    ][
        'predictions'
    ]

    assert prediction[
        'target_name'
    ] == target_name


def test_reporting_pipeline_preserves_target_task():

    result = run_reporting_pipeline(
        _analysis_result(
            target_task='regression'
        )
    )

    assert result[
        'target_task'
    ] == 'regression'

    prediction = result[
        'report'
    ][
        'sections'
    ][
        'predictions'
    ]

    assert prediction[
        'target_task'
    ] == 'regression'


def test_reporting_pipeline_keeps_targets_isolated():

    first = run_reporting_pipeline(
        _analysis_result(
            target_name=
                'Target_Expense_Total_1D'
        )
    )

    second = run_reporting_pipeline(
        _analysis_result(
            target_name=
                'Target_Income_Total_1D'
        )
    )

    assert first[
        'target_name'
    ] != second[
        'target_name'
    ]

    first_prediction = first[
        'report'
    ][
        'sections'
    ][
        'predictions'
    ]

    second_prediction = second[
        'report'
    ][
        'sections'
    ][
        'predictions'
    ]

    assert first_prediction[
        'target_name'
    ] == 'Target_Expense_Total_1D'

    assert second_prediction[
        'target_name'
    ] == 'Target_Income_Total_1D'


# ==========================================================
# PARTIAL ANALYSIS FLOW
# ==========================================================

def test_reporting_accepts_partial_analysis():

    analysis_result = {

        'status':
            'valid',

        'prediction_analysis': {

            'has_predictions':
                True,

            'prediction_count':
                2,

            'target_name':
                'Target_Expense_Total_1D',

            'target_task':
                'regression',

            'prediction_values':
                [100, 120],
        },

        'error_analysis':
            None,

        'reliability_analysis': {

            'available':
                False,
        },

        'monitoring_analysis': {

            'available':
                False,
        },

        'alert_analysis': {

            'available':
                False,
        },

        'recommendation_analysis': {

            'available':
                False,
        },

        'executive_summary': [

            '2 prediction(s) are available.',
        ],
    }

    result = run_reporting_pipeline(
        analysis_result
    )

    assert isinstance(
        result,
        dict,
    )

    assert result[
        'report'
    ][
        'status'
    ] == REPORT_VALID


# ==========================================================
# INPUT IMMUTABILITY
# ==========================================================

def test_reporting_pipeline_does_not_modify_analysis_result():

    analysis_result = _analysis_result()

    original = deepcopy(
        analysis_result
    )

    run_reporting_pipeline(
        analysis_result
    )

    assert analysis_result == original


# ==========================================================
# AVAILABILITY
# ==========================================================

def test_report_is_available_after_full_integration():

    result = run_reporting_pipeline(
        _analysis_result()
    )

    assert is_report_available(
        result
    ) is True


def test_report_contains_data_after_full_integration():

    result = run_reporting_pipeline(
        _analysis_result()
    )

    assert has_report_data(
        result
    ) is True


# ==========================================================
# COMPLETE INTEGRATION CONTRACT
# ==========================================================

def test_complete_reporting_pipeline_integration_contract():

    result = run_reporting_pipeline(
        _analysis_result()
    )

    assert result[
        'status'
    ] == REPORT_VALID

    assert result[
        'target_name'
    ] == 'Target_Expense_Total_1D'

    assert result[
        'target_task'
    ] == 'regression'

    report = result[
        'report'
    ]

    assert isinstance(
        report,
        dict,
    )

    assert report[
        'status'
    ] == REPORT_VALID

    assert report[
        'analysis_status'
    ] == 'valid'

    assert 'sections' in report

    sections = report[
        'sections'
    ]

    assert 'predictions' in sections

    assert 'errors' in sections

    assert 'reliability' in sections

    assert 'monitoring' in sections

    assert 'alerts' in sections

    assert 'recommendations' in sections

    assert 'executive_summary' in report

    assert sections[
        'predictions'
    ][
        'target_name'
    ] == 'Target_Expense_Total_1D'