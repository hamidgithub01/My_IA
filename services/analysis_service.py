# ==========================================================
# ANALYSIS SERVICE
# ==========================================================

from ml.analysis.pipeline import (
    run_analysis_pipeline,
)


# ==========================================================
# BASIC VALIDATION
# ==========================================================

def _validate_optional_result(
    result,
    name,
):
    """
    Validate an optional subsystem result.
    """

    if result is None:
        return

    if not isinstance(
        result,
        dict,
    ):
        raise ValueError(
            f'{name} must be a dictionary.'
        )


# ==========================================================
# RUN ANALYSIS
# ==========================================================

def run_analysis(
    prediction_result=None,
    evaluation_result=None,
    reliability_result=None,
    monitoring_result=None,
    alert_result=None,
    recommendation_result=None,
):
    """
    Run the Analysis pipeline for the frontend.

    This service is the boundary between the frontend
    and the ML Analysis layer.

    No analysis logic is implemented here.
    The actual analysis remains inside ml.analysis.
    """

    if prediction_result is None:
        prediction_result = {}

    if not isinstance(
        prediction_result,
        dict,
    ):
        raise ValueError(
            'prediction_result must be a dictionary.'
        )

    _validate_optional_result(
        evaluation_result,
        'evaluation_result',
    )

    _validate_optional_result(
        reliability_result,
        'reliability_result',
    )

    _validate_optional_result(
        monitoring_result,
        'monitoring_result',
    )

    _validate_optional_result(
        alert_result,
        'alert_result',
    )

    _validate_optional_result(
        recommendation_result,
        'recommendation_result',
    )

    return run_analysis_pipeline(
        prediction_result=prediction_result,
        evaluation_result=evaluation_result,
        reliability_result=reliability_result,
        monitoring_result=monitoring_result,
        alert_result=alert_result,
        recommendation_result=recommendation_result,
    )


# ==========================================================
# EMPTY ANALYSIS
# ==========================================================

def get_empty_analysis():
    """
    Return a valid Analysis result when no upstream data
    is currently available.

    No synthetic prediction values are introduced.
    """

    return run_analysis(
        prediction_result={}
    )


# ==========================================================
# FRONTEND VIEW HELPERS
# ==========================================================

def get_analysis_status(
    analysis_result,
):
    """
    Return the high-level Analysis status.
    """

    if not isinstance(
        analysis_result,
        dict,
    ):
        raise ValueError(
            'analysis_result must be a dictionary.'
        )

    return analysis_result.get(
        'status'
    )


def get_analysis_data(
    analysis_result,
):
    """
    Return the underlying analysis payload.
    """

    if not isinstance(
        analysis_result,
        dict,
    ):
        raise ValueError(
            'analysis_result must be a dictionary.'
        )

    analysis = analysis_result.get(
        'analysis'
    )

    if not isinstance(
        analysis,
        dict,
    ):
        return {}

    return analysis


# ==========================================================
# COMPONENT ACCESSORS
# ==========================================================

def get_prediction_analysis(
    analysis_result,
):
    return get_analysis_data(
        analysis_result
    ).get(
        'prediction_analysis'
    )


def get_error_analysis(
    analysis_result,
):
    return get_analysis_data(
        analysis_result
    ).get(
        'error_analysis'
    )


def get_reliability_analysis(
    analysis_result,
):
    return get_analysis_data(
        analysis_result
    ).get(
        'reliability_analysis'
    )


def get_monitoring_analysis(
    analysis_result,
):
    return get_analysis_data(
        analysis_result
    ).get(
        'monitoring_analysis'
    )


def get_alert_analysis(
    analysis_result,
):
    return get_analysis_data(
        analysis_result
    ).get(
        'alert_analysis'
    )


def get_recommendation_analysis(
    analysis_result,
):
    return get_analysis_data(
        analysis_result
    ).get(
        'recommendation_analysis'
    )


def get_executive_summary(
    analysis_result,
):
    summary = get_analysis_data(
        analysis_result
    ).get(
        'executive_summary'
    )

    if not isinstance(
        summary,
        list,
    ):
        return []

    return summary