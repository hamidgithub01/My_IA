# ==========================================================
# ALERT STATUS
# ==========================================================

ALERT_VALID = 'valid'
ALERT_NONE = 'none'
ALERT_INVALID = 'invalid'


# ==========================================================
# ALERT TYPES
# ==========================================================

ALERT_LOW_RELIABILITY = (
    'low_reliability'
)

ALERT_RELIABILITY_DECLINE = (
    'reliability_decline'
)

ALERT_HIGH_ERROR = (
    'high_error'
)

ALERT_INSUFFICIENT_DATA = (
    'insufficient_data'
)

ALERT_UNRELIABLE = (
    'unreliable'
)


# ==========================================================
# SEVERITY
# ==========================================================

SEVERITY_INFO = 'info'
SEVERITY_WARNING = 'warning'
SEVERITY_HIGH = 'high'
SEVERITY_CRITICAL = 'critical'


# ==========================================================
# BASIC HELPERS
# ==========================================================

def _to_float(
    value,
):
    """
    Convert a value to float safely.
    """

    try:

        return float(value)

    except (
        TypeError,
        ValueError,
    ):

        raise ValueError(
            f'Value must be numeric: {value!r}'
        )


def _validate_monitoring_result(
    monitoring_result,
):
    """
    Validate a monitoring result.

    The function intentionally accepts a dictionary
    rather than depending on a specific monitoring
    implementation.
    """

    if monitoring_result is None:

        raise ValueError(
            'monitoring_result is required.'
        )

    if not isinstance(
        monitoring_result,
        dict,
    ):

        raise ValueError(
            'monitoring_result must be a dictionary.'
        )


# ==========================================================
# ALERT CREATION
# ==========================================================

def _create_alert(
    alert_type,
    severity,
    message,
    reason=None,
    target_name=None,
    metric=None,
    current_value=None,
    threshold=None,
):
    """
    Create a standardized alert dictionary.
    """

    return {

        'alert_type':
            alert_type,

        'severity':
            severity,

        'message':
            message,

        'reason':
            reason,

        'target_name':
            target_name,

        'metric':
            metric,

        'current_value':
            current_value,

        'threshold':
            threshold,
    }


# ==========================================================
# RELIABILITY ALERT
# ==========================================================

def _check_reliability_level(
    monitoring_result,
    alerts,
):
    """
    Generate an alert based on reliability level.
    """

    reliability_level = (
        monitoring_result.get(
            'reliability_level'
        )
    )

    target_name = (
        monitoring_result.get(
            'target_name'
        )
    )

    if reliability_level == 'low':

        alerts.append(
            _create_alert(
                alert_type=(
                    ALERT_LOW_RELIABILITY
                ),
                severity=SEVERITY_HIGH,
                message=(
                    'Prediction reliability is low.'
                ),
                reason=(
                    'The monitored model has '
                    'fallen below the acceptable '
                    'reliability level.'
                ),
                target_name=target_name,
                metric='reliability_level',
                current_value=(
                    reliability_level
                ),
            )
        )

    elif reliability_level == 'unknown':

        alerts.append(
            _create_alert(
                alert_type=(
                    ALERT_INSUFFICIENT_DATA
                ),
                severity=SEVERITY_WARNING,
                message=(
                    'Prediction reliability '
                    'cannot yet be determined.'
                ),
                reason=(
                    'There is not enough reliable '
                    'monitoring data.'
                ),
                target_name=target_name,
                metric='reliability_level',
                current_value=(
                    reliability_level
                ),
            )
        )


# ==========================================================
# EXPLICIT UNRELIABLE STATUS
# ==========================================================

def _check_unreliable_status(
    monitoring_result,
    alerts,
):
    """
    Detect an explicit unreliable monitoring status.
    """

    status = monitoring_result.get(
        'status'
    )

    if status != 'unreliable':

        return

    target_name = (
        monitoring_result.get(
            'target_name'
        )
    )

    alerts.append(
        _create_alert(
            alert_type=(
                ALERT_UNRELIABLE
            ),
            severity=SEVERITY_CRITICAL,
            message=(
                'Prediction system is currently '
                'considered unreliable.'
            ),
            reason=(
                'The monitoring system explicitly '
                'marked the prediction reliability '
                'as unreliable.'
            ),
            target_name=target_name,
            metric='status',
            current_value=status,
        )
    )


# ==========================================================
# ERROR ALERT
# ==========================================================

def _check_error_rate(
    monitoring_result,
    alerts,
    maximum_error_rate=None,
):
    """
    Generate an alert when classification error rate
    exceeds an explicitly supplied threshold.

    No arbitrary threshold is invented.
    """

    if maximum_error_rate is None:

        return

    maximum_error_rate = _to_float(
        maximum_error_rate
    )

    if not (
        0.0
        <= maximum_error_rate
        <= 1.0
    ):

        raise ValueError(
            'maximum_error_rate must be between '
            '0 and 1.'
        )

    error_rate = monitoring_result.get(
        'error_rate'
    )

    if error_rate is None:

        return

    error_rate = _to_float(
        error_rate
    )

    if error_rate <= maximum_error_rate:

        return

    target_name = (
        monitoring_result.get(
            'target_name'
        )
    )

    alerts.append(
        _create_alert(
            alert_type=ALERT_HIGH_ERROR,
            severity=SEVERITY_HIGH,
            message=(
                'Prediction error rate exceeds '
                'the acceptable threshold.'
            ),
            reason=(
                'Observed prediction error rate '
                'is higher than the configured '
                'maximum.'
            ),
            target_name=target_name,
            metric='error_rate',
            current_value=error_rate,
            threshold=maximum_error_rate,
        )
    )


# ==========================================================
# RELIABILITY DECLINE
# ==========================================================

def _check_reliability_decline(
    monitoring_result,
    alerts,
    minimum_decline=None,
):
    """
    Detect a meaningful decline in reliability.

    Expected monitoring fields:

        previous_quality_score
        quality_score
    """

    if minimum_decline is None:

        return

    minimum_decline = _to_float(
        minimum_decline
    )

    if minimum_decline < 0:

        raise ValueError(
            'minimum_decline cannot be negative.'
        )

    previous_score = (
        monitoring_result.get(
            'previous_quality_score'
        )
    )

    current_score = (
        monitoring_result.get(
            'quality_score'
        )
    )

    if (
        previous_score is None
        or current_score is None
    ):

        return

    previous_score = _to_float(
        previous_score
    )

    current_score = _to_float(
        current_score
    )

    decline = (
        previous_score
        - current_score
    )

    if decline < minimum_decline:

        return

    target_name = (
        monitoring_result.get(
            'target_name'
        )
    )

    alerts.append(
        _create_alert(
            alert_type=(
                ALERT_RELIABILITY_DECLINE
            ),
            severity=SEVERITY_WARNING,
            message=(
                'Prediction reliability has '
                'declined.'
            ),
            reason=(
                'The current quality score is '
                'lower than the previous monitored '
                'quality score.'
            ),
            target_name=target_name,
            metric='quality_score',
            current_value=current_score,
            threshold=(
                previous_score
                - minimum_decline
            ),
        )
    )


# ==========================================================
# PUBLIC ALERT ANALYSIS
# ==========================================================

def analyze_alerts(
    monitoring_result,
    maximum_error_rate=None,
    minimum_reliability_decline=None,
):
    """
    Analyze a prediction monitoring result and
    generate operational alerts.

    Parameters:

        monitoring_result:
            Result produced by the prediction
            reliability monitoring layer.

        maximum_error_rate:
            Optional explicit classification
            error-rate threshold.

        minimum_reliability_decline:
            Optional minimum quality-score decline
            required to generate a decline alert.

    Important:

        The function never invents thresholds.

        If a threshold is not supplied, the corresponding
        threshold-based alert is not generated.
    """

    _validate_monitoring_result(
        monitoring_result
    )

    alerts = []

    _check_reliability_level(
        monitoring_result,
        alerts,
    )

    _check_unreliable_status(
        monitoring_result,
        alerts,
    )

    _check_error_rate(
        monitoring_result,
        alerts,
        maximum_error_rate=(
            maximum_error_rate
        ),
    )

    _check_reliability_decline(
        monitoring_result,
        alerts,
        minimum_decline=(
            minimum_reliability_decline
        ),
    )

    if alerts:

        status = ALERT_VALID

    else:

        status = ALERT_NONE

    return {

        'status':
            status,

        'alert_count':
            len(alerts),

        'alerts':
            alerts,

        'target_name':
            monitoring_result.get(
                'target_name'
            ),
    }


# ==========================================================
# CONVENIENCE FUNCTION
# ==========================================================

def has_alerts(
    alert_result,
):
    """
    Return True when at least one alert exists.
    """

    if alert_result is None:

        raise ValueError(
            'alert_result is required.'
        )

    if not isinstance(
        alert_result,
        dict,
    ):

        raise ValueError(
            'alert_result must be a dictionary.'
        )

    return (
        alert_result.get(
            'alert_count',
            0,
        )
        > 0
    )

# ==========================================================
# BACKWARD COMPATIBILITY
# ==========================================================

def generate_alerts(
    monitoring_result,
    maximum_error_rate=None,
    minimum_reliability_decline=None,
):
    """
    Compatibility wrapper for the integration layer.

    Delegates alert generation to analyze_alerts().
    """

    return analyze_alerts(
        monitoring_result,
        maximum_error_rate=maximum_error_rate,
        minimum_reliability_decline=(
            minimum_reliability_decline
        ),
    )