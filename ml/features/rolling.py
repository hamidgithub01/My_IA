def create_rolling_features(row, previous_rows=None):
    """
    Create rolling historical features.

    The current row is never included.

    Windows:
        3 days
        7 days
        14 days
        30 days
    """

    previous_rows = previous_rows or []

    def recent_rows(window):
        return previous_rows[-window:]

    def average(rows, field):
        if not rows:
            return 0.0

        values = [
            float(
                item.get(field) or 0.0
            )
            for item in rows
        ]

        return sum(values) / len(values)

    def average_balance(rows):
        if not rows:
            return 0.0

        values = [
            float(
                item.get('Income_Total')
                or 0.0
            )
            -
            float(
                item.get('Expense_Total')
                or 0.0
            )
            for item in rows
        ]

        return sum(values) / len(values)

    def average_events(rows):
        if not rows:
            return 0.0

        values = [
            float(
                item.get('Event_Count')
                or 0
            )
            for item in rows
        ]

        return sum(values) / len(values)

    rows_3 = recent_rows(3)
    rows_7 = recent_rows(7)
    rows_14 = recent_rows(14)
    rows_30 = recent_rows(30)

    return {
        'Rolling_3D_Avg_Expense':
            average(
                rows_3,
                'Expense_Total',
            ),

        'Rolling_7D_Avg_Expense':
            average(
                rows_7,
                'Expense_Total',
            ),

        'Rolling_14D_Avg_Expense':
            average(
                rows_14,
                'Expense_Total',
            ),

        'Rolling_30D_Avg_Expense':
            average(
                rows_30,
                'Expense_Total',
            ),

        'Rolling_3D_Avg_Income':
            average(
                rows_3,
                'Income_Total',
            ),

        'Rolling_7D_Avg_Income':
            average(
                rows_7,
                'Income_Total',
            ),

        'Rolling_14D_Avg_Income':
            average(
                rows_14,
                'Income_Total',
            ),

        'Rolling_30D_Avg_Income':
            average(
                rows_30,
                'Income_Total',
            ),

        'Rolling_3D_Avg_Balance':
            average_balance(rows_3),

        'Rolling_7D_Avg_Balance':
            average_balance(rows_7),

        'Rolling_14D_Avg_Balance':
            average_balance(rows_14),

        'Rolling_30D_Avg_Balance':
            average_balance(rows_30),

        'Rolling_3D_Avg_Events':
            average_events(rows_3),

        'Rolling_7D_Avg_Events':
            average_events(rows_7),

        'Rolling_14D_Avg_Events':
            average_events(rows_14),

        'Rolling_30D_Avg_Events':
            average_events(rows_30),
    }