# ==========================================================
# ANALYSIS PIPELINE
# ==========================================================

from ml.analysis.analyzer import (
    ANALYSIS_VALID,
    ANALYSIS_INSUFFICIENT_DATA,
    analyze_system,
)


# ==========================================================
# BASIC VALIDATION
# ==========================================================

def _validate_prediction_result(
    prediction_result,
):
    """
    Validate the mandatory prediction result.
    """

    if prediction_result is None:

        raise ValueError(
            'prediction_result is required.'
        )

    if not isinstance(
        prediction_result,
        dict,
    ):

        raise ValueError(
            'prediction_result must be a dictionary.'
        )


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
# PIPELINE EXECUTION
# ==========================================================

def run_analysis_pipeline(
    prediction_result,
    evaluation_result=None,
    reliability_result=None,
    monitoring_result=None,
    alert_result=None,
    recommendation_result=None,
):
    """
    Execute the complete Analysis pipeline.

    The pipeline receives results produced by upstream
    system layers and delegates the actual analysis to
    analyze_system().

    Required:

        prediction_result

    Optional:

        evaluation_result
        reliability_result
        monitoring_result
        alert_result
        recommendation_result

    The pipeline does not modify upstream results and
    does not reimplement analysis logic.
    """

    # ------------------------------------------------------
    # Mandatory input
    # ------------------------------------------------------

    _validate_prediction_result(
        prediction_result
    )

    # ------------------------------------------------------
    # Optional inputs
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # Delegate to Analysis layer
    # ------------------------------------------------------

    analysis_result = analyze_system(
        prediction_result=prediction_result,
        evaluation_result=evaluation_result,
        reliability_result=reliability_result,
        monitoring_result=monitoring_result,
        alert_result=alert_result,
        recommendation_result=recommendation_result,
    )

    # ------------------------------------------------------
    # Pipeline result
    # ------------------------------------------------------

    return {

        'status':
            analysis_result[
                'status'
            ],

        'analysis':
            analysis_result,

        'target_name':
            prediction_result.get(
                'target_name'
            ),

        'target_task':
            prediction_result.get(
                'target_task'
            ),
    }


# ==========================================================
# PIPELINE STATUS HELPERS
# ==========================================================

def is_analysis_available(
    pipeline_result,
):
    """
    Return True when the Analysis pipeline produced
    a valid analysis result.
    """

    if pipeline_result is None:

        raise ValueError(
            'pipeline_result is required.'
        )

    if not isinstance(
        pipeline_result,
        dict,
    ):

        raise ValueError(
            'pipeline_result must be a dictionary.'
        )

    return (
        pipeline_result.get(
            'status'
        )
        == ANALYSIS_VALID
    )


def has_analysis_data(
    pipeline_result,
):
    """
    Return True when the pipeline contains analysis data.
    """

    if pipeline_result is None:

        raise ValueError(
            'pipeline_result is required.'
        )

    if not isinstance(
        pipeline_result,
        dict,
    ):

        raise ValueError(
            'pipeline_result must be a dictionary.'
        )

    analysis = pipeline_result.get(
        'analysis'
    )

    if not isinstance(
        analysis,
        dict,
    ):

        return False

    return (
        analysis.get(
            'status'
        )
        == ANALYSIS_VALID
    )


# ==========================================================
# BACKWARD / INTEGRATION COMPATIBILITY
# ==========================================================

def analyze_pipeline(
    prediction_result,
    evaluation_result=None,
    reliability_result=None,
    monitoring_result=None,
    alert_result=None,
    recommendation_result=None,
):
    """
    Compatibility wrapper for the Analysis pipeline.

    Delegates to run_analysis_pipeline().
    """

    return run_analysis_pipeline(
        prediction_result=prediction_result,
        evaluation_result=evaluation_result,
        reliability_result=reliability_result,
        monitoring_result=monitoring_result,
        alert_result=alert_result,
        recommendation_result=recommendation_result,
    )