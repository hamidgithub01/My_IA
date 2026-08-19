# ==========================================================
# REPORTING PIPELINE
# ==========================================================

from ml.reporting.reporter import (
    REPORT_VALID,
    REPORT_INSUFFICIENT_DATA,
    build_report,
)


# ==========================================================
# BASIC VALIDATION
# ==========================================================

def _validate_analysis_result(
    analysis_result,
):
    """
    Validate the mandatory Analysis result.
    """

    if analysis_result is None:

        raise ValueError(
            'analysis_result is required.'
        )

    if not isinstance(
        analysis_result,
        dict,
    ):

        raise ValueError(
            'analysis_result must be a dictionary.'
        )


# ==========================================================
# PIPELINE EXECUTION
# ==========================================================

def run_reporting_pipeline(
    analysis_result,
):
    """
    Execute the complete Reporting pipeline.

    The pipeline receives the result produced by the
    Analysis layer and delegates report construction
    to reporter.py.

    Required:

        analysis_result

    The pipeline does not modify the Analysis result
    and does not reimplement reporting logic.
    """

    # ------------------------------------------------------
    # Validate mandatory input
    # ------------------------------------------------------

    _validate_analysis_result(
        analysis_result
    )

    # ------------------------------------------------------
    # Delegate to Reporting layer
    # ------------------------------------------------------

    report_result = build_report(
        analysis_result
    )

    # ------------------------------------------------------
    # Preserve target identity
    # ------------------------------------------------------

    prediction_analysis = (
        analysis_result.get(
            'prediction_analysis'
        )
    )

    if not isinstance(
        prediction_analysis,
        dict,
    ):

        prediction_analysis = {}

    target_name = prediction_analysis.get(
        'target_name'
    )

    target_task = prediction_analysis.get(
        'target_task'
    )

    # ------------------------------------------------------
    # Pipeline result
    # ------------------------------------------------------

    return {

        'status':
            report_result.get(
                'status'
            ),

        'report':
            report_result,

        'target_name':
            target_name,

        'target_task':
            target_task,
    }


# ==========================================================
# PIPELINE STATUS HELPERS
# ==========================================================

def is_report_available(
    pipeline_result,
):
    """
    Return True when the Reporting pipeline produced
    a valid report.
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
        == REPORT_VALID
    )


def has_report_data(
    pipeline_result,
):
    """
    Return True when the pipeline contains report data.
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

    report = pipeline_result.get(
        'report'
    )

    if not isinstance(
        report,
        dict,
    ):

        return False

    return (
        report.get(
            'status'
        )
        == REPORT_VALID
    )


# ==========================================================
# BACKWARD / INTEGRATION COMPATIBILITY
# ==========================================================

def generate_reporting_pipeline(
    analysis_result,
):
    """
    Compatibility wrapper for the Reporting pipeline.

    Delegates to run_reporting_pipeline().
    """

    return run_reporting_pipeline(
        analysis_result=analysis_result
    )


def run_report_pipeline(
    analysis_result,
):
    """
    Compatibility alias for the Reporting pipeline.
    """

    return run_reporting_pipeline(
        analysis_result=analysis_result
    )