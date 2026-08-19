# ==========================================================
# ANALYSIS CONTRACT TESTS
# ==========================================================

from ml.analysis.analyzer import (
    ANALYSIS_VALID,
    ANALYSIS_INSUFFICIENT_DATA,
    analyze_system,
)


# ==========================================================
# HELPERS
# ==========================================================

def _prediction_result():
    return {
        'target_name': 'Target_Test',
        'target_task': 'regression',
        'predictions': [100, 120, 140],
    }


def _evaluation_result():
    return {
        'target_name': 'Target_Test',
        'target_task': 'regression',
        'actual_values': [90, 110, 130],
        'predicted_values': [100, 120, 140],
        'metrics': {
            'mae': 10.0,
        },
    }


def _reliability_result():
    return {
        'status': 'reliable',
        'reliability_level': 'high',
        'quality_score': 0.92,
        'sample_count': 100,
    }


def _monitoring_result():
    return {
        'status': 'valid',
        'alert_count': 0,
        'alerts': [],
    }


def _alert_result():
    return {
        'status': 'valid',
        'alert_count': 1,
        'alerts': [
            {
                'alert_type': 'high_error',
                'severity': 'high',
                'target_name': 'Target_Test',
            }
        ],
    }


def _recommendation_result():
    return {
        'status': 'valid',
        'recommendation_count': 1,
        'recommendations': [
            {
                'recommendation_type': 'review_model',
                'priority': 'high',
                'target_name': 'Target_Test',
            }
        ],
    }


# ==========================================================
# TOP-LEVEL RESULT CONTRACT
# ==========================================================

def test_analysis_result_contract():

    result = analyze_system(
        _prediction_result()
    )

    assert isinstance(
        result,
        dict,
    )

    required_keys = {
        'status',
        'prediction_analysis',
        'error_analysis',
        'reliability_analysis',
        'monitoring_analysis',
        'alert_analysis',
        'recommendation_analysis',
        'executive_summary',
    }

    assert required_keys.issubset(
        result.keys()
    )


# ==========================================================
# VALID STATUS CONTRACT
# ==========================================================

def test_analysis_valid_status_contract():

    result = analyze_system(
        _prediction_result()
    )

    assert (
        result['status']
        == ANALYSIS_VALID
    )


# ==========================================================
# PREDICTION CONTRACT
# ==========================================================

def test_prediction_analysis_contract():

    result = analyze_system(
        _prediction_result()
    )

    prediction = result[
        'prediction_analysis'
    ]

    assert isinstance(
        prediction,
        dict,
    )

    required_keys = {
        'prediction_count',
        'target_name',
        'target_task',
        'has_predictions',
        'prediction_values',
        'numeric_predictions',
        'confidence',
    }

    assert required_keys.issubset(
        prediction.keys()
    )

    assert (
        prediction['target_name']
        == 'Target_Test'
    )

    assert (
        prediction['target_task']
        == 'regression'
    )


# ==========================================================
# OPTIONAL COMPONENT CONTRACT
# ==========================================================

def test_optional_components_have_stable_contracts():

    result = analyze_system(
        _prediction_result()
    )

    reliability = result[
        'reliability_analysis'
    ]

    monitoring = result[
        'monitoring_analysis'
    ]

    alerts = result[
        'alert_analysis'
    ]

    recommendations = result[
        'recommendation_analysis'
    ]

    assert isinstance(
        reliability,
        dict,
    )

    assert isinstance(
        monitoring,
        dict,
    )

    assert isinstance(
        alerts,
        dict,
    )

    assert isinstance(
        recommendations,
        dict,
    )


# ==========================================================
# FULL ANALYSIS CONTRACT
# ==========================================================

def test_full_analysis_preserves_all_layers():

    result = analyze_system(
        _prediction_result(),
        evaluation_result=_evaluation_result(),
        reliability_result=_reliability_result(),
        monitoring_result=_monitoring_result(),
        alert_result=_alert_result(),
        recommendation_result=_recommendation_result(),
    )

    assert (
        result['status']
        == ANALYSIS_VALID
    )

    assert (
        result['error_analysis']
        is not None
    )

    assert (
        result['reliability_analysis']['available']
        is True
    )

    assert (
        result['monitoring_analysis']['available']
        is True
    )

    assert (
        result['alert_analysis']['available']
        is True
    )

    assert (
        result['recommendation_analysis']['available']
        is True
    )


# ==========================================================
# TARGET PRESERVATION
# ==========================================================

def test_analysis_preserves_target_identity():

    result = analyze_system(
        _prediction_result(),
        evaluation_result=_evaluation_result(),
    )

    assert (
        result[
            'prediction_analysis'
        ]['target_name']
        == 'Target_Test'
    )

    assert (
        result[
            'prediction_analysis'
        ]['target_task']
        == 'regression'
    )

    assert (
        result[
            'error_analysis'
        ]['target_task']
        == 'regression'
    )


# ==========================================================
# OPTIONAL LAYERS CAN BE ABSENT
# ==========================================================

def test_analysis_accepts_missing_optional_layers():

    result = analyze_system(
        _prediction_result()
    )

    assert (
        result['error_analysis']
        is None
    )

    assert (
        result[
            'reliability_analysis'
        ]['available']
        is False
    )

    assert (
        result[
            'monitoring_analysis'
        ]['available']
        is False
    )

    assert (
        result[
            'alert_analysis'
        ]['available']
        is False
    )

    assert (
        result[
            'recommendation_analysis'
        ]['available']
        is False
    )


# ==========================================================
# EXECUTIVE SUMMARY CONTRACT
# ==========================================================

def test_executive_summary_contract():

    result = analyze_system(
        _prediction_result()
    )

    summary = result[
        'executive_summary'
    ]

    assert isinstance(
        summary,
        list,
    )

    assert len(summary) > 0

    assert all(
        isinstance(
            statement,
            str,
        )
        for statement in summary
    )


# ==========================================================
# INSUFFICIENT DATA CONTRACT
# ==========================================================

def test_analysis_insufficient_data_contract():

    result = analyze_system(
        {
            'target_name': 'Target_Test',
            'target_task': 'regression',
            'predictions': [],
        }
    )

    assert (
        result['status']
        == ANALYSIS_INSUFFICIENT_DATA
    )


# ==========================================================
# INVALID INPUT CONTRACT
# ==========================================================

def test_analysis_rejects_missing_prediction_result():

    try:

        analyze_system(
            None
        )

    except ValueError:

        pass

    else:

        raise AssertionError(
            'analyze_system() must reject '
            'missing prediction_result.'
        )


def test_analysis_rejects_non_dictionary_prediction_result():

    try:

        analyze_system(
            ['invalid']
        )

    except ValueError:

        pass

    else:

        raise AssertionError(
            'analyze_system() must reject '
            'non-dictionary prediction_result.'
        )


# ==========================================================
# LAYER INDEPENDENCE
# ==========================================================

def test_analysis_does_not_require_all_upstream_layers():

    result = analyze_system(
        _prediction_result(),
        alert_result=_alert_result(),
    )

    assert (
        result['status']
        == ANALYSIS_VALID
    )

    assert (
        result[
            'alert_analysis'
        ]['available']
        is True
    )

    assert (
        result['error_analysis']
        is None
    )

    assert (
        result[
            'reliability_analysis'
        ]['available']
        is False
    )

    assert (
        result[
            'monitoring_analysis'
        ]['available']
        is False
    )


# ==========================================================
# COMPLETE PIPELINE CONTRACT
# ==========================================================

def test_complete_analysis_pipeline_contract():

    result = analyze_system(
        _prediction_result(),
        evaluation_result=_evaluation_result(),
        reliability_result=_reliability_result(),
        monitoring_result=_monitoring_result(),
        alert_result=_alert_result(),
        recommendation_result=_recommendation_result(),
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
        result[
            'prediction_analysis'
        ]['has_predictions']
        is True
    )

    assert (
        result[
            'error_analysis'
        ] is not None
    )

    assert (
        result[
            'reliability_analysis'
        ]['available']
        is True
    )

    assert (
        result[
            'monitoring_analysis'
        ]['available']
        is True
    )

    assert (
        result[
            'alert_analysis'
        ]['available']
        is True
    )

    assert (
        result[
            'recommendation_analysis'
        ]['available']
        is True
    )

    assert isinstance(
        result[
            'executive_summary'
        ],
        list,
    )