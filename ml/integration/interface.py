from copy import deepcopy


# ==========================================================
# INTEGRATION STATUS
# ==========================================================

INTEGRATION_VALID = 'valid'
INTEGRATION_INVALID = 'invalid'
INTEGRATION_INSUFFICIENT_DATA = 'insufficient_data'


# ==========================================================
# INPUT VALIDATION
# ==========================================================

def _validate_prediction_result(
    prediction_result,
):
    """
    Validate the prediction result received from
    the prediction layer.
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


def _validate_analysis_result(
    analysis_result,
):
    """
    Validate the analysis result received from
    the analysis layer.
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


def _validate_report_result(
    report_result,
):
    """
    Validate the reporting result received from
    the reporting layer.
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


# ==========================================================
# PREDICTION INPUT
# ==========================================================

def prepare_prediction_input(
    target_name,
    features,
):
    """
    Prepare prediction input for the UI.

    No prediction is performed here.
    """

    if target_name is None:

        raise ValueError(
            'target_name is required.'
        )

    if not isinstance(
        target_name,
        str,
    ):

        raise ValueError(
            'target_name must be a string.'
        )

    if not target_name.strip():

        raise ValueError(
            'target_name cannot be empty.'
        )

    if features is None:

        raise ValueError(
            'features are required.'
        )

    if not isinstance(
        features,
        (list, tuple, dict),
    ):

        raise ValueError(
            'features must be a list, tuple, or dictionary.'
        )

    return {

        'target_name':
            target_name,

        'features':
            deepcopy(
                features
            ),
    }


# ==========================================================
# PREDICTION RESULT
# ==========================================================

def prepare_prediction_output(
    prediction_result,
):
    """
    Convert the prediction result into a stable
    UI-facing structure.
    """

    _validate_prediction_result(
        prediction_result
    )

    return {

        'available':
            True,

        'status':
            prediction_result.get(
                'status'
            ),

        'target_name':
            prediction_result.get(
                'target_name'
            ),

        'target_task':
            prediction_result.get(
                'target_task'
            ),

        'prediction':
            deepcopy(
                prediction_result
            ),
    }


# ==========================================================
# ANALYSIS RESULT
# ==========================================================

def prepare_analysis_output(
    analysis_result,
):
    """
    Convert the analysis result into a stable
    UI-facing structure.
    """

    _validate_analysis_result(
        analysis_result
    )

    return {

        'available':
            True,

        'status':
            analysis_result.get(
                'status'
            ),

        'analysis_status':
            analysis_result.get(
                'analysis_status'
            ),

        'analysis':
            deepcopy(
                analysis_result
            ),
    }


# ==========================================================
# REPORT RESULT
# ==========================================================

def prepare_report_output(
    report_result,
):
    """
    Convert the reporting result into a stable
    UI-facing structure.
    """

    _validate_report_result(
        report_result
    )

    return {

        'available':
            True,

        'status':
            report_result.get(
                'status'
            ),

        'target_name':
            report_result.get(
                'target_name'
            ),

        'target_task':
            report_result.get(
                'target_task'
            ),

        'report':
            deepcopy(
                report_result
            ),
    }


# ==========================================================
# OPTIONAL RESULT
# ==========================================================

def _prepare_optional_result(
    result,
    key,
):
    """
    Preserve an optional upstream result without
    inventing or transforming its internal contract.
    """

    if result is None:

        return {

            'available':
                False,

            key:
                None,
        }

    if not isinstance(
        result,
        dict,
    ):

        raise ValueError(
            f'{key} must be a dictionary.'
        )

    return {

        'available':
            True,

        key:
            deepcopy(
                result
            ),
    }


# ==========================================================
# UI INTEGRATION RESULT
# ==========================================================

def build_ui_result(
    prediction_result,
    analysis_result=None,
    reliability_result=None,
    monitoring_result=None,
    alert_result=None,
    recommendation_result=None,
    report_result=None,
):
    """
    Build the complete UI-facing result from the
    already completed upstream layers.

    This function does not execute ML logic.
    It only integrates existing results.
    """

    _validate_prediction_result(
        prediction_result
    )

    target_name = prediction_result.get(
        'target_name'
    )

    target_task = prediction_result.get(
        'target_task'
    )

    result = {

        'status':
            INTEGRATION_VALID,

        'target_name':
            target_name,

        'target_task':
            target_task,

        'prediction':
            prepare_prediction_output(
                prediction_result
            ),

        'analysis':
            None,

        'reliability':
            None,

        'monitoring':
            None,

        'alerts':
            None,

        'recommendations':
            None,

        'report':
            None,
    }

    if analysis_result is not None:

        result[
            'analysis'
        ] = prepare_analysis_output(
            analysis_result
        )

    if reliability_result is not None:

        result[
            'reliability'
        ] = _prepare_optional_result(
            reliability_result,
            'reliability',
        )

    if monitoring_result is not None:

        result[
            'monitoring'
        ] = _prepare_optional_result(
            monitoring_result,
            'monitoring',
        )

    if alert_result is not None:

        result[
            'alerts'
        ] = _prepare_optional_result(
            alert_result,
            'alerts',
        )

    if recommendation_result is not None:

        result[
            'recommendations'
        ] = _prepare_optional_result(
            recommendation_result,
            'recommendations',
        )

    if report_result is not None:

        result[
            'report'
        ] = prepare_report_output(
            report_result
        )

    return result


# ==========================================================
# UI AVAILABILITY
# ==========================================================

def is_ui_result_available(
    result,
):
    """
    Return whether a valid UI integration result exists.
    """

    if not isinstance(
        result,
        dict,
    ):

        return False

    return (
        result.get(
            'status'
        )
        == INTEGRATION_VALID
    )


def has_ui_data(
    result,
):
    """
    Return whether the UI integration result contains
    usable prediction data.
    """

    if not isinstance(
        result,
        dict,
    ):

        return False

    if not is_ui_result_available(
        result
    ):

        return False

    prediction = result.get(
        'prediction'
    )

    if not isinstance(
        prediction,
        dict,
    ):

        return False

    return (
        prediction.get(
            'available'
        )
        is True
    )


# ==========================================================
# UI PIPELINE
# ==========================================================

def run_ui_pipeline(
    prediction_result,
    analysis_result=None,
    reliability_result=None,
    monitoring_result=None,
    alert_result=None,
    recommendation_result=None,
    report_result=None,
):
    """
    Build the final UI-facing integration result.

    All upstream processing must already be completed.
    """

    return build_ui_result(
        prediction_result=prediction_result,
        analysis_result=analysis_result,
        reliability_result=reliability_result,
        monitoring_result=monitoring_result,
        alert_result=alert_result,
        recommendation_result=recommendation_result,
        report_result=report_result,
    )


# ==========================================================
# WRAPPER
# ==========================================================

def integrate_for_ui(
    prediction_result,
    analysis_result=None,
    reliability_result=None,
    monitoring_result=None,
    alert_result=None,
    recommendation_result=None,
    report_result=None,
):
    """
    Public wrapper for UI integration.
    """

    return run_ui_pipeline(
        prediction_result=prediction_result,
        analysis_result=analysis_result,
        reliability_result=reliability_result,
        monitoring_result=monitoring_result,
        alert_result=alert_result,
        recommendation_result=recommendation_result,
        report_result=report_result,
    )