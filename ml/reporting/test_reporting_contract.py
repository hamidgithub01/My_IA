# ==========================================================
# REPORTING CONTRACT TESTS
# ==========================================================

import pytest

from ml.reporting.reporter import (
    REPORT_VALID,
    REPORT_INSUFFICIENT_DATA,
    build_report,
    is_report_available,
    has_report_data,
)


# ==========================================================
# TEST DATA
# ==========================================================

def make_valid_analysis():

    return {
        'status': 'valid',

        'prediction_analysis': {
            'has_predictions': True,
            'prediction_count': 3,
            'target_name': 'Target_Expense_Total_1D',
            'target_task': 'regression',
            'prediction_values': [100, 120, 140],
            'numeric_predictions': True,
            'minimum_prediction': 100.0,
            'maximum_prediction': 140.0,
            'mean_prediction': 120.0,
            'confidence': 0.92,
        },

        'error_analysis': {
            'available': True,
            'target_task': 'regression',
            'sample_count': 3,
            'mean_absolute_error': 4.0,
        },

        'reliability_analysis': {
            'available': True,
            'status': 'reliable',
            'reliability_level': 'high',
            'quality_score': 0.91,
        },

        'monitoring_analysis': {
            'available': True,
            'status': 'stable',
            'alert_count': 0,
            'alerts': [],
        },

        'alert_analysis': {
            'available': True,
            'alert_count': 1,
            'critical_count': 0,
            'high_count': 1,
            'medium_count': 0,
            'low_count': 0,
            'alerts': [
                {
                    'severity': 'high',
                    'target_name': 'Target_Expense_Total_1D',
                }
            ],
        },

        'recommendation_analysis': {
            'available': True,
            'status': 'generated',
            'recommendation_count': 1,
            'recommendations': [
                {
                    'type': 'monitor_closely',
                    'target_name': 'Target_Expense_Total_1D',
                }
            ],
        },

        'executive_summary': [
            '3 prediction(s) are available.',
            'Reliability level: high.',
            'Mean absolute error: 4.000000.',
            '1 alert(s) require attention.',
            '1 recommendation(s) are available.',
        ],
    }


# ==========================================================
# REPORT RESULT CONTRACT
# ==========================================================

def test_reporting_result_contract():

    result = build_report(
        make_valid_analysis()
    )

    assert isinstance(
        result,
        dict,
    )

    assert set(
        result.keys()
    ) == {
        'status',
        'analysis_status',
        'executive_summary',
        'sections',
    }


def test_reporting_status_contract():

    result = build_report(
        make_valid_analysis()
    )

    assert result[
        'status'
    ] in {
        REPORT_VALID,
        REPORT_INSUFFICIENT_DATA,
    }


def test_valid_report_has_valid_status():

    result = build_report(
        make_valid_analysis()
    )

    assert result[
        'status'
    ] == REPORT_VALID


# ==========================================================
# SECTION CONTRACT
# ==========================================================

def test_all_report_sections_exist():

    result = build_report(
        make_valid_analysis()
    )

    sections = result[
        'sections'
    ]

    assert set(
        sections.keys()
    ) == {
        'predictions',
        'errors',
        'reliability',
        'monitoring',
        'alerts',
        'recommendations',
    }


def test_prediction_section_contract():

    result = build_report(
        make_valid_analysis()
    )

    section = result[
        'sections'
    ][
        'predictions'
    ]

    required_fields = {
        'available',
        'prediction_count',
        'target_name',
        'target_task',
        'prediction_values',
        'numeric_predictions',
        'minimum_prediction',
        'maximum_prediction',
        'mean_prediction',
        'confidence',
    }

    assert required_fields <= set(
        section.keys()
    )


def test_optional_sections_have_available_flag():

    result = build_report(
        make_valid_analysis()
    )

    sections = result[
        'sections'
    ]

    for name in [
        'errors',
        'reliability',
        'monitoring',
        'alerts',
        'recommendations',
    ]:

        assert (
            'available'
            in sections[name]
        )


# ==========================================================
# TARGET CONTRACT
# ==========================================================

def test_reporting_preserves_target_identity():

    result = build_report(
        make_valid_analysis()
    )

    prediction_section = result[
        'sections'
    ][
        'predictions'
    ]

    assert prediction_section[
        'target_name'
    ] == 'Target_Expense_Total_1D'

    assert prediction_section[
        'target_task'
    ] == 'regression'


def test_reporting_does_not_mix_targets():

    analysis_a = make_valid_analysis()

    analysis_b = make_valid_analysis()

    analysis_a[
        'prediction_analysis'
    ][
        'target_name'
    ] = 'Target_A'

    analysis_b[
        'prediction_analysis'
    ][
        'target_name'
    ] = 'Target_B'

    report_a = build_report(
        analysis_a
    )

    report_b = build_report(
        analysis_b
    )

    assert report_a[
        'sections'
    ][
        'predictions'
    ][
        'target_name'
    ] == 'Target_A'

    assert report_b[
        'sections'
    ][
        'predictions'
    ][
        'target_name'
    ] == 'Target_B'


# ==========================================================
# SUMMARY CONTRACT
# ==========================================================

def test_executive_summary_contract():

    result = build_report(
        make_valid_analysis()
    )

    summary = result[
        'executive_summary'
    ]

    assert isinstance(
        summary,
        list,
    )

    assert all(
        isinstance(
            item,
            str,
        )
        for item in summary
    )


# ==========================================================
# OPTIONAL INPUT CONTRACT
# ==========================================================

def test_reporting_accepts_missing_optional_analysis():

    analysis = {

        'status': 'valid',

        'prediction_analysis': {
            'has_predictions': True,
            'prediction_count': 1,
            'target_name': 'Target_A',
            'target_task': 'regression',
            'prediction_values': [100],
        },

        'executive_summary': [
            '1 prediction(s) are available.',
        ],
    }

    result = build_report(
        analysis
    )

    assert result[
        'status'
    ] == REPORT_VALID

    sections = result[
        'sections'
    ]

    assert sections[
        'predictions'
    ][
        'available'
    ] is True

    assert sections[
        'errors'
    ][
        'available'
    ] is False

    assert sections[
        'reliability'
    ][
        'available'
    ] is False

    assert sections[
        'monitoring'
    ][
        'available'
    ] is False

    assert sections[
        'alerts'
    ][
        'available'
    ] is False

    assert sections[
        'recommendations'
    ][
        'available'
    ] is False


# ==========================================================
# INSUFFICIENT DATA CONTRACT
# ==========================================================

def test_reporting_insufficient_data_contract():

    analysis = {

        'status':
            'insufficient_data',

        'prediction_analysis': {
            'has_predictions': False,
            'prediction_count': 0,
            'target_name': None,
            'target_task': None,
            'prediction_values': [],
        },

        'executive_summary': [
            'No predictions are available.',
        ],
    }

    result = build_report(
        analysis
    )

    assert result[
        'status'
    ] == REPORT_INSUFFICIENT_DATA

    assert (
        is_report_available(
            result
        )
        is False
    )

    assert (
        has_report_data(
            result
        )
        is False
    )


# ==========================================================
# REQUIRED INPUT CONTRACT
# ==========================================================

def test_reporting_requires_analysis_result():

    with pytest.raises(
        ValueError,
        match='analysis_result is required',
    ):

        build_report(
            None
        )


def test_reporting_rejects_non_dictionary_input():

    with pytest.raises(
        ValueError,
        match='analysis_result must be a dictionary',
    ):

        build_report(
            []
        )


def test_reporting_requires_analysis_status():

    analysis = {
        'prediction_analysis': {
            'has_predictions': True,
            'prediction_count': 1,
        }
    }

    with pytest.raises(
        ValueError,
        match='analysis_result status is required',
    ):

        build_report(
            analysis
        )


# ==========================================================
# HELPER CONTRACTS
# ==========================================================

def test_is_report_available_contract():

    result = build_report(
        make_valid_analysis()
    )

    assert isinstance(
        is_report_available(
            result
        ),
        bool,
    )


def test_has_report_data_contract():

    result = build_report(
        make_valid_analysis()
    )

    assert isinstance(
        has_report_data(
            result
        ),
        bool,
    )


def test_is_report_available_rejects_invalid_input():

    with pytest.raises(
        ValueError,
        match='report_result is required',
    ):

        is_report_available(
            None
        )


def test_has_report_data_rejects_invalid_input():

    with pytest.raises(
        ValueError,
        match='report_result must be a dictionary',
    ):

        has_report_data(
            []
        )


# ==========================================================
# DATA PRESERVATION CONTRACT
# ==========================================================

def test_reporting_preserves_prediction_values():

    result = build_report(
        make_valid_analysis()
    )

    assert result[
        'sections'
    ][
        'predictions'
    ][
        'prediction_values'
    ] == [
        100,
        120,
        140,
    ]


def test_reporting_preserves_reliability():

    result = build_report(
        make_valid_analysis()
    )

    reliability = result[
        'sections'
    ][
        'reliability'
    ]

    assert reliability[
        'reliability_level'
    ] == 'high'

    assert reliability[
        'quality_score'
    ] == 0.91


def test_reporting_preserves_alerts():

    result = build_report(
        make_valid_analysis()
    )

    alerts = result[
        'sections'
    ][
        'alerts'
    ]

    assert alerts[
        'alert_count'
    ] == 1

    assert alerts[
        'alerts'
    ][0][
        'severity'
    ] == 'high'


def test_reporting_preserves_recommendations():

    result = build_report(
        make_valid_analysis()
    )

    recommendations = result[
        'sections'
    ][
        'recommendations'
    ]

    assert recommendations[
        'recommendation_count'
    ] == 1

    assert recommendations[
        'recommendations'
    ][0][
        'type'
    ] == 'monitor_closely'


# ==========================================================
# INPUT IMMUTABILITY CONTRACT
# ==========================================================

def test_reporting_does_not_modify_analysis_result():

    analysis = make_valid_analysis()

    original_prediction = dict(
        analysis[
            'prediction_analysis'
        ]
    )

    original_target = (
        analysis[
            'prediction_analysis'
        ][
            'target_name'
        ]
    )

    build_report(
        analysis
    )

    assert analysis[
        'prediction_analysis'
    ] == original_prediction

    assert analysis[
        'prediction_analysis'
    ][
        'target_name'
    ] == original_target