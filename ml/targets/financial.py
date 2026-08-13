def create_financial_targets(row):
    """
    Create financial targets from one prepared daily row.

    Targets describe the financial outcome of the day.
    They are kept separate from input features so the model
    can learn to predict future financial behavior.
    """

    expense_total = float(
        row.get('Expense_Total') or 0.0
    )

    income_total = float(
        row.get('Income_Total') or 0.0
    )

    daily_balance = (
        income_total - expense_total
    )

    return {
        'Target_Has_Expense':
            int(expense_total > 0),

        'Target_Has_Income':
            int(income_total > 0),

        'Target_Positive_Balance':
            int(daily_balance > 0),

        'Target_High_Expense':
            int(
                expense_total
                > 0
            ),
    }