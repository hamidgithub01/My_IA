from pathlib import Path

from nicegui import ui

from components.header import create_header
from services.reports.generator import (
    get_report_metrics,
    generate_expense_report,
    generate_budget_report,
)


@ui.page('/reports')
def reports_page():

    create_header('Reports')

    # ==================================================
    # CSS
    # ==================================================

    css_file = Path('styles/reports.css')

    if css_file.exists():

        css_version = css_file.stat().st_mtime_ns

        ui.add_head_html(
            f'<link rel="stylesheet" '
            f'href="/styles/reports.css?v={css_version}">'
        )

    # ==================================================
    # Data
    # ==================================================

    metrics = get_report_metrics()
    expense_report = generate_expense_report()
    budget_report = generate_budget_report()

    # ==================================================
    # Page
    # ==================================================

    with ui.column().classes('reports-page'):

        # ==================================================
        # Hero
        # ==================================================

        with ui.row().classes('reports-hero'):

            with ui.column().classes('reports-hero-content'):

                ui.label(
                    'Financial Reports'
                ).classes('reports-title')

                ui.label(
                    'Understand your financial activity, '
                    'spending patterns, and budget performance.'
                ).classes('reports-subtitle')

            with ui.column().classes('reports-hero-meta'):

                ui.icon(
                    'assessment',
                    size='42px'
                ).classes('reports-hero-icon')

                ui.label(
                    'Financial Overview'
                ).classes('reports-hero-label')

        # ==================================================
        # KPI Metrics
        # ==================================================

        with ui.row().classes('reports-metrics-grid'):

            # ----------------------------------------------
            # Income
            # ----------------------------------------------

            with ui.card().classes(
                'report-metric-card report-metric-income'
            ):

                with ui.row().classes(
                    'report-metric-top'
                ):

                    with ui.column().classes(
                        'report-metric-content'
                    ):

                        ui.label(
                            'Total Income'
                        ).classes(
                            'report-metric-label'
                        )

                        ui.label(
                            f"{metrics['total_income']:,.2f}"
                        ).classes(
                            'report-metric-value'
                        )

                    with ui.element(
                        'div'
                    ).classes(
                        'report-metric-icon'
                    ):

                        ui.icon('trending_up')

                ui.label(
                    'Money received'
                ).classes(
                    'report-metric-caption'
                )

            # ----------------------------------------------
            # Expenses
            # ----------------------------------------------

            with ui.card().classes(
                'report-metric-card report-metric-expenses'
            ):

                with ui.row().classes(
                    'report-metric-top'
                ):

                    with ui.column().classes(
                        'report-metric-content'
                    ):

                        ui.label(
                            'Total Expenses'
                        ).classes(
                            'report-metric-label'
                        )

                        ui.label(
                            f"{metrics['total_expenses']:,.2f}"
                        ).classes(
                            'report-metric-value'
                        )

                    with ui.element(
                        'div'
                    ).classes(
                        'report-metric-icon'
                    ):

                        ui.icon('trending_down')

                ui.label(
                    'Money spent'
                ).classes(
                    'report-metric-caption'
                )

            # ----------------------------------------------
            # Balance
            # ----------------------------------------------

            balance_class = (
                'report-metric-positive'
                if metrics['balance'] >= 0
                else 'report-metric-negative'
            )

            with ui.card().classes(
                f'report-metric-card {balance_class}'
            ):

                with ui.row().classes(
                    'report-metric-top'
                ):

                    with ui.column().classes(
                        'report-metric-content'
                    ):

                        ui.label(
                            'Net Balance'
                        ).classes(
                            'report-metric-label'
                        )

                        ui.label(
                            f"{metrics['balance']:,.2f}"
                        ).classes(
                            'report-metric-value'
                        )

                    with ui.element(
                        'div'
                    ).classes(
                        'report-metric-icon'
                    ):

                        ui.icon('account_balance')

                ui.label(
                    'Income minus expenses'
                ).classes(
                    'report-metric-caption'
                )

            # ----------------------------------------------
            # Savings Rate
            # ----------------------------------------------

            with ui.card().classes(
                'report-metric-card report-metric-savings'
            ):

                with ui.row().classes(
                    'report-metric-top'
                ):

                    with ui.column().classes(
                        'report-metric-content'
                    ):

                        ui.label(
                            'Savings Rate'
                        ).classes(
                            'report-metric-label'
                        )

                        ui.label(
                            f"{metrics['savings_rate']:.1f}%"
                        ).classes(
                            'report-metric-value'
                        )

                    with ui.element(
                        'div'
                    ).classes(
                        'report-metric-icon'
                    ):

                        ui.icon('savings')

                ui.label(
                    'Balance relative to income'
                ).classes(
                    'report-metric-caption'
                )

        # ==================================================
        # Financial Position
        # ==================================================

        with ui.card().classes(
            'reports-section-card'
        ):

            with ui.column().classes(
                'reports-section-heading'
            ):

                ui.label(
                    'Financial Position'
                ).classes(
                    'reports-section-title'
                )

                ui.label(
                    'A simple comparison between money received '
                    'and money spent.'
                ).classes(
                    'reports-section-subtitle'
                )

            income = metrics['total_income']
            expenses = metrics['total_expenses']

            total_flow = income + expenses

            with ui.row().classes(
                'financial-flow'
            ):

                with ui.column().classes(
                    'financial-flow-item'
                ):

                    ui.label(
                        'Income'
                    ).classes(
                        'financial-flow-label'
                    )

                    ui.label(
                        f'{income:,.2f}'
                    ).classes(
                        'financial-flow-value'
                    )

                with ui.column().classes(
                    'financial-flow-track'
                ):

                    if total_flow > 0:

                        income_width = (
                            income / total_flow
                        ) * 100

                        expense_width = (
                            expenses / total_flow
                        ) * 100

                    else:

                        income_width = 0
                        expense_width = 0

                    with ui.element(
                        'div'
                    ).classes(
                        'financial-flow-bar'
                    ):

                        ui.element(
                            'div'
                        ).classes(
                            'financial-flow-income'
                        ).style(
                            f'width: {income_width:.2f}%'
                        )

                        ui.element(
                            'div'
                        ).classes(
                            'financial-flow-expenses'
                        ).style(
                            f'width: {expense_width:.2f}%'
                        )

                with ui.column().classes(
                    'financial-flow-item'
                ):

                    ui.label(
                        'Expenses'
                    ).classes(
                        'financial-flow-label'
                    )

                    ui.label(
                        f'{expenses:,.2f}'
                    ).classes(
                        'financial-flow-value'
                    )

        # ==================================================
        # Expense Analysis
        # ==================================================

        with ui.row().classes(
            'reports-analysis-grid'
        ):

            # ----------------------------------------------
            # Categories
            # ----------------------------------------------

            with ui.card().classes(
                'reports-section-card report-analysis-card'
            ):

                with ui.column().classes(
                    'reports-section-heading'
                ):

                    ui.label(
                        'Expense Breakdown'
                    ).classes(
                        'reports-section-title'
                    )

                    ui.label(
                        'Where your money is going.'
                    ).classes(
                        'reports-section-subtitle'
                    )

                categories = expense_report[
                    'by_category'
                ]

                percentages = expense_report[
                    'category_percentages'
                ]

                if not categories:

                    with ui.column().classes(
                        'reports-empty-state'
                    ):

                        ui.icon(
                            'pie_chart',
                            size='40px'
                        )

                        ui.label(
                            'No expense data available.'
                        ).classes(
                            'reports-empty-title'
                        )

                else:

                    for category, amount in sorted(
                        categories.items(),
                        key=lambda item: item[1],
                        reverse=True,
                    ):

                        percentage = percentages.get(
                            category,
                            0.0
                        )

                        with ui.column().classes(
                            'expense-breakdown-item'
                        ):

                            with ui.row().classes(
                                'expense-breakdown-header'
                            ):

                                ui.label(
                                    category
                                ).classes(
                                    'expense-breakdown-category'
                                )

                                ui.label(
                                    f'{amount:,.2f} '
                                    f'({percentage:.1f}%)'
                                ).classes(
                                    'expense-breakdown-amount'
                                )

                            with ui.element(
                                'div'
                            ).classes(
                                'expense-breakdown-track'
                            ):

                                ui.element(
                                    'div'
                                ).classes(
                                    'expense-breakdown-progress'
                                ).style(
                                    f'width: '
                                    f'{min(percentage, 100):.2f}%'
                                )

            # ----------------------------------------------
            # Spending Overview
            # ----------------------------------------------

            with ui.card().classes(
                'reports-section-card report-analysis-card'
            ):

                with ui.column().classes(
                    'reports-section-heading'
                ):

                    ui.label(
                        'Spending Overview'
                    ).classes(
                        'reports-section-title'
                    )

                    ui.label(
                        'Recent spending activity by month.'
                    ).classes(
                        'reports-section-subtitle'
                    )

                monthly_expenses = expense_report[
                    'by_month'
                ]

                if not monthly_expenses:

                    with ui.column().classes(
                        'reports-empty-state'
                    ):

                        ui.icon(
                            'bar_chart',
                            size='40px'
                        )

                        ui.label(
                            'No monthly data available.'
                        ).classes(
                            'reports-empty-title'
                        )

                else:

                    max_monthly = max(
                        monthly_expenses.values()
                    )

                    for month, amount in list(
                        monthly_expenses.items()
                    )[-6:]:

                        if max_monthly > 0:
                            width = (
                                amount / max_monthly
                            ) * 100
                        else:
                            width = 0

                        with ui.column().classes(
                            'monthly-expense-item'
                        ):

                            with ui.row().classes(
                                'monthly-expense-header'
                            ):

                                ui.label(
                                    month
                                ).classes(
                                    'monthly-expense-month'
                                )

                                ui.label(
                                    f'{amount:,.2f}'
                                ).classes(
                                    'monthly-expense-value'
                                )

                            with ui.element(
                                'div'
                            ).classes(
                                'monthly-expense-track'
                            ):

                                ui.element(
                                    'div'
                                ).classes(
                                    'monthly-expense-progress'
                                ).style(
                                    f'width: {width:.2f}%'
                                )

        # ==================================================
        # Budget Health
        # ==================================================

        with ui.card().classes(
            'reports-section-card'
        ):

            with ui.column().classes(
                'reports-section-heading'
            ):

                ui.label(
                    'Budget Health'
                ).classes(
                    'reports-section-title'
                )

                ui.label(
                    'How your current spending compares '
                    'with your budgets.'
                ).classes(
                    'reports-section-subtitle'
                )

            with ui.row().classes(
                'budget-summary-grid'
            ):

                with ui.column().classes(
                    'budget-summary-item'
                ):

                    ui.label(
                        'Budget Limit'
                    ).classes(
                        'budget-summary-label'
                    )

                    ui.label(
                        f"{budget_report['total_limit']:,.2f}"
                    ).classes(
                        'budget-summary-value'
                    )

                with ui.column().classes(
                    'budget-summary-item'
                ):

                    ui.label(
                        'Spent'
                    ).classes(
                        'budget-summary-label'
                    )

                    ui.label(
                        f"{budget_report['total_spent']:,.2f}"
                    ).classes(
                        'budget-summary-value'
                    )

                with ui.column().classes(
                    'budget-summary-item'
                ):

                    ui.label(
                        'Remaining'
                    ).classes(
                        'budget-summary-label'
                    )

                    ui.label(
                        f"{budget_report['total_remaining']:,.2f}"
                    ).classes(
                        'budget-summary-value'
                    )

                with ui.column().classes(
                    'budget-summary-item'
                ):

                    ui.label(
                        'Usage'
                    ).classes(
                        'budget-summary-label'
                    )

                    ui.label(
                        f"{budget_report['usage_percentage']:.1f}%"
                    ).classes(
                        'budget-summary-value'
                    )

            budgets = budget_report['budgets']

            if budgets:

                with ui.column().classes(
                    'budget-status-list'
                ):

                    for budget in budgets:

                        status_class = (
                            budget['Status']
                            .lower()
                            .replace(' ', '-')
                        )

                        with ui.row().classes(
                            'budget-status-row'
                        ):

                            with ui.column().classes(
                                'budget-status-main'
                            ):

                                ui.label(
                                    budget['Category']
                                ).classes(
                                    'budget-status-category'
                                )

                                ui.label(
                                    str(
                                        budget['Month']
                                    )
                                ).classes(
                                    'budget-status-month'
                                )

                            with ui.column().classes(
                                'budget-status-numbers'
                            ):

                                ui.label(
                                    f"{budget['Spent']:,.2f} / "
                                    f"{budget['Limit']:,.2f}"
                                ).classes(
                                    'budget-status-amount'
                                )

                                ui.label(
                                    budget['Status']
                                ).classes(
                                    f'budget-status-badge '
                                    f'budget-status-{status_class}'
                                )

        # ==================================================
        # Report Footer
        # ==================================================

        with ui.row().classes(
            'reports-footer'
        ):

            ui.label(
                'Personal Finance AI'
            ).classes(
                'reports-footer-brand'
            )

            ui.label(
                'Financial report generated from '
                'your recorded data.'
            ).classes(
                'reports-footer-text'
            )