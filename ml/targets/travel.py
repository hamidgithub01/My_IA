
# =========================================================
# TRAVEL TARGETS
# =========================================================


# =========================================================
# SAFE VALUE HELPERS
# =========================================================

def _get_travel(row):
    """
    Safely extract and normalize travel status.
    """

    return str(
        row.get('Travel')
        or ''
    ).strip().lower()


def _is_travel_day(row):
    """
    Determine whether one specific day is a travel day.
    """

    return _get_travel(row) in {
        'yes',
        'true',
        '1',
    }


# =========================================================
# DAILY TRAVEL TARGETS
# =========================================================

def create_travel_targets_daily(
    future_row,
    horizon_name,
):
    """
    Create a travel target for one exact future day.

    Examples:

        1D -> T + 1
        2D -> T + 2
        3D -> T + 3
        ...
        30D -> T + 30

    The target therefore answers:

        "Is T + N a travel day?"
    """

    target_name = (
        f'Target_Travel_Day_{horizon_name}'
    )

    if future_row is None:

        return {
            target_name:
                float('nan'),
        }

    return {
        target_name:
            int(
                _is_travel_day(
                    future_row
                )
            ),
    }


# =========================================================
# PERIOD TRAVEL TARGETS
# =========================================================

def create_travel_targets_period(
    future_rows,
    horizon_name,
):
    """
    Create a travel target for a future period.

    The target is 1 when at least one day inside
    the supplied period is a travel day.

    Supported period summaries:

        7D_SUMMARY
            T + 1 ... T + 7

        30D_SUMMARY
            T + 1 ... T + 30

    These summaries do not replace the individual
    daily travel targets.
    """

    target_name = (
        f'Target_Travel_Day_{horizon_name}'
    )

    if not future_rows:

        return {
            target_name:
                float('nan'),
        }

    travel_day = any(
        _is_travel_day(row)
        for row in future_rows
    )

    return {
        target_name:
            int(travel_day),
    }


# =========================================================
# PUBLIC TRAVEL TARGETS
# =========================================================

def create_travel_targets(
    future_rows,
    horizon_name='1D',
):
    """
    Public Travel Target Engineering entry point.

    Daily horizons:

        1D
        2D
        3D
        4D
        5D
        6D
        7D
        8D
        ...
        30D

    Each daily horizon represents exactly one
    future day.

    Period summary horizons:

        7D_SUMMARY
        30D_SUMMARY

    The daily targets preserve exact timing.

    The summary targets provide a broader period-level
    view without replacing the daily information.
    """

    # =====================================================
    # DAILY HORIZONS
    # =====================================================

    daily_horizons = {
        f'{days}D'
        for days in range(1, 31)
    }

    if horizon_name in daily_horizons:

        if not future_rows:

            return create_travel_targets_daily(
                None,
                horizon_name,
            )

        return create_travel_targets_daily(
            future_rows[0],
            horizon_name,
        )

    # =====================================================
    # PERIOD SUMMARY HORIZONS
    # =====================================================

    period_horizons = {
        '7D_SUMMARY',
        '30D_SUMMARY',
    }

    if horizon_name in period_horizons:

        return create_travel_targets_period(
            future_rows,
            horizon_name,
        )

    # =====================================================
    # INVALID HORIZON
    # =====================================================

    raise ValueError(
        f'Unsupported travel horizon: '
        f'{horizon_name}'
    )
