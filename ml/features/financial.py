def create_financial_features(row):
    """
    Create financial features from one prepared daily row.
    """

    expense_total = float(
        row.get('Expense_Total') or 0.0
    )

    income_total = float(
        row.get('Income_Total') or 0.0
    )

    expense_count = int(
        row.get('Expense_Count') or 0
    )

    income_count = int(
        row.get('Income_Count') or 0
    )

    event_count = int(
        row.get('Event_Count') or 0
    )

    balance = income_total - expense_total

    expense_to_income_ratio = (
        expense_total / income_total
        if income_total > 0
        else 0.0
    )

    return {
        'Expense_Total': expense_total,

        'Expense_Count': expense_count,

        'Income_Total': income_total,

        'Income_Count': income_count,

        'Daily_Balance': balance,

        'Expense_to_Income_Ratio':
            expense_to_income_ratio,

        'Event_Count': event_count,
    }