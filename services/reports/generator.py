from services.analysis.financial import (
    get_financial_summary,
    get_recent_income,
    get_recent_expenses,
    get_budget_status,
    get_expenses_by_category,
    get_income_vs_expenses,
    get_expenses_by_date,
    get_expenses_by_month,
    get_average_daily_expense,
    get_expense_category_percentages,
)


# ==================================================
# FINANCIAL REPORT
# ==================================================

def generate_financial_report():
    """
    Generate the complete financial report
    using the existing analysis services.
    """

    summary = get_financial_summary()

    return {
        'summary': summary,

        'income_vs_expenses': (
            get_income_vs_expenses()
        ),

        'average_daily_expense': (
            get_average_daily_expense()
        ),

        'expenses_by_category': (
            get_expenses_by_category()
        ),

        'expense_category_percentages': (
            get_expense_category_percentages()
        ),

        'expenses_by_month': (
            get_expenses_by_month()
        ),

        'expenses_by_date': (
            get_expenses_by_date()
        ),

        'budget_status': (
            get_budget_status()
        ),

        'recent_income': (
            get_recent_income()
        ),

        'recent_expenses': (
            get_recent_expenses()
        ),
    }


# ==================================================
# REPORT METRICS
# ==================================================

def get_report_metrics():
    """
    Return the main financial metrics required
    by the Reports interface.
    """

    summary = get_financial_summary()

    total_income = summary['total_income']
    total_expenses = summary['total_expenses']
    balance = summary['balance']

    if total_income > 0:
        savings_rate = (
            balance / total_income
        ) * 100
    else:
        savings_rate = 0.0

    return {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': balance,
        'total_budget_limits': (
            summary['total_budget_limits']
        ),
        'savings_rate': savings_rate,
        'average_daily_expense': (
            get_average_daily_expense()
        ),
    }


# ==================================================
# EXPENSE REPORT
# ==================================================

def generate_expense_report():
    """
    Generate the expense section of the report.
    """

    return {
        'by_category': (
            get_expenses_by_category()
        ),

        'category_percentages': (
            get_expense_category_percentages()
        ),

        'by_month': (
            get_expenses_by_month()
        ),

        'by_date': (
            get_expenses_by_date()
        ),

        'average_daily': (
            get_average_daily_expense()
        ),

        'recent_expenses': (
            get_recent_expenses()
        ),
    }


# ==================================================
# INCOME REPORT
# ==================================================

def generate_income_report():
    """
    Generate the income section of the report.
    """

    income_vs_expenses = get_income_vs_expenses()

    return {
        'total_income': (
            income_vs_expenses['income']
        ),

        'total_expenses': (
            income_vs_expenses['expenses']
        ),

        'net_balance': (
            income_vs_expenses['income']
            - income_vs_expenses['expenses']
        ),

        'recent_income': (
            get_recent_income()
        ),
    }


# ==================================================
# BUDGET REPORT
# ==================================================

def generate_budget_report():
    """
    Generate the budget section of the report.
    """

    budget_status = get_budget_status()

    total_limit = sum(
        item['Limit']
        for item in budget_status
    )

    total_spent = sum(
        item['Spent']
        for item in budget_status
    )

    total_remaining = sum(
        item['Remaining']
        for item in budget_status
    )

    if total_limit > 0:
        usage_percentage = (
            total_spent / total_limit
        ) * 100
    else:
        usage_percentage = 0.0

    return {
        'budgets': budget_status,
        'total_limit': total_limit,
        'total_spent': total_spent,
        'total_remaining': total_remaining,
        'usage_percentage': usage_percentage,
    }