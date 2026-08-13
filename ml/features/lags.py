def create_lag_features(row, previous_rows=None):
    """
    Create lag features from previous daily records.

    The current row is never included.

    Lags:
        1 day
        2 days
        3 days
        7 days
        14 days
        28 days
    """

    previous_rows = previous_rows or []

    def get_expense(index):
        if len(previous_rows) < index:
            return 0.0

        return float(
            previous_rows[-index].get(
                'Expense_Total'
            ) or 0.0
        )

    def get_income(index):
        if len(previous_rows) < index:
            return 0.0

        return float(
            previous_rows[-index].get(
                'Income_Total'
            ) or 0.0
        )

    def get_events(index):
        if len(previous_rows) < index:
            return 0

        return int(
            previous_rows[-index].get(
                'Event_Count'
            ) or 0
        )

    return {
        'Lag_1_Expense': get_expense(1),
        'Lag_2_Expense': get_expense(2),
        'Lag_3_Expense': get_expense(3),
        'Lag_7_Expense': get_expense(7),
        'Lag_14_Expense': get_expense(14),
        'Lag_28_Expense': get_expense(28),

        'Lag_1_Income': get_income(1),
        'Lag_2_Income': get_income(2),
        'Lag_7_Income': get_income(7),
        'Lag_14_Income': get_income(14),
        'Lag_28_Income': get_income(28),

        'Lag_1_Events': get_events(1),
        'Lag_2_Events': get_events(2),
        'Lag_7_Events': get_events(7),
        'Lag_14_Events': get_events(14),
        'Lag_28_Events': get_events(28),
    }