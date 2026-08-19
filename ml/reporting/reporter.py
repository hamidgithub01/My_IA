# ==========================================================
# REPORTING STATUS
# ==========================================================

REPORT_VALID = 'valid'
REPORT_INSUFFICIENT_DATA = 'insufficient_data'


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


def _safe_list(value):
    """
    Safely convert a value into a list.
    """

    if value is None:

        return []

    if isinstance(
        value,
        list,
    ):

        return value

    try:

        return list(value)

    except TypeError:

        raise ValueError(
            'Expected a list-like value.'
        )


# ==========================================================
# SECTION BUILDERS
# ==========================================================

def _build_prediction_section(
    analysis_result,
):
    """
    Build the prediction reporting section.
    """

    prediction_analysis = (
        analysis_result.get(
            'prediction_analysis'
        )
        or {}
    )

    return {

        'available':
            prediction_analysis.get(
                'has_predictions',
                False,
            ),

        'prediction_count':
            prediction_analysis.get(
                'prediction_count',
                0,
            ),

        'target_name':
            prediction_analysis.get(
                'target_name'
            ),

        'target_task':
            prediction_analysis.get(
                'target_task'
            ),

        'prediction_values':
            _safe_list(
                prediction_analysis.get(
                    'prediction_values',
                    [],
                )
            ),

        'numeric_predictions':
            prediction_analysis.get(
                'numeric_predictions',
                False,
            ),

        'minimum_prediction':
            prediction_analysis.get(
                'minimum_prediction'
            ),

        'maximum_prediction':
            prediction_analysis.get(
                'maximum_prediction'
            ),

        'mean_prediction':
            prediction_analysis.get(
                'mean_prediction'
            ),

        'confidence':
            prediction_analysis.get(
                'confidence'
            ),
    }


def _build_error_section(
    analysis_result,
):
    """
    Build the error reporting section.
    """

    error_analysis = (
        analysis_result.get(
            'error_analysis'
        )
    )

    if error_analysis is None:

        return {

            'available':
                False,
        }

    section = dict(
        error_analysis
    )

    section[
        'available'
    ] = True

    return section


def _build_reliability_section(
    analysis_result,
):
    """
    Build the reliability reporting section.
    """

    reliability_analysis = (
        analysis_result.get(
            'reliability_analysis'
        )
        or {}
    )

    section = dict(
        reliability_analysis
    )

    section.setdefault(
        'available',
        False,
    )

    return section


def _build_monitoring_section(
    analysis_result,
):
    """
    Build the monitoring reporting section.
    """

    monitoring_analysis = (
        analysis_result.get(
            'monitoring_analysis'
        )
        or {}
    )

    section = dict(
        monitoring_analysis
    )

    section.setdefault(
        'available',
        False,
    )

    section[
        'alerts'
    ] = _safe_list(
        section.get(
            'alerts',
            [],
        )
    )

    return section


def _build_alert_section(
    analysis_result,
):
    """
    Build the alert reporting section.
    """

    alert_analysis = (
        analysis_result.get(
            'alert_analysis'
        )
        or {}
    )

    section = dict(
        alert_analysis
    )

    section.setdefault(
        'available',
        False,
    )

    section[
        'alerts'
    ] = _safe_list(
        section.get(
            'alerts',
            [],
        )
    )

    return section


def _build_recommendation_section(
    analysis_result,
):
    """
    Build the recommendation reporting section.
    """

    recommendation_analysis = (
        analysis_result.get(
            'recommendation_analysis'
        )
        or {}
    )

    section = dict(
        recommendation_analysis
    )

    section.setdefault(
        'available',
        False,
    )

    section[
        'recommendations'
    ] = _safe_list(
        section.get(
            'recommendations',
            [],
        )
    )

    return section


# ==========================================================
# EXECUTIVE SUMMARY
# ==========================================================

def _build_executive_summary(
    analysis_result,
):
    """
    Preserve the executive summary generated by Analysis.

    Reporting does not invent new conclusions.
    """

    return _safe_list(
        analysis_result.get(
            'executive_summary',
            [],
        )
    )


# ==========================================================
# REPORT BUILDER
# ==========================================================

def build_report(
    analysis_result,
):
    """
    Convert a complete Analysis result into a structured
    reporting result.

    Reporting only organizes information produced by the
    Analysis layer. It does not perform new analysis.
    """

    _validate_analysis_result(
        analysis_result
    )

    analysis_status = (
        analysis_result.get(
            'status'
        )
    )

    if analysis_status is None:

        raise ValueError(
            'analysis_result status is required.'
        )

    prediction_section = (
        _build_prediction_section(
            analysis_result
        )
    )

    error_section = (
        _build_error_section(
            analysis_result
        )
    )

    reliability_section = (
        _build_reliability_section(
            analysis_result
        )
    )

    monitoring_section = (
        _build_monitoring_section(
            analysis_result
        )
    )

    alert_section = (
        _build_alert_section(
            analysis_result
        )
    )

    recommendation_section = (
        _build_recommendation_section(
            analysis_result
        )
    )

    executive_summary = (
        _build_executive_summary(
            analysis_result
        )
    )

    has_report_data = any(
        [
            prediction_section[
                'available'
            ],

            error_section[
                'available'
            ],

            reliability_section[
                'available'
            ],

            monitoring_section[
                'available'
            ],

            alert_section[
                'available'
            ],

            recommendation_section[
                'available'
            ],
        ]
    )

    if has_report_data:

        status = REPORT_VALID

    else:

        status = (
            REPORT_INSUFFICIENT_DATA
        )

    return {

        'status':
            status,

        'analysis_status':
            analysis_status,

        'executive_summary':
            executive_summary,

        'sections': {

            'predictions':
                prediction_section,

            'errors':
                error_section,

            'reliability':
                reliability_section,

            'monitoring':
                monitoring_section,

            'alerts':
                alert_section,

            'recommendations':
                recommendation_section,
        },
    }


# ==========================================================
# REPORT STATUS HELPERS
# ==========================================================

def is_report_available(
    report_result,
):
    """
    Return True when a valid report is available.
    """

    if report_result is None:

        raise ValueError(
            'report_result is required.'
        )

    if not isinstance(
        report_result,
        dict,
    ):

        raise ValueError(
            'report_result must be a dictionary.'
        )

    return (
        report_result.get(
            'status'
        )
        == REPORT_VALID
    )


def has_report_data(
    report_result,
):
    """
    Return True when the report contains sections.
    """

    if report_result is None:

        raise ValueError(
            'report_result is required.'
        )

    if not isinstance(
        report_result,
        dict,
    ):

        raise ValueError(
            'report_result must be a dictionary.'
        )

    sections = report_result.get(
        'sections'
    )

    if not isinstance(
        sections,
        dict,
    ):

        return False

    return any(
        isinstance(
            section,
            dict,
        )
        and section.get(
            'available',
            False,
        )
        for section in sections.values()
    )


# ==========================================================
# BACKWARD / INTEGRATION COMPATIBILITY
# ==========================================================

def generate_report(
    analysis_result,
):
    """
    Compatibility wrapper for report generation.
    """

    return build_report(
        analysis_result
    )