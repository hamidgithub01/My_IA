
from ml.targets.common import (
    DAILY_HORIZONS,
    PERIOD_HORIZONS,
    normalize_text,
)


# =========================================================
# TRAVEL TARGETS
# =========================================================


# =========================================================
# TRAVEL CLASSIFICATION
# =========================================================

def _is_travel_day(row):
    """
    Determine whether one specific day is a travel day.
    """

    return normalize_text(
        row.get('Travel')
    ) in {
        'yes',
        'true',
        '1',
    }


# =========================================================
# EMPTY TARGETS
# =========================================================

def _empty_targets(horizon_name):
    """
    Return empty travel targets for a future horizon.
    """

    return {
        f'Target_Travel_Day_{horizon_name}':
            float('nan'),
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

    Each daily horizon represents one specific
    future day.
    """

    if not future_row:

        return _empty_targets(
            horizon_name
        )

    return {
        f'Target_Travel_Day_{horizon_name}':
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
    """

    if not future_rows:

        return _empty_targets(
            horizon_name
        )

    return {
        f'Target_Travel_Day_{horizon_name}':
            int(
                any(
                    _is_travel_day(row)
                    for row in future_rows
                )
            ),
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

        Defined by DAILY_HORIZONS.

    Period horizons:

        8_15D
        16_30D
        30D
    """

    if future_rows is None:

        future_rows = []

    # =====================================================
    # DAILY HORIZONS
    # =====================================================

    if horizon_name in DAILY_HORIZONS:

        future_row = (
            future_rows[0]
            if future_rows
            else None
        )

        return create_travel_targets_daily(
            future_row,
            horizon_name,
        )

    # =====================================================
    # PERIOD HORIZONS
    # =====================================================

    if horizon_name in PERIOD_HORIZONS:

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
