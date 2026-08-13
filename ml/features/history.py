def create_history_features(row, previous_rows=None):
    """
    Create historical features from previous daily records.

    The current row is not included in the historical calculations.
    """

    if not previous_rows:
        return {
            'Previous_Day_Expense': 0.0,
            'Previous_Day_Income': 0.0,
            'Previous_Day_Balance': 0.0,
            'Previous_Day_Events': 0,
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
        'Previous_Day_Expense': expense,

        'Previous_Day_Income': income,

        'Previous_Day_Balance':
            income - expense,

        'Previous_Day_Events': events,
    }