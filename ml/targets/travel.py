# =========================================================
# TRAVEL TARGETS
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
    Determine whether one day was a travel day.
    """

    return _get_travel(row) in {
        'yes',
        'true',
        '1',
    }


# =========================================================
# SINGLE-DAY TRAVEL TARGET
# =========================================================

def create_travel_targets_1d(
    future_row,
):
    """
    Create the travel target for the next day.

    future_row represents T + 1.
    """

    return {
        'Target_Travel_Day_1D':
            int(
                _is_travel_day(
                    future_row
                )
            ),
    }


# =========================================================
# MULTI-DAY TRAVEL TARGETS
# =========================================================

def create_travel_targets_multi_day(
    future_rows,
    horizon_name,
):
    """
    Create travel targets for a future period.

    The target is 1 when at least one day in the
    future period is a travel day.
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
# PUBLIC ENTRY POINT
# =========================================================

def create_travel_targets(
    future_rows,
    horizon_name='1D',
):
    """
    Public Travel Target Engineering entry point.

    Parameters
    ----------
    future_rows : list[dict]
        Future rows belonging to the requested horizon.

    horizon_name : str
        '1D', '7D', or '30D'.

    Returns
    -------
    dict
        Travel target for the requested horizon.
    """

    # -----------------------------------------------------
    # 1 DAY
    # -----------------------------------------------------

    if horizon_name == '1D':

        if not future_rows:

            return {
                'Target_Travel_Day_1D':
                    float('nan'),
            }

        return create_travel_targets_1d(
            future_rows[0]
        )

    # -----------------------------------------------------
    # 7 DAYS / 30 DAYS
    # -----------------------------------------------------

    if horizon_name in {
        '7D',
        '30D',
    }:

        return create_travel_targets_multi_day(
            future_rows,
            horizon_name,
        )

    raise ValueError(
        f'Unsupported travel horizon: '
        f'{horizon_name}'
    )