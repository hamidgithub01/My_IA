# =========================================================
# EVENT TARGETS
# =========================================================


def _get_event_count(row):
    """
    Safely extract event count from one row.
    """

    return int(
        row.get('Event_Count')
        or 0
    )


def _has_special_event(row):
    """
    Determine whether the row contains a special event.
    """

    special_event = str(
        row.get('Special_Event')
        or ''
    ).strip()

    return bool(special_event)


# =========================================================
# SINGLE-DAY EVENT TARGETS
# =========================================================

def create_event_targets_1d(
    future_row,
):
    """
    Create event targets for the next day.

    future_row represents T + 1.
    """

    event_count = _get_event_count(
        future_row
    )

    special_event = _has_special_event(
        future_row
    )

    return {

        'Target_Has_Event_1D':
            int(
                event_count > 0
            ),

        'Target_Multiple_Events_1D':
            int(
                event_count >= 2
            ),

        'Target_Has_Special_Event_1D':
            int(
                special_event
            ),
    }


# =========================================================
# MULTI-DAY EVENT TARGETS
# =========================================================

def create_event_targets_multi_day(
    future_rows,
    horizon_name,
):
    """
    Create event targets for a future period.

    A target becomes 1 when the corresponding event
    condition occurs on at least one future day.

    Example:

        Event counts over 7 days:

            0, 0, 1, 0, 2, 0, 0

        Results:

            Has_Event       = 1
            Multiple_Events = 1
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

        event_count = _get_event_count(
            row
        )

        special_event = _has_special_event(
            row
        )

        # -------------------------------------------------
        # Any event
        # -------------------------------------------------

        if event_count > 0:
            has_event = True

        # -------------------------------------------------
        # Multiple events in one day
        # -------------------------------------------------

        if event_count >= 2:
            multiple_events = True

        # -------------------------------------------------
        # Special event
        # -------------------------------------------------

        if special_event:
            has_special_event = True

    return {

        f'Target_Has_Event_{horizon_name}':
            int(
                has_event
            ),

        f'Target_Multiple_Events_{horizon_name}':
            int(
                multiple_events
            ),

        f'Target_Has_Special_Event_{horizon_name}':
            int(
                has_special_event
            ),
    }


# =========================================================
# PUBLIC ENTRY POINT
# =========================================================

def create_event_targets(
    future_rows,
    horizon_name='1D',
):
    """
    Public Event Target Engineering entry point.

    Parameters
    ----------
    future_rows : list[dict]
        Future rows belonging to the requested horizon.

    horizon_name : str
        '1D', '7D', or '30D'.

    Returns
    -------
    dict
        Event targets for the requested horizon.
    """

    if horizon_name == '1D':

        if not future_rows:

            return {

                'Target_Has_Event_1D':
                    float('nan'),

                'Target_Multiple_Events_1D':
                    float('nan'),

                'Target_Has_Special_Event_1D':
                    float('nan'),
            }

        return create_event_targets_1d(
            future_rows[0]
        )

    if horizon_name in {
        '7D',
        '30D',
    }:

        return create_event_targets_multi_day(
            future_rows,
            horizon_name,
        )

    raise ValueError(
        f'Unsupported event horizon: '
        f'{horizon_name}'
    )