from services.analysis.financial import (
    get_financial_summary,
    get_budget_status,
    get_expenses_by_category,
    get_income_vs_expenses,
    get_expenses_by_month,
    get_average_daily_expense,
    get_expense_category_percentages,
    get_recent_income,
    get_recent_expenses,
)


# ==========================================================
# FINANCIAL ANALYSIS SERVICE
# ==========================================================

def get_analysis_data():
    """
    Return all financial analysis data required by
    the Analysis page.

    This service coordinates the existing financial
    analysis layer without duplicating its calculations.
    """

    summary = get_financial_summary()

    income_vs_expenses = (
        get_income_vs_expenses()
    )

    expenses_by_category = (
        get_expenses_by_category()
    )

    expense_category_percentages = (
        get_expense_category_percentages()
    )

    expenses_by_month = (
        get_expenses_by_month()
    )

    budget_status = (
        get_budget_status()
    )

    average_daily_expense = (
        get_average_daily_expense()
    )

    recent_income = (
        get_recent_income()
    )

    recent_expenses = (
        get_recent_expenses()
    )

    return {
        'summary': summary,

        'income_vs_expenses':
            income_vs_expenses,

        'expenses_by_category':
            expenses_by_category,

        'expense_category_percentages':
            expense_category_percentages,

        'expenses_by_month':
            expenses_by_month,

        'budget_status':
            budget_status,

        'average_daily_expense':
            average_daily_expense,

        'recent_income':
            recent_income,

        'recent_expenses':
            recent_expenses,
    }


# ==========================================================
# SUMMARY
# ==========================================================

def get_summary_data():
    """
    Return the main financial indicators.
    """

    return get_financial_summary()


# ==========================================================
# INCOME VS EXPENSES
# ==========================================================

def get_income_expense_data():
    """
    Return total income and total expenses.
    """

    return get_income_vs_expenses()


# ==========================================================
# CATEGORY ANALYSIS
# ==========================================================

def get_category_analysis():
    """
    Return expense totals and percentages by category.
    """

    return {
        'totals':
            get_expenses_by_category(),

        'percentages':
            get_expense_category_percentages(),
    }


# ==========================================================
# MONTHLY ANALYSIS
# ==========================================================

def get_monthly_expense_data():
    """
    Return total expenses grouped by month.
    """

    return get_expenses_by_month()


# ==========================================================
# DAILY ANALYSIS
# ==========================================================

def get_daily_expense_average():
    """
    Return the average expense for a day containing
    recorded expenses.
    """

    return get_average_daily_expense()


# ==========================================================
# BUDGET ANALYSIS
# ==========================================================

def get_budget_analysis():
    """
    Return budget usage and status information.
    """

    return get_budget_status()


# ==========================================================
# RECENT ACTIVITY
# ==========================================================

def get_recent_activity():
    """
    Return recent income and expense records.
    """

    return {
        'income':
            get_recent_income(),

        'expenses':
            get_recent_expenses(),
    }


# ==========================================================
# PAGE DATA
# ==========================================================

def load_analysis_page_data():
    """
    Load the complete dataset required by the Analysis page.

    This is the main frontend entry point.
    """

    return get_analysis_data()