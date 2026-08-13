def create_lag_features(row, previous_rows=None):
    """
    Create lag features from previous daily records.

    The current row is excluded from all lag calculations.
    """

    if not previous_rows:
        return {
            'Lag_1_Expense': 0.0,
            'Lag_1_Income': 0.0,
            'Lag_1_Balance': 0.0,
            'Lag_1_Events': 0,
        }

    previous = previous_rows[-1]

    expense = float(
        previous.get('Expense_Total') or 0.0
    )

    income = float(
        previous.get('Income_Total') or 0.0
    )

    events = int(
        previous.get('Event_Count') or 0
    )

    return {
        'Lag_1_Expense': expense,

        'Lag_1_Income': income,

        'Lag_1_Balance':
            income - expense,

        'Lag_1_Events': events,
    }