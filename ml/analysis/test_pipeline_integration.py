# ==========================================================
# ANALYSIS PIPELINE INTEGRATION TESTS
# ==========================================================

from ml.analysis.analyzer import (
    ANALYSIS_VALID,
)

from ml.analysis.pipeline import (
    run_analysis_pipeline,
    is_analysis_available,
    has_analysis_data,
)


# ==========================================================
# TEST DATA
# ==========================================================

def _prediction_result(
    target_name='Target_Expense_Total_1D',
    target_task='regression',
):
    """
    Simulate a production prediction result.
    """

    return {

        'target_name':
            target_name,

        'target_task':
            target_task,

        'predictions':
            [100.0, 120.0, 140.0],

        'confidence':
            0.91,
    }


def _evaluation_result():
    """
    Simulate an upstream evaluation result.
    """

    return {

        'target_name':
            'Target_Expense_Total_1D',

        'target_task':
            'regression',

        'actual_values':
            [95.0, 125.0, 135.0],

        'predicted_values':
            [100.0, 120.0, 140.0],

        'metrics': {

            'mae':
                5.0,

            'rmse':
                5.0,
        },
    }


def _reliability_result():
    """
    Simulate prediction reliability output.
    """

    return {

        'target_name':
            'Target_Expense_Total_1D',

        'status':
            'reliable',

        'reliability_level':
            'high',

        'quality_score':
            0.91,

        'sample_count':
            100,

        'expected_calibration_error':
            0.04,
    }


def _monitoring_result():
    """
    Simulate prediction reliability monitoring output.
    """

    return {

        'target_name':
            'Target_Expense_Total_1D',

        'status':
            'stable',

        'alert_count':
            0,

        'alerts':
            [],
    }


def _alert_result():
    """
    Simulate alert-layer output.
    """

    return {

        'status':
            'valid',

        'alert_count':
            1,

        'target_name':
            'Target_Expense_Total_1D',

        'alerts': [

            {

                'alert_type':
                    'low_reliability',

                'severity':
                    'high',

                'message':
                    'Prediction reliability is low.',

                'target_name':
                    'Target_Expense_Total_1D',

            }

        ],
    }


def _recommendation_result():
    """
    Simulate recommendation-layer output.
    """

    return {

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

                'target_name':
                    'Target_Expense_Total_1D',

            }

        ],
    }


# ==========================================================
# BASIC END-TO-END FLOW
# ==========================================================

def test_analysis_pipeline_accepts_prediction_result():

    result = run_analysis_pipeline(
        prediction_result=
            _prediction_result()
    )

    assert isinstance(
        result,
        dict,
    )

    assert result[
        'status'
    ] == ANALYSIS_VALID

    assert result[
        'analysis'
    ][
        'prediction_analysis'
    ][
        'has_predictions'
    ] is True


# ==========================================================
# FULL UPSTREAM FLOW
# ==========================================================

def test_analysis_pipeline_accepts_all_upstream_layers():

    result = run_analysis_pipeline(

        prediction_result=
            _prediction_result(),

        evaluation_result=
            _evaluation_result(),

        reliability_result=
            _reliability_result(),

        monitoring_result=
            _monitoring_result(),

        alert_result=
            _alert_result(),

        recommendation_result=
            _recommendation_result(),
    )

    assert result[
        'status'
    ] == ANALYSIS_VALID

    analysis = result[
        'analysis'
    ]

    assert analysis[
        'prediction_analysis'
    ] is not None

    assert analysis[
        'error_analysis'
    ] is not None

    assert analysis[
        'reliability_analysis'
    ] is not None

    assert analysis[
        'monitoring_analysis'
    ] is not None

    assert analysis[
        'alert_analysis'
    ] is not None

    assert analysis[
        'recommendation_analysis'
    ] is not None


# ==========================================================
# PREDICTION → ANALYSIS
# ==========================================================

def test_prediction_layer_reaches_analysis():

    prediction = _prediction_result()

    result = run_analysis_pipeline(
        prediction_result=prediction
    )

    prediction_analysis = (
        result[
            'analysis'
        ][
            'prediction_analysis'
        ]
    )

    assert prediction_analysis[
        'prediction_count'
    ] == 3

    assert prediction_analysis[
        'prediction_values'
    ] == [
        100.0,
        120.0,
        140.0,
    ]

    assert prediction_analysis[
        'target_name'
    ] == 'Target_Expense_Total_1D'


# ==========================================================
# EVALUATION → ERROR ANALYSIS
# ==========================================================

def test_evaluation_layer_reaches_error_analysis():

    result = run_analysis_pipeline(

        prediction_result=
            _prediction_result(),

        evaluation_result=
            _evaluation_result(),
    )

    error_analysis = (
        result[
            'analysis'
        ][
            'error_analysis'
        ]
    )

    assert error_analysis is not None

    assert error_analysis[
        'target_task'
    ] == 'regression'

    assert error_analysis[
        'sample_count'
    ] == 3

    assert error_analysis[
        'mean_absolute_error'
    ] == 5.0


# ==========================================================
# RELIABILITY → ANALYSIS
# ==========================================================

def test_reliability_layer_reaches_analysis():

    result = run_analysis_pipeline(

        prediction_result=
            _prediction_result(),

        reliability_result=
            _reliability_result(),
    )

    reliability_analysis = (
        result[
            'analysis'
        ][
            'reliability_analysis'
        ]
    )

    assert reliability_analysis[
        'available'
    ] is True

    assert reliability_analysis[
        'status'
    ] == 'reliable'

    assert reliability_analysis[
        'reliability_level'
    ] == 'high'

    assert reliability_analysis[
        'quality_score'
    ] == 0.91


# ==========================================================
# MONITORING → ANALYSIS
# ==========================================================

def test_monitoring_layer_reaches_analysis():

    result = run_analysis_pipeline(

        prediction_result=
            _prediction_result(),

        monitoring_result=
            _monitoring_result(),
    )

    monitoring_analysis = (
        result[
            'analysis'
        ][
            'monitoring_analysis'
        ]
    )

    assert monitoring_analysis[
        'available'
    ] is True

    assert monitoring_analysis[
        'status'
    ] == 'stable'

    assert monitoring_analysis[
        'alert_count'
    ] == 0


# ==========================================================
# ALERTS → ANALYSIS
# ==========================================================

def test_alert_layer_reaches_analysis():

    result = run_analysis_pipeline(

        prediction_result=
            _prediction_result(),

        alert_result=
            _alert_result(),
    )

    alert_analysis = (
        result[
            'analysis'
        ][
            'alert_analysis'
        ]
    )

    assert alert_analysis[
        'available'
    ] is True

    assert alert_analysis[
        'alert_count'
    ] == 1

    assert alert_analysis[
        'high_count'
    ] == 1


# ==========================================================
# RECOMMENDATIONS → ANALYSIS
# ==========================================================

def test_recommendation_layer_reaches_analysis():

    result = run_analysis_pipeline(

        prediction_result=
            _prediction_result(),

        recommendation_result=
            _recommendation_result(),
    )

    recommendation_analysis = (
        result[
            'analysis'
        ][
            'recommendation_analysis'
        ]
    )

    assert recommendation_analysis[
        'available'
    ] is True

    assert recommendation_analysis[
        'recommendation_count'
    ] == 1

    assert len(
        recommendation_analysis[
            'recommendations'
        ]
    ) == 1


# ==========================================================
# EXECUTIVE SUMMARY
# ==========================================================

def test_full_pipeline_produces_executive_summary():

    result = run_analysis_pipeline(

        prediction_result=
            _prediction_result(),

        evaluation_result=
            _evaluation_result(),

        reliability_result=
            _reliability_result(),

        monitoring_result=
            _monitoring_result(),

        alert_result=
            _alert_result(),

        recommendation_result=
            _recommendation_result(),
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

    combined_summary = ' '.join(
        summary
    )

    assert (
        'prediction'
        in combined_summary.lower()
    )


# ==========================================================
# TARGET IDENTITY
# ==========================================================

def test_pipeline_preserves_target_identity():

    target_name = (
        'Target_Expense_Total_1D'
    )

    result = run_analysis_pipeline(

        prediction_result=
            _prediction_result(
                target_name=target_name
            ),

        evaluation_result=
            _evaluation_result(),

        reliability_result=
            _reliability_result(),

        monitoring_result=
            _monitoring_result(),

        alert_result=
            _alert_result(),

        recommendation_result=
            _recommendation_result(),
    )

    assert result[
        'target_name'
    ] == target_name

    assert result[
        'analysis'
    ][
        'prediction_analysis'
    ][
        'target_name'
    ] == target_name


# ==========================================================
# TARGET ISOLATION
# ==========================================================

def test_pipeline_keeps_targets_isolated():

    first_target = (
        'Target_Expense_Total_1D'
    )

    second_target = (
        'Target_Income_Total_1D'
    )

    first_result = run_analysis_pipeline(

        prediction_result=
            _prediction_result(
                target_name=first_target
            )
    )

    second_result = run_analysis_pipeline(

        prediction_result=
            _prediction_result(
                target_name=second_target
            )
    )

    assert first_result[
        'target_name'
    ] == first_target

    assert second_result[
        'target_name'
    ] == second_target

    assert first_result[
        'target_name'
    ] != second_result[
        'target_name'
    ]

    assert first_result[
        'analysis'
    ][
        'prediction_analysis'
    ][
        'target_name'
    ] == first_target

    assert second_result[
        'analysis'
    ][
        'prediction_analysis'
    ][
        'target_name'
    ] == second_target


# ==========================================================
# OPTIONAL LAYER COMBINATIONS
# ==========================================================

def test_pipeline_accepts_partial_upstream_flow():

    result = run_analysis_pipeline(

        prediction_result=
            _prediction_result(),

        reliability_result=
            _reliability_result(),

        alert_result=
            _alert_result(),
    )

    analysis = result[
        'analysis'
    ]

    assert analysis[
        'prediction_analysis'
    ][
        'has_predictions'
    ] is True

    assert analysis[
        'reliability_analysis'
    ][
        'available'
    ] is True

    assert analysis[
        'alert_analysis'
    ][
        'available'
    ] is True

    assert analysis[
        'error_analysis'
    ] is None


# ==========================================================
# MISSING OPTIONAL LAYERS
# ==========================================================

def test_pipeline_remains_valid_without_optional_layers():

    result = run_analysis_pipeline(

        prediction_result=
            _prediction_result()
    )

    analysis = result[
        'analysis'
    ]

    assert result[
        'status'
    ] == ANALYSIS_VALID

    assert analysis[
        'prediction_analysis'
    ][
        'has_predictions'
    ] is True

    assert analysis[
        'error_analysis'
    ] is None

    assert analysis[
        'reliability_analysis'
    ][
        'available'
    ] is False

    assert analysis[
        'monitoring_analysis'
    ][
        'available'
    ] is False

    assert analysis[
        'alert_analysis'
    ][
        'available'
    ] is False

    assert analysis[
        'recommendation_analysis'
    ][
        'available'
    ] is False


# ==========================================================
# PIPELINE HELPERS
# ==========================================================

def test_analysis_availability_after_full_pipeline():

    result = run_analysis_pipeline(

        prediction_result=
            _prediction_result(),

        evaluation_result=
            _evaluation_result(),

        reliability_result=
            _reliability_result(),

        monitoring_result=
            _monitoring_result(),
    )

    assert (
        is_analysis_available(
            result
        )
        is True
    )

    assert (
        has_analysis_data(
            result
        )
        is True
    )


# ==========================================================
# INPUT IMMUTABILITY
# ==========================================================

def test_pipeline_does_not_modify_upstream_prediction():

    prediction = _prediction_result()

    original_prediction = (
        prediction.copy()
    )

    run_analysis_pipeline(
        prediction_result=prediction
    )

    assert prediction == (
        original_prediction
    )


# ==========================================================
# COMPLETE DATA FLOW CONTRACT
# ==========================================================

def test_complete_analysis_pipeline_contract():

    result = run_analysis_pipeline(

        prediction_result=
            _prediction_result(),

        evaluation_result=
            _evaluation_result(),

        reliability_result=
            _reliability_result(),

        monitoring_result=
            _monitoring_result(),

        alert_result=
            _alert_result(),

        recommendation_result=
            _recommendation_result(),
    )

    # ------------------------------------------------------
    # Top-level pipeline contract
    # ------------------------------------------------------

    assert set(
        result.keys()
    ) >= {

        'status',

        'analysis',

        'target_name',

        'target_task',
    }

    assert result[
        'status'
    ] == ANALYSIS_VALID

    assert isinstance(
        result[
            'analysis'
        ],
        dict,
    )

    # ------------------------------------------------------
    # Analysis contract
    # ------------------------------------------------------

    analysis = result[
        'analysis'
    ]

    assert set(
        analysis.keys()
    ) >= {

        'status',

        'prediction_analysis',

        'error_analysis',

        'reliability_analysis',

        'monitoring_analysis',

        'alert_analysis',

        'recommendation_analysis',

        'executive_summary',
    }

    # ------------------------------------------------------
    # Target contract
    # ------------------------------------------------------

    assert result[
        'target_name'
    ] == 'Target_Expense_Total_1D'

    assert result[
        'target_task'
    ] == 'regression'

    # ------------------------------------------------------
    # Final summary contract
    # ------------------------------------------------------

    assert isinstance(
        analysis[
            'executive_summary'
        ],
        list,
    )

    assert len(
        analysis[
            'executive_summary'
        ]
    ) > 0