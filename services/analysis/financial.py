
from database.queries import (
    get_all_income,
    get_all_expenses,
    get_all_budgets,
)


def get_total_income():
    """
    Calculate total income from all income records.
    """

    income_records = get_all_income()

    return sum(
        float(record['Amount'])
        for record in income_records
        if record.get('Amount') is not None
    )


def get_total_expenses():
    """
    Calculate total expenses from all expense records.
    """

    expense_records = get_all_expenses()

    return sum(
        float(record['Amount'])
        for record in expense_records
        if record.get('Amount') is not None
    )


def get_balance():
    """
    Calculate current balance.

    Balance = Total Income - Total Expenses
    """

    total_income = get_total_income()
    total_expenses = get_total_expenses()

    return total_income - total_expenses


def get_total_budget_limits():
    """
    Calculate the sum of all budget limits.
    """

    budgets = get_all_budgets()

    return sum(
        float(budget['Limit'])
        for budget in budgets
        if budget.get('Limit') is not None
    )


def get_financial_summary():
    """
    Return the main financial indicators.
    """

    total_income = get_total_income()
    total_expenses = get_total_expenses()
    balance = total_income - total_expenses
    total_budget_limits = get_total_budget_limits()

    return {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': balance,
        'total_budget_limits': total_budget_limits,
    }


def get_recent_income(limit=5):
    """
    Return the most recent income records.
    """

    income_records = get_all_income()

    return income_records[:limit]


def get_recent_expenses(limit=5):
    """
    Return the most recent expense records.
    """

    expense_records = get_all_expenses()

    return expense_records[:limit]


def get_budget_status():
    """
    Return budget usage information for each budget.

    Spending is matched by:
    - Category
    - Month

    This prevents expenses from being incorrectly
    assigned to unrelated budgets.
    """

    budgets = get_all_budgets()
    expenses = get_all_expenses()

    results = []

    for budget in budgets:

        budget_month = budget['Month']
        budget_category = budget['Category']
        budget_limit = float(budget['Limit'])

        spent = 0.0

        for expense in expenses:

            expense_date = expense['Date']
            expense_category = expense['Category']

            # Match category
            if expense_category != budget_category:
                continue

            # Match year and month
            if (
                expense_date.year == budget_month.year
                and expense_date.month == budget_month.month
            ):
                spent += float(expense['Amount'])

        if budget_limit > 0:
            percentage = (spent / budget_limit) * 100
        else:
            percentage = 0.0

        remaining = budget_limit - spent

        if spent == 0:
            status = 'No spending'

        elif percentage <= 80:
            status = 'On track'

        elif percentage <= 100:
            status = 'Near limit'

        else:
            status = 'Over budget'

        results.append({
            'Month': budget_month,
            'Category': budget_category,
            'Limit': budget_limit,
            'Spent': spent,
            'Remaining': remaining,
            'Percentage': percentage,
            'Status': status,
            'Notes': budget.get('Notes') or '',
        })

    return results

def get_expenses_by_category():
    expenses = get_all_expenses()

    category_totals = {}

    for expense in expenses:
        category = expense['Category']
        amount = float(expense['Amount'])

        if category not in category_totals:
            category_totals[category] = 0.0

        category_totals[category] += amount

    return category_totals

def get_income_vs_expenses():
    income = get_all_income()
    expenses = get_all_expenses()

    total_income = sum(
        float(item['Amount'])
        for item in income
    )

    total_expenses = sum(
        float(item['Amount'])
        for item in expenses
    )

    return {
        'income': total_income,
        'expenses': total_expenses,
    }

def get_expenses_by_date():
    expenses = get_all_expenses()

    daily_totals = {}

    for expense in expenses:
        date = expense['Date']
        amount = float(expense['Amount'])

        if date not in daily_totals:
            daily_totals[date] = 0.0

        daily_totals[date] += amount

    return dict(sorted(daily_totals.items()))

def get_expenses_by_month():
    expenses = get_all_expenses()

    monthly_totals = {}

    for expense in expenses:
        date = expense['Date']
        month = date.strftime('%Y-%m')
        amount = float(expense['Amount'])

        if month not in monthly_totals:
            monthly_totals[month] = 0.0

        monthly_totals[month] += amount

    return dict(sorted(monthly_totals.items()))

def get_average_daily_expense():
    daily_expenses = get_expenses_by_date()

    if not daily_expenses:
        return 0.0

    total_expenses = sum(
        daily_expenses.values()
    )

    number_of_days = len(
        daily_expenses
    )

    return total_expenses / number_of_days

def get_expense_category_percentages():
    expenses_by_category = get_expenses_by_category()

    total_expenses = sum(
        expenses_by_category.values()
    )

    if total_expenses == 0:
        return {}

    return {
        category: (amount / total_expenses) * 100
        for category, amount in expenses_by_category.items()
    }

