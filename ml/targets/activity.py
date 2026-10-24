
from math import isfinite

from ml.targets.common import (
    DAILY_HORIZONS,
    PERIOD_HORIZONS,
)


# =========================================================
# SAFE VALUE HELPERS
# =========================================================

def _get_numeric_value(row, field):
    """Return a valid finite number, or None if unknown."""

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


def _get_activity_count(row):
    """Extract a valid non-negative integer activity count."""

    value = _get_numeric_value(row, 'Activity_Count')

    if value is None or value < 0 or not value.is_integer():
        return None

    return int(value)


def _get_activity_duration(row):
    """Extract a valid non-negative activity duration in minutes."""

    value = _get_numeric_value(
        row,
        'Activity_Duration_Minutes',
    )

    if value is None or value < 0:
        return None

    return value


# =========================================================
# ACTIVITY CLASSIFICATION
# =========================================================

def _has_activity(row):
    """
    Determine whether activity occurred.

    Positive evidence confirms activity.
    Zero means no activity only when both measurements
    are known and equal to zero.
    """

    count = _get_activity_count(row)
    duration = _get_activity_duration(row)

    if count is not None and count > 0:
        return True

    if duration is not None and duration > 0:
        return True

    if count is None or duration is None:
        return None

    return False


def _is_high_activity(row):
    """
    High activity means:

        activity count >= 2

    OR

        activity duration >= 120 minutes
    """

    count = _get_activity_count(row)
    duration = _get_activity_duration(row)

    if count is not None and count >= 2:
        return True

    if duration is not None and duration >= 120:
        return True

    if count is None or duration is None:
        return None

    return False


def _is_long_activity(row):
    """Activity duration is at least 60 minutes."""

    duration = _get_activity_duration(row)

    if duration is None:
        return None

    return duration >= 60


# =========================================================
# TARGET CONVERSION HELPERS
# =========================================================

def _to_target_value(value):
    """Convert a known classification to 0 or 1."""

    if value is None:
        return float('nan')

    return int(value)


def _period_target(values):
    """
    Summarize whether a condition occurred at least once.

    Any confirmed occurrence => 1.
    No confirmed occurrence but unknown observations => NaN.
    All observations known and no occurrence => 0.
    """

    if any(value is True for value in values):
        return 1

    if any(value is None for value in values):
        return float('nan')

    return 0


# =========================================================
# EMPTY ACTIVITY TARGETS
# =========================================================

def _empty_targets(horizon_name):
    """Return unknown activity targets for a horizon."""

    return {
        f'Target_Has_Activity_{horizon_name}': float('nan'),
        f'Target_High_Activity_{horizon_name}': float('nan'),
        f'Target_Long_Activity_{horizon_name}': float('nan'),
    }


# =========================================================
# DAILY ACTIVITY TARGETS
# =========================================================

def create_activity_targets_daily(
    future_row,
    horizon_name,
):
    """Create activity targets for one specific future day."""

    if not future_row:
        return _empty_targets(horizon_name)

    return {
        f'Target_Has_Activity_{horizon_name}':
            _to_target_value(_has_activity(future_row)),

        f'Target_High_Activity_{horizon_name}':
            _to_target_value(_is_high_activity(future_row)),

        f'Target_Long_Activity_{horizon_name}':
            _to_target_value(_is_long_activity(future_row)),
    }


# =========================================================
# PERIOD ACTIVITY TARGETS
# =========================================================

def create_activity_targets_period(
    future_rows,
    horizon_name,
):
    """Create activity targets summarizing a future period."""

    if not future_rows:
        return _empty_targets(horizon_name)

    return {
        f'Target_Has_Activity_{horizon_name}':
            _period_target([
                _has_activity(row) for row in future_rows
            ]),

        f'Target_High_Activity_{horizon_name}':
            _period_target([
                _is_high_activity(row) for row in future_rows
            ]),

        f'Target_Long_Activity_{horizon_name}':
            _period_target([
                _is_long_activity(row) for row in future_rows
            ]),
    }


# =========================================================
# PUBLIC ACTIVITY TARGETS
# =========================================================

def create_activity_targets(
    future_rows,
    horizon_name='1D',
):
    """Public activity target engineering entry point."""

    if future_rows is None:
        future_rows = []

    if horizon_name in DAILY_HORIZONS:
        future_row = future_rows[0] if future_rows else None

        return create_activity_targets_daily(
            future_row,
            horizon_name,
        )

    if horizon_name in PERIOD_HORIZONS:
        return create_activity_targets_period(
            future_rows,
            horizon_name,
        )

    raise ValueError(
        f'Unsupported activity horizon: {horizon_name}'
    )
