
from pathlib import Path

from nicegui import ui

from components.header import create_header

from services.analysis.financial import (
    get_financial_summary,
    get_income_vs_expenses,
    get_expenses_by_category,
    get_expenses_by_date,
    get_average_daily_expense,
    get_expense_category_percentages,
    get_budget_status,
)


@ui.page('/analysis')
def analysis_page():

    create_header('Analysis')

    # --------------------------------------------------
    # Load CSS
    # --------------------------------------------------

    css_file = Path('styles/analysis.css')

    if css_file.exists():
        css_version = css_file.stat().st_mtime_ns

        ui.add_head_html(
            f'<link rel="stylesheet" '
            f'href="/styles/analysis.css?v={css_version}">'
        )

    # --------------------------------------------------
    # Load analysis data
    # --------------------------------------------------

    summary = get_financial_summary()

    total_income = summary['total_income']
    total_expenses = summary['total_expenses']
    balance = summary['balance']

    income_vs_expenses = get_income_vs_expenses()

    expenses_by_category = get_expenses_by_category()

    expenses_by_date = get_expenses_by_date()

    average_daily_expense = get_average_daily_expense()

    category_percentages = (
        get_expense_category_percentages()
    )

    budget_status = get_budget_status()

    # --------------------------------------------------
    # Page
    # --------------------------------------------------

    with ui.column().classes('analysis-page'):

        # --------------------------------------------------
        # Page Header
        # --------------------------------------------------

        with ui.column().classes('analysis-header'):

            ui.label(
                'Financial Analysis'
            ).classes('analysis-title')

            ui.label(
                'Detailed analysis of your personal finances.'
            ).classes('analysis-subtitle')

        # --------------------------------------------------
        # Financial Overview
        # --------------------------------------------------

        ui.label(
            'Financial Overview'
        ).classes('analysis-section-title')

        with ui.row().classes('analysis-cards'):

            with ui.card().classes('analysis-card'):

                ui.label(
                    'Total Income'
                ).classes('analysis-card-label')

                ui.label(
                    f'{total_income:,.2f}'
                ).classes('analysis-card-value')

            with ui.card().classes('analysis-card'):

                ui.label(
                    'Total Expenses'
                ).classes('analysis-card-label')

                ui.label(
                    f'{total_expenses:,.2f}'
                ).classes('analysis-card-value')

            with ui.card().classes('analysis-card'):

                ui.label(
                    'Balance'
                ).classes('analysis-card-label')

                balance_class = (
                    'analysis-positive'
                    if balance > 0
                    else 'analysis-negative'
                    if balance < 0
                    else 'analysis-neutral'
                )

                ui.label(
                    f'{balance:,.2f}'
                ).classes(
                    f'analysis-card-value {balance_class}'
                )

        # --------------------------------------------------
        # Spending Indicators
        # --------------------------------------------------

        ui.label(
            'Spending Indicators'
        ).classes('analysis-section-title')

        with ui.row().classes('analysis-cards'):

            with ui.card().classes('analysis-card'):

                ui.label(
                    'Average Daily Expense'
                ).classes('analysis-card-label')

                ui.label(
                    f'{average_daily_expense:,.2f}'
                ).classes('analysis-card-value')

            with ui.card().classes('analysis-card'):

                ui.label(
                    'Top Spending Category'
                ).classes('analysis-card-label')

                if category_percentages:

                    top_category = max(
                        category_percentages,
                        key=category_percentages.get,
                    )

                    top_percentage = (
                        category_percentages[top_category]
                    )

                    ui.label(
                        top_category
                    ).classes('analysis-card-value')

                    ui.label(
                        f'{top_percentage:.2f}% of total expenses'
                    ).classes('analysis-card-detail')

                else:

                    ui.label(
                        'No spending data'
                    ).classes('analysis-card-value')

        # --------------------------------------------------
        # Charts
        # --------------------------------------------------

        ui.label(
            'Charts'
        ).classes('analysis-section-title')

        with ui.row().classes('analysis-charts-row'):

            # Income vs Expenses
            with ui.card().classes('analysis-chart-card'):

                ui.label(
                    'Income vs Expenses'
                ).classes('analysis-chart-title')

                ui.echart({
                    'tooltip': {
                        'trigger': 'axis',
                    },
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
                }).classes(
                    'analysis-chart'
                )

            # Expenses by Category
            with ui.card().classes('analysis-chart-card'):

                ui.label(
                    'Expenses by Category'
                ).classes('analysis-chart-title')

                if expenses_by_category:

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
                                    for (
                                        category,
                                        amount
                                    ) in expenses_by_category.items()
                                ],
                            }
                        ],
                    }).classes(
                        'analysis-chart'
                    )

                else:

                    ui.label(
                        'No expense data available.'
                    ).classes(
                        'analysis-neutral-text'
                    )

        # --------------------------------------------------
        # Daily Expenses
        # --------------------------------------------------

        with ui.card().classes(
            'analysis-chart-card analysis-full-width'
        ):

            ui.label(
                'Daily Expenses'
            ).classes('analysis-chart-title')

            if expenses_by_date:

                ui.echart({
                    'tooltip': {
                        'trigger': 'axis',
                    },
                    'xAxis': {
                        'type': 'category',
                        'data': [
                            str(date)
                            for date in expenses_by_date.keys()
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
                }).classes(
                    'analysis-chart'
                )

            else:

                ui.label(
                    'No expense data available.'
                ).classes(
                    'analysis-neutral-text'
                )

        # --------------------------------------------------
        # Budget Performance
        # --------------------------------------------------

        ui.label(
            'Budget Performance'
        ).classes('analysis-section-title')

        with ui.card().classes(
            'budget-analysis-card'
        ):

            if not budget_status:

                ui.label(
                    'No budgets found.'
                ).classes(
                    'analysis-neutral-text'
                )

            else:

                for budget in budget_status:

                    with ui.column().classes(
                        'budget-analysis-item'
                    ):

                        with ui.row().classes(
                            'budget-analysis-header'
                        ):

                            ui.label(
                                budget['Category']
                            ).classes(
                                'budget-analysis-category'
                            )

                            ui.label(
                                budget['Status']
                            ).classes(
                                'budget-analysis-status'
                            )

                        with ui.row().classes(
                            'budget-analysis-amounts'
                        ):

                            ui.label(
                                f"Spent: "
                                f"{budget['Spent']:,.2f}"
                            )

                            ui.label(
                                f"Limit: "
                                f"{budget['Limit']:,.2f}"
                            )

                            ui.label(
                                f"{budget['Percentage']:.2f}%"
                            )

                        percentage = min(
                            max(
                                budget['Percentage'],
                                0
                            ),
                            100
                        )

                        ui.linear_progress(
                            value=percentage / 100
                        ).classes(
                            'budget-analysis-progress'
                        )

                        if budget['Remaining'] >= 0:

                            ui.label(
                                f"Remaining: "
                                f"{budget['Remaining']:,.2f}"
                            ).classes(
                                'analysis-neutral-text'
                            )

                        else:

                            ui.label(
                                f"Over budget: "
                                f"{abs(budget['Remaining']):,.2f}"
                            ).classes(
                                'analysis-negative'
                            )

                        ui.separator()
