
from ml.targets.common import (
    DAILY_HORIZONS,
    PERIOD_HORIZONS,
    to_float,
    to_int,
    normalize_text,
)


# =========================================================
# PATTERN TARGETS
# =========================================================


# =========================================================
# SAFE VALUE HELPERS
# =========================================================

def _get_expense_total(row):
    """
    Safely extract expense total.
    """

    return to_float(
        row.get('Expense_Total')
    )


def _get_income_total(row):
    """
    Safely extract income total.
    """

    return to_float(
        row.get('Income_Total')
    )


def _get_event_count(row):
    """
    Safely extract event count.
    """

    return to_int(
        row.get('Event_Count')
    )


def _get_activity_count(row):
    """
    Safely extract activity count.
    """

    return to_int(
        row.get('Activity_Count')
    )


def _get_activity_duration(row):
    """
    Safely extract activity duration.
    """

    return to_float(
        row.get('Activity_Duration_Minutes')
    )


def _get_stress_level(row):
    """
    Safely extract stress level.
    """

    return to_float(
        row.get('Stress_Level')
    )


def _get_sleep_hours(row):
    """
    Safely extract sleep hours.
    """

    return to_float(
        row.get('Sleep_Hours')
    )


def _get_health_records(row):
    """
    Safely extract health record count.
    """

    return to_int(
        row.get('Health_Record_Count')
    )


def _get_travel(row):
    """
    Safely extract and normalize travel status.
    """

    return normalize_text(
        row.get('Travel')
    )


def _has_special_event(row):
    """
    Determine whether a special event exists.
    """

    return bool(
        normalize_text(
            row.get('Special_Event')
        )
    )


# =========================================================
# PATTERN CLASSIFICATION
# =========================================================

def _is_busy_day(row):
    """
    Determine whether one day was particularly busy.

    A day is considered busy when at least one of the
    following conditions is satisfied:

        - 2 or more events
        - 2 or more activities
        - 120 or more minutes of activity
    """

    return (
        _get_event_count(row) >= 2
        or _get_activity_count(row) >= 2
        or _get_activity_duration(row) >= 120
    )


def _has_financial_activity(row):
    """
    Determine whether financial activity occurred.
    """

    return (
        _get_expense_total(row) > 0
        or _get_income_total(row) > 0
    )


def _is_difficult_day(row):
    """
    Determine whether the day contained notable
    behavioral or health difficulty.

    A difficult day occurs when at least one of the
    following conditions is satisfied:

        - stress >= 7
        - sleep < 6 hours
        - at least one health record
    """

    stress_level = _get_stress_level(row)
    sleep_hours = _get_sleep_hours(row)
    health_records = _get_health_records(row)

    return (
        stress_level >= 7
        or (
            sleep_hours > 0
            and sleep_hours < 6
        )
        or health_records > 0
    )


def _is_active_day(row):
    """
    Determine whether meaningful physical activity
    occurred.
    """

    return (
        _get_activity_count(row) > 0
        or _get_activity_duration(row) >= 60
    )


def _is_travel_day(row):
    """
    Determine whether the day involved travel.
    """

    return _get_travel(row) in {
        'yes',
        'true',
        '1',
    }


def _is_special_day(row):
    """
    Determine whether the day had notable special
    characteristics.

    A special day occurs when at least one of the
    following conditions is satisfied:

        - special event exists
        - travel occurs
        - 2 or more events occur
    """

    return (
        _has_special_event(row)
        or _is_travel_day(row)
        or _get_event_count(row) >= 2
    )


# =========================================================
# EMPTY TARGETS
# =========================================================

def _empty_targets(horizon_name):
    """
    Return empty pattern targets for a future horizon.
    """

    return {
        f'Target_Busy_Day_{horizon_name}':
            float('nan'),

        f'Target_Financial_Activity_{horizon_name}':
            float('nan'),

        f'Target_Difficult_Day_{horizon_name}':
            float('nan'),

        f'Target_Active_Day_{horizon_name}':
            float('nan'),

        f'Target_Travel_Day_{horizon_name}':
            float('nan'),

        f'Target_Special_Day_{horizon_name}':
            float('nan'),
    }


# =========================================================
# DAILY PATTERN TARGETS
# =========================================================

def create_pattern_targets_daily(
    future_row,
    horizon_name,
):
    """
    Create pattern targets for one exact future day.

    Each future day receives independent targets.
    """

    if not future_row:

        return _empty_targets(
            horizon_name
        )

    return {
        f'Target_Busy_Day_{horizon_name}':
            int(
                _is_busy_day(
                    future_row
                )
            ),

        f'Target_Financial_Activity_{horizon_name}':
            int(
                _has_financial_activity(
                    future_row
                )
            ),

        f'Target_Difficult_Day_{horizon_name}':
            int(
                _is_difficult_day(
                    future_row
                )
            ),

        f'Target_Active_Day_{horizon_name}':
            int(
                _is_active_day(
                    future_row
                )
            ),

        f'Target_Travel_Day_{horizon_name}':
            int(
                _is_travel_day(
                    future_row
                )
            ),

        f'Target_Special_Day_{horizon_name}':
            int(
                _is_special_day(
                    future_row
                )
            ),
    }


# =========================================================
# PERIOD PATTERN TARGETS
# =========================================================

def create_pattern_targets_period(
    future_rows,
    horizon_name,
):
    """
    Create pattern targets for a future period.

    A period target becomes 1 when the corresponding
    pattern occurs on at least one day within the period.
    """

    if not future_rows:

        return _empty_targets(
            horizon_name
        )

    return {
        f'Target_Busy_Day_{horizon_name}':
            int(
                any(
                    _is_busy_day(row)
                    for row in future_rows
                )
            ),

        f'Target_Financial_Activity_{horizon_name}':
            int(
                any(
                    _has_financial_activity(row)
                    for row in future_rows
                )
            ),

        f'Target_Difficult_Day_{horizon_name}':
            int(
                any(
                    _is_difficult_day(row)
                    for row in future_rows
                )
            ),

        f'Target_Active_Day_{horizon_name}':
            int(
                any(
                    _is_active_day(row)
                    for row in future_rows
                )
            ),

        f'Target_Travel_Day_{horizon_name}':
            int(
                any(
                    _is_travel_day(row)
                    for row in future_rows
                )
            ),

        f'Target_Special_Day_{horizon_name}':
            int(
                any(
                    _is_special_day(row)
                    for row in future_rows
                )
            ),
    }


# =========================================================
# PUBLIC PATTERN TARGETS
# =========================================================

def create_pattern_targets(
    future_rows,
    horizon_name='1D',
):
    """
    Public Pattern Target Engineering entry point.

    Daily horizons represent one exact future day.

    Period horizons summarize a future period.
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

        return create_pattern_targets_daily(
            future_row,
            horizon_name,
        )

    # =====================================================
    # PERIOD HORIZONS
    # =====================================================

    if horizon_name in PERIOD_HORIZONS:

        return create_pattern_targets_period(
            future_rows,
            horizon_name,
        )

    # =====================================================
    # INVALID HORIZON
    # =====================================================

    raise ValueError(
        f'Unsupported pattern horizon: '
        f'{horizon_name}'
    )
