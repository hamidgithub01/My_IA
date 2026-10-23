from math import isfinite

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

    A high expense is at least 50% above the historical
    average daily expense.

    Return NaN when a valid historical baseline
    is unavailable.
    """

    if expense_total is None:
        return float('nan')

    if historical_average_expense is None:
        return float('nan')

    try:
        expense_total = float(expense_total)
        historical_average_expense = float(
            historical_average_expense
        )
    except (TypeError, ValueError):
        return float('nan')

    if (
        not isfinite(expense_total)
        or not isfinite(historical_average_expense)
    ):
        return float('nan')

    if historical_average_expense <= 0:
        return float('nan')

    if expense_total < 0:
        return float('nan')

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

    Only valid historical Expense_Total values are used.
    Explicit zero values remain valid observations.
    """

    if not previous_rows:
        return None

    historical_expenses = []

    for row in previous_rows:
        value = row.get('Expense_Total')

        if value is None:
            continue

        try:
            expense = float(value)
        except (TypeError, ValueError):
            continue

        if not isfinite(expense):
            continue

        if expense < 0:
            continue

        historical_expenses.append(expense)

    if not historical_expenses:
        return None

    return sum(historical_expenses) / len(historical_expenses)


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
    High expense is NaN when no valid historical baseline
    is available.
    """

    previous_rows = previous_rows or []

    if not future_rows:
        return _empty_targets(horizon_name)

    expense_total = 0.0
    income_total = 0.0

    expense_days = 0
    income_days = 0

    for row in future_rows:
        daily_expense = to_float(
            row.get('Expense_Total')
        )

        daily_income = to_float(
            row.get('Income_Total')
        )

        expense_total += daily_expense
        income_total += daily_income

        if daily_expense > 0:
            expense_days += 1

        if daily_income > 0:
            income_days += 1

    balance = income_total - expense_total

    historical_average_expense = (
        _get_historical_average_expense(
            previous_rows
        )
    )

    high_expense_values = [
        _calculate_high_expense(
            to_float(row.get('Expense_Total')),
            historical_average_expense,
        )
        for row in future_rows
    ]

    # If the historical baseline is unavailable, the
    # period's high-expense classification is unknown.
    if (
        historical_average_expense is None
        or not isfinite(historical_average_expense)
        or historical_average_expense <= 0
    ):
        high_expense = float('nan')
    else:
        high_expense = int(
            any(value == 1 for value in high_expense_values)
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
