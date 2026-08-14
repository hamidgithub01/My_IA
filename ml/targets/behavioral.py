
from ml.targets.common import (
    DAILY_HORIZONS,
    PERIOD_HORIZONS,
    to_float,
)


# =========================================================
# SAFE VALUE HELPERS
# =========================================================

def _get_stress_level(row):
    """
    Safely extract stress level.
    """

    return to_float(
        row.get('Stress_Level')
    )


def _get_sleep_hours(row):
    """
    Safely extract sleep duration.
    """

    return to_float(
        row.get('Sleep_Hours')
    )


def _get_social_activity(row):
    """
    Safely extract and normalize social activity level.
    """

    return str(
        row.get('Social_Activity')
        or ''
    ).strip().lower()


def _get_work_status(row):
    """
    Safely extract and normalize work status.
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

    sleep_hours = _get_sleep_hours(row)

    return (
        sleep_hours > 0
        and sleep_hours < 6
    )


def _is_very_low_sleep(row):
    """
    Very low sleep means more than zero but less than 5 hours.
    """

    sleep_hours = _get_sleep_hours(row)

    return (
        sleep_hours > 0
        and sleep_hours < 5
    )


def _is_high_social_activity(row):
    """
    High social activity.
    """

    return (
        _get_social_activity(row) == 'high'
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
    Determine whether the day represents a difficult
    behavioral day.

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
# EMPTY TARGETS
# =========================================================

def _empty_targets(horizon_name):
    """
    Return empty behavioral targets for a future horizon.
    """

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


# =========================================================
# DAILY BEHAVIORAL TARGETS
# =========================================================

def create_behavioral_targets_daily(
    future_row,
    horizon_name,
):
    """
    Create behavioral targets for one specific future day.

    Each future day receives independent targets.
    """

    if not future_row:
        return _empty_targets(
            horizon_name
        )

    return {
        f'Target_High_Stress_{horizon_name}':
            int(
                _is_high_stress(
                    future_row
                )
            ),

        f'Target_Moderate_or_High_Stress_{horizon_name}':
            int(
                _is_moderate_or_high_stress(
                    future_row
                )
            ),

        f'Target_Low_Sleep_{horizon_name}':
            int(
                _is_low_sleep(
                    future_row
                )
            ),

        f'Target_Very_Low_Sleep_{horizon_name}':
            int(
                _is_very_low_sleep(
                    future_row
                )
            ),

        f'Target_High_Social_Activity_{horizon_name}':
            int(
                _is_high_social_activity(
                    future_row
                )
            ),

        f'Target_Moderate_or_High_Social_Activity_{horizon_name}':
            int(
                _is_moderate_or_high_social_activity(
                    future_row
                )
            ),

        f'Target_Working_Day_{horizon_name}':
            int(
                _is_working_day(
                    future_row
                )
            ),

        f'Target_Difficult_Behavioral_Day_{horizon_name}':
            int(
                _is_difficult_behavioral_day(
                    future_row
                )
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

    A period target becomes 1 when the corresponding
    condition occurs on at least one future day.
    """

    if not future_rows:
        return _empty_targets(
            horizon_name
        )

    return {
        f'Target_High_Stress_{horizon_name}':
            int(
                any(
                    _is_high_stress(row)
                    for row in future_rows
                )
            ),

        f'Target_Moderate_or_High_Stress_{horizon_name}':
            int(
                any(
                    _is_moderate_or_high_stress(row)
                    for row in future_rows
                )
            ),

        f'Target_Low_Sleep_{horizon_name}':
            int(
                any(
                    _is_low_sleep(row)
                    for row in future_rows
                )
            ),

        f'Target_Very_Low_Sleep_{horizon_name}':
            int(
                any(
                    _is_very_low_sleep(row)
                    for row in future_rows
                )
            ),

        f'Target_High_Social_Activity_{horizon_name}':
            int(
                any(
                    _is_high_social_activity(row)
                    for row in future_rows
                )
            ),

        f'Target_Moderate_or_High_Social_Activity_{horizon_name}':
            int(
                any(
                    _is_moderate_or_high_social_activity(row)
                    for row in future_rows
                )
            ),

        f'Target_Working_Day_{horizon_name}':
            int(
                any(
                    _is_working_day(row)
                    for row in future_rows
                )
            ),

        f'Target_Difficult_Behavioral_Day_{horizon_name}':
            int(
                any(
                    _is_difficult_behavioral_day(row)
                    for row in future_rows
                )
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

    Daily horizons represent one exact future day.

    Period horizons summarize a complete future period.
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

        return create_behavioral_targets_daily(
            future_row,
            horizon_name,
        )

    # =====================================================
    # PERIOD HORIZONS
    # =====================================================

    if horizon_name in PERIOD_HORIZONS:

        return create_behavioral_targets_period(
            future_rows,
            horizon_name,
        )

    # =====================================================
    # INVALID HORIZON
    # =====================================================

    raise ValueError(
        f'Unsupported behavioral horizon: '
        f'{horizon_name}'
    )
