from nicegui import ui

from frontend.services.analysis_service import (
load_analysis_page_data,
)

from frontend.components import (
app_card,
metric_card,
section_title,
badge,
)

# ==========================================================

# ANALYSIS PAGE

# ==========================================================

def analysis_page():


    data = load_analysis_page_data()

    with ui.column().classes(
        'w-full '
        'min-w-0 '
        'gap-6'
    ):

        _page_header()

        _overview_section(
            data.get('summary', {})
        )

        _income_expense_section(
            data.get('income_vs_expenses', {})
        )

        _category_section(
            data.get('expenses_by_category', {}),
            data.get(
                'expense_category_percentages',
                {},
            ),
        )

        _monthly_section(
            data.get('expenses_by_month', {})
        )

        _budget_section(
            data.get('budget_status', [])
        )

        _daily_average_section(
            data.get(
                'average_daily_expense',
                0,
            )
        )

        _recent_activity_section(
            data.get('recent_income', []),
            data.get('recent_expenses', []),
        )


# ==========================================================

# PAGE HEADER

# ==========================================================

def _page_header():


    with ui.row().classes(
        'w-full '
        'items-start '
        'justify-between '
        'gap-4 '
        'flex-wrap'
    ):

        with ui.column().classes(
            'gap-1 '
            'min-w-0'
        ):

            ui.label(
                'Analysis'
            ).classes(
                'text-2xl '
                'md:text-3xl '
                'font-bold '
                'text-primary-app'
            )

            ui.label(
                'Understand your financial activity, spending patterns, '
                'budgets, and overall financial position.'
            ).classes(
                'text-sm '
                'text-secondary-app'
            )

        with ui.row().classes(
            'items-center '
            'gap-2'
        ):

            badge(
                'Financial Analysis',
                variant='info',
                icon='analytics',
            )

            ui.button(
                'Refresh',
                icon='refresh',
                on_click=lambda: ui.navigate.reload(),
            ).props(
                'unelevated no-caps'
            ).classes(
                'app-button'
            )


    # ==========================================================

    # OVERVIEW

    # ==========================================================

def _overview_section(summary):


    with ui.column().classes(
        'w-full '
        'gap-3'
    ):

        section_title(
            'Financial Overview',
            'Main financial indicators',
        )

        with ui.element('div').classes(
            'grid '
            'grid-cols-1 '
            'sm:grid-cols-2 '
            'xl:grid-cols-4 '
            'gap-4 '
            'w-full'
        ):

            metric_card(
                title='Total Income',
                value=_money(
                    summary.get(
                        'total_income',
                        0,
                    )
                ),
                subtitle='All recorded income',
                icon='account_balance',
            )

            metric_card(
                title='Total Expenses',
                value=_money(
                    summary.get(
                        'total_expenses',
                        0,
                    )
                ),
                subtitle='All recorded expenses',
                icon='payments',
            )

            metric_card(
                title='Balance',
                value=_money(
                    summary.get(
                        'balance',
                        0,
                    )
                ),
                subtitle='Income minus expenses',
                icon='account_balance_wallet',
            )

            metric_card(
                title='Budget Limits',
                value=_money(
                    summary.get(
                        'total_budget_limits',
                        0,
                    )
                ),
                subtitle='Total configured budget limits',
                icon='savings',
            )

# ==========================================================

# INCOME VS EXPENSES

# ==========================================================

def _income_expense_section(data):


    income = _to_float(
        data.get(
            'income',
            0,
        )
    )

    expenses = _to_float(
        data.get(
            'expenses',
            0,
        )
    )

    balance = income - expenses

    with app_card(
        title='Income vs Expenses',
        subtitle='Cumulative financial activity',
        icon='compare_arrows',
    ):

        with ui.element('div').classes(
            'grid '
            'grid-cols-1 '
            'md:grid-cols-3 '
            'gap-4 '
            'w-full'
        ):

            _analysis_value(
                'Income',
                _money(income),
                'account_balance',
                'success',
            )

            _analysis_value(
                'Expenses',
                _money(expenses),
                'payments',
                'warning',
            )

            variant = (
                'success'
                if balance >= 0
                else 'danger'
            )

            _analysis_value(
                'Net Balance',
                _money(balance),
                'account_balance_wallet',
                variant,
            )


# ==========================================================

# CATEGORY ANALYSIS

# ==========================================================

def _category_section(
    category_totals,
    category_percentages,
    ):


    with ui.column().classes(
        'w-full '
        'gap-3'
    ):

        section_title(
            'Spending by Category',
            'Where your recorded expenses are going',
        )

        if not category_totals:

            _empty_state(
                'No expense category data available.',
                'category',
            )

            return

        with ui.element('div').classes(
            'grid '
            'grid-cols-1 '
            'md:grid-cols-2 '
            'xl:grid-cols-3 '
            'gap-4 '
            'w-full'
        ):

            categories = sorted(
                category_totals.items(),
                key=lambda item: item[1],
                reverse=True,
            )

            for category, amount in categories:

                percentage = _to_float(
                    category_percentages.get(
                        category,
                        0,
                    )
                )

                with app_card(
                    title=str(category),
                    subtitle=f'{percentage:.1f}% of total expenses',
                    icon='category',
                ):

                    with ui.column().classes(
                        'w-full '
                        'gap-3'
                    ):

                        ui.label(
                            _money(amount)
                        ).classes(
                            'text-2xl '
                            'font-bold '
                            'text-primary-app'
                        )

                        ui.linear_progress(
                            value=max(
                                0,
                                min(
                                    percentage / 100,
                                    1,
                                ),
                            )
                        ).props(
                            'rounded'
                        ).classes(
                            'w-full'
                        )

                        ui.label(
                            f'{percentage:.1f}%'
                        ).classes(
                            'text-xs '
                            'text-secondary-app'
                        )


# ==========================================================

# MONTHLY ANALYSIS

# ==========================================================

def _monthly_section(monthly_data):


    with ui.column().classes(
        'w-full '
        'gap-3'
    ):

        section_title(
            'Monthly Spending',
            'Total expenses grouped by month',
        )

        if not monthly_data:

            _empty_state(
                'No monthly expense data available.',
                'calendar_month',
            )

            return

        with app_card(
            title='Expense Trend',
            subtitle='Monthly totals',
            icon='show_chart',
        ):

            with ui.column().classes(
                'w-full '
                'gap-3'
            ):

                items = list(
                    monthly_data.items()
                )

                max_value = max(
                    (
                        _to_float(value)
                        for _, value in items
                    ),
                    default=0,
                )

                for month, amount in items:

                    amount = _to_float(
                        amount
                    )

                    percentage = (
                        amount / max_value
                        if max_value > 0
                        else 0
                    )

                    with ui.row().classes(
                        'w-full '
                        'items-center '
                        'gap-3'
                    ):

                        ui.label(
                            str(month)
                        ).classes(
                            'w-24 '
                            'shrink-0 '
                            'text-sm '
                            'text-secondary-app'
                        )

                        ui.linear_progress(
                            value=percentage
                        ).props(
                            'rounded'
                        ).classes(
                            'flex-1'
                        )

                        ui.label(
                            _money(amount)
                        ).classes(
                            'w-28 '
                            'text-right '
                            'text-sm '
                            'font-medium '
                            'text-primary-app'
                        )


# ==========================================================

# BUDGET ANALYSIS

# ==========================================================

def _budget_section(budget_status):


    with ui.column().classes(
        'w-full '
        'gap-3'
    ):

        section_title(
            'Budget Analysis',
            'Budget usage by month and category',
        )

        if not budget_status:

            _empty_state(
                'No budgets have been configured yet.',
                'account_balance_wallet',
            )

            return

        with ui.element('div').classes(
            'grid '
            'grid-cols-1 '
            'xl:grid-cols-2 '
            'gap-4 '
            'w-full'
        ):

            for budget in budget_status:

                limit = _to_float(
                    budget.get(
                        'Limit',
                        0,
                    )
                )

                spent = _to_float(
                    budget.get(
                        'Spent',
                        0,
                    )
                )

                remaining = _to_float(
                    budget.get(
                        'Remaining',
                        limit - spent,
                    )
                )

                percentage = _to_float(
                    budget.get(
                        'Percentage',
                        0,
                    )
                )

                status = budget.get(
                    'Status',
                    'Unknown',
                )

                variant = _budget_variant(
                    status
                )

                with app_card(
                    title=str(
                        budget.get(
                            'Category',
                            'Budget',
                        )
                    ),
                    subtitle=_format_month(
                        budget.get('Month')
                    ),
                    icon='account_balance_wallet',
                ):

                    with ui.column().classes(
                        'w-full '
                        'gap-3'
                    ):

                        with ui.row().classes(
                            'w-full '
                            'items-center '
                            'justify-between '
                            'gap-3'
                        ):

                            ui.label(
                                _money(spent)
                            ).classes(
                                'text-xl '
                                'font-bold '
                                'text-primary-app'
                            )

                            badge(
                                status,
                                variant=variant,
                            )

                        ui.linear_progress(
                            value=max(
                                0,
                                min(
                                    percentage / 100,
                                    1,
                                ),
                            )
                        ).props(
                            'rounded'
                        ).classes(
                            'w-full'
                        )

                        with ui.row().classes(
                            'w-full '
                            'justify-between '
                            'gap-3 '
                            'text-xs '
                            'text-secondary-app'
                        ):

                            ui.label(
                                f'Limit: {_money(limit)}'
                            )

                            ui.label(
                                f'{percentage:.1f}% used'
                            )

                            ui.label(
                                f'Remaining: {_money(remaining)}'
                            )


# ==========================================================

# DAILY AVERAGE

# ==========================================================

def _daily_average_section(value):


    value = _to_float(value)

    with app_card(
        title='Average Daily Expense',
        subtitle='Average across days with recorded expenses',
        icon='today',
    ):

        with ui.row().classes(
            'w-full '
            'items-center '
            'justify-between '
            'gap-4 '
            'flex-wrap'
        ):

            with ui.column().classes(
                'gap-1'
            ):

                ui.label(
                    _money(value)
                ).classes(
                    'text-3xl '
                    'font-bold '
                    'text-primary-app'
                )

                ui.label(
                    'per recorded expense day'
                ).classes(
                    'text-sm '
                    'text-secondary-app'
                )

            badge(
                'Calculated',
                variant='info',
                icon='calculate',
            )


# ==========================================================

# RECENT ACTIVITY

# ==========================================================

def _recent_activity_section(
recent_income,
recent_expenses,
):


    with ui.column().classes(
        'w-full '
        'gap-3'
    ):

        section_title(
            'Recent Financial Activity',
            'Latest recorded income and expenses',
        )

        with ui.element('div').classes(
            'grid '
            'grid-cols-1 '
            'xl:grid-cols-2 '
            'gap-4 '
            'w-full'
        ):

            _activity_card(
                title='Recent Income',
                records=recent_income,
                icon='trending_up',
                amount_variant='success',
                income=True,
            )

            _activity_card(
                title='Recent Expenses',
                records=recent_expenses,
                icon='trending_down',
                amount_variant='warning',
                income=False,
            )


# ==========================================================

# ACTIVITY CARD

# ==========================================================

def _activity_card(
*,
title,
records,
icon,
amount_variant,
income,
):

    with app_card(
        title=title,
        subtitle='Latest records',
        icon=icon,
    ):

        if not records:

            _empty_state(
                'No records available.',
                icon,
            )

            return

        with ui.column().classes(
            'w-full '
            'gap-0'
        ):

            for index, record in enumerate(
                records
            ):

                if index > 0:
                    ui.separator()

                date = record.get(
                    'Date',
                    '',
                )

                description = record.get(
                    'Description'
                )

                if not description:

                    description = (
                        record.get(
                            'Source'
                        )
                        if income
                        else record.get(
                            'Category'
                        )
                    )

                amount = _to_float(
                    record.get(
                        'Amount',
                        0,
                    )
                )

                with ui.row().classes(
                    'w-full '
                    'items-center '
                    'justify-between '
                    'gap-3 '
                    'py-3'
                ):

                    with ui.column().classes(
                        'gap-0 '
                        'min-w-0'
                    ):

                        ui.label(
                            str(
                                description
                                or 'Transaction'
                            )
                        ).classes(
                            'text-sm '
                            'font-medium '
                            'text-primary-app '
                            'truncate'
                        )

                        ui.label(
                            str(date)
                        ).classes(
                            'text-xs '
                            'text-secondary-app'
                        )

                    badge(
                        _money(amount),
                        variant=amount_variant,
                    )


# ==========================================================

# SMALL ANALYSIS VALUE

# ==========================================================

def _analysis_value(
label,
value,
icon,
variant,
):


    with ui.column().classes(
        'gap-2 '
        'p-4 '
        'rounded-xl '
        'bg-[var(--surface-soft)]'
    ):

        with ui.row().classes(
            'items-center '
            'gap-2'
        ):

            ui.icon(icon).classes(
                'text-lg'
            )

            ui.label(
                label
            ).classes(
                'text-sm '
                'text-secondary-app'
            )

        ui.label(
            value
        ).classes(
            'text-xl '
            'font-bold '
            'text-primary-app'
        )

        badge(
            'Positive' if variant == 'success'
            else 'Current',
            variant=variant,
        )


# ==========================================================

# EMPTY STATE

# ==========================================================

def _empty_state(
message,
icon='info',
):

    with ui.element('div').classes(
        'w-full '
        'flex flex-col '
        'items-center '
        'justify-center '
        'rounded-xl '
        'bg-[var(--surface-soft)] '
        'border border-dashed border-gray-200 '
        'text-center '
        'gap-2 '
        'py-10'
    ):

        ui.icon(icon).classes(
            'text-4xl text-gray-300'
        )

        ui.label(
            message
        ).classes(
            'text-sm '
            'text-secondary-app'
        )


# ==========================================================

# HELPERS

# ==========================================================

def _to_float(value):


    if value is None:
        return 0.0

    try:
        return float(value)

    except (
        TypeError,
        ValueError,
    ):

        return 0.0


def _money(value):


    return f'${_to_float(value):,.2f}'


def _budget_variant(status):

    normalized = str(
        status or ''
    ).lower()

    if normalized == 'on track':
        return 'success'

    if normalized == 'near limit':
        return 'warning'

    if normalized == 'over budget':
        return 'danger'

    if normalized == 'no spending':
        return 'neutral'

    return 'info'


def _format_month(value):


    if value is None:
        return 'No month'

    try:
        return value.strftime(
            '%B %Y'
        )

    except AttributeError:
        return str(value)
