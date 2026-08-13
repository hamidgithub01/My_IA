def create_rolling_features(row, previous_rows=None):
    """
    Create rolling features from previous daily records.

    The current row is excluded from all rolling calculations.
    """

    if not previous_rows:
        return {
            'Rolling_3D_Avg_Expense': 0.0,
            'Rolling_3D_Avg_Income': 0.0,
            'Rolling_3D_Avg_Balance': 0.0,
            'Rolling_3D_Avg_Events': 0.0,
        }

    recent_rows = previous_rows[-3:]

    expenses = [
        float(r.get('Expense_Total') or 0.0)
        for r in recent_rows
    ]

    incomes = [
        float(r.get('Income_Total') or 0.0)
        for r in recent_rows
    ]

    balances = [
        float(r.get('Income_Total') or 0.0)
        - float(r.get('Expense_Total') or 0.0)
        for r in recent_rows
    ]

    events = [
        int(r.get('Event_Count') or 0)
        for r in recent_rows
    ]

    return {
        'Rolling_3D_Avg_Expense':
            sum(expenses) / len(expenses),

        'Rolling_3D_Avg_Income':
            sum(incomes) / len(incomes),

        'Rolling_3D_Avg_Balance':
            sum(balances) / len(balances),

        'Rolling_3D_Avg_Events':
            sum(events) / len(events),
    }