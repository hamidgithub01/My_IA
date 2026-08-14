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


def create_lag_features(row, previous_rows=None):
    """
    Create true calendar-based lag features.

    Lag_7 means the value exactly 7 calendar days before
    the target date.

    The target row is never used.
    """

    previous_rows = previous_rows or []

    target_date = _to_date(
        row.get('Date')
    )

    if target_date is None:
        return {
            'Lag_1_Expense': 0.0,
            'Lag_2_Expense': 0.0,
            'Lag_3_Expense': 0.0,
            'Lag_7_Expense': 0.0,
            'Lag_14_Expense': 0.0,
            'Lag_28_Expense': 0.0,

            'Lag_1_Income': 0.0,
            'Lag_2_Income': 0.0,
            'Lag_7_Income': 0.0,
            'Lag_14_Income': 0.0,
            'Lag_28_Income': 0.0,

            'Lag_1_Events': 0,
            'Lag_2_Events': 0,
            'Lag_7_Events': 0,
            'Lag_14_Events': 0,
            'Lag_28_Events': 0,

            'Lag_1_Health_Severity': 0.0,
            'Lag_7_Health_Severity': 0.0,
            'Lag_14_Health_Severity': 0.0,

            'Lag_1_Activity_Duration': 0.0,
            'Lag_7_Activity_Duration': 0.0,
            'Lag_14_Activity_Duration': 0.0,

            'Lag_1_Sleep_Duration': 0.0,
            'Lag_7_Sleep_Duration': 0.0,
            'Lag_14_Sleep_Duration': 0.0,
        }

    rows_by_date = {}

    for historical_row in previous_rows:

        historical_date = _to_date(
            historical_row.get('Date')
        )

        if historical_date is None:
            continue

        if historical_date >= target_date:
            continue

        rows_by_date[
            historical_date
        ] = historical_row

    def get_row(days):
        return rows_by_date.get(
            target_date - timedelta(days=days)
        )

    def value(days, field, default=0.0):
        historical_row = get_row(days)

        if historical_row is None:
            return default

        return float(
            historical_row.get(field) or default
        )

    return {
        # Financial
        'Lag_1_Expense':
            value(1, 'Expense_Total'),

        'Lag_2_Expense':
            value(2, 'Expense_Total'),

        'Lag_3_Expense':
            value(3, 'Expense_Total'),

        'Lag_7_Expense':
            value(7, 'Expense_Total'),

        'Lag_14_Expense':
            value(14, 'Expense_Total'),

        'Lag_28_Expense':
            value(28, 'Expense_Total'),

        'Lag_1_Income':
            value(1, 'Income_Total'),

        'Lag_2_Income':
            value(2, 'Income_Total'),

        'Lag_7_Income':
            value(7, 'Income_Total'),

        'Lag_14_Income':
            value(14, 'Income_Total'),

        'Lag_28_Income':
            value(28, 'Income_Total'),

        'Lag_1_Events':
            value(1, 'Event_Count', 0),

        'Lag_2_Events':
            value(2, 'Event_Count', 0),

        'Lag_7_Events':
            value(7, 'Event_Count', 0),

        'Lag_14_Events':
            value(14, 'Event_Count', 0),

        'Lag_28_Events':
            value(28, 'Event_Count', 0),

        # Health
        'Lag_1_Health_Severity':
            value(1, 'Max_Health_Severity'),

        'Lag_7_Health_Severity':
            value(7, 'Max_Health_Severity'),

        'Lag_14_Health_Severity':
            value(14, 'Max_Health_Severity'),

        # Activity
        'Lag_1_Activity_Duration':
            value(1, 'Activity_Duration_Minutes'),

        'Lag_7_Activity_Duration':
            value(7, 'Activity_Duration_Minutes'),

        'Lag_14_Activity_Duration':
            value(14, 'Activity_Duration_Minutes'),

        # Sleep
        'Lag_1_Sleep_Duration':
            value(1, 'Sleep_Duration_Minutes'),

        'Lag_7_Sleep_Duration':
            value(7, 'Sleep_Duration_Minutes'),

        'Lag_14_Sleep_Duration':
            value(14, 'Sleep_Duration_Minutes'),
    }