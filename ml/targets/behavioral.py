# =========================================================
# BEHAVIORAL TARGETS
# =========================================================


# =========================================================
# SAFE VALUE HELPERS
# =========================================================

def _get_stress_level(row):
    """
    Safely extract stress level.
    """

    try:
        return float(
            row.get('Stress_Level')
            or 0.0
        )

    except (
        TypeError,
        ValueError,
    ):
        return 0.0


def _get_sleep_hours(row):
    """
    Safely extract sleep duration.
    """

    try:
        return float(
            row.get('Sleep_Hours')
            or 0.0
        )

    except (
        TypeError,
        ValueError,
    ):
        return 0.0


def _get_social_activity(row):
    """
    Safely extract social activity level.
    """

    return str(
        row.get('Social_Activity')
        or ''
    ).strip().lower()


def _get_work_status(row):
    """
    Safely extract work status.
    """

    return str(
        row.get('Work_Status')
        or ''
    ).strip().lower()


# =========================================================
# BEHAVIORAL CLASSIFICATION
# =========================================================

def _is_high_stress(row):
    """
    High stress means stress level >= 7.
    """

    return (
        _get_stress_level(row) >= 7
    )


def _is_moderate_or_high_stress(row):
    """
    Moderate or high stress means stress level >= 5.
    """

    return (
        _get_stress_level(row) >= 5
    )


def _is_low_sleep(row):
    """
    Low sleep means more than zero but less than 6 hours.
    """

    sleep_hours = _get_sleep_hours(
        row
    )

    return (
        sleep_hours > 0
        and sleep_hours < 6
    )


def _is_very_low_sleep(row):
    """
    Very low sleep means more than zero but less than 5 hours.
    """

    sleep_hours = _get_sleep_hours(
        row
    )

    return (
        sleep_hours > 0
        and sleep_hours < 5
    )


def _is_high_social_activity(row):
    """
    High social activity.
    """

    return (
        _get_social_activity(row)
        == 'high'
    )


def _is_moderate_or_high_social_activity(row):
    """
    Moderate, medium, or high social activity.
    """

    return (
        _get_social_activity(row)
        in {
            'moderate',
            'medium',
            'high',
        }
    )


def _is_working_day(row):
    """
    Determine whether the day is a working day.
    """

    return (
        _get_work_status(row)
        in {
            'working',
            'work',
        }
    )


def _is_difficult_behavioral_day(row):
    """
    Determine whether the day represents a
    difficult behavioral day.

    A difficult behavioral day is defined by:

        High stress
        OR
        Very low sleep
    """

    return (
        _is_high_stress(row)
        or _is_very_low_sleep(row)
    )


# =========================================================
# DAILY BEHAVIORAL TARGETS
# =========================================================

def create_behavioral_targets_daily(
    future_row,
    horizon_name,
):
    """
    Create behavioral targets for one specific
    future day.

    horizon_name identifies the exact future day.

    Examples:

        1D -> T + 1
        2D -> T + 2
        3D -> T + 3
        ...
        7D -> T + 7

    The important difference from the old design is
    that each future day has its own independent target.
    """

    if not future_row:

        return {
            f'Target_High_Stress_{horizon_name}':
                float('nan'),

            f'Target_Moderate_or_High_Stress_{horizon_name}':
                float('nan'),

            f'Target_Low_Sleep_{horizon_name}':
                float('nan'),

            f'Target_Very_Low_Sleep_{horizon_name}':
                float('nan'),

            f'Target_High_Social_Activity_{horizon_name}':
                float('nan'),

            f'Target_Moderate_or_High_Social_Activity_{horizon_name}':
                float('nan'),

            f'Target_Working_Day_{horizon_name}':
                float('nan'),

            f'Target_Difficult_Behavioral_Day_{horizon_name}':
                float('nan'),
        }

    high_stress = _is_high_stress(
        future_row
    )

    moderate_or_high_stress = (
        _is_moderate_or_high_stress(
            future_row
        )
    )

    low_sleep = _is_low_sleep(
        future_row
    )

    very_low_sleep = _is_very_low_sleep(
        future_row
    )

    high_social_activity = (
        _is_high_social_activity(
            future_row
        )
    )

    moderate_or_high_social_activity = (
        _is_moderate_or_high_social_activity(
            future_row
        )
    )

    working_day = _is_working_day(
        future_row
    )

    difficult_behavioral_day = (
        _is_difficult_behavioral_day(
            future_row
        )
    )

    return {

        f'Target_High_Stress_{horizon_name}':
            int(high_stress),

        f'Target_Moderate_or_High_Stress_{horizon_name}':
            int(
                moderate_or_high_stress
            ),

        f'Target_Low_Sleep_{horizon_name}':
            int(low_sleep),

        f'Target_Very_Low_Sleep_{horizon_name}':
            int(very_low_sleep),

        f'Target_High_Social_Activity_{horizon_name}':
            int(high_social_activity),

        f'Target_Moderate_or_High_Social_Activity_{horizon_name}':
            int(
                moderate_or_high_social_activity
            ),

        f'Target_Working_Day_{horizon_name}':
            int(working_day),

        f'Target_Difficult_Behavioral_Day_{horizon_name}':
            int(
                difficult_behavioral_day
            ),
    }


# =========================================================
# PERIOD BEHAVIORAL TARGETS
# =========================================================

def create_behavioral_targets_period(
    future_rows,
    horizon_name,
):
    """
    Create behavioral targets for a future period.

    Unlike the daily targets, period targets do not
    describe each individual day.

    They answer questions such as:

        Did high stress occur at least once
        during the period?

        Did low sleep occur at least once?

        Was there at least one working day?

        Was there at least one difficult behavioral day?

    This provides a useful higher-level summary while
    preserving the detailed daily predictions separately.
    """

    if not future_rows:

        return {
            f'Target_High_Stress_{horizon_name}':
                float('nan'),

            f'Target_Moderate_or_High_Stress_{horizon_name}':
                float('nan'),

            f'Target_Low_Sleep_{horizon_name}':
                float('nan'),

            f'Target_Very_Low_Sleep_{horizon_name}':
                float('nan'),

            f'Target_High_Social_Activity_{horizon_name}':
                float('nan'),

            f'Target_Moderate_or_High_Social_Activity_{horizon_name}':
                float('nan'),

            f'Target_Working_Day_{horizon_name}':
                float('nan'),

            f'Target_Difficult_Behavioral_Day_{horizon_name}':
                float('nan'),
        }

    high_stress = False

    moderate_or_high_stress = False

    low_sleep = False

    very_low_sleep = False

    high_social_activity = False

    moderate_or_high_social_activity = False

    working_day = False

    difficult_behavioral_day = False

    for row in future_rows:

        if _is_high_stress(row):
            high_stress = True

        if _is_moderate_or_high_stress(row):
            moderate_or_high_stress = True

        if _is_low_sleep(row):
            low_sleep = True

        if _is_very_low_sleep(row):
            very_low_sleep = True

        if _is_high_social_activity(row):
            high_social_activity = True

        if _is_moderate_or_high_social_activity(row):
            moderate_or_high_social_activity = True

        if _is_working_day(row):
            working_day = True

        if _is_difficult_behavioral_day(row):
            difficult_behavioral_day = True

    return {

        f'Target_High_Stress_{horizon_name}':
            int(high_stress),

        f'Target_Moderate_or_High_Stress_{horizon_name}':
            int(
                moderate_or_high_stress
            ),

        f'Target_Low_Sleep_{horizon_name}':
            int(low_sleep),

        f'Target_Very_Low_Sleep_{horizon_name}':
            int(very_low_sleep),

        f'Target_High_Social_Activity_{horizon_name}':
            int(high_social_activity),

        f'Target_Moderate_or_High_Social_Activity_{horizon_name}':
            int(
                moderate_or_high_social_activity
            ),

        f'Target_Working_Day_{horizon_name}':
            int(working_day),

        f'Target_Difficult_Behavioral_Day_{horizon_name}':
            int(
                difficult_behavioral_day
            ),
    }


# =========================================================
# PUBLIC BEHAVIORAL TARGETS
# =========================================================

def create_behavioral_targets(
    future_rows,
    horizon_name='1D',
):
    """
    Public Behavioral Target Engineering entry point.

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

    Period horizons represent a complete future period.
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

            return create_behavioral_targets_daily(
                None,
                horizon_name,
            )

        return create_behavioral_targets_daily(
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

        return create_behavioral_targets_period(
            future_rows,
            horizon_name,
        )

    # -----------------------------------------------------
    # INVALID HORIZON
    # -----------------------------------------------------

    raise ValueError(
        f'Unsupported behavioral horizon: '
        f'{horizon_name}'
    )