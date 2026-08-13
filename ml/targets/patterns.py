def create_pattern_targets(row):
    """
    Create pattern-related targets from one prepared daily row.

    Targets describe recurring or notable patterns
    that may be learned from historical daily data.
    """

    expense_total = float(
        row.get('Expense_Total') or 0.0
    )

    income_total = float(
        row.get('Income_Total') or 0.0
    )

    event_count = int(
        row.get('Event_Count') or 0
    )

    stress_level = float(
        row.get('Stress_Level') or 0.0
    )

    sleep_hours = float(
        row.get('Sleep_Hours') or 0.0
    )

    return {
        'Target_Busy_Day':
            int(
                event_count >= 2
                or expense_total > 0
            ),

        'Target_Financial_Activity':
            int(
                expense_total > 0
                or income_total > 0
            ),

        'Target_Difficult_Day':
            int(
                stress_level >= 7
                or (
                    sleep_hours > 0
                    and sleep_hours < 6
                )
            ),
    }