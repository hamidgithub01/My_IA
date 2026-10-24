
from math import isfinite

from ml.targets.common import (
    DAILY_HORIZONS,
    PERIOD_HORIZONS,
)


# =========================================================
# SAFE VALUE HELPERS
# =========================================================

def _get_numeric_value(row, field):
    """
    Return a valid finite numeric value, or None when unknown.
    Explicit numeric zero remains a valid value.
    """

    if not row:
        return None

    value = row.get(field)

    if value is None:
        return None

    try:
        value = float(value)
    except (TypeError, ValueError):
        return None

    if not isfinite(value):
        return None

    return value


def _get_stress_level(row):
    """Safely extract stress level."""

    return _get_numeric_value(row, 'Stress_Level')


def _get_sleep_hours(row):
    """Safely extract sleep duration."""

    return _get_numeric_value(row, 'Sleep_Hours')


def _get_social_activity(row):
    """Return normalized social activity, or None if unknown."""

    if not row:
        return None

    value = row.get('Social_Activity')

    if value is None:
        return None

    value = str(value).strip().lower()

    return value if value else None


def _get_work_status(row):
    """Return normalized work status, or None if unknown."""

    if not row:
        return None

    value = row.get('Work_Status')

    if value is None:
        return None

    value = str(value).strip().lower()

    return value if value else None


# =========================================================
# BEHAVIORAL CLASSIFICATION
# =========================================================

def _is_high_stress(row):
    """High stress means stress level >= 7."""

    value = _get_stress_level(row)

    if value is None:
        return None

    return value >= 7


def _is_moderate_or_high_stress(row):
    """Moderate or high stress means stress level >= 5."""

    value = _get_stress_level(row)

    if value is None:
        return None

    return value >= 5


def _is_low_sleep(row):
    """Low sleep means more than zero but less than 6 hours."""

    value = _get_sleep_hours(row)

    if value is None:
        return None

    return 0 < value < 6


def _is_very_low_sleep(row):
    """Very low sleep means more than zero but less than 5 hours."""

    value = _get_sleep_hours(row)

    if value is None:
        return None

    return 0 < value < 5


def _is_high_social_activity(row):
    """High social activity."""

    value = _get_social_activity(row)

    if value is None:
        return None

    return value == 'high'


def _is_moderate_or_high_social_activity(row):
    """Moderate, medium, or high social activity."""

    value = _get_social_activity(row)

    if value is None:
        return None

    return value in {
        'moderate',
        'medium',
        'high',
    }


def _is_working_day(row):
    """Determine whether the day is a working day."""

    value = _get_work_status(row)

    if value is None:
        return None

    return value in {
        'working',
        'work',
    }


def _is_difficult_behavioral_day(row):
    """
    A difficult behavioral day means high stress
    OR very low sleep.

    Return None if neither condition is true and at least
    one required measurement is unknown.
    """

    high_stress = _is_high_stress(row)
    very_low_sleep = _is_very_low_sleep(row)

    if high_stress is True or very_low_sleep is True:
        return True

    if high_stress is None or very_low_sleep is None:
        return None

    return False


# =========================================================
# TARGET CONVERSION HELPERS
# =========================================================

def _to_target_value(value):
    """Convert a known Boolean classification to 0 or 1."""

    if value is None:
        return float('nan')

    return int(value)


def _period_target(values):
    """
    Summarize an 'occurs at least once' condition.

    Any confirmed occurrence => 1.
    No occurrence but at least one unknown => NaN.
    All observations known and no occurrence => 0.
    """

    if any(value is True for value in values):
        return 1

    if any(value is None for value in values):
        return float('nan')

    return 0


# =========================================================
# EMPTY TARGETS
# =========================================================

def _empty_targets(horizon_name):
    """Return unknown behavioral targets for a horizon."""

    return {
        f'Target_High_Stress_{horizon_name}': float('nan'),

        f'Target_Moderate_or_High_Stress_{horizon_name}':
            float('nan'),

        f'Target_Low_Sleep_{horizon_name}': float('nan'),

        f'Target_Very_Low_Sleep_{horizon_name}': float('nan'),

        f'Target_High_Social_Activity_{horizon_name}':
            float('nan'),

        f'Target_Moderate_or_High_Social_Activity_{horizon_name}':
            float('nan'),

        f'Target_Working_Day_{horizon_name}': float('nan'),

        f'Target_Difficult_Behavioral_Day_{horizon_name}':
            float('nan'),
    }


# =========================================================
# DAILY BEHAVIORAL TARGETS
# =========================================================

def create_behavioral_targets_daily(
    future_row,
    horizon_name,
):
    """Create behavioral targets for one specific future day."""

    if not future_row:
        return _empty_targets(horizon_name)

    return {
        f'Target_High_Stress_{horizon_name}':
            _to_target_value(_is_high_stress(future_row)),

        f'Target_Moderate_or_High_Stress_{horizon_name}':
            _to_target_value(
                _is_moderate_or_high_stress(future_row)
            ),

        f'Target_Low_Sleep_{horizon_name}':
            _to_target_value(_is_low_sleep(future_row)),

        f'Target_Very_Low_Sleep_{horizon_name}':
            _to_target_value(_is_very_low_sleep(future_row)),

        f'Target_High_Social_Activity_{horizon_name}':
            _to_target_value(_is_high_social_activity(future_row)),

        f'Target_Moderate_or_High_Social_Activity_{horizon_name}':
            _to_target_value(
                _is_moderate_or_high_social_activity(future_row)
            ),

        f'Target_Working_Day_{horizon_name}':
            _to_target_value(_is_working_day(future_row)),

        f'Target_Difficult_Behavioral_Day_{horizon_name}':
            _to_target_value(
                _is_difficult_behavioral_day(future_row)
            ),
    }


# =========================================================
# PERIOD BEHAVIORAL TARGETS
# =========================================================

def create_behavioral_targets_period(
    future_rows,
    horizon_name,
):
    """
    Create period targets.

    A target is 1 if its condition occurs at least once.
    If no occurrence is confirmed but some observations
    are unknown, the target is NaN.
    """

    if not future_rows:
        return _empty_targets(horizon_name)

    return {
        f'Target_High_Stress_{horizon_name}':
            _period_target([
                _is_high_stress(row) for row in future_rows
            ]),

        f'Target_Moderate_or_High_Stress_{horizon_name}':
            _period_target([
                _is_moderate_or_high_stress(row)
                for row in future_rows
            ]),

        f'Target_Low_Sleep_{horizon_name}':
            _period_target([
                _is_low_sleep(row) for row in future_rows
            ]),

        f'Target_Very_Low_Sleep_{horizon_name}':
            _period_target([
                _is_very_low_sleep(row) for row in future_rows
            ]),

        f'Target_High_Social_Activity_{horizon_name}':
            _period_target([
                _is_high_social_activity(row)
                for row in future_rows
            ]),

        f'Target_Moderate_or_High_Social_Activity_{horizon_name}':
            _period_target([
                _is_moderate_or_high_social_activity(row)
                for row in future_rows
            ]),

        f'Target_Working_Day_{horizon_name}':
            _period_target([
                _is_working_day(row) for row in future_rows
            ]),

        f'Target_Difficult_Behavioral_Day_{horizon_name}':
            _period_target([
                _is_difficult_behavioral_day(row)
                for row in future_rows
            ]),
    }


# =========================================================
# PUBLIC BEHAVIORAL TARGETS
# =========================================================

def create_behavioral_targets(
    future_rows,
    horizon_name='1D',
):
    """Public behavioral target engineering entry point."""

    if future_rows is None:
        future_rows = []

    if horizon_name in DAILY_HORIZONS:
        future_row = future_rows[0] if future_rows else None

        return create_behavioral_targets_daily(
            future_row,
            horizon_name,
        )

    if horizon_name in PERIOD_HORIZONS:
        return create_behavioral_targets_period(
            future_rows,
            horizon_name,
        )

    raise ValueError(
        f'Unsupported behavioral horizon: {horizon_name}'
    )
