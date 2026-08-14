# =========================================================
# PATTERN TARGETS
# =========================================================


def _get_expense_total(row):
    return float(
        row.get('Expense_Total')
        or 0.0
    )


def _get_income_total(row):
    return float(
        row.get('Income_Total')
        or 0.0
    )


def _get_event_count(row):
    return int(
        row.get('Event_Count')
        or 0
    )


def _get_activity_count(row):
    return int(
        row.get('Activity_Count')
        or 0
    )


def _get_activity_duration(row):
    return float(
        row.get(
            'Activity_Duration_Minutes'
        )
        or 0.0
    )


def _get_stress_level(row):
    return float(
        row.get('Stress_Level')
        or 0.0
    )


def _get_sleep_hours(row):
    return float(
        row.get('Sleep_Hours')
        or 0.0
    )


def _get_health_records(row):
    return int(
        row.get('Health_Record_Count')
        or 0
    )


def _get_travel(row):
    return str(
        row.get('Travel')
        or ''
    ).strip().lower()


def _has_special_event(row):
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
    """

    return (
        _has_special_event(row)
        or _is_travel_day(row)
        or _get_event_count(row) >= 2
    )


# =========================================================
# SINGLE-DAY PATTERN TARGETS
# =========================================================

def create_pattern_targets_1d(
    future_row,
):
    """
    Create pattern targets for the next day.

    future_row represents T + 1.
    """

    return {

        'Target_Busy_Day_1D':
            int(
                _is_busy_day(
                    future_row
                )
            ),

        'Target_Financial_Activity_1D':
            int(
                _has_financial_activity(
                    future_row
                )
            ),

        'Target_Difficult_Day_1D':
            int(
                _is_difficult_day(
                    future_row
                )
            ),

        'Target_Active_Day_1D':
            int(
                _is_active_day(
                    future_row
                )
            ),

        'Target_Travel_Day_1D':
            int(
                _is_travel_day(
                    future_row
                )
            ),

        'Target_Special_Day_1D':
            int(
                _is_special_day(
                    future_row
                )
            ),
    }


# =========================================================
# MULTI-DAY PATTERN TARGETS
# =========================================================

def create_pattern_targets_multi_day(
    future_rows,
    horizon_name,
):
    """
    Create pattern targets for a future period.

    A target is 1 when the corresponding pattern
    occurs on at least one future day.
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
# PUBLIC ENTRY POINT
# =========================================================

def create_pattern_targets(
    future_rows,
    horizon_name='1D',
):
    """
    Public Pattern Target Engineering entry point.

    Parameters
    ----------
    future_rows : list[dict]
        Future rows belonging to the requested horizon.

    horizon_name : str
        '1D', '7D', or '30D'.

    Returns
    -------
    dict
        Pattern targets for the requested horizon.
    """

    # -----------------------------------------------------
    # 1 DAY
    # -----------------------------------------------------

    if horizon_name == '1D':

        if not future_rows:

            return {

                'Target_Busy_Day_1D':
                    float('nan'),

                'Target_Financial_Activity_1D':
                    float('nan'),

                'Target_Difficult_Day_1D':
                    float('nan'),

                'Target_Active_Day_1D':
                    float('nan'),

                'Target_Travel_Day_1D':
                    float('nan'),

                'Target_Special_Day_1D':
                    float('nan'),
            }

        return create_pattern_targets_1d(
            future_rows[0]
        )

    # -----------------------------------------------------
    # 7 DAYS / 30 DAYS
    # -----------------------------------------------------

    if horizon_name in {
        '7D',
        '30D',
    }:

        return create_pattern_targets_multi_day(
            future_rows,
            horizon_name,
        )

    raise ValueError(
        f'Unsupported pattern horizon: '
        f'{horizon_name}'
    )