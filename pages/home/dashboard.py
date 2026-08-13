from pathlib import Path

from nicegui import ui

from components.layout import create_page_layout

from services.analysis.financial import (
    get_financial_summary,
    get_recent_income,
    get_recent_expenses,
    get_budget_status,
    get_income_vs_expenses,
    get_expenses_by_category,
    get_expenses_by_date,
)


@ui.page('/')
def main_page():

    # ==================================================
    # SHARED APPLICATION LAYOUT
    # ==================================================

    content = create_page_layout(
        title='Dashboard',
        active_page='Dashboard',
    )

    # ==================================================
    # DASHBOARD CONTENT
    # ==================================================

    with content:

        # --------------------------------------------------
        # PAGE CSS
        # --------------------------------------------------

        css_file = Path('styles/home.css')

        if css_file.exists():

            css_version = css_file.stat().st_mtime_ns

            ui.add_head_html(
                f'<link rel="stylesheet" '
                f'href="/styles/home.css?v={css_version}">'
            )

        # --------------------------------------------------
        # FINANCIAL DATA
        # --------------------------------------------------

        summary = get_financial_summary()

        total_income = summary['total_income']
        total_expenses = summary['total_expenses']
        balance = summary['balance']
        total_budget_limits = summary['total_budget_limits']

        # --------------------------------------------------
        # DASHBOARD HEADER
        # --------------------------------------------------

        with ui.column().classes('dashboard-header'):

            ui.label(
                'Dashboard'
            ).classes('dashboard-title')

            ui.label(
                'Overview of your personal finances.'
            ).classes('dashboard-subtitle')

        # --------------------------------------------------
        # FINANCIAL CARDS
        # --------------------------------------------------

        with ui.row().classes('financial-cards'):

            # Total Income
            with ui.card().classes('financial-card'):

                with ui.row().classes('budget-amounts'):

                    with ui.column().classes('gap-1'):

                        ui.label(
                            'Total Income'
                        ).classes('financial-card-label')

                        ui.label(
                            f'{total_income:,.2f}'
                        ).classes('financial-card-value')

                    ui.icon(
                        'trending_up',
                        size='40px'
                    )

            # Total Expenses
            with ui.card().classes('financial-card'):

                with ui.row().classes('budget-amounts'):

                    with ui.column().classes('gap-1'):

                        ui.label(
                            'Total Expenses'
                        ).classes('financial-card-label')

                        ui.label(
                            f'{total_expenses:,.2f}'
                        ).classes('financial-card-value')

                    ui.icon(
                        'trending_down',
                        size='40px'
                    )

            # Balance
            with ui.card().classes('financial-card'):

                with ui.row().classes('budget-amounts'):

                    with ui.column().classes('gap-1'):

                        ui.label(
                            'Balance'
                        ).classes('financial-card-label')

                        ui.label(
                            f'{balance:,.2f}'
                        ).classes('financial-card-value')

                    ui.icon(
                        'account_balance',
                        size='40px'
                    )

            # Budget Limits
            with ui.card().classes('financial-card'):

                with ui.row().classes('budget-amounts'):

                    with ui.column().classes('gap-1'):

                        ui.label(
                            'Budget Limits'
                        ).classes('financial-card-label')

                        ui.label(
                            f'{total_budget_limits:,.2f}'
                        ).classes('financial-card-value')

                    ui.icon(
                        'account_balance_wallet',
                        size='40px'
                    )

        # --------------------------------------------------
        # RECENT TRANSACTIONS
        # --------------------------------------------------

        recent_income = get_recent_income()
        recent_expenses = get_recent_expenses()

        with ui.row().classes('transactions-row'):

            # --------------------------------------------------
            # RECENT INCOME
            # --------------------------------------------------

            with ui.card().classes('transaction-card'):

                ui.label(
                    'Recent Income'
                ).classes('section-title')

                if not recent_income:

                    ui.label(
                        'No income records found.'
                    ).classes('text-gray-500')

                else:

                    for income in recent_income:

                        with ui.row().classes('transaction-row'):

                            with ui.column().classes('transaction-main'):

                                ui.label(
                                    income['Source']
                                ).classes('transaction-category')

                                ui.label(
                                    income['Description'] or ''
                                ).classes('transaction-description')

                            ui.label(
                                f"{float(income['Amount']):,.2f}"
                            ).classes('transaction-amount')

            # --------------------------------------------------
            # RECENT EXPENSES
            # --------------------------------------------------

            with ui.card().classes('transaction-card'):

                ui.label(
                    'Recent Expenses'
                ).classes('section-title')

                if not recent_expenses:

                    ui.label(
                        'No expense records found.'
                    ).classes('text-gray-500')

                else:

                    for expense in recent_expenses:

                        with ui.row().classes('transaction-row'):

                            with ui.column().classes('transaction-main'):

                                ui.label(
                                    expense['Category']
                                ).classes('transaction-category')

                                ui.label(
                                    expense['Description'] or ''
                                ).classes('transaction-description')

                            ui.label(
                                f"- {float(expense['Amount']):,.2f}"
                            ).classes('transaction-amount')

        # --------------------------------------------------
        # BUDGET STATUS
        # --------------------------------------------------

        budget_status = get_budget_status()

        with ui.card().classes('budget-status-card'):

            ui.label(
                'Budget Status'
            ).classes(
                'text-xl font-semibold mb-4'
            )

            if not budget_status:

                ui.label(
                    'No budgets found.'
                ).classes('text-gray-500')

            else:

                for budget in budget_status:

                    with ui.column().classes('budget-item'):

                        # Header
                        with ui.row().classes('budget-header'):

                            ui.label(
                                budget['Category']
                            ).classes('budget-category')

                            ui.label(
                                budget['Status']
                            ).classes('budget-status')

                        # Amounts
                        with ui.row().classes('budget-amounts'):

                            ui.label(
                                f"Spent: {budget['Spent']:,.2f}"
                            ).classes('text-gray-600')

                            ui.label(
                                f"Limit: {budget['Limit']:,.2f}"
                            ).classes('text-gray-600')

                        # Progress
                        percentage = min(
                            max(budget['Percentage'], 0),
                            100
                        )

                        ui.linear_progress(
                            value=percentage / 100
                        ).classes('budget-progress')

                        # Remaining / Over budget
                        if budget['Remaining'] >= 0:

                            ui.label(
                                f"Remaining: {budget['Remaining']:,.2f}"
                            ).classes(
                                'text-sm text-gray-500'
                            )

                        else:

                            ui.label(
                                f"Over budget: "
                                f"{abs(budget['Remaining']):,.2f}"
                            ).classes('text-sm')

                        ui.separator()

        # --------------------------------------------------
        # FINANCIAL STATUS
        # --------------------------------------------------

        with ui.card().classes('financial-status-card'):

            ui.label(
                'Financial Status'
            ).classes('financial-status-title')

            if balance > 0:

                ui.label(
                    'Your current balance is positive.'
                ).classes(
                    'financial-status-positive'
                )

            elif balance < 0:

                ui.label(
                    'Your current balance is negative.'
                ).classes(
                    'financial-status-negative'
                )

            else:

                ui.label(
                    'Your income and expenses are currently balanced.'
                ).classes(
                    'financial-status-neutral'
                )

        # --------------------------------------------------
        # INCOME VS EXPENSES
        # --------------------------------------------------

        income_vs_expenses = get_income_vs_expenses()

        with ui.card().classes('financial-chart-card'):

            ui.label(
                'Income vs Expenses'
            ).classes('financial-status-title')

            ui.echart({
                'xAxis': {
                    'type': 'category',
                    'data': [
                        'Income',
                        'Expenses',
                    ],
                },

                'yAxis': {
                    'type': 'value',
                },

                'series': [
                    {
                        'type': 'bar',
                        'data': [
                            income_vs_expenses['income'],
                            income_vs_expenses['expenses'],
                        ],
                        'barWidth': '45%',
                    }
                ],

                'tooltip': {
                    'trigger': 'axis',
                },
            }).classes('w-full').style(
                'height: 350px'
            )

        # --------------------------------------------------
        # EXPENSES BY CATEGORY
        # --------------------------------------------------

        expenses_by_category = get_expenses_by_category()

        with ui.card().classes('financial-chart-card'):

            ui.label(
                'Expenses by Category'
            ).classes('financial-status-title')

            if not expenses_by_category:

                ui.label(
                    'No expense data available.'
                ).classes(
                    'financial-status-neutral'
                )

            else:

                ui.echart({

                    'tooltip': {
                        'trigger': 'item',
                    },

                    'legend': {
                        'orient': 'vertical',
                        'left': 'left',
                    },

                    'series': [
                        {
                            'name': 'Expenses',
                            'type': 'pie',
                            'radius': '65%',

                            'data': [
                                {
                                    'name': category,
                                    'value': amount,
                                }

                                for category, amount
                                in expenses_by_category.items()
                            ],

                            'emphasis': {
                                'itemStyle': {
                                    'shadowBlur': 10,
                                    'shadowOffsetX': 0,
                                }
                            },
                        }
                    ],
                }).classes('w-full').style(
                    'height: 400px'
                )

        # --------------------------------------------------
        # DAILY EXPENSES
        # --------------------------------------------------

        expenses_by_date = get_expenses_by_date()

        with ui.card().classes('financial-chart-card'):

            ui.label(
                'Daily Expenses'
            ).classes('financial-status-title')

            if not expenses_by_date:

                ui.label(
                    'No expense data available.'
                ).classes(
                    'financial-status-neutral'
                )

            else:

                ui.echart({

                    'tooltip': {
                        'trigger': 'axis',
                    },

                    'xAxis': {
                        'type': 'category',

                        'data': [
                            str(date)
                            for date
                            in expenses_by_date.keys()
                        ],
                    },

                    'yAxis': {
                        'type': 'value',
                    },

                    'series': [
                        {
                            'name': 'Expenses',
                            'type': 'line',

                            'data': list(
                                expenses_by_date.values()
                            ),

                            'smooth': True,
                            'areaStyle': {},
                        }
                    ],
                }).classes('w-full').style(
                    'height: 350px'
                )