# =========================================================
# EVENT TARGETS
# =========================================================


# =========================================================
# SAFE VALUE HELPERS
# =========================================================

def _get_event_count(row):
    """
    Safely extract event count from one row.
    """

    try:
        return int(
            row.get('Event_Count')
            or 0
        )

    except (
        TypeError,
        ValueError,
    ):
        return 0


def _has_special_event(row):
    """
    Determine whether the row contains a special event.
    """

    special_event = str(
        row.get('Special_Event')
        or ''
    ).strip()

    return bool(
        special_event
    )


# =========================================================
# EVENT CLASSIFICATION
# =========================================================

def _has_event(row):
    """
    Determine whether at least one event occurs.
    """

    return (
        _get_event_count(row) > 0
    )


def _has_multiple_events(row):
    """
    Determine whether the day contains multiple events.

    Multiple events means at least two events
    on the same day.
    """

    return (
        _get_event_count(row) >= 2
    )


# =========================================================
# DAILY EVENT TARGETS
# =========================================================

def create_event_targets_daily(
    future_row,
    horizon_name,
):
    """
    Create event targets for one specific
    future day.

    Examples:

        1D -> T + 1
        2D -> T + 2
        ...
        7D -> T + 7

    Each future day receives independent event
    targets.
    """

    if not future_row:

        return {

            f'Target_Has_Event_{horizon_name}':
                float('nan'),

            f'Target_Multiple_Events_{horizon_name}':
                float('nan'),

            f'Target_Has_Special_Event_{horizon_name}':
                float('nan'),
        }

    return {

        f'Target_Has_Event_{horizon_name}':
            int(
                _has_event(
                    future_row
                )
            ),

        f'Target_Multiple_Events_{horizon_name}':
            int(
                _has_multiple_events(
                    future_row
                )
            ),

        f'Target_Has_Special_Event_{horizon_name}':
            int(
                _has_special_event(
                    future_row
                )
            ),
    }


# =========================================================
# PERIOD EVENT TARGETS
# =========================================================

def create_event_targets_period(
    future_rows,
    horizon_name,
):
    """
    Create event targets for a future period.

    A period target becomes 1 when the corresponding
    event condition occurs on at least one future day.

    Definitions:

        Has_Event
            At least one future day has an event.

        Multiple_Events
            At least one future day contains
            two or more events.

        Has_Special_Event
            At least one future day contains
            a special event.
    """

    if not future_rows:

        return {

            f'Target_Has_Event_{horizon_name}':
                float('nan'),

            f'Target_Multiple_Events_{horizon_name}':
                float('nan'),

            f'Target_Has_Special_Event_{horizon_name}':
                float('nan'),
        }

    has_event = False
    multiple_events = False
    has_special_event = False

    for row in future_rows:

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

def create_event_targets(
    future_rows,
    horizon_name='1D',
):
    """
    Public Event Target Engineering entry point.

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

    Period horizons summarize a complete future period.
    """

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

            return create_event_targets_daily(
                None,
                horizon_name,
            )

        return create_event_targets_daily(
            future_rows[0],
            horizon_name,
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

        return create_event_targets_period(
            future_rows,
            horizon_name,
        )

    # -----------------------------------------------------
    # INVALID HORIZON
    # -----------------------------------------------------

    raise ValueError(
        f'Unsupported event horizon: '
        f'{horizon_name}'
    )