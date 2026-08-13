
from nicegui import ui, app


# ==================================================
# HOME
# ==================================================

from pages.home.dashboard import main_page


# ==================================================
# BUDGETS
# ==================================================

from pages.budgets.add_budget import add_budget_page
from pages.budgets.budget_overview import budget_overview_page
from pages.budgets.budget_details import budget_details_page
from pages.budgets.edit_budget import edit_budget_page


# ==================================================
# ANALYSIS
# ==================================================

from pages.analysis.analysis import analysis_page


# ==================================================
# EXPENSES
# ==================================================

from pages.expenses.expense_records import expense_records_page
from pages.expenses.add_expense import add_expense_page
from pages.expenses.edit_expense import edit_expense_page
from pages.expenses.expense_details import expense_details_page


# ==================================================
# INCOME
# ==================================================

from pages.income.income_records import income_records_page
from pages.income.add_income import add_income_page
from pages.income.edit_income import edit_income_page
from pages.income.income_details import income_details_page


# ==================================================
# DAYS
# ==================================================

from pages.days.daily_records import daily_records_page
from pages.days.add_day import add_day_page
from pages.days.day_details import day_details_page
from pages.days.edit_day import edit_day_page

# ==================================================
# STATIC FILES
# ==================================================

app.add_static_files(
    '/styles',
    'styles'
)


# ==================================================
# EVENTS
# ==================================================

from pages.events.event_records import event_records_page
from pages.events.add_event import add_event_page
from pages.events.edit_event import edit_event_page
from pages.events.event_details import event_details_page

# ==================================================
# settings
# ==================================================

from pages.settings import settings_page

# ==================================================
# REPORTS
# ==================================================

from pages.reports.reports import reports_page

# ==================================================
# PREDICTION
# ==================================================

from pages.predictions.prediction import prediction_page


# ==================================================
# HEALTH
# ==================================================

from pages.health.health_records import health_records_page
from pages.health.add_health import add_health_page
from pages.health.health_details import health_details_page
from pages.health.edit_health import edit_health_page

# ==================================================
# SLEEP
# ==================================================

from pages.sleep.sleep_records import sleep_records_page
from pages.sleep.add_sleep import add_sleep_page
from pages.sleep.sleep_details import sleep_details_page
from pages.sleep.edit_sleep import edit_sleep_page


ui.run(
    host='127.0.0.1',
    port=8080,
    title='Personal Finance AI',
    favicon='assets/budget.png'
)
