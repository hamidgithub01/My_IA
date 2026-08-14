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

    try:
        return float(
            row.get('Expense_Total')
            or 0.0
        )

    except (
        TypeError,
        ValueError,
    ):
        return 0.0


def _get_income_total(row):
    """
    Safely extract income total.
    """

    try:
        return float(
            row.get('Income_Total')
            or 0.0
        )

    except (
        TypeError,
        ValueError,
    ):
        return 0.0


def _get_event_count(row):
    """
    Safely extract event count.
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


def _get_activity_count(row):
    """
    Safely extract activity count.
    """

    try:
        return int(
            row.get('Activity_Count')
            or 0
        )

    except (
        TypeError,
        ValueError,
    ):
        return 0


def _get_activity_duration(row):
    """
    Safely extract activity duration.
    """

    try:
        return float(
            row.get(
                'Activity_Duration_Minutes'
            )
            or 0.0
        )

    except (
        TypeError,
        ValueError,
    ):
        return 0.0


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
    Safely extract sleep hours.
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


def _get_health_records(row):
    """
    Safely extract health record count.
    """

    try:
        return int(
            row.get('Health_Record_Count')
            or 0
        )

    except (
        TypeError,
        ValueError,
    ):
        return 0


def _get_travel(row):
    """
    Safely extract travel status.
    """

    return str(
        row.get('Travel')
        or ''
    ).strip().lower()


def _has_special_event(row):
    """
    Determine whether a special event exists.
    """

    return bool(
        str(
            row.get('Special_Event')
            or ''
        ).strip()
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

    event_count = _get_event_count(row)

    activity_count = _get_activity_count(row)

    activity_duration = _get_activity_duration(row)

    return (
        event_count >= 2
        or activity_count >= 2
        or activity_duration >= 120
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

    activity_count = _get_activity_count(row)

    activity_duration = _get_activity_duration(row)

    return (
        activity_count > 0
        or activity_duration >= 60
    )


def _is_travel_day(row):
    """
    Determine whether the day involved travel.
    """

    travel = _get_travel(row)

    return travel in {
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
# DAILY PATTERN TARGETS
# =========================================================

def create_pattern_targets_daily(
    future_row,
    horizon_name,
):
    """
    Create pattern targets for one exact future day.

    Examples:

        1D -> T + 1
        2D -> T + 2
        3D -> T + 3
        4D -> T + 4
        5D -> T + 5
        6D -> T + 6
        7D -> T + 7
    """

    if not future_row:

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

    Supported periods:

        8_15D
            T + 8 ... T + 15

        16_30D
            T + 16 ... T + 30

        30D
            T + 1 ... T + 30

    These period targets summarize the period and do not
    replace the detailed daily targets.
    """

    if not future_rows:

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

    busy_day = False
    financial_activity = False
    difficult_day = False
    active_day = False
    travel_day = False
    special_day = False

    for row in future_rows:

        if _is_busy_day(row):
            busy_day = True

        if _has_financial_activity(row):
            financial_activity = True

        if _is_difficult_day(row):
            difficult_day = True

        if _is_active_day(row):
            active_day = True

        if _is_travel_day(row):
            travel_day = True

        if _is_special_day(row):
            special_day = True

    return {

        f'Target_Busy_Day_{horizon_name}':
            int(busy_day),

        f'Target_Financial_Activity_{horizon_name}':
            int(financial_activity),

        f'Target_Difficult_Day_{horizon_name}':
            int(difficult_day),

        f'Target_Active_Day_{horizon_name}':
            int(active_day),

        f'Target_Travel_Day_{horizon_name}':
            int(travel_day),

        f'Target_Special_Day_{horizon_name}':
            int(special_day),
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

    Daily horizons:

        1D
        2D
        3D
        4D
        5D
        6D
        7D

    Period horizons:

        8_15D
        16_30D
        30D

    Daily horizons represent one exact future day.

    Period horizons summarize a future period.
    """

    # =====================================================
    # DAILY HORIZONS
    # =====================================================

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

            return create_pattern_targets_daily(
                None,
                horizon_name,
            )

        return create_pattern_targets_daily(
            future_rows[0],
            horizon_name,
        )

    # =====================================================
    # PERIOD HORIZONS
    # =====================================================

    period_horizons = {
        '8_15D',
        '16_30D',
        '30D',
    }

    if horizon_name in period_horizons:

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