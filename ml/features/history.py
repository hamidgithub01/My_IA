from datetime import date, datetime


def _to_date(value):
    """
    Convert a supported value to date.
    """

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    if isinstance(value, str):

        try:
            return date.fromisoformat(
                value[:10]
            )

        except ValueError:
            return None

    return None


def create_history_features(
    row,
    previous_rows=None,
):
    """
    Create historical pattern features.

    The current row is NEVER included.

    Historical context includes:

        - previous day
        - same weekday
        - recent historical averages
    """

    previous_rows = previous_rows or []

    target_date = _to_date(
        row.get('Date')
    )

    if target_date is None:
        return {
            'Previous_Day_Expense': 0.0,
            'Previous_Day_Income': 0.0,
            'Previous_Day_Balance': 0.0,
            'Previous_Day_Events': 0,
            'Same_Weekday_Avg_Expense': 0.0,
            'Same_Weekday_Avg_Income': 0.0,
            'Same_Weekday_Avg_Balance': 0.0,
            'Same_Weekday_Avg_Events': 0.0,
            'Same_Weekday_Count': 0,
        }

    # ------------------------------------------------------
    # Previous day
    # ------------------------------------------------------

    if previous_rows:

        previous = previous_rows[-1]

        previous_expense = float(
            previous.get(
                'Expense_Total'
            ) or 0.0
        )

        previous_income = float(
            previous.get(
                'Income_Total'
            ) or 0.0
        )

        previous_events = int(
            previous.get(
                'Event_Count'
            ) or 0
        )

        previous_balance = (
            previous_income
            - previous_expense
        )

    else:

        previous_expense = 0.0
        previous_income = 0.0
        previous_events = 0
        previous_balance = 0.0

    # ------------------------------------------------------
    # Same weekday history
    # ------------------------------------------------------

    same_weekday = []

    for historical_row in previous_rows:

        historical_date = _to_date(
            historical_row.get('Date')
        )

        if historical_date is None:
            continue

        if (
            historical_date.weekday()
            == target_date.weekday()
        ):
            same_weekday.append(
                historical_row
            )

    if same_weekday:

        expenses = [
            float(
                item.get(
                    'Expense_Total'
                ) or 0.0
            )
            for item in same_weekday
        ]

        incomes = [
            float(
                item.get(
                    'Income_Total'
                ) or 0.0
            )
            for item in same_weekday
        ]

        balances = [
            float(
                item.get(
                    'Income_Total'
                ) or 0.0
            )
            -
            float(
                item.get(
                    'Expense_Total'
                ) or 0.0
            )
            for item in same_weekday
        ]

        events = [
            float(
                item.get(
                    'Event_Count'
                ) or 0
            )
            for item in same_weekday
        ]

        same_weekday_avg_expense = (
            sum(expenses)
            / len(expenses)
        )

        same_weekday_avg_income = (
            sum(incomes)
            / len(incomes)
        )

        same_weekday_avg_balance = (
            sum(balances)
            / len(balances)
        )

        same_weekday_avg_events = (
            sum(events)
            / len(events)
        )

    else:

        same_weekday_avg_expense = 0.0
        same_weekday_avg_income = 0.0
        same_weekday_avg_balance = 0.0
        same_weekday_avg_events = 0.0

    return {
        'Previous_Day_Expense':
            previous_expense,

        'Previous_Day_Income':
            previous_income,

        'Previous_Day_Balance':
            previous_balance,

        'Previous_Day_Events':
            previous_events,

        'Same_Weekday_Avg_Expense':
            same_weekday_avg_expense,

        'Same_Weekday_Avg_Income':
            same_weekday_avg_income,

        'Same_Weekday_Avg_Balance':
            same_weekday_avg_balance,

        'Same_Weekday_Avg_Events':
            same_weekday_avg_events,

        'Same_Weekday_Count':
            len(same_weekday),
    }