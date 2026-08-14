# =========================================================
# BEHAVIORAL TARGETS
# =========================================================


def _get_stress_level(row):
    """
    Safely extract stress level.
    """

    return float(
        row.get('Stress_Level')
        or 0.0
    )


def _get_sleep_hours(row):
    """
    Safely extract sleep duration.
    """

    return float(
        row.get('Sleep_Hours')
        or 0.0
    )


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
# SINGLE-DAY BEHAVIORAL TARGETS
# =========================================================

def create_behavioral_targets_1d(
    future_row,
):
    """
    Create behavioral targets for the next day.

    future_row represents T + 1.
    """

    stress_level = _get_stress_level(
        future_row
    )

    sleep_hours = _get_sleep_hours(
        future_row
    )

    social_activity = _get_social_activity(
        future_row
    )

    work_status = _get_work_status(
        future_row
    )

    # -----------------------------------------------------
    # Stress
    # -----------------------------------------------------

    high_stress = int(
        stress_level >= 7
    )

    moderate_or_high_stress = int(
        stress_level >= 5
    )

    # -----------------------------------------------------
    # Sleep
    # -----------------------------------------------------

    low_sleep = int(
        sleep_hours > 0
        and sleep_hours < 6
    )

    very_low_sleep = int(
        sleep_hours > 0
        and sleep_hours < 5
    )

    # -----------------------------------------------------
    # Social activity
    # -----------------------------------------------------

    high_social_activity = int(
        social_activity == 'high'
    )

    moderate_or_high_social_activity = int(
        social_activity
        in {
            'moderate',
            'medium',
            'high',
        }
    )

    # -----------------------------------------------------
    # Work
    # -----------------------------------------------------

    working_day = int(
        work_status
        in {
            'working',
            'work',
        }
    )

    # -----------------------------------------------------
    # Difficult behavioral day
    # -----------------------------------------------------

    difficult_behavioral_day = int(
        high_stress
        or very_low_sleep
    )

    return {

        'Target_High_Stress_1D':
            high_stress,

        'Target_Moderate_or_High_Stress_1D':
            moderate_or_high_stress,

        'Target_Low_Sleep_1D':
            low_sleep,

        'Target_Very_Low_Sleep_1D':
            very_low_sleep,

        'Target_High_Social_Activity_1D':
            high_social_activity,

        'Target_Moderate_or_High_Social_Activity_1D':
            moderate_or_high_social_activity,

        'Target_Working_Day_1D':
            working_day,

        'Target_Difficult_Behavioral_Day_1D':
            difficult_behavioral_day,
    }


# =========================================================
# MULTI-DAY BEHAVIORAL TARGETS
# =========================================================

def create_behavioral_targets_multi_day(
    future_rows,
    horizon_name,
):
    """
    Create behavioral targets for a future period.

    A multi-day target is positive when the corresponding
    behavioral condition occurs on at least one future day.

    Example:

        7D

        Stress:
            0, 0, 1, 0, 0, 0, 0

        Target_High_Stress_7D = 1

    The current day is never included.
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

        stress_level = _get_stress_level(
            row
        )

        sleep_hours = _get_sleep_hours(
            row
        )

        social_activity = _get_social_activity(
            row
        )

        work_status = _get_work_status(
            row
        )

        # -------------------------------------------------
        # Stress
        # -------------------------------------------------

        if stress_level >= 7:
            high_stress = True

        if stress_level >= 5:
            moderate_or_high_stress = True

        # -------------------------------------------------
        # Sleep
        # -------------------------------------------------

        if (
            sleep_hours > 0
            and sleep_hours < 6
        ):
            low_sleep = True

        if (
            sleep_hours > 0
            and sleep_hours < 5
        ):
            very_low_sleep = True

        # -------------------------------------------------
        # Social activity
        # -------------------------------------------------

        if social_activity == 'high':
            high_social_activity = True

        if social_activity in {
            'moderate',
            'medium',
            'high',
        }:
            moderate_or_high_social_activity = True

        # -------------------------------------------------
        # Work
        # -------------------------------------------------

        if work_status in {
            'working',
            'work',
        }:
            working_day = True

        # -------------------------------------------------
        # Difficult behavioral day
        # -------------------------------------------------

        if (
            stress_level >= 7
            or (
                sleep_hours > 0
                and sleep_hours < 5
            )
        ):
            difficult_behavioral_day = True

    return {

        f'Target_High_Stress_{horizon_name}':
            int(high_stress),

        f'Target_Moderate_or_High_Stress_{horizon_name}':
            int(moderate_or_high_stress),

        f'Target_Low_Sleep_{horizon_name}':
            int(low_sleep),

        f'Target_Very_Low_Sleep_{horizon_name}':
            int(very_low_sleep),

        f'Target_High_Social_Activity_{horizon_name}':
            int(high_social_activity),

        f'Target_Moderate_or_High_Social_Activity_{horizon_name}':
            int(moderate_or_high_social_activity),

        f'Target_Working_Day_{horizon_name}':
            int(working_day),

        f'Target_Difficult_Behavioral_Day_{horizon_name}':
            int(difficult_behavioral_day),
    }


# =========================================================
# PUBLIC ENTRY POINT
# =========================================================

def create_behavioral_targets(
    future_rows,
    horizon_name='1D',
):
    """
    Public Behavioral Target Engineering entry point.

    Parameters
    ----------
    future_rows : list[dict]
        Future rows belonging to the requested horizon.

    horizon_name : str
        '1D', '7D', or '30D'.

    Returns
    -------
    dict
        Behavioral targets for the requested horizon.
    """

    if horizon_name == '1D':

        if not future_rows:

            return {
                'Target_High_Stress_1D':
                    float('nan'),

                'Target_Moderate_or_High_Stress_1D':
                    float('nan'),

                'Target_Low_Sleep_1D':
                    float('nan'),

                'Target_Very_Low_Sleep_1D':
                    float('nan'),

                'Target_High_Social_Activity_1D':
                    float('nan'),

                'Target_Moderate_or_High_Social_Activity_1D':
                    float('nan'),

                'Target_Working_Day_1D':
                    float('nan'),

                'Target_Difficult_Behavioral_Day_1D':
                    float('nan'),
            }

        return create_behavioral_targets_1d(
            future_rows[0]
        )

    if horizon_name in {
        '7D',
        '30D',
    }:

        return create_behavioral_targets_multi_day(
            future_rows,
            horizon_name,
        )

    raise ValueError(
        f'Unsupported behavioral horizon: '
        f'{horizon_name}'
    )