
from math import isfinite

from ml.targets.common import (
    DAILY_HORIZONS,
    PERIOD_HORIZONS,
    normalize_text,
)


# =========================================================
# SAFE VALUE HELPERS
# =========================================================

def _get_event_count(row):
    """
    Return a valid non-negative integer event count.

    Missing values default to zero according to the
    project's event-recording policy.
    Invalid numeric values raise ValueError.
    """

    if not row:
        return 0

    value = row.get('Event_Count')

    if value is None or (
        isinstance(value, str) and not value.strip()
    ):
        return 0

    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        raise ValueError(
            f'Invalid Event_Count value: {value!r}'
        )

    if not isfinite(numeric_value):
        raise ValueError(
            f'Event_Count must be finite: {value!r}'
        )

    if numeric_value < 0 or not numeric_value.is_integer():
        raise ValueError(
            f'Event_Count must be a non-negative integer: {value!r}'
        )

    return int(numeric_value)


def _has_special_event(row):
    """
    Determine whether the row contains a special event.

    Missing or empty values mean no special event,
    according to the project's event-recording policy.
    """

    if not row:
        return False

    return bool(
        normalize_text(
            row.get('Special_Event')
        )
    )


# =========================================================
# EVENT CLASSIFICATION
# =========================================================

def _has_event(row):
    """Determine whether at least one event occurs."""

    return _get_event_count(row) > 0


def _has_multiple_events(row):
    """Determine whether at least two events occur."""

    return _get_event_count(row) >= 2


# =========================================================
# EMPTY TARGETS
# =========================================================

def _empty_targets(horizon_name):
    """Return unknown targets when future data is unavailable."""

    return {
        f'Target_Has_Event_{horizon_name}': float('nan'),
        f'Target_Multiple_Events_{horizon_name}': float('nan'),
        f'Target_Has_Special_Event_{horizon_name}': float('nan'),
    }


# =========================================================
# DAILY EVENT TARGETS
# =========================================================

def create_event_targets_daily(future_row, horizon_name):
    """Create event targets for one specific future day."""

    if not future_row:
        return _empty_targets(horizon_name)

    return {
        f'Target_Has_Event_{horizon_name}':
            int(_has_event(future_row)),

        f'Target_Multiple_Events_{horizon_name}':
            int(_has_multiple_events(future_row)),

        f'Target_Has_Special_Event_{horizon_name}':
            int(_has_special_event(future_row)),
    }


# =========================================================
# PERIOD EVENT TARGETS
# =========================================================

def create_event_targets_period(future_rows, horizon_name):
    """
    Create event targets for a complete future period.

    A target is 1 if the condition occurs on at least
    one day, otherwise 0.
    """

    if not future_rows:
        return _empty_targets(horizon_name)

    has_event = False
    multiple_events = False
    has_special_event = False

    for row in future_rows:
        if not row:
            continue

        if _has_event(row):
            has_event = True

        if _has_multiple_events(row):
            multiple_events = True

        if _has_special_event(row):
            has_special_event = True

    return {
        f'Target_Has_Event_{horizon_name}':
            int(has_event),

        f'Target_Multiple_Events_{horizon_name}':
            int(multiple_events),

        f'Target_Has_Special_Event_{horizon_name}':
            int(has_special_event),
    }


# =========================================================
# PUBLIC EVENT TARGETS
# =========================================================

def create_event_targets(future_rows, horizon_name='1D'):
    """
    Public Event Target Engineering entry point.

    Daily horizons represent one exact future day.
    Period horizons summarize a complete future period.
    """

    if future_rows is None:
        future_rows = []

    if horizon_name in DAILY_HORIZONS:
        future_row = future_rows[0] if future_rows else None

        return create_event_targets_daily(
            future_row,
            horizon_name,
        )

    if horizon_name in PERIOD_HORIZONS:
        return create_event_targets_period(
            future_rows,
            horizon_name,
        )

    raise ValueError(
        f'Unsupported event horizon: {horizon_name}'
    )
