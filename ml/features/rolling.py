from datetime import date, datetime, timedelta


def _to_date(value):
    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    if isinstance(value, str):
        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            return None

    return None


def create_rolling_features(row, previous_rows=None):
    """
    Create calendar-based rolling historical features.

    Only dates before the target date are used.

    Windows:
        3 days
        7 days
        14 days
        30 days
    """

    previous_rows = previous_rows or []

    target_date = _to_date(
        row.get('Date')
    )

    if target_date is None:
        return {}

    def rows_in_window(days):
        start_date = (
            target_date
            - timedelta(days=days)
        )

        return [
            historical_row
            for historical_row in previous_rows
            if (
                _to_date(
                    historical_row.get('Date')
                ) is not None
                and start_date
                <= _to_date(
                    historical_row.get('Date')
                )
                < target_date
            )
        ]

    def average(rows, field):
        if not rows:
            return 0.0

        values = [
            float(
                row.get(field) or 0.0
            )
            for row in rows
        ]

        return sum(values) / len(values)

    def average_balance(rows):
        if not rows:
            return 0.0

        values = [
            float(
                row.get('Income_Total') or 0.0
            )
            -
            float(
                row.get('Expense_Total') or 0.0
            )
            for row in rows
        ]

        return sum(values) / len(values)

    rows_3 = rows_in_window(3)
    rows_7 = rows_in_window(7)
    rows_14 = rows_in_window(14)
    rows_30 = rows_in_window(30)

    return {
        # Expense
        'Rolling_3D_Avg_Expense':
            average(rows_3, 'Expense_Total'),

        'Rolling_7D_Avg_Expense':
            average(rows_7, 'Expense_Total'),

        'Rolling_14D_Avg_Expense':
            average(rows_14, 'Expense_Total'),

        'Rolling_30D_Avg_Expense':
            average(rows_30, 'Expense_Total'),

        # Income
        'Rolling_3D_Avg_Income':
            average(rows_3, 'Income_Total'),

        'Rolling_7D_Avg_Income':
            average(rows_7, 'Income_Total'),

        'Rolling_14D_Avg_Income':
            average(rows_14, 'Income_Total'),

        'Rolling_30D_Avg_Income':
            average(rows_30, 'Income_Total'),

        # Balance
        'Rolling_3D_Avg_Balance':
            average_balance(rows_3),

        'Rolling_7D_Avg_Balance':
            average_balance(rows_7),

        'Rolling_14D_Avg_Balance':
            average_balance(rows_14),

        'Rolling_30D_Avg_Balance':
            average_balance(rows_30),

        # Health
        'Rolling_3D_Avg_Health_Severity':
            average(
                rows_3,
                'Max_Health_Severity'
            ),

        'Rolling_7D_Avg_Health_Severity':
            average(
                rows_7,
                'Max_Health_Severity'
            ),

        'Rolling_14D_Avg_Health_Severity':
            average(
                rows_14,
                'Max_Health_Severity'
            ),

        'Rolling_30D_Avg_Health_Severity':
            average(
                rows_30,
                'Max_Health_Severity'
            ),

        'Rolling_3D_Avg_Energy':
            average(
                rows_3,
                'Avg_Energy_Level'
            ),

        'Rolling_7D_Avg_Energy':
            average(
                rows_7,
                'Avg_Energy_Level'
            ),

        'Rolling_14D_Avg_Energy':
            average(
                rows_14,
                'Avg_Energy_Level'
            ),

        # Activity
        'Rolling_3D_Avg_Activity_Duration':
            average(
                rows_3,
                'Activity_Duration_Minutes'
            ),

        'Rolling_7D_Avg_Activity_Duration':
            average(
                rows_7,
                'Activity_Duration_Minutes'
            ),

        'Rolling_14D_Avg_Activity_Duration':
            average(
                rows_14,
                'Activity_Duration_Minutes'
            ),

        'Rolling_30D_Avg_Activity_Duration':
            average(
                rows_30,
                'Activity_Duration_Minutes'
            ),

        # Sleep
        'Rolling_3D_Avg_Sleep_Duration':
            average(
                rows_3,
                'Sleep_Duration_Minutes'
            ),

        'Rolling_7D_Avg_Sleep_Duration':
            average(
                rows_7,
                'Sleep_Duration_Minutes'
            ),

        'Rolling_14D_Avg_Sleep_Duration':
            average(
                rows_14,
                'Sleep_Duration_Minutes'
            ),

        'Rolling_30D_Avg_Sleep_Duration':
            average(
                rows_30,
                'Sleep_Duration_Minutes'
            ),

        'Rolling_3D_Avg_Sleep_Quality':
            average(
                rows_3,
                'Avg_Sleep_Quality'
            ),

        'Rolling_7D_Avg_Sleep_Quality':
            average(
                rows_7,
                'Avg_Sleep_Quality'
            ),

        'Rolling_14D_Avg_Sleep_Quality':
            average(
                rows_14,
                'Avg_Sleep_Quality'
            ),

        'Rolling_30D_Avg_Sleep_Quality':
            average(
                rows_30,
                'Avg_Sleep_Quality'
            ),
    }