from nicegui import ui

from frontend.components import (
    app_card,
    metric_card,
    section_title,
    badge,
)


# ==========================================================
# REPORTS PAGE
# ==========================================================

def reports_page():

    with ui.column().classes(
        'w-full '
        'min-w-0 '
        'gap-6'
    ):

        _page_header()

        _report_overview()

        _financial_report()

        _behavior_report()

        _life_report()

        _report_actions()


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
                'Reports'
            ).classes(
                'text-2xl '
                'md:text-3xl '
                'font-bold '
                'text-primary-app'
            )

            ui.label(
                'A complete view of your financial activity, behavior, progress, and personal trends.'
            ).classes(
                'text-sm '
                'text-secondary-app'
            )

        with ui.row().classes(
            'items-center '
            'gap-2 '
            'flex-wrap'
        ):

            badge(
                'Reports Ready',
                variant='success',
                icon='description',
            )

            ui.button(
                'Refresh',
                icon='refresh',
            ).props(
                'unelevated no-caps'
            ).classes(
                'app-button'
            )


# ==========================================================
# REPORT OVERVIEW
# ==========================================================

def _report_overview():

    with ui.column().classes(
        'w-full '
        'gap-3'
    ):

        section_title(
            'Report Overview',
            'High-level indicators collected from the available personal data.',
            icon='analytics',
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
                title='Financial Report',
                value='Ready',
                subtitle='Income, expenses and budgets',
                icon='account_balance',
            )

            metric_card(
                title='Behavior Report',
                value='Ready',
                subtitle='Patterns and behavioral trends',
                icon='psychology',
            )

            metric_card(
                title='Life Report',
                value='Ready',
                subtitle='Daily life and context',
                icon='calendar_month',
            )

            metric_card(
                title='Insights',
                value='Ready',
                subtitle='Cross-domain interpretation',
                icon='auto_awesome',
            )


# ==========================================================
# FINANCIAL REPORT
# ==========================================================

def _financial_report():

    with ui.column().classes(
        'w-full '
        'gap-3'
    ):

        section_title(
            'Financial Report',
            'A structured summary of financial activity and financial health.',
            icon='account_balance',
        )

        with ui.element('div').classes(
            'grid '
            'grid-cols-1 '
            'xl:grid-cols-3 '
            'gap-4 '
            'w-full'
        ):

            with app_card(
                title='Financial Summary',
                subtitle='Key financial indicators',
                icon='payments',
                classes='xl:col-span-2',
            ):

                _empty_report(
                    title='Financial report will appear here',
                    message=(
                        'Once real financial data is available, this section '
                        'will summarize income, expenses, savings, budgets, '
                        'and important financial changes.'
                    ),
                    icon='account_balance',
                )

            with app_card(
                title='Financial Health',
                subtitle='Overall financial position',
                icon='health_and_safety',
            ):

                _report_status(
                    'Financial health',
                    'Awaiting real data',
                    'info',
                )

                ui.separator().classes(
                    'my-4'
                )

                _report_item(
                    'Income',
                    'Not calculated',
                )

                _report_item(
                    'Expenses',
                    'Not calculated',
                )

                _report_item(
                    'Savings',
                    'Not calculated',
                )

                _report_item(
                    'Budget usage',
                    'Not calculated',
                )


# ==========================================================
# BEHAVIOR REPORT
# ==========================================================

def _behavior_report():

    with app_card(
        title='Behavior & Pattern Report',
        subtitle='Understanding recurring behavior, changes, and emerging patterns.',
        icon='psychology',
    ):

        with ui.element('div').classes(
            'grid '
            'grid-cols-1 '
            'md:grid-cols-3 '
            'gap-4 '
            'w-full'
        ):

            _report_domain(
                'Recurring Patterns',
                'Repeated behaviors detected across your history.',
                'repeat',
            )

            _report_domain(
                'Behavior Changes',
                'Important changes compared with previous periods.',
                'trending_up',
            )

            _report_domain(
                'Anomalies',
                'Unusual events or deviations that deserve attention.',
                'warning',
            )


# ==========================================================
# LIFE REPORT
# ==========================================================

def _life_report():

    with ui.column().classes(
        'w-full '
        'gap-3'
    ):

        section_title(
            'Life & Context Report',
            'A broader view that goes beyond money.',
            icon='hub',
        )

        with ui.element('div').classes(
            'grid '
            'grid-cols-1 '
            'sm:grid-cols-2 '
            'xl:grid-cols-4 '
            'gap-4 '
            'w-full'
        ):

            _life_domain(
                'Daily Life',
                'Daily activity and routine patterns.',
                'today',
            )

            _life_domain(
                'Health',
                'Health-related trends from available records.',
                'favorite',
            )

            _life_domain(
                'Sleep',
                'Sleep patterns and changes over time.',
                'bedtime',
            )

            _life_domain(
                'Goals',
                'Progress toward personal targets and objectives.',
                'track_changes',
            )


# ==========================================================
# REPORT ACTIONS
# ==========================================================

def _report_actions():

    with app_card(
        title='Report Actions',
        subtitle='Generate, review, or export future reports.',
        icon='description',
    ):

        with ui.row().classes(
            'w-full '
            'items-center '
            'gap-3 '
            'flex-wrap'
        ):

            ui.button(
                'Generate Report',
                icon='auto_awesome',
            ).props(
                'unelevated no-caps'
            ).classes(
                'app-button'
            )

            ui.button(
                'Export Report',
                icon='download',
            ).props(
                'flat no-caps'
            ).classes(
                'text-primary'
            )

            ui.button(
                'Report History',
                icon='history',
            ).props(
                'flat no-caps'
            ).classes(
                'text-primary'
            )


# ==========================================================
# EMPTY REPORT
# ==========================================================

def _empty_report(
    title,
    message,
    icon,
):

    with ui.column().classes(
        'w-full '
        'min-h-56 '
        'items-center '
        'justify-center '
        'text-center '
        'p-6 '
        'gap-2'
    ):

        with ui.element('div').classes(
            'app-icon '
            'w-14 '
            'h-14'
        ):

            ui.icon(
                icon
            ).classes(
                'text-2xl'
            )

        ui.label(
            title
        ).classes(
            'text-sm '
            'font-semibold '
            'text-primary-app '
            'mt-2'
        )

        ui.label(
            message
        ).classes(
            'text-xs '
            'text-secondary-app '
            'max-w-xl '
            'leading-5'
        )


# ==========================================================
# REPORT STATUS
# ==========================================================

def _report_status(
    label,
    value,
    variant='neutral',
):

    with ui.row().classes(
        'w-full '
        'items-center '
        'justify-between '
        'gap-3'
    ):

        ui.label(
            label
        ).classes(
            'text-sm '
            'text-secondary-app'
        )

        badge(
            value,
            variant=variant,
        )


# ==========================================================
# REPORT ITEM
# ==========================================================

def _report_item(
    label,
    value,
):

    with ui.row().classes(
        'w-full '
        'items-center '
        'justify-between '
        'gap-3 '
        'py-1'
    ):

        ui.label(
            label
        ).classes(
            'text-sm '
            'text-secondary-app'
        )

        ui.label(
            value
        ).classes(
            'text-xs '
            'font-medium '
            'text-muted-app'
        )


# ==========================================================
# REPORT DOMAIN
# ==========================================================

def _report_domain(
    title,
    description,
    icon,
):

    with ui.column().classes(
        'gap-3 '
        'p-4 '
        'rounded-xl '
        'bg-[var(--surface-soft)] '
        'min-h-36'
    ):

        with ui.element('div').classes(
            'app-icon '
            'w-10 '
            'h-10'
        ):

            ui.icon(
                icon
            ).classes(
                'text-xl'
            )

        ui.label(
            title
        ).classes(
            'text-sm '
            'font-semibold '
            'text-primary-app'
        )

        ui.label(
            description
        ).classes(
            'text-xs '
            'leading-5 '
            'text-secondary-app'
        )


# ==========================================================
# LIFE DOMAIN
# ==========================================================

def _life_domain(
    title,
    description,
    icon,
):

    with ui.card().classes(
        'app-card '
        'w-full '
        'min-w-0 '
        'p-5 '
        'rounded-2xl '
        'border '
        'border-gray-200 '
        'shadow-sm '
        'bg-white'
    ):

        with ui.row().classes(
            'items-start '
            'gap-3'
        ):

            with ui.element('div').classes(
                'app-icon '
                'w-10 '
                'h-10 '
                'shrink-0'
            ):

                ui.icon(
                    icon
                ).classes(
                    'text-xl'
                )

            with ui.column().classes(
                'gap-1 '
                'min-w-0'
            ):

                ui.label(
                    title
                ).classes(
                    'text-sm '
                    'font-semibold '
                    'text-primary-app'
                )

                ui.label(
                    description
                ).classes(
                    'text-xs '
                    'leading-5 '
                    'text-secondary-app'
                )

        ui.separator().classes(
            'my-3'
        )

        badge(
            'Awaiting data',
            variant='neutral',
        )