from math import isfinite

from ml.targets.common import (
    DAILY_HORIZONS,
    PERIOD_HORIZONS,
    normalize_text,
)


# =========================================================
# CONFIGURATION
# =========================================================

VALID_HEALTH_STATUSES = {
    'good',
    'normal',
    'tired',
    'sick',
}

HIGH_SEVERITY_THRESHOLD = 7
LOW_ENERGY_THRESHOLD = 4

MIN_SCALE_VALUE = 0
MAX_SCALE_VALUE = 10


# =========================================================
# SAFE VALUE HELPERS
# =========================================================

def _get_health_status(row):
    """
    Return a normalized health status.

    Supported statuses:
        Good
        Normal
        Tired
        Sick

    Missing or invalid statuses return None.
    """

    value = normalize_text(
        row.get('Health_Status')
    )

    if value not in VALID_HEALTH_STATUSES:
        return None

    return value


def _get_numeric_value(row, column):
    """
    Safely read a numeric value from a row.

    Missing, invalid, non-finite, or out-of-range
    values return None.

    Valid scale: 0 to 10.
    """

    value = row.get(column)

    if value is None:
        return None

    if isinstance(value, bool):
        return None

    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None

    if not isfinite(number):
        return None

    if not (
        MIN_SCALE_VALUE
        <= number
        <= MAX_SCALE_VALUE
    ):
        return None

    return number



def _get_health_severity(row):
    """
    Read health severity from the database field.

    Valid values are between 0 and 10.
    """

    return _get_numeric_value(
        row,
        'Severity',
    )


def _get_energy_level(row):
    """
    Read energy level from the database field.

    Valid values are between 0 and 10.
    """

    return _get_numeric_value(
        row,
        'Energy_Level',
    )



# =========================================================
# THREE-STATE CLASSIFICATION HELPERS
# =========================================================

def _is_high_health_severity(row):
    """
    Return:
        True  -> severity >= 7
        False -> valid severity below 7
        None  -> severity unknown or invalid
    """

    severity = _get_health_severity(row)

    if severity is None:
        return None

    return (
        severity >= HIGH_SEVERITY_THRESHOLD
    )



def _is_low_energy(row):
    """
    Return:
        True  -> 0 <= energy < 4
        False -> energy >= 4
        None  -> energy unknown or invalid
    """

    energy = _get_energy_level(row)

    if energy is None:
        return None

    return (
        energy < LOW_ENERGY_THRESHOLD
    )


def _has_health_problem(row):
    """
    Sick means a reported health problem.

    Good, Normal, and Tired are not classified
    as illness by this target.

    Missing or invalid status remains unknown.
    """

    status = _get_health_status(row)

    if status is None:
        return None

    return status == 'sick'


def _is_significant_health_day(row):
    """
    A significant health day occurs when at least
    one of these conditions is present:

        - Health_Status is Sick
        - Health_Status is Tired
        - Severity >= 7
        - Energy is below 4

    A confirmed positive condition takes precedence
    over unknown values.

    If no positive condition exists but one or more
    required values are unknown, return None.
    """

    status = _get_health_status(row)

    high_severity = _is_high_health_severity(row)

    low_energy = _is_low_energy(row)

    if status in {'sick', 'tired'}:
        return True

    if high_severity is True:
        return True

    if low_energy is True:
        return True

    if (
        status is None
        or high_severity is None
        or low_energy is None
    ):
        return None

    return False


# =========================================================
# HEALTH STATUS TARGETS
# =========================================================

def _create_health_status_targets(
    rows,
    horizon_name,
):
    """
    Create one indicator target per health status.

    For a daily horizon, the known status is represented
    by exactly one positive target.

    For a period horizon, each target indicates whether
    that status occurred at least once during the period.

    Missing statuses are not silently converted to zero.
    """

    target_statuses = {
        'Good': 'good',
        'Normal': 'normal',
        'Tired': 'tired',
        'Sick': 'sick',
    }

    observed_statuses = [
        _get_health_status(row)
        for row in rows
    ]

    all_statuses_known = all(
        status is not None
        for status in observed_statuses
    )

    targets = {}

    for target_name, status_value in (
        target_statuses.items()
    ):
        key = (
            f'Target_Health_Status_{target_name}_'
            f'{horizon_name}'
        )

        if status_value in observed_statuses:
            targets[key] = 1

        elif all_statuses_known:
            targets[key] = 0

        else:
            targets[key] = float('nan')

    return targets


# =========================================================
# BINARY HEALTH TARGETS
# =========================================================

def _aggregate_any_condition(values):
    """
    Aggregate a condition across a complete period.

    Return:
        1   if any day is positive
        0   if every day is known and negative
        NaN if no positive day exists but some values
            are unknown
    """

    if any(value is True for value in values):
        return 1

    if all(value is False for value in values):
        return 0

    return float('nan')


def _create_binary_health_targets(
    rows,
    horizon_name,
):
    """
    Create the existing health targets while preserving
    unknown values instead of treating them as negative.
    """

    health_problem_values = [
        _has_health_problem(row)
        for row in rows
    ]

    severity_values = [
        _is_high_health_severity(row)
        for row in rows
    ]

    energy_values = [
        _is_low_energy(row)
        for row in rows
    ]

    significant_values = [
        _is_significant_health_day(row)
        for row in rows
    ]

    return {
        f'Target_Health_Problem_{horizon_name}':
            _aggregate_any_condition(
                health_problem_values
            ),

        f'Target_High_Health_Severity_{horizon_name}':
            _aggregate_any_condition(
                severity_values
            ),

        f'Target_Low_Energy_{horizon_name}':
            _aggregate_any_condition(
                energy_values
            ),

        f'Target_Significant_Health_Day_{horizon_name}':
            _aggregate_any_condition(
                significant_values
            ),
    }


# =========================================================
# DAILY HEALTH TARGETS
# =========================================================

def create_health_targets_daily(
    future_row,
    horizon_name,
):
    """
    Create health targets for one exact future day.
    """

    if future_row is None:
        return _nan_health_targets(
            horizon_name
        )

    targets = _create_health_status_targets(
        [future_row],
        horizon_name,
    )

    targets.update(
        _create_binary_health_targets(
            [future_row],
            horizon_name,
        )
    )

    return targets


# =========================================================
# PERIOD HEALTH TARGETS
# =========================================================

def create_health_targets_period(
    future_rows,
    horizon_name,
):
    """
    Create health targets for a future period.

    Status targets indicate whether each status occurred
    at least once during the period.

    Binary condition targets indicate whether each
    condition occurred at least once during the period.
    """

    if not future_rows:
        return _nan_health_targets(
            horizon_name
        )

    targets = _create_health_status_targets(
        future_rows,
        horizon_name,
    )

    targets.update(
        _create_binary_health_targets(
            future_rows,
            horizon_name,
        )
    )

    return targets


# =========================================================
# UNKNOWN TARGET STRUCTURE
# =========================================================

def _nan_health_targets(horizon_name):
    """
    Return every health target as unknown.
    """

    targets = {
        f'Target_Health_Status_{status}_{horizon_name}':
            float('nan')
        for status in (
            'Good',
            'Normal',
            'Tired',
            'Sick',
        )
    }

    targets.update({
        f'Target_Health_Problem_{horizon_name}':
            float('nan'),

        f'Target_High_Health_Severity_{horizon_name}':
            float('nan'),

        f'Target_Low_Energy_{horizon_name}':
            float('nan'),

        f'Target_Significant_Health_Day_{horizon_name}':
            float('nan'),
    })

    return targets


# =========================================================
# PUBLIC ENTRY POINT
# =========================================================

def create_health_targets(
    future_rows,
    horizon_name='1D',
):
    """
    Public Health Target Engineering entry point.

    Daily horizons represent one exact future day.

    Period horizons represent aggregate information
    about a future period.
    """

    if horizon_name in DAILY_HORIZONS:

        future_row = (
            future_rows[0]
            if future_rows
            else None
        )

        return create_health_targets_daily(
            future_row,
            horizon_name,
        )

    if horizon_name in PERIOD_HORIZONS:

        return create_health_targets_period(
            future_rows or [],
            horizon_name,
        )

    raise ValueError(
        f'Unsupported health horizon: '
        f'{horizon_name}'
    )