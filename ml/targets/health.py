# =========================================================

# HEALTH TARGETS

# =========================================================

# =========================================================

# SAFE VALUE HELPERS

# =========================================================

def _get_health_problem(row):
    """
    Safely extract the health-problem status.
    """

    value = row.get(
        'Health_Problem'
    )

    if isinstance(value, bool):
        return value

    normalized = str(
        value or ''
    ).strip().lower()

    return normalized in {
        'yes',
        'true',
        '1',
        'problem',
        'present',
    }


def _get_health_severity(row):
    """
    Safely extract health severity.

    ```
    Invalid or missing values are treated as 0.
    """

    try:

        return float(
            row.get(
                'Health_Severity'
            )
            or 0.0
        )

    except (
        TypeError,
        ValueError,
    ):

        return 0.0


def _get_energy_level(row):
    """
    Safely extract energy level.

    ```
    Invalid or missing values are treated as 0.
    """

    try:

        return float(
            row.get(
                'Energy_Level'
            )
            or 0.0
        )

    except (
        TypeError,
        ValueError,
    ):

        return 0.0


# =========================================================

# HEALTH CLASSIFICATION

# =========================================================

def _has_health_problem(row):
    """
    Determine whether a health problem exists.
    """

    
    return _get_health_problem(
        row
    )


def _is_high_health_severity(row):
    """
    Determine whether health severity is high.

    ```
    High severity:

        severity >= 7
    """

    return (
        _get_health_severity(row)
        >= 7
    )


def _is_low_energy(row):
    """
    Determine whether energy level is low.

    ```
    Energy scale:

        0 - 10

    Low energy:

        1 <= energy < 4

    Zero is treated as missing/unknown rather than
    automatically being classified as low energy.
    """

    energy_level = _get_energy_level(
        row
    )

    return (
        energy_level > 0
        and energy_level < 4
    )


def _is_significant_health_day(row):
    """
    Determine whether a day is health-significant.

    ```
    A significant health day occurs when at least one
    of the following is present:

        - health problem
        - high health severity
        - low energy
    """

    return (
        _has_health_problem(row)
        or _is_high_health_severity(row)
        or _is_low_energy(row)
    )


# =========================================================

# DAILY HEALTH TARGETS

# =========================================================

def create_health_targets_daily(
future_row,
horizon_name,
):
    """
    Create health targets for one exact future day.

    ```
    Examples:

        1D -> T + 1
        2D -> T + 2
        ...
        7D -> T + 7

    The returned targets describe only that specific
    future day.
    """

    if not future_row:

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

    return {

        f'Target_Health_Problem_{horizon_name}':
            int(
                _has_health_problem(
                    future_row
                )
            ),

        f'Target_High_Health_Severity_{horizon_name}':
            int(
                _is_high_health_severity(
                    future_row
                )
            ),

        f'Target_Low_Energy_{horizon_name}':
            int(
                _is_low_energy(
                    future_row
                )
            ),

        f'Target_Significant_Health_Day_{horizon_name}':
            int(
                _is_significant_health_day(
                    future_row
                )
            ),
    }


# =========================================================

# PERIOD HEALTH TARGETS

# =========================================================

def create_health_targets_period(
future_rows,
horizon_name,
):
    
    """
    Create health targets for a future period.

    ```
    A period target becomes 1 when the corresponding
    condition occurs on at least one day in the period.

    These targets are summaries.

    They do NOT replace the individual daily targets.

    Examples:

        8_15D
            summarizes T + 8 ... T + 15

        16_30D
            summarizes T + 16 ... T + 30

        30D
            summarizes T + 1 ... T + 30
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

        if _has_health_problem(row):

            health_problem = True

        if _is_high_health_severity(row):

            high_health_severity = True

        if _is_low_energy(row):

            low_energy = True

        if _is_significant_health_day(row):

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

# PUBLIC HEALTH TARGETS

# =========================================================

def create_health_targets(
    future_rows,
    horizon_name='1D',
    ):
    """
    Public Health Target Engineering entry point.

    ```
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

    Period horizons represent aggregated information
    about a future period.
    """

    if future_rows is None:

        future_rows = []

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

        future_row = (
            future_rows[0]
            if future_rows
            else None
        )

        return create_health_targets_daily(
            future_row,
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

        return create_health_targets_period(
            future_rows,
            horizon_name,
        )

    # =====================================================
    # INVALID HORIZON
    # =====================================================

    raise ValueError(
        f'Unsupported health horizon: '
        f'{horizon_name}'
    )
