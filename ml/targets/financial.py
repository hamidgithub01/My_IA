# =========================================================
# FINANCIAL TARGETS
# =========================================================


def _to_float(value):
    """
    Safely convert a value to float.
    """

    try:
        return float(value or 0.0)

    except (
        TypeError,
        ValueError,
    ):
        return 0.0


# =========================================================
# SINGLE-DAY FINANCIAL TARGETS
# =========================================================

def create_financial_targets_1d(
    future_row,
):
    """
    Create financial targets for one future day.

    future_row represents T + 1.

    Targets describe the actual financial outcome
    of the future day.
    """

    expense_total = _to_float(
        future_row.get('Expense_Total')
    )

    income_total = _to_float(
        future_row.get('Income_Total')
    )

    balance = (
        income_total
        - expense_total
    )

    return {

        'Target_Expense_Total_1D':
            expense_total,

        'Target_Income_Total_1D':
            income_total,

        'Target_Balance_1D':
            balance,

        'Target_Expense_Days_1D':
            int(
                expense_total > 0
            ),

        'Target_Income_Days_1D':
            int(
                income_total > 0
            ),
    }


# =========================================================
# HIGH EXPENSE
# =========================================================

def _calculate_high_expense(
    expense_total,
    historical_average_expense,
):
    """
    Determine whether an expense is unusually high.

    A high expense is one that is at least 50% above
    the historical average expense.

    No historical information means that the target
    cannot be classified as unusually high.
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
# MULTI-DAY FINANCIAL TARGETS
# =========================================================

def create_financial_targets_multi_day(
    future_rows,
    horizon_name,
    previous_rows=None,
):
    """
    Create financial targets for a future period.

    future_rows contains only future dates.

    For example:

        7D:
            T + 1 ... T + 7

        30D:
            T + 1 ... T + 30

    previous_rows contains only dates before T and is
    used exclusively to establish the user's historical
    spending baseline.
    """

    previous_rows = previous_rows or []

    if not future_rows:

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

    # -----------------------------------------------------
    # Future financial totals
    # -----------------------------------------------------

    expense_total = 0.0
    income_total = 0.0

    expense_days = 0
    income_days = 0

    for row in future_rows:

        daily_expense = _to_float(
            row.get('Expense_Total')
        )

        daily_income = _to_float(
            row.get('Income_Total')
        )

        expense_total += daily_expense
        income_total += daily_income

        if daily_expense > 0:
            expense_days += 1

        if daily_income > 0:
            income_days += 1

    balance = (
        income_total
        - expense_total
    )

    # -----------------------------------------------------
    # Historical expense baseline
    # -----------------------------------------------------

    historical_expenses = [

        _to_float(
            row.get('Expense_Total')
        )

        for row in previous_rows

    ]

    if historical_expenses:

        historical_average_expense = (
            sum(historical_expenses)
            / len(historical_expenses)
        )

    else:

        historical_average_expense = 0.0

    # -----------------------------------------------------
    # High-expense days
    # -----------------------------------------------------

    high_expense = 0

    for row in future_rows:

        daily_expense = _to_float(
            row.get('Expense_Total')
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
# PUBLIC ENTRY POINT
# =========================================================

def create_financial_targets(
    future_rows,
    horizon_name='1D',
    previous_rows=None,
):
    """
    Public Financial Target Engineering entry point.

    Parameters
    ----------
    future_rows : list[dict]
        Future rows belonging to the requested horizon.

    horizon_name : str
        '1D', '7D', or '30D'.

    previous_rows : list[dict]
        Historical rows before the current prediction day.

    Returns
    -------
    dict
        Financial targets for the requested horizon.
    """

    previous_rows = previous_rows or []

    if future_rows is None:
        future_rows = []

    if horizon_name == '1D':

        if not future_rows:

            return {

                'Target_Expense_Total_1D':
                    float('nan'),

                'Target_Income_Total_1D':
                    float('nan'),

                'Target_Balance_1D':
                    float('nan'),

                'Target_Expense_Days_1D':
                    float('nan'),

                'Target_Income_Days_1D':
                    float('nan'),

                'Target_High_Expense_1D':
                    float('nan'),
            }

        return create_financial_targets_1d(
            future_rows[0]
        ) | {

            'Target_High_Expense_1D':
                _calculate_high_expense(
                    _to_float(
                        future_rows[0].get(
                            'Expense_Total'
                        )
                    ),
                    (
                        sum(
                            _to_float(
                                row.get(
                                    'Expense_Total'
                                )
                            )
                            for row in previous_rows
                        )
                        / len(previous_rows)
                    )
                    if previous_rows
                    else 0.0,
                ),
        }

    if horizon_name in {
        '7D',
        '30D',
    }:

        return create_financial_targets_multi_day(
            future_rows,
            horizon_name,
            previous_rows,
        )

    raise ValueError(
        f'Unsupported financial horizon: '
        f'{horizon_name}'
    )