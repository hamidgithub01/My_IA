# ==========================================================
# REPORTING PIPELINE TESTS
# ==========================================================

import copy

import pytest

from ml.reporting.pipeline import (
    run_reporting_pipeline,
    generate_reporting_pipeline,
    run_report_pipeline,
    is_report_available,
    has_report_data,
)

from ml.reporting.reporter import (
    REPORT_VALID,
)


# ==========================================================
# TEST DATA
# ==========================================================

def _prediction_analysis(
    target_name='Target_Expense_Total_1D',
    target_task='regression',
):
    return {
        'prediction_count': 3,
        'target_name': target_name,
        'target_task': target_task,
        'has_predictions': True,
        'prediction_values': [
            100,
            120,
            140,
        ],
        'numeric_predictions': True,
        'minimum_prediction': 100.0,
        'maximum_prediction': 140.0,
        'mean_prediction': 120.0,
        'confidence': 0.9,
    }


def _analysis_result(
    target_name='Target_Expense_Total_1D',
    target_task='regression',
):
    return {
        'status': 'valid',

        'prediction_analysis':
            _prediction_analysis(
                target_name=target_name,
                target_task=target_task,
            ),

        'error_analysis': {
            'target_task': target_task,
            'sample_count': 3,
            'mean_absolute_error': 5.0,
        },

        'reliability_analysis': {
            'available': True,
            'status': 'reliable',
            'reliability_level': 'high',
            'quality_score': 0.95,
        },

        'monitoring_analysis': {
            'available': True,
            'status': 'stable',
            'alert_count': 0,
            'alerts': [],
        },

        'alert_analysis': {
            'available': True,
            'alert_count': 0,
            'critical_count': 0,
            'high_count': 0,
            'medium_count': 0,
            'low_count': 0,
            'alerts': [],
        },

        'recommendation_analysis': {
            'available': True,
            'recommendation_count': 0,
            'recommendations': [],
        },

        'executive_summary': [
            '3 prediction(s) are available.',
            'Reliability level: high.',
            'Mean absolute error: 5.000000.',
            'No active alerts were detected.',
        ],
    }


# ==========================================================
# BASIC PIPELINE
# ==========================================================

def test_pipeline_with_valid_analysis():

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

    assert 'report' in result


def test_pipeline_result_contract():

    result = run_reporting_pipeline(
        _analysis_result()
    )

    assert set(
        result.keys()
    ) == {
        'status',
        'report',
        'target_name',
        'target_task',
    }


def test_pipeline_preserves_target():

    result = run_reporting_pipeline(
        _analysis_result(
            target_name='Target_Income_1D',
            target_task='regression',
        )
    )

    assert result[
        'target_name'
    ] == 'Target_Income_1D'

    assert result[
        'target_task'
    ] == 'regression'


# ==========================================================
# FULL REPORTING FLOW
# ==========================================================

def test_pipeline_full_analysis():

    result = run_reporting_pipeline(
        _analysis_result()
    )

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

    assert 'analysis_status' in report

    assert 'executive_summary' in report

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


# ==========================================================
# REPORT DATA PRESERVATION
# ==========================================================

def test_pipeline_preserves_prediction_information():

    result = run_reporting_pipeline(
        _analysis_result()
    )

    prediction = result[
        'report'
    ][
        'sections'
    ][
        'predictions'
    ]

    assert prediction[
        'target_name'
    ] == 'Target_Expense_Total_1D'

    assert prediction[
        'target_task'
    ] == 'regression'

    assert prediction[
        'prediction_values'
    ] == [
        100,
        120,
        140,
    ]


def test_pipeline_preserves_reliability_information():

    result = run_reporting_pipeline(
        _analysis_result()
    )

    reliability = result[
        'report'
    ][
        'sections'
    ][
        'reliability'
    ]

    assert reliability[
        'reliability_level'
    ] == 'high'

    assert reliability[
        'quality_score'
    ] == 0.95


def test_pipeline_preserves_alert_information():

    result = run_reporting_pipeline(
        _analysis_result()
    )

    alerts = result[
        'report'
    ][
        'sections'
    ][
        'alerts'
    ]

    assert alerts[
        'alert_count'
    ] == 0

    assert alerts[
        'alerts'
    ] == []


def test_pipeline_preserves_recommendations():

    result = run_reporting_pipeline(
        _analysis_result()
    )

    recommendations = result[
        'report'
    ][
        'sections'
    ][
        'recommendations'
    ]

    assert recommendations[
        'recommendation_count'
    ] == 0

    assert recommendations[
        'recommendations'
    ] == []


def test_pipeline_contains_executive_summary():

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
# TARGET ISOLATION
# ==========================================================

def test_pipeline_keeps_targets_isolated():

    first = run_reporting_pipeline(
        _analysis_result(
            target_name='Target_Expense_Total_1D'
        )
    )

    second = run_reporting_pipeline(
        _analysis_result(
            target_name='Target_Income_Total_1D'
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
# INPUT IMMUTABILITY
# ==========================================================

def test_pipeline_does_not_modify_analysis_input():

    analysis_result = _analysis_result()

    original = copy.deepcopy(
        analysis_result
    )

    run_reporting_pipeline(
        analysis_result
    )

    assert analysis_result == original


# ==========================================================
# STATUS HELPERS
# ==========================================================

def test_is_report_available():

    result = run_reporting_pipeline(
        _analysis_result()
    )

    assert is_report_available(
        result
    ) is True


def test_has_report_data():

    result = run_reporting_pipeline(
        _analysis_result()
    )

    assert has_report_data(
        result
    ) is True


def test_is_report_available_false():

    result = {
        'status': 'insufficient_data',
        'report': {},
        'target_name': None,
        'target_task': None,
    }

    assert is_report_available(
        result
    ) is False


def test_has_report_data_false():

    result = {
        'status': 'insufficient_data',
        'report': {
            'status': 'insufficient_data',
        },
        'target_name': None,
        'target_task': None,
    }

    assert has_report_data(
        result
    ) is False


# ==========================================================
# COMPATIBILITY WRAPPERS
# ==========================================================

def test_generate_reporting_pipeline_wrapper():

    analysis_result = _analysis_result()

    result = generate_reporting_pipeline(
        analysis_result
    )

    assert result[
        'status'
    ] == REPORT_VALID

    assert result[
        'target_name'
    ] == 'Target_Expense_Total_1D'


def test_run_report_pipeline_wrapper():

    analysis_result = _analysis_result()

    result = run_report_pipeline(
        analysis_result
    )

    assert result[
        'status'
    ] == REPORT_VALID

    assert result[
        'target_name'
    ] == 'Target_Expense_Total_1D'


# ==========================================================
# VALIDATION
# ==========================================================

def test_pipeline_requires_analysis_result():

    with pytest.raises(
        ValueError,
        match='analysis_result is required',
    ):

        run_reporting_pipeline(
            None
        )


def test_pipeline_rejects_non_dictionary_analysis_result():

    with pytest.raises(
        ValueError,
        match='analysis_result must be a dictionary',
    ):

        run_reporting_pipeline(
            []
        )


def test_is_report_available_rejects_invalid_input():

    with pytest.raises(
        ValueError,
        match='pipeline_result is required',
    ):

        is_report_available(
            None
        )


def test_is_report_available_rejects_non_dictionary():

    with pytest.raises(
        ValueError,
        match='pipeline_result must be a dictionary',
    ):

        is_report_available(
            []
        )


def test_has_report_data_rejects_invalid_input():

    with pytest.raises(
        ValueError,
        match='pipeline_result is required',
    ):

        has_report_data(
            None
        )


def test_has_report_data_rejects_non_dictionary():

    with pytest.raises(
        ValueError,
        match='pipeline_result must be a dictionary',
    ):

        has_report_data(
            []
        )