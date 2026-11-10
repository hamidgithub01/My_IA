
from nicegui import ui

from frontend.services.alert_service import (
    load_alerts_page_data,
)


# ==========================================================
# DESIGN
# ==========================================================

COLORS = {
    'primary': '#2563EB',
    'success': '#16A34A',
    'warning': '#D97706',
    'danger': '#DC2626',
    'purple': '#7C3AED',
    'cyan': '#0891B2',
    'text': '#172033',
    'muted': '#64748B',
    'border': '#E2E8F0',
    'background': '#F8FAFC',
}


# ==========================================================
# FORMATTING
# ==========================================================

def _display(value, fallback='Not available'):
    if value is None or value == '':
        return fallback

    return str(value)


def _target_label(name):
    return (
        str(name or 'General')
        .replace('Target_', '')
        .replace('_', ' ')
        .strip()
    )


def _severity_color(severity):
    return {
        'critical': COLORS['danger'],
        'high': COLORS['danger'],
        'warning': COLORS['warning'],
        'medium': COLORS['warning'],
        'info': COLORS['cyan'],
        'low': COLORS['primary'],
    }.get(
        str(severity).lower(),
        COLORS['muted'],
    )


def _issue_source_label(source):
    labels = {
        'file_registry': 'Model Registry',
        'model_history': 'Model History Database',
        'evaluation_service': 'Evaluation Service',
    }

    return labels.get(
        source,
        _display(source),
    )


# ==========================================================
# SHARED UI COMPONENTS
# ==========================================================

def _section_title(title, subtitle=None, icon=None):
    with ui.row().classes('w-full items-center gap-3'):
        if icon:
            ui.icon(icon).style(
                f'font-size: 25px; color: {COLORS["primary"]};'
            )

        with ui.column().classes('gap-0'):
            ui.label(title).style(
                'font-size: 20px; font-weight: 750; '
                'color: #172033;'
            )

            if subtitle:
                ui.label(subtitle).style(
                    'font-size: 13px; color: #64748B;'
                )


def _stat_card(title, value, description, icon, color):
    with ui.card().classes('flex-1').style(
        'min-width: 185px; padding: 18px; '
        'border: 1px solid #E2E8F0; border-radius: 15px; '
        'box-shadow: 0 2px 8px rgba(15,23,42,0.04);'
    ):
        with ui.row().classes(
            'w-full items-center justify-between'
        ):
            ui.label(title).style(
                'font-size: 13px; color: #64748B; '
                'font-weight: 600;'
            )

            ui.icon(icon).style(
                f'font-size: 23px; color: {color};'
            )

        ui.label(str(value)).style(
            f'font-size: 30px; font-weight: 800; color: {color};'
        )

        ui.label(description).style(
            'font-size: 12px; color: #64748B;'
        )


def _notice(title, description, color, icon):
    with ui.card().classes('w-full').style(
        f'border: 1px solid {color}40; '
        f'border-left: 5px solid {color}; '
        'border-radius: 12px; padding: 14px; '
        'background: #FFFFFF; box-shadow: none;'
    ):
        with ui.row().classes('items-start gap-3'):
            ui.icon(icon).style(
                f'font-size: 25px; color: {color};'
            )

            with ui.column().classes('gap-1 flex-1'):
                ui.label(title).style(
                    f'font-weight: 750; color: {color}; '
                    'font-size: 14px;'
                )

                ui.label(description).style(
                    'font-size: 13px; color: #475569; '
                    'line-height: 1.6;'
                )


def _information_item(title, value):
    with ui.column().classes('gap-1'):
        ui.label(title).style(
            'font-size: 12px; color: #64748B;'
        )

        ui.label(
            _display(value)
        ).style(
            'font-size: 14px; font-weight: 650; '
            'color: #172033; overflow-wrap: anywhere;'
        )


# ==========================================================
# DEVELOPMENT DATA NOTICE
# ==========================================================

def _render_development_notice():
    _notice(
        'Development data environment',
        (
            'The current database contains synthetic and randomly '
            'generated data used for development and testing. '
            'Results based on this data do not establish real-user '
            'behavior or real-world model performance. '
            'The application is being prepared for training and '
            'analysis using real user data.'
        ),
        COLORS['warning'],
        'science',
    )


# ==========================================================
# OVERVIEW
# ==========================================================

def _render_overview(data):
    _section_title(
        'System Overview',
        'A summary of current evaluation issues and available records.',
        'dashboard',
    )

    overview = data.get('overview') or {}

    if not isinstance(overview, dict):
        overview = {}

    with ui.row().classes('w-full flex-wrap gap-3'):
        _stat_card(
            'Active Alerts',
            data.get('alert_count', 0),
            'Issues requiring attention',
            'notifications_active',
            COLORS['danger'] if data.get('alert_count', 0) else COLORS['success'],
        )

        _stat_card(
            'Recommendations',
            data.get('recommendation_count', 0),
            'Suggested actions',
            'lightbulb',
            COLORS['primary'],
        )

        _stat_card(
            'Registered Versions',
            data.get('registry_version_count', 0),
            'Versions stored in Model Registry',
            'inventory_2',
            COLORS['purple'],
        )

        _stat_card(
            'Evaluation Records',
            data.get('evaluation_record_count', 0),
            'Registry and historical records',
            'fact_check',
            COLORS['cyan'],
        )

    with ui.row().classes('w-full flex-wrap gap-3'):
        _stat_card(
            'Missing Metrics',
            overview.get('versions_without_evaluation', 0),
            'Versions without recorded evaluation',
            'query_stats',
            COLORS['warning'],
        )

        _stat_card(
            'Unknown Validity',
            overview.get('unknown_evaluations', 0),
            'Evaluation validity not confirmed',
            'help_outline',
            COLORS['warning'],
        )

        _stat_card(
            'Historical Records',
            data.get('legacy_history_record_count', 0),
            'Records from previous history',
            'history',
            COLORS['purple'],
        )


# ==========================================================
# ALERTS
# ==========================================================

def _render_alert(alert):
    if not isinstance(alert, dict):
        return

    severity = alert.get('severity', 'info')
    color = _severity_color(severity)

    title = _display(
        alert.get('title'),
        'System alert',
    )

    message = _display(
        alert.get('message'),
        'No additional information is available.',
    )

    with ui.card().classes('w-full').style(
        f'border: 1px solid {color}35; '
        f'border-left: 5px solid {color}; '
        'border-radius: 13px; padding: 17px; '
        'box-shadow: 0 2px 8px rgba(15,23,42,0.035);'
    ):
        with ui.row().classes(
            'w-full items-start justify-between gap-3'
        ):
            with ui.row().classes('items-center gap-2'):
                ui.icon('warning_amber').style(
                    f'font-size: 22px; color: {color};'
                )

                ui.label(title).style(
                    'font-size: 15px; font-weight: 750; '
                    'color: #172033;'
                )

            ui.label(
                str(severity).replace('_', ' ').upper()
            ).style(
                f'font-size: 10px; font-weight: 800; '
                f'color: {color}; background: {color}15; '
                'padding: 5px 9px; border-radius: 20px;'
            )

        ui.label(message).style(
            'font-size: 13px; color: #475569; '
            'line-height: 1.7;'
        )

        ui.separator().style(
            'background: #E2E8F0;'
        )

        target_name = alert.get('target_name')
        version = alert.get('version')
        source = alert.get('source')

        with ui.row().classes('w-full flex-wrap gap-5'):
            if target_name:
                _information_item(
                    'Prediction Task',
                    _target_label(target_name),
                )

            if version:
                _information_item(
                    'Model Version',
                    version,
                )

            _information_item(
                'Source',
                _issue_source_label(source),
            )


def _render_alerts(alerts):
    _section_title(
        'System Alerts',
        'Issues detected in available evaluation and registry records.',
        'notifications_active',
    )

    if not alerts:
        _notice(
            'No active alerts',
            (
                'No issues were detected in the available records. '
                'This does not necessarily mean that all models '
                'have confirmed evaluation validity.'
            ),
            COLORS['success'],
            'check_circle',
        )
        return

    for alert in alerts:
        _render_alert(alert)


# ==========================================================
# RECOMMENDATIONS
# ==========================================================

def _render_recommendation(recommendation):
    if not isinstance(recommendation, dict):
        return

    priority = recommendation.get(
        'priority',
        'medium',
    )

    color = _severity_color(priority)

    with ui.card().classes('w-full').style(
        'border: 1px solid #E2E8F0; '
        'border-radius: 13px; padding: 17px; '
        'box-shadow: 0 2px 8px rgba(15,23,42,0.035);'
    ):
        with ui.row().classes(
            'w-full items-start justify-between gap-3'
        ):
            with ui.row().classes('items-center gap-2'):
                ui.icon('lightbulb').style(
                    f'font-size: 23px; color: {COLORS["primary"]};'
                )

                ui.label(
                    _display(
                        recommendation.get('title'),
                        'Suggested action',
                    )
                ).style(
                    'font-size: 15px; font-weight: 750; '
                    'color: #172033;'
                )

            ui.label(
                str(priority).upper()
            ).style(
                f'font-size: 10px; font-weight: 800; '
                f'color: {color}; background: {color}15; '
                'padding: 5px 9px; border-radius: 20px;'
            )

        ui.label(
            _display(
                recommendation.get('message'),
                'No additional information is available.',
            )
        ).style(
            'font-size: 13px; color: #475569; '
            'line-height: 1.7;'
        )

        target_name = recommendation.get('target_name')
        version = recommendation.get('version')

        if target_name or version:
            ui.separator().style(
                'background: #E2E8F0;'
            )

            with ui.row().classes('w-full flex-wrap gap-5'):
                if target_name:
                    _information_item(
                        'Prediction Task',
                        _target_label(target_name),
                    )

                if version:
                    _information_item(
                        'Model Version',
                        version,
                    )

        ui.label(
            'Suggested action only — no operation has been executed.'
        ).style(
            'font-size: 11px; color: #64748B; '
            'font-style: italic;'
        )


def _render_recommendations(recommendations):
    _section_title(
        'Recommendations',
        'Suggested actions based on detected system issues.',
        'lightbulb',
    )

    if not recommendations:
        _notice(
            'No recommendations available',
            (
                'There are currently no suggested actions '
                'based on the available records.'
            ),
            COLORS['cyan'],
            'info',
        )
        return

    for recommendation in recommendations:
        _render_recommendation(recommendation)


# ==========================================================
# INFORMATION
# ==========================================================

def _render_information(information):
    _section_title(
        'Additional Information',
        'Important statuses that should not automatically be treated as errors.',
        'info',
    )

    if not information:
        _notice(
            'No additional information',
            'There are no additional status messages to display.',
            COLORS['cyan'],
            'info',
        )
        return

    for item in information:
        if not isinstance(item, dict):
            continue

        with ui.card().classes('w-full').style(
            'border: 1px solid #BAE6FD; '
            'border-left: 5px solid #0891B2; '
            'border-radius: 12px; padding: 16px; '
            'box-shadow: none;'
        ):
            ui.label(
                _display(
                    item.get('title'),
                    'Information',
                )
            ).style(
                'font-size: 15px; font-weight: 750; '
                'color: #0E7490;'
            )

            ui.label(
                _display(item.get('message'))
            ).style(
                'font-size: 13px; color: #475569; '
                'line-height: 1.7;'
            )

            if item.get('count') is not None:
                ui.label(
                    f'Affected records: {item["count"]}'
                ).style(
                    'font-size: 12px; font-weight: 700; '
                    'color: #0E7490;'
                )


# ==========================================================
# MONITORING STATUS
# ==========================================================

def _render_monitoring_status(status):
    _section_title(
        'Prediction Monitoring',
        'Tracking predictions against their actual outcomes.',
        'monitor_heart',
    )

    if status == 'connected':
        _notice(
            'Prediction monitoring is connected',
            (
                'The monitoring service is connected. '
                'Available monitoring results can be reviewed here.'
            ),
            COLORS['success'],
            'check_circle',
        )

    else:
        _notice(
            'Production monitoring is not connected',
            (
                'The application is not currently receiving connected '
                'prediction monitoring results. Actual prediction errors '
                'and reliability changes cannot yet be reported here.'
            ),
            COLORS['warning'],
            'info',
        )


# ==========================================================
# SOURCE ERRORS
# ==========================================================

def _render_source_errors(errors):
    if not isinstance(errors, list) or not errors:
        return

    with ui.expansion(
        f'Data source details ({len(errors)})',
        icon='database',
    ).classes('w-full'):
        ui.label(
            'Technical details about data sources that could not be loaded.'
        ).style(
            'font-size: 12px; color: #64748B;'
        )

        for error in errors:
            if not isinstance(error, dict):
                continue

            with ui.card().classes('w-full').style(
                'background: #F8FAFC; '
                'border: 1px solid #E2E8F0; '
                'border-radius: 10px; padding: 12px; '
                'box-shadow: none;'
            ):
                ui.label(
                    _issue_source_label(
                        error.get('source')
                    )
                ).style(
                    'font-size: 13px; font-weight: 750; '
                    'color: #172033;'
                )

                ui.label(
                    _display(error.get('message'))
                ).style(
                    'font-size: 12px; color: #64748B; '
                    'overflow-wrap: anywhere;'
                )


# ==========================================================
# PAGE
# ==========================================================

def alerts_page():
    ui.label('Alerts & Recommendations').style(
        'font-size: 28px; font-weight: 850; color: #172033;'
    )

    ui.label(
        'Understand system issues, review suggested actions, '
        'and monitor the status of your prediction models.'
    ).style(
        'font-size: 14px; color: #64748B; line-height: 1.7;'
    )

    # ------------------------------------------------------
    # Development data context
    # ------------------------------------------------------

    _render_development_notice()

    # ------------------------------------------------------
    # Load page data
    # ------------------------------------------------------

    try:
        data = load_alerts_page_data()

    except Exception:
        _notice(
            'Unable to load alerts',
            (
                'The system could not retrieve alert information. '
                'Please try again later.'
            ),
            COLORS['danger'],
            'error',
        )
        return

    if not isinstance(data, dict):
        _notice(
            'Invalid response',
            'The alert service returned an unexpected result.',
            COLORS['danger'],
            'error',
        )
        return

    status = data.get('status')

    if status == 'source_error':
        _notice(
            'Alert information is unavailable',
            (
                'The system could not retrieve the required evaluation '
                'information. Check the available data sources.'
            ),
            COLORS['danger'],
            'error',
        )

        _render_source_errors(
            data.get('source_errors', [])
        )

        return

    alerts = data.get('alerts') or []
    recommendations = data.get('recommendations') or []
    information = data.get('information') or []

    if not isinstance(alerts, list):
        alerts = []

    if not isinstance(recommendations, list):
        recommendations = []

    if not isinstance(information, list):
        information = []

    ui.separator()

    # ------------------------------------------------------
    # Overview
    # ------------------------------------------------------

    _render_overview(data)

    ui.separator()

    # ------------------------------------------------------
    # Alerts
    # ------------------------------------------------------

    _render_alerts(alerts)

    ui.separator()

    # ------------------------------------------------------
    # Recommendations
    # ------------------------------------------------------

    _render_recommendations(recommendations)

    ui.separator()

    # ------------------------------------------------------
    # Additional information
    # ------------------------------------------------------

    _render_information(information)

    ui.separator()

    # ------------------------------------------------------
    # Prediction monitoring
    # ------------------------------------------------------

    _render_monitoring_status(
        data.get('monitoring_status')
    )

    # ------------------------------------------------------
    # Source details
    # ------------------------------------------------------

    _render_source_errors(
        data.get('source_errors', [])
    )
