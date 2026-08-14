
from ml.targets.common import (
    DAILY_HORIZONS,
    PERIOD_HORIZONS,
    normalize_text,
)


# =========================================================
# HISTORICAL LOCATION
# =========================================================

def _get_previous_location(previous_rows):
    """
    Return the latest known historical location.

    Only rows before the prediction date should be
    supplied in previous_rows.
    """

    if not previous_rows:
        return ''

    for row in reversed(previous_rows):

        location = normalize_text(
            row.get('Location')
        )

        if location:
            return location

    return ''


# =========================================================
# EMPTY LOCATION TARGETS
# =========================================================

def _empty_location_targets(horizon_name):
    """
    Return empty location targets for a future horizon.
    """

    return {

        f'Target_Has_Location_{horizon_name}':
            float('nan'),

        f'Target_Location_Changed_{horizon_name}':
            float('nan'),

        f'Target_Same_Location_{horizon_name}':
            float('nan'),

        f'Target_Location_{horizon_name}':
            None,
    }


# =========================================================
# DAILY LOCATION TARGETS
# =========================================================

def create_location_targets_daily(
    future_row,
    horizon_name,
    previous_rows=None,
):
    """
    Create location targets for one specific future day.

    Each future day receives independent location targets.
    """

    previous_rows = previous_rows or []

    if not future_row:
        return _empty_location_targets(
            horizon_name
        )

    current_location = normalize_text(
        future_row.get('Location')
    )

    previous_location = _get_previous_location(
        previous_rows
    )

    has_location = bool(
        current_location
    )

    location_changed = (
        bool(current_location)
        and bool(previous_location)
        and current_location != previous_location
    )

    same_location = (
        bool(current_location)
        and bool(previous_location)
        and current_location == previous_location
    )

    return {

        f'Target_Has_Location_{horizon_name}':
            int(has_location),

        f'Target_Location_Changed_{horizon_name}':
            int(location_changed),

        f'Target_Same_Location_{horizon_name}':
            int(same_location),

        f'Target_Location_{horizon_name}':
            current_location or None,
    }


# =========================================================
# PERIOD LOCATION TARGETS
# =========================================================

def create_location_targets_period(
    future_rows,
    horizon_name,
    previous_rows=None,
):
    """
    Create location targets for a future period.

    The period target is a summary and does not replace
    the detailed daily location targets.
    """

    previous_rows = previous_rows or []

    if not future_rows:
        return _empty_location_targets(
            horizon_name
        )

    previous_location = _get_previous_location(
        previous_rows
    )

    future_locations = [

        normalize_text(
            row.get('Location')
        )

        for row in future_rows

    ]

    future_locations = [
        location
        for location in future_locations
        if location
    ]

    has_location = bool(
        future_locations
    )

    location_changed = bool(
        previous_location
        and any(
            location != previous_location
            for location in future_locations
        )
    )

    same_location = bool(
        previous_location
        and any(
            location == previous_location
            for location in future_locations
        )
    )

    target_location = (
        future_locations[-1]
        if future_locations
        else None
    )

    return {

        f'Target_Has_Location_{horizon_name}':
            int(has_location),

        f'Target_Location_Changed_{horizon_name}':
            int(location_changed),

        f'Target_Same_Location_{horizon_name}':
            int(same_location),

        f'Target_Location_{horizon_name}':
            target_location,
    }


# =========================================================
# PUBLIC LOCATION TARGETS
# =========================================================

def create_location_targets(
    future_rows,
    horizon_name='1D',
    previous_rows=None,
):
    """
    Public Location Target Engineering entry point.

    Daily horizons represent one exact future day.

    Period horizons summarize a future period.
    """

    future_rows = future_rows or []
    previous_rows = previous_rows or []

    # -----------------------------------------------------
    # DAILY HORIZONS
    # -----------------------------------------------------

    if horizon_name in DAILY_HORIZONS:

        future_row = (
            future_rows[0]
            if future_rows
            else None
        )

        return create_location_targets_daily(
            future_row,
            horizon_name,
            previous_rows,
        )

    # -----------------------------------------------------
    # PERIOD HORIZONS
    # -----------------------------------------------------

    if horizon_name in PERIOD_HORIZONS:

        return create_location_targets_period(
            future_rows,
            horizon_name,
            previous_rows,
        )

    # -----------------------------------------------------
    # INVALID HORIZON
    # -----------------------------------------------------

    raise ValueError(
        f'Unsupported location horizon: '
        f'{horizon_name}'
    )
