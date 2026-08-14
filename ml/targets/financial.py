# =========================================================

# FINANCIAL TARGETS

# =========================================================

# =========================================================

# SAFE VALUE HELPERS

# =========================================================

def _to_float(value):
    """
    Safely convert a value to float.

    ```
    Invalid or missing values are treated as 0.0.
    """

    try:

        return float(
            value or 0.0
        )

    except (
        TypeError,
        ValueError,
    ):

        return 0.0
    

    # =========================================================

    # HIGH EXPENSE

    # =========================================================

def _calculate_high_expense(
    expense_total,
    historical_average_expense,
    ):
    """
    Determine whether an expense is unusually high.

    ```
    A high expense is defined as an expense that is
    at least 50% above the historical average daily
    expense.

    If no historical baseline is available, the result
    is 0.
    """

    if (
        expense_total <= 0
        or historical_average_expense <= 0
    ):

        return 0

    return int(
        expense_total
        >= historical_average_expense * 1.5
    )
    

    # =========================================================

    # EMPTY DAILY TARGETS

    # =========================================================

def _empty_daily_targets(
    horizon_name,
    ):
    """
    Return empty targets for one exact future day.
    """

    return {

        f'Target_Expense_Total_{horizon_name}':
            float('nan'),

        f'Target_Income_Total_{horizon_name}':
            float('nan'),

        f'Target_Balance_{horizon_name}':
            float('nan'),

        f'Target_Expense_Days_{horizon_name}':
            float('nan'),

        f'Target_Income_Days_{horizon_name}':
            float('nan'),

        f'Target_High_Expense_{horizon_name}':
            float('nan'),
    }
    

    # =========================================================

    # EMPTY PERIOD TARGETS

    # =========================================================

def _empty_period_targets(
    horizon_name,
    ):
    """
    Return empty targets for a future period.
    """

    return {

        f'Target_Expense_Total_{horizon_name}':
            float('nan'),

        f'Target_Income_Total_{horizon_name}':
            float('nan'),

        f'Target_Balance_{horizon_name}':
            float('nan'),

        f'Target_Expense_Days_{horizon_name}':
            float('nan'),

        f'Target_Income_Days_{horizon_name}':
            float('nan'),

        f'Target_High_Expense_{horizon_name}':
            float('nan'),
    }


    # =========================================================

    # DAILY FINANCIAL TARGETS

    # =========================================================

def create_financial_targets_daily(
    future_row,
    horizon_name,
    previous_rows=None,
    ):
    """
    Create financial targets for one exact future day.

    ```
    Examples:

        1D -> T + 1
        2D -> T + 2
        ...
        7D -> T + 7

    The target describes the actual financial outcome
    of that exact future day.
    """

    previous_rows = previous_rows or []

    if not future_row:

        return _empty_daily_targets(
            horizon_name
        )

    expense_total = _to_float(
        future_row.get(
            'Expense_Total'
        )
    )

    income_total = _to_float(
        future_row.get(
            'Income_Total'
        )
    )

    balance = (
        income_total
        - expense_total
    )

    # -----------------------------------------------------
    # Historical baseline
    # -----------------------------------------------------

    historical_expenses = [

        _to_float(
            row.get(
                'Expense_Total'
            )
        )

        for row in previous_rows
    ]

    if historical_expenses:

        historical_average_expense = (
            sum(
                historical_expenses
            )
            / len(
                historical_expenses
            )
        )

    else:

        historical_average_expense = 0.0

    return {

        f'Target_Expense_Total_{horizon_name}':
            expense_total,

        f'Target_Income_Total_{horizon_name}':
            income_total,

        f'Target_Balance_{horizon_name}':
            balance,

        f'Target_Expense_Days_{horizon_name}':
            int(
                expense_total > 0
            ),

        f'Target_Income_Days_{horizon_name}':
            int(
                income_total > 0
            ),

        f'Target_High_Expense_{horizon_name}':
            _calculate_high_expense(
                expense_total,
                historical_average_expense,
            ),
    }


    # =========================================================

    # PERIOD FINANCIAL TARGETS

    # =========================================================

def create_financial_targets_period(
    future_rows,
    horizon_name,
    previous_rows=None,
    ):
    """
    Create financial targets for a future period.

    ```
    Period targets summarize the supplied future rows.

    Examples:

        8_15D
            T + 8 ... T + 15

        16_30D
            T + 16 ... T + 30

        30D
            T + 1 ... T + 30

    These targets provide a period-level financial
    summary while the daily targets preserve exact
    day-by-day information.
    """

    previous_rows = previous_rows or []

    if not future_rows:

        return _empty_period_targets(
            horizon_name
        )

    # -----------------------------------------------------
    # Future financial totals
    # -----------------------------------------------------

    expense_total = 0.0
    income_total = 0.0

    expense_days = 0
    income_days = 0

    for row in future_rows:

        daily_expense = _to_float(
            row.get(
                'Expense_Total'
            )
        )

        daily_income = _to_float(
            row.get(
                'Income_Total'
            )
        )

        expense_total += (
            daily_expense
        )

        income_total += (
            daily_income
        )

        if daily_expense > 0:

            expense_days += 1

        if daily_income > 0:

            income_days += 1

    # -----------------------------------------------------
    # Period balance
    # -----------------------------------------------------

    balance = (
        income_total
        - expense_total
    )

    # -----------------------------------------------------
    # Historical expense baseline
    # -----------------------------------------------------

    historical_expenses = [

        _to_float(
            row.get(
                'Expense_Total'
            )
        )

        for row in previous_rows
    ]

    if historical_expenses:

        historical_average_expense = (
            sum(
                historical_expenses
            )
            / len(
                historical_expenses
            )
        )

    else:

        historical_average_expense = 0.0

    # -----------------------------------------------------
    # High-expense future day
    # -----------------------------------------------------

    high_expense = 0

    for row in future_rows:

        daily_expense = _to_float(
            row.get(
                'Expense_Total'
            )
        )

        if _calculate_high_expense(
            daily_expense,
            historical_average_expense,
        ):

            high_expense = 1

            break

    return {

        f'Target_Expense_Total_{horizon_name}':
            expense_total,

        f'Target_Income_Total_{horizon_name}':
            income_total,

        f'Target_Balance_{horizon_name}':
            balance,

        f'Target_Expense_Days_{horizon_name}':
            expense_days,

        f'Target_Income_Days_{horizon_name}':
            income_days,

        f'Target_High_Expense_{horizon_name}':
            high_expense,
    }


    # =========================================================

    # PUBLIC FINANCIAL TARGETS

    # =========================================================

def create_financial_targets(
    future_rows,
    horizon_name='1D',
    previous_rows=None,
    ):
    """
    Public Financial Target Engineering entry point.

    ```
    Supported exact-day horizons:

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

    Exact-day targets describe one specific future day.

    Period targets summarize all future days supplied
    to the function.
    """

    previous_rows = (
        previous_rows or []
    )

    if future_rows is None:

        future_rows = []

    # =====================================================
    # EXACT DAILY HORIZONS
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

            return _empty_daily_targets(
                horizon_name
            )

        return create_financial_targets_daily(
            future_rows[0],
            horizon_name,
            previous_rows,
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

        return create_financial_targets_period(
            future_rows,
            horizon_name,
            previous_rows,
        )

    # =====================================================
    # INVALID HORIZON
    # =====================================================

    raise ValueError(
        f'Unsupported financial horizon: '
        f'{horizon_name}'
    )
