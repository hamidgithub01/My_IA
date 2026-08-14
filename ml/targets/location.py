# =========================================================
# LOCATION TARGETS
# =========================================================


# =========================================================
# NORMALIZATION
# =========================================================

def _normalize_location(value):
    """
    Safely normalize a location value.
    """

    return str(
        value or ''
    ).strip().lower()


# =========================================================
# HISTORICAL LOCATION
# =========================================================

def _get_previous_location(
    previous_rows,
):
    """
    Return the latest known historical location.

    Only rows before the prediction date should be
    supplied in previous_rows.
    """

    if not previous_rows:
        return ''

    for row in reversed(
        previous_rows
    ):

        location = _normalize_location(
            row.get('Location')
        )

        if location:
            return location

    return ''


# =========================================================
# DAILY LOCATION TARGETS
# =========================================================

def create_location_targets_daily(
    future_row,
    horizon_name,
    previous_rows=None,
):
    """
    Create location targets for one specific
    future day.

    Examples:

        1D -> T + 1
        2D -> T + 2
        ...
        7D -> T + 7

    previous_rows contains only historical rows
    before the current prediction date.
    """

    previous_rows = previous_rows or []

    if not future_row:

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

    current_location = _normalize_location(
        future_row.get('Location')
    )

    previous_location = _get_previous_location(
        previous_rows
    )

    has_location = bool(
        current_location
    )

    location_changed = bool(
        current_location
        and previous_location
        and current_location
        != previous_location
    )

    same_location = bool(
        current_location
        and previous_location
        and current_location
        == previous_location
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

    Definitions:

        Has_Location
            At least one future day has a known location.

        Location_Changed
            At least one future location differs from
            the latest known historical location.

        Same_Location
            At least one future day uses the same
            location as the latest historical location.

        Location
            The most recently known location inside
            the future period.

    The period target is a summary and does not replace
    the detailed daily location targets.
    """

    previous_rows = previous_rows or []

    if not future_rows:

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

    previous_location = _get_previous_location(
        previous_rows
    )

    has_location = False
    location_changed = False
    same_location = False

    future_locations = []

    for row in future_rows:

        location = _normalize_location(
            row.get('Location')
        )

        if not location:
            continue

        has_location = True

        future_locations.append(
            location
        )

        if previous_location:

            if location != previous_location:
                location_changed = True

            if location == previous_location:
                same_location = True

    if future_locations:

        target_location = (
            future_locations[-1]
        )

    else:

        target_location = None

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

    Supported daily horizons:

        1D
        2D
        3D
        4D
        5D
        6D
        7D

    Supported period horizons:

        8_15D
        16_30D
        30D

    Daily horizons represent one exact future day.

    Period horizons summarize a future period.
    """

    previous_rows = previous_rows or []

    # -----------------------------------------------------
    # DAILY HORIZONS
    # -----------------------------------------------------

    daily_horizons = {
        '1D',
        '2D',
        '3D',
        '4D',
        '5D',
        '6D',
        '7D',
    }

    if horizon_name in daily_horizons:

        if not future_rows:

            return create_location_targets_daily(
                None,
                horizon_name,
                previous_rows,
            )

        return create_location_targets_daily(
            future_rows[0],
            horizon_name,
            previous_rows,
        )

    # -----------------------------------------------------
    # PERIOD HORIZONS
    # -----------------------------------------------------

    period_horizons = {
        '8_15D',
        '16_30D',
        '30D',
    }

    if horizon_name in period_horizons:

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