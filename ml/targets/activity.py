# =========================================================
# ACTIVITY TARGETS
# =========================================================


def _get_activity_count(row):
    """
    Safely extract activity count from one row.
    """

    return int(
        row.get('Activity_Count')
        or 0
    )


def _get_activity_duration(row):
    """
    Safely extract total activity duration
    from one row.
    """

    return float(
        row.get(
            'Activity_Duration_Minutes'
        )
        or 0.0
    )


# =========================================================
# SINGLE-DAY ACTIVITY TARGETS
# =========================================================

def create_activity_targets_1d(
    future_row,
):
    """
    Create activity targets for the next day.

    future_row represents T + 1.

    Targets:

        Target_Has_Activity_1D
        Target_High_Activity_1D
        Target_Long_Activity_1D
    """

    activity_count = _get_activity_count(
        future_row
    )

    activity_duration = _get_activity_duration(
        future_row
    )

    return {
        'Target_Has_Activity_1D':
            int(
                activity_count > 0
            ),

        'Target_High_Activity_1D':
            int(
                activity_count >= 2
                or activity_duration >= 120
            ),

        'Target_Long_Activity_1D':
            int(
                activity_duration >= 60
            ),
    }


# =========================================================
# MULTI-DAY ACTIVITY TARGETS
# =========================================================

def create_activity_targets_multi_day(
    future_rows,
    horizon_name,
):
    """
    Create activity targets for a future horizon.

    Parameters
    ----------
    future_rows : list[dict]
        Rows belonging to the future horizon.

    horizon_name : str
        '7D' or '30D'.

    Returns
    -------
    dict

    The targets describe whether activity occurs
    during the supplied future period.

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

        activity_count = _get_activity_count(
            row
        )

        activity_duration = _get_activity_duration(
            row
        )

        if activity_count > 0:
            has_activity = True

        if (
            activity_count >= 2
            or activity_duration >= 120
        ):
            high_activity = True

        if activity_duration >= 60:
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

    For 1D:

        future_rows must contain T + 1.

    For 7D:

        future_rows contains T + 1 ... T + 7.

    For 30D:

        future_rows contains T + 1 ... T + 30.
    """

    if horizon_name == '1D':

        if not future_rows:

            return {
                'Target_Has_Activity_1D':
                    float('nan'),

                'Target_High_Activity_1D':
                    float('nan'),

                'Target_Long_Activity_1D':
                    float('nan'),
            }

        return create_activity_targets_1d(
            future_rows[0]
        )

    if horizon_name in {
        '7D',
        '30D',
    }:

        return create_activity_targets_multi_day(
            future_rows,
            horizon_name,
        )

    raise ValueError(
        f'Unsupported activity horizon: '
        f'{horizon_name}'
    )