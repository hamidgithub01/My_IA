# =========================================================
# HEALTH TARGETS
# =========================================================


def _get_health_impact(row):
    """
    Safely extract health impact.
    """

    return str(
        row.get('Health_Impact')
        or ''
    ).strip().lower()


def _get_health_status(row):
    """
    Safely extract health status.
    """

    return str(
        row.get('Health_Status')
        or ''
    ).strip().lower()


def _get_health_severity(row):
    """
    Safely extract maximum health severity.
    """

    return float(
        row.get('Max_Health_Severity')
        or row.get('Severity')
        or 0.0
    )


def _get_energy_level(row):
    """
    Safely extract average energy level.
    """

    return float(
        row.get('Avg_Energy_Level')
        or row.get('Energy_Level')
        or 0.0
    )


# =========================================================
# HEALTH CONDITION HELPERS
# =========================================================

def _has_health_problem(
    row,
):
    """
    Determine whether a health problem exists.
    """

    health_impact = _get_health_impact(
        row
    )

    health_status = _get_health_status(
        row
    )

    severity = _get_health_severity(
        row
    )

    return (
        health_impact
        in {
            'moderate',
            'medium',
            'high',
        }
        or health_status
        in {
            'sick',
            'ill',
            'unwell',
            'problem',
            'moderate',
            'high',
        }
        or severity > 0
    )


def _is_high_health_severity(
    row,
):
    """
    Determine whether health severity is high.
    """

    severity = _get_health_severity(
        row
    )

    return severity >= 7


def _is_low_energy(
    row,
):
    """
    Determine whether energy level is low.
    """

    energy = _get_energy_level(
        row
    )

    return (
        energy > 0
        and energy <= 3
    )


def _is_significant_health_day(
    row,
):
    """
    Determine whether the day represents a
    significant health-related day.
    """

    has_problem = _has_health_problem(
        row
    )

    severity = _get_health_severity(
        row
    )

    low_energy = _is_low_energy(
        row
    )

    return (
        has_problem
        and (
            severity >= 5
            or low_energy
        )
    )


# =========================================================
# SINGLE-DAY HEALTH TARGETS
# =========================================================

def create_health_targets_1d(
    future_row,
):
    """
    Create health targets for the next day.

    future_row represents T + 1.

    The current day T is never used.
    """

    return {

        'Target_Health_Problem_1D':
            int(
                _has_health_problem(
                    future_row
                )
            ),

        'Target_High_Health_Severity_1D':
            int(
                _is_high_health_severity(
                    future_row
                )
            ),

        'Target_Low_Energy_1D':
            int(
                _is_low_energy(
                    future_row
                )
            ),

        'Target_Significant_Health_Day_1D':
            int(
                _is_significant_health_day(
                    future_row
                )
            ),
    }


# =========================================================
# MULTI-DAY HEALTH TARGETS
# =========================================================

def create_health_targets_multi_day(
    future_rows,
    horizon_name,
):
    """
    Create health targets for a future period.

    A multi-day target becomes 1 when the corresponding
    health condition occurs on at least one future day.

    Example:

        7D:

            Health problem:
            0, 0, 1, 0, 0, 0, 0

            Target_Health_Problem_7D = 1

    The current day is never included.
    """

    if not future_rows:

        return {

            f'Target_Health_Problem_{horizon_name}':
                float('nan'),

            f'Target_High_Health_Severity_{horizon_name}':
                float('nan'),

            f'Target_Low_Energy_{horizon_name}':
                float('nan'),

            f'Target_Significant_Health_Day_{horizon_name}':
                float('nan'),
        }

    health_problem = False
    high_health_severity = False
    low_energy = False
    significant_health_day = False

    for row in future_rows:

        # -------------------------------------------------
        # Health problem
        # -------------------------------------------------

        if _has_health_problem(
            row
        ):

            health_problem = True

        # -------------------------------------------------
        # High severity
        # -------------------------------------------------

        if _is_high_health_severity(
            row
        ):

            high_health_severity = True

        # -------------------------------------------------
        # Low energy
        # -------------------------------------------------

        if _is_low_energy(
            row
        ):

            low_energy = True

        # -------------------------------------------------
        # Significant health day
        # -------------------------------------------------

        if _is_significant_health_day(
            row
        ):

            significant_health_day = True

    return {

        f'Target_Health_Problem_{horizon_name}':
            int(
                health_problem
            ),

        f'Target_High_Health_Severity_{horizon_name}':
            int(
                high_health_severity
            ),

        f'Target_Low_Energy_{horizon_name}':
            int(
                low_energy
            ),

        f'Target_Significant_Health_Day_{horizon_name}':
            int(
                significant_health_day
            ),
    }


# =========================================================
# PUBLIC ENTRY POINT
# =========================================================

def create_health_targets(
    future_rows,
    horizon_name='1D',
):
    """
    Public Health Target Engineering entry point.

    Parameters
    ----------
    future_rows : list[dict]
        Future rows belonging to the requested horizon.

    horizon_name : str
        '1D', '7D', or '30D'.

    Returns
    -------
    dict
        Health targets for the requested horizon.
    """

    # -----------------------------------------------------
    # 1 DAY
    # -----------------------------------------------------

    if horizon_name == '1D':

        if not future_rows:

            return {

                'Target_Health_Problem_1D':
                    float('nan'),

                'Target_High_Health_Severity_1D':
                    float('nan'),

                'Target_Low_Energy_1D':
                    float('nan'),

                'Target_Significant_Health_Day_1D':
                    float('nan'),
            }

        return create_health_targets_1d(
            future_rows[0]
        )

    # -----------------------------------------------------
    # 7 DAYS / 30 DAYS
    # -----------------------------------------------------

    if horizon_name in {
        '7D',
        '30D',
    }:

        return create_health_targets_multi_day(
            future_rows,
            horizon_name,
        )

    raise ValueError(
        f'Unsupported health horizon: '
        f'{horizon_name}'
    )