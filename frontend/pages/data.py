

from nicegui import ui

from frontend.components import (
    app_card,
    metric_card,
    section_title,
    badge,
    empty_chart,
)
from frontend.services.data_service import load_data_page_data


# ==========================================================
# DATA PAGE
# ==========================================================

def data_page():

    @ui.refreshable
    def render_page():
        try:
            data = load_data_page_data()
            error_message = None
        except Exception as exc:
            data = None
            error_message = str(exc)

        with ui.column().classes('w-full min-w-0 gap-6'):
            _page_header(render_page.refresh)

            if data is None:
                with app_card(
                    title='Data unavailable',
                    subtitle='The database counts could not be loaded',
                    icon='database',
                ):
                    ui.label(
                        'Check the database connection, then use Refresh.'
                    ).classes('text-sm text-secondary-app')

                    ui.label(error_message or 'Unknown error').classes(
                        'text-xs text-secondary-app'
                    )
            else:
                _overview_section(data)
                _data_sources_section(data)

            _data_quality_section()
            _activity_section()

    render_page()


# ==========================================================
# PAGE HEADER
# ==========================================================

def _page_header(on_refresh):

    with ui.row().classes(
        'w-full items-start justify-between gap-4 flex-wrap'
    ):
        with ui.column().classes('gap-1 min-w-0'):
            ui.label('Data').classes(
                'text-2xl md:text-3xl font-bold text-primary-app'
            )

            ui.label(
                'Your personal data foundation for analysis and AI.'
            ).classes('text-sm text-secondary-app')

        with ui.row().classes('items-center gap-2 flex-wrap'):
            badge(
                'Connected',
                variant='success',
                icon='database',
            )

            ui.button(
                'Refresh',
                icon='refresh',
                on_click=on_refresh,
            ).props('unelevated no-caps').classes('app-button')


# ==========================================================
# OVERVIEW
# ==========================================================

def _overview_section(data):

    with ui.column().classes('w-full gap-3'):
        section_title(
            'Data Overview',
            'Current information available to the system',
        )

        with ui.element('div').classes(
            'grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 '
            'gap-4 w-full'
        ):
            metric_card(
                title='Total Records',
                value=str(data['total_records']),
                subtitle='All recorded data',
                icon='dataset',
            )

            metric_card(
                title='Expenses',
                value=str(data['expenses']),
                subtitle='Expense records',
                icon='payments',
            )

            metric_card(
                title='Income',
                value=str(data['income']),
                subtitle='Income records',
                icon='account_balance',
            )

            metric_card(
                title='Last Update',
                value='—',
                subtitle='Update timestamp not available',
                icon='update',
            )


# ==========================================================
# DATA SOURCES
# ==========================================================

def _data_sources_section(data):

    counts = data['table_counts']

    # These tables do not have separate cards in the current design.
    context_tables = (
        'settings',
        'activities',
        'goals',
        'model_history',
        'plans',
        'prediction_feedback',
        'recurring',
        'travel',
    )

    context_count = sum(
        counts.get(table, 0)
        for table in context_tables
    )

    with ui.column().classes('w-full gap-3'):
        section_title(
            'Data Sources',
            'Personal information available to the intelligence system',
        )

        with ui.element('div').classes(
            'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 '
            'xl:grid-cols-4 gap-4 w-full'
        ):
            _source_card(
                'Expenses',
                'Financial spending records',
                'payments',
                counts.get('expenses', 0),
            )

            _source_card(
                'Income',
                'Income and earnings records',
                'account_balance',
                counts.get('income', 0),
            )

            _source_card(
                'Days',
                'Daily life and activity data',
                'today',
                counts.get('days', 0),
            )

            _source_card(
                'Events',
                'Important events and context',
                'event',
                counts.get('events', 0),
            )

            _source_card(
                'Health',
                'Health-related personal data',
                'favorite',
                counts.get('health_records', 0),
            )

            _source_card(
                'Sleep',
                'Sleep and recovery information',
                'bedtime',
                counts.get('sleep', 0),
            )

            _source_card(
                'Budgets',
                'Financial planning information',
                'account_balance_wallet',
                counts.get('budgets', 0),
            )

            _source_card(
                'Context',
                'Other context and system records (8 tables)',
                'psychology',
                context_count,
            )


# ==========================================================
# SOURCE CARD
# ==========================================================

def _source_card(title, description, icon, count):

    with ui.card().classes('app-card w-full min-w-0 p-4'):
        with ui.row().classes('w-full items-center gap-3'):
            with ui.element('div').classes(
                'app-icon w-10 h-10 shrink-0'
            ):
                ui.icon(icon).classes('text-xl')

            with ui.column().classes('gap-0 min-w-0 flex-1'):
                ui.label(title).classes(
                    'text-sm font-semibold text-primary-app'
                )

                ui.label(description).classes(
                    'text-xs text-secondary-app'
                )

        with ui.row().classes(
            'w-full items-center justify-between mt-4'
        ):
            ui.label('Records').classes('text-xs text-muted-app')

            badge(
                str(count),
                variant='neutral',
            )


# ==========================================================
# DATA QUALITY
# ==========================================================

def _data_quality_section():

    with app_card(
        title='Data Quality',
        subtitle='Readiness of the available data',
        icon='verified',
    ):
        with ui.element('div').classes(
            'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 '
            'gap-4 w-full'
        ):
            _quality_item(
                'Data Status',
                'Waiting for data',
                'neutral',
            )

            _quality_item(
                'Completeness',
                '—',
                'neutral',
            )

            _quality_item(
                'Consistency',
                '—',
                'neutral',
            )

            _quality_item(
                'AI Readiness',
                'Not ready',
                'neutral',
            )


# ==========================================================
# QUALITY ITEM
# ==========================================================

def _quality_item(label, value, variant='neutral'):

    with ui.column().classes('gap-1 min-w-0'):
        ui.label(label).classes(
            'text-xs text-secondary-app'
        )

        badge(
            value,
            variant=variant,
        )


# ==========================================================
# ACTIVITY
# ==========================================================

def _activity_section():

    with ui.column().classes('w-full gap-3'):
        section_title(
            'Data Activity',
            'Recent changes and incoming information',
        )

        with app_card(
            title='Recent Data',
            subtitle='Latest records added to the system',
            icon='history',
        ):
            empty_chart(
                title='No data available',
                message=(
                    'Records will appear here automatically '
                    'when real data is added to the database.'
                ),
                icon='database',
                height='260px',
            )
