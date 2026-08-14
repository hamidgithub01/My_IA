
from ml.targets.common import (
    DAILY_HORIZONS,
    PERIOD_HORIZONS,
    to_float,
)


# =========================================================
# HIGH EXPENSE
# =========================================================

def _calculate_high_expense(
    expense_total,
    historical_average_expense,
):
    """
    Determine whether an expense is unusually high.

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
# HISTORICAL EXPENSE BASELINE
# =========================================================

def _get_historical_average_expense(
    previous_rows,
):
    """
    Calculate the historical average daily expense.

    Only previous rows supplied to the function are used.
    """

    if not previous_rows:
        return 0.0

    historical_expenses = [

        to_float(
            row.get('Expense_Total')
        )

        for row in previous_rows
    ]

    return (
        sum(historical_expenses)
        / len(historical_expenses)
    )


# =========================================================
# EMPTY FINANCIAL TARGETS
# =========================================================

def _empty_targets(
    horizon_name,
):
    """
    Return empty financial targets for a future horizon.
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

    Each future day receives independent financial targets.
    """

    previous_rows = previous_rows or []

    if not future_row:
        return _empty_targets(
            horizon_name
        )

    expense_total = to_float(
        future_row.get(
            'Expense_Total'
        )
    )

    income_total = to_float(
        future_row.get(
            'Income_Total'
        )
    )

    balance = (
        income_total
        - expense_total
    )

    historical_average_expense = (
        _get_historical_average_expense(
            previous_rows
        )
    )

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

    Period targets summarize the supplied future rows.
    """

    previous_rows = previous_rows or []

    if not future_rows:
        return _empty_targets(
            horizon_name
        )

    expense_total = 0.0
    income_total = 0.0

    expense_days = 0
    income_days = 0

    for row in future_rows:

        daily_expense = to_float(
            row.get(
                'Expense_Total'
            )
        )

        daily_income = to_float(
            row.get(
                'Income_Total'
            )
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

    historical_average_expense = (
        _get_historical_average_expense(
            previous_rows
        )
    )

    high_expense = int(
        any(
            _calculate_high_expense(
                to_float(
                    row.get(
                        'Expense_Total'
                    )
                ),
                historical_average_expense,
            )
            for row in future_rows
        )
    )

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

    Daily horizons represent one exact future day.

    Period horizons summarize a complete future period.
    """

    future_rows = future_rows or []
    previous_rows = previous_rows or []

    # -----------------------------------------------------
    # DAILY HORIZONS
    # -----------------------------------------------------

    if horizon_name in DAILY_HORIZONS:

        future_row = (
            future_rows[0]
            if future_rows
            else None
        )

        return create_financial_targets_daily(
            future_row,
            horizon_name,
            previous_rows,
        )

    # -----------------------------------------------------
    # PERIOD HORIZONS
    # -----------------------------------------------------

    if horizon_name in PERIOD_HORIZONS:

        return create_financial_targets_period(
            future_rows,
            horizon_name,
            previous_rows,
        )

    # -----------------------------------------------------
    # INVALID HORIZON
    # -----------------------------------------------------

    raise ValueError(
        f'Unsupported financial horizon: '
        f'{horizon_name}'
    )
