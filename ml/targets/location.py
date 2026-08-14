# =========================================================
# LOCATION TARGETS
# =========================================================


def _normalize_location(value):
    """
    Normalize a location value safely.
    """

    return str(
        value or ''
    ).strip().lower()


# =========================================================
# SINGLE-DAY LOCATION TARGETS
# =========================================================

def create_location_targets_1d(
    future_row,
    previous_rows=None,
):
    """
    Create location targets for the next day.

    future_row represents T + 1.

    previous_rows contains only rows before the
    current target day and is used to determine
    whether the future location represents a change.
    """

    previous_rows = previous_rows or []

    current_location = _normalize_location(
        future_row.get('Location')
    )

    previous_location = ''

    # -----------------------------------------------------
    # Find the latest known historical location
    # -----------------------------------------------------

    for historical_row in reversed(
        previous_rows
    ):

        historical_location = _normalize_location(
            historical_row.get('Location')
        )

        if historical_location:

            previous_location = (
                historical_location
            )

            break

    # -----------------------------------------------------
    # Location targets
    # -----------------------------------------------------

    has_location = int(
        bool(current_location)
    )

    location_changed = int(
        bool(
            current_location
            and previous_location
            and current_location
            != previous_location
        )
    )

    same_location = int(
        bool(
            current_location
            and previous_location
            and current_location
            == previous_location
        )
    )

    return {

        'Target_Has_Location_1D':
            has_location,

        'Target_Location_Changed_1D':
            location_changed,

        'Target_Same_Location_1D':
            same_location,

        'Target_Location_1D':
            current_location or None,
    }


# =========================================================
# MULTI-DAY LOCATION TARGETS
# =========================================================

def create_location_targets_multi_day(
    future_rows,
    horizon_name,
    previous_rows=None,
):
    """
    Create location targets for a future period.

    Definitions:

        Target_Has_Location
            At least one future day has a known location.

        Target_Location_Changed
            The user changes location during the
            future period compared with the latest
            known historical location.

        Target_Same_Location
            At least one future day has the same
            location as the latest known historical
            location.

        Target_Location
            The most recently observed future location.

    The actual location is retained as a categorical
    target because it can later be used for
    multi-class prediction.
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

    # -----------------------------------------------------
    # Find latest historical location
    # -----------------------------------------------------

    previous_location = ''

    for historical_row in reversed(
        previous_rows
    ):

        historical_location = _normalize_location(
            historical_row.get('Location')
        )

        if historical_location:

            previous_location = (
                historical_location
            )

            break

    # -----------------------------------------------------
    # Analyze future locations
    # -----------------------------------------------------

    has_location = False
    location_changed = False
    same_location = False

    future_locations = []

    for future_row in future_rows:

        location = _normalize_location(
            future_row.get('Location')
        )

        if not location:
            continue

        has_location = True

        future_locations.append(
            location
        )

        # -------------------------------------------------
        # Compare with historical location
        # -------------------------------------------------

        if previous_location:

            if location != previous_location:

                location_changed = True

            if location == previous_location:

                same_location = True

    # -----------------------------------------------------
    # Most recent known future location
    # -----------------------------------------------------

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
# PUBLIC ENTRY POINT
# =========================================================

def create_location_targets(
    future_rows,
    horizon_name='1D',
    previous_rows=None,
):
    """
    Public Location Target Engineering entry point.

    Parameters
    ----------
    future_rows : list[dict]
        Future rows belonging to the requested horizon.

    horizon_name : str
        '1D', '7D', or '30D'.

    previous_rows : list[dict]
        Historical rows before the prediction date.

    Returns
    -------
    dict
        Location targets for the requested horizon.
    """

    previous_rows = previous_rows or []

    # -----------------------------------------------------
    # 1 DAY
    # -----------------------------------------------------

    if horizon_name == '1D':

        if not future_rows:

            return {

                'Target_Has_Location_1D':
                    float('nan'),

                'Target_Location_Changed_1D':
                    float('nan'),

                'Target_Same_Location_1D':
                    float('nan'),

                'Target_Location_1D':
                    None,
            }

        return create_location_targets_1d(
            future_rows[0],
            previous_rows,
        )

    # -----------------------------------------------------
    # 7 DAYS / 30 DAYS
    # -----------------------------------------------------

    if horizon_name in {
        '7D',
        '30D',
    }:

        return create_location_targets_multi_day(
            future_rows,
            horizon_name,
            previous_rows,
        )

    raise ValueError(
        f'Unsupported location horizon: '
        f'{horizon_name}'
    )