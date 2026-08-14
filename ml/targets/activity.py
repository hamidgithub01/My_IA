from ml.targets.common import (
    DAILY_HORIZONS,
    PERIOD_HORIZONS,
    to_float,
    to_int,
)

# =========================================================
# SAFE VALUE HELPERS
# =========================================================

def _get_activity_count(row):
    """
    Safely extract activity count from one row.
    """

    return to_int(
        row.get('Activity_Count')
    )


def _get_activity_duration(row):
    """
    Safely extract total activity duration
    from one row.
    """

    return to_float(
        row.get(
            'Activity_Duration_Minutes'
        )
    )


# =========================================================
# ACTIVITY CLASSIFICATION
# =========================================================

def _has_activity(row):
    """
    Determine whether any activity occurred.
    """

    return (
        _get_activity_count(row) > 0
    )


def _is_high_activity(row):
    """
    Determine whether the day contains high activity.

    High activity means:

        activity count >= 2

    OR

        activity duration >= 120 minutes
    """

    activity_count = _get_activity_count(
        row
    )

    activity_duration = _get_activity_duration(
        row
    )

    return (
        activity_count >= 2
        or activity_duration >= 120
    )


def _is_long_activity(row):
    """
    Determine whether activity lasted at least
    60 minutes.
    """

    return (
        _get_activity_duration(row)
        >= 60
    )


# =========================================================
# DAILY ACTIVITY TARGETS
# =========================================================

def create_activity_targets_daily(
    future_row,
    horizon_name,
):
    """
    Create activity targets for one specific
    future day.

    Examples:

        1D -> T + 1
        2D -> T + 2
        ...
        7D -> T + 7

    Each future day receives its own independent
    activity targets.
    """

    if not future_row:

        return {

            f'Target_Has_Activity_{horizon_name}':
                float('nan'),

            f'Target_High_Activity_{horizon_name}':
                float('nan'),

            f'Target_Long_Activity_{horizon_name}':
                float('nan'),
        }

    return {

        f'Target_Has_Activity_{horizon_name}':
            int(
                _has_activity(
                    future_row
                )
            ),

        f'Target_High_Activity_{horizon_name}':
            int(
                _is_high_activity(
                    future_row
                )
            ),

        f'Target_Long_Activity_{horizon_name}':
            int(
                _is_long_activity(
                    future_row
                )
            ),
    }


# =========================================================
# PERIOD ACTIVITY TARGETS
# =========================================================

def create_activity_targets_period(
    future_rows,
    horizon_name,
):
    """
    Create activity targets for a future period.

    Period targets summarize the existence of activity
    conditions within the supplied period.

    They do not replace the detailed daily targets.

    Definitions:

        Has_Activity
            At least one future day has activity.

        High_Activity
            At least one future day satisfies the
            high-activity condition.

        Long_Activity
            At least one future day has 60+ minutes
            of activity.
    """

    if not future_rows:

        return {

            f'Target_Has_Activity_{horizon_name}':
                float('nan'),

            f'Target_High_Activity_{horizon_name}':
                float('nan'),

            f'Target_Long_Activity_{horizon_name}':
                float('nan'),
        }

    has_activity = False
    high_activity = False
    long_activity = False

    for row in future_rows:

        if _has_activity(row):
            has_activity = True

        if _is_high_activity(row):
            high_activity = True

        if _is_long_activity(row):
            long_activity = True

    return {

        f'Target_Has_Activity_{horizon_name}':
            int(has_activity),

        f'Target_High_Activity_{horizon_name}':
            int(high_activity),

        f'Target_Long_Activity_{horizon_name}':
            int(long_activity),
    }


# =========================================================
# PUBLIC ACTIVITY TARGETS
# =========================================================

def create_activity_targets(
    future_rows,
    horizon_name='1D',
):
    """
    Public Activity Target Engineering entry point.

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

    if horizon_name in DAILY_HORIZONS:

        if not future_rows:

            return create_activity_targets_daily(
                None,
                horizon_name,
            )

        return create_activity_targets_daily(
            future_rows[0],
            horizon_name,
        )

    # -----------------------------------------------------
    # PERIOD HORIZONS
    # -----------------------------------------------------

    if horizon_name in PERIOD_HORIZONS:

        return create_activity_targets_period(
            future_rows,
            horizon_name,
        )

    # -----------------------------------------------------
    # INVALID HORIZON
    # -----------------------------------------------------

    raise ValueError(
        f'Unsupported activity horizon: '
        f'{horizon_name}'
    )