# ==========================================================
# REPORTER TESTS
# ==========================================================

import pytest

from ml.reporting.reporter import (
    REPORT_VALID,
    REPORT_INSUFFICIENT_DATA,
    build_report,
    generate_report,
    is_report_available,
    has_report_data,
)


# ==========================================================
# TEST DATA
# ==========================================================

def make_analysis_result():

    return {

        'status':
            'valid',

        'prediction_analysis': {

            'has_predictions':
                True,

            'prediction_count':
                3,

            'target_name':
                'Target_Expense_Total_1D',

            'target_task':
                'regression',

            'prediction_values':
                [100, 120, 140],

            'numeric_predictions':
                True,

            'minimum_prediction':
                100.0,

            'maximum_prediction':
                140.0,

            'mean_prediction':
                120.0,

            'confidence':
                0.92,
        },

        'error_analysis': {

            'available':
                True,

            'target_task':
                'regression',

            'sample_count':
                3,

            'mean_error':
                2.0,

            'mean_absolute_error':
                4.0,

            'over_predictions':
                2,

            'under_predictions':
                1,

            'exact_predictions':
                0,
        },

        'reliability_analysis': {

            'available':
                True,

            'status':
                'reliable',

            'reliability_level':
                'high',

            'quality_score':
                0.91,

            'sample_count':
                100,
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
                1,

            'critical_count':
                0,

            'high_count':
                1,

            'medium_count':
                0,

            'low_count':
                0,

            'alerts': [

                {
                    'severity':
                        'high',

                    'target_name':
                        'Target_Expense_Total_1D',
                }
            ],
        },

        'recommendation_analysis': {

            'available':
                True,

            'status':
                'generated',

            'recommendation_count':
                1,

            'recommendations': [

                {
                    'type':
                        'monitor_closely',

                    'target_name':
                        'Target_Expense_Total_1D',
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
# BASIC REPORT TESTS
# ==========================================================

def test_build_report():

    result = build_report(
        make_analysis_result()
    )

    assert isinstance(
        result,
        dict,
    )

    assert result[
        'status'
    ] == REPORT_VALID


def test_report_result_contract():

    result = build_report(
        make_analysis_result()
    )

    assert set(
        result.keys()
    ) == {

        'status',

        'analysis_status',

        'executive_summary',

        'sections',
    }


def test_report_analysis_status_is_preserved():

    result = build_report(
        make_analysis_result()
    )

    assert result[
        'analysis_status'
    ] == 'valid'


# ==========================================================
# PREDICTION SECTION
# ==========================================================

def test_prediction_section():

    result = build_report(
        make_analysis_result()
    )

    predictions = result[
        'sections'
    ][
        'predictions'
    ]

    assert predictions[
        'available'
    ] is True

    assert predictions[
        'prediction_count'
    ] == 3

    assert predictions[
        'target_name'
    ] == 'Target_Expense_Total_1D'

    assert predictions[
        'target_task'
    ] == 'regression'

    assert predictions[
        'prediction_values'
    ] == [100, 120, 140]

    assert predictions[
        'mean_prediction'
    ] == 120.0


# ==========================================================
# ERROR SECTION
# ==========================================================

def test_error_section():

    result = build_report(
        make_analysis_result()
    )

    errors = result[
        'sections'
    ][
        'errors'
    ]

    assert errors[
        'available'
    ] is True

    assert errors[
        'target_task'
    ] == 'regression'

    assert errors[
        'mean_absolute_error'
    ] == 4.0


# ==========================================================
# RELIABILITY SECTION
# ==========================================================

def test_reliability_section():

    result = build_report(
        make_analysis_result()
    )

    reliability = result[
        'sections'
    ][
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
    ] == 0.91


# ==========================================================
# MONITORING SECTION
# ==========================================================

def test_monitoring_section():

    result = build_report(
        make_analysis_result()
    )

    monitoring = result[
        'sections'
    ][
        'monitoring'
    ]

    assert monitoring[
        'available'
    ] is True

    assert monitoring[
        'status'
    ] == 'stable'

    assert monitoring[
        'alert_count'
    ] == 0

    assert monitoring[
        'alerts'
    ] == []


# ==========================================================
# ALERT SECTION
# ==========================================================

def test_alert_section():

    result = build_report(
        make_analysis_result()
    )

    alerts = result[
        'sections'
    ][
        'alerts'
    ]

    assert alerts[
        'available'
    ] is True

    assert alerts[
        'alert_count'
    ] == 1

    assert alerts[
        'high_count'
    ] == 1

    assert len(
        alerts[
            'alerts'
        ]
    ) == 1


# ==========================================================
# RECOMMENDATION SECTION
# ==========================================================

def test_recommendation_section():

    result = build_report(
        make_analysis_result()
    )

    recommendations = result[
        'sections'
    ][
        'recommendations'
    ]

    assert recommendations[
        'available'
    ] is True

    assert recommendations[
        'recommendation_count'
    ] == 1

    assert len(
        recommendations[
            'recommendations'
        ]
    ) == 1


# ==========================================================
# EXECUTIVE SUMMARY
# ==========================================================

def test_executive_summary():

    result = build_report(
        make_analysis_result()
    )

    summary = result[
        'executive_summary'
    ]

    assert isinstance(
        summary,
        list,
    )

    assert len(
        summary
    ) == 5

    assert (
        '3 prediction(s) are available.'
        in summary
    )


# ==========================================================
# MISSING OPTIONAL SECTIONS
# ==========================================================

def test_missing_optional_sections():

    analysis = {

        'status':
            'valid',

        'prediction_analysis': {

            'has_predictions':
                True,

            'prediction_count':
                2,

            'target_name':
                'Target_A',

            'target_task':
                'regression',

            'prediction_values':
                [10, 20],
        },

        'executive_summary': [

            '2 prediction(s) are available.',
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
# EMPTY ANALYSIS
# ==========================================================

def test_insufficient_analysis_data():

    analysis = {

        'status':
            'insufficient_data',

        'prediction_analysis': {

            'has_predictions':
                False,

            'prediction_count':
                0,

            'target_name':
                None,

            'target_task':
                None,

            'prediction_values':
                [],
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


# ==========================================================
# STATUS HELPERS
# ==========================================================

def test_is_report_available():

    result = build_report(
        make_analysis_result()
    )

    assert (
        is_report_available(
            result
        )
        is True
    )


def test_is_report_available_false():

    result = build_report({

        'status':
            'insufficient_data',

        'prediction_analysis': {

            'has_predictions':
                False,

            'prediction_count':
                0,
        },

        'executive_summary':
            [],
    })

    assert (
        is_report_available(
            result
        )
        is False
    )


def test_has_report_data():

    result = build_report(
        make_analysis_result()
    )

    assert (
        has_report_data(
            result
        )
        is True
    )


def test_has_report_data_false():

    result = build_report({

        'status':
            'insufficient_data',

        'prediction_analysis': {

            'has_predictions':
                False,

            'prediction_count':
                0,
        },

        'executive_summary':
            [],
    })

    assert (
        has_report_data(
            result
        )
        is False
    )


# ==========================================================
# VALIDATION
# ==========================================================

def test_missing_analysis_result():

    with pytest.raises(
        ValueError,
        match='analysis_result is required',
    ):

        build_report(
            None
        )


def test_invalid_analysis_result():

    with pytest.raises(
        ValueError,
        match='analysis_result must be a dictionary',
    ):

        build_report(
            []
        )


def test_missing_analysis_status():

    analysis = {

        'prediction_analysis': {

            'has_predictions':
                True,

            'prediction_count':
                1,
        },
    }

    with pytest.raises(
        ValueError,
        match='analysis_result status is required',
    ):

        build_report(
            analysis
        )


# ==========================================================
# DATA NORMALIZATION
# ==========================================================

def test_alerts_are_normalized_to_list():

    analysis = make_analysis_result()

    analysis[
        'alert_analysis'
    ][
        'alerts'
    ] = None

    result = build_report(
        analysis
    )

    assert result[
        'sections'
    ][
        'alerts'
    ][
        'alerts'
    ] == []


def test_recommendations_are_normalized_to_list():

    analysis = make_analysis_result()

    analysis[
        'recommendation_analysis'
    ][
        'recommendations'
    ] = None

    result = build_report(
        analysis
    )

    assert result[
        'sections'
    ][
        'recommendations'
    ][
        'recommendations'
    ] == []


# ==========================================================
# TARGET PRESERVATION
# ==========================================================

def test_report_preserves_target_identity():

    analysis = make_analysis_result()

    result = build_report(
        analysis
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


# ==========================================================
# INPUT IMMUTABILITY
# ==========================================================

def test_report_does_not_modify_analysis_input():

    analysis = make_analysis_result()

    original = {

        'status':
            analysis['status'],

        'prediction_analysis':
            dict(
                analysis[
                    'prediction_analysis'
                ]
            ),
    }

    build_report(
        analysis
    )

    assert analysis[
        'status'
    ] == original[
        'status'
    ]

    assert analysis[
        'prediction_analysis'
    ] == original[
        'prediction_analysis'
    ]


# ==========================================================
# COMPATIBILITY WRAPPER
# ==========================================================

def test_generate_report_wrapper():

    analysis = make_analysis_result()

    direct = build_report(
        analysis
    )

    wrapped = generate_report(
        analysis
    )

    assert wrapped == direct


# ==========================================================
# INVALID HELPER INPUTS
# ==========================================================

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