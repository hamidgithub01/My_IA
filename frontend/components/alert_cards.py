from nicegui import ui


def alert_card(
    *,
    title,
    message,
    severity='info',
    timestamp=None,
    action_label=None,
    on_action=None,
):
    severity_config = {
        'info': {
            'icon': 'info',
            'container': 'bg-sky-50 border-sky-100',
            'icon_bg': 'bg-sky-100 text-sky-700',
            'title': 'text-sky-900',
            'text': 'text-sky-700',
        },
        'success': {
            'icon': 'check_circle',
            'container': 'bg-green-50 border-green-100',
            'icon_bg': 'bg-green-100 text-green-700',
            'title': 'text-green-900',
            'text': 'text-green-700',
        },
        'warning': {
            'icon': 'warning',
            'container': 'bg-amber-50 border-amber-100',
            'icon_bg': 'bg-amber-100 text-amber-700',
            'title': 'text-amber-900',
            'text': 'text-amber-700',
        },
        'danger': {
            'icon': 'error',
            'container': 'bg-red-50 border-red-100',
            'icon_bg': 'bg-red-100 text-red-700',
            'title': 'text-red-900',
            'text': 'text-red-700',
        },
    }

    config = severity_config.get(
        severity,
        severity_config['info'],
    )

    with ui.element('div').classes(
        'w-full '
        'rounded-xl '
        'border '
        'p-4 '
        f'{config["container"]}'
    ):
        with ui.row().classes(
            'w-full items-start gap-3'
        ):
            with ui.element('div').classes(
                f'w-9 h-9 shrink-0 '
                f'flex items-center justify-center '
                f'rounded-lg {config["icon_bg"]}'
            ):
                ui.icon(
                    config['icon']
                ).classes(
                    'text-lg'
                )

            with ui.column().classes(
                'flex-1 min-w-0 gap-1'
            ):
                ui.label(title).classes(
                    f'text-sm font-semibold '
                    f'{config["title"]}'
                )

                ui.label(message).classes(
                    f'text-sm {config["text"]}'
                )

                if timestamp:
                    ui.label(timestamp).classes(
                        'text-xs text-muted-app mt-1'
                    )

                if action_label:
                    ui.button(
                        action_label,
                        on_click=on_action,
                    ).props(
                        'flat no-caps'
                    ).classes(
                        'self-start mt-2 '
                        'px-0 text-sm font-semibold'
                    )


def recommendation_card(
    *,
    title,
    message,
    priority='medium',
    icon='lightbulb_outline',
    action_label=None,
    on_action=None,
):
    priority_config = {
        'low': {
            'badge': 'bg-gray-100 text-gray-600',
            'label': 'Low',
        },
        'medium': {
            'badge': 'bg-sky-50 text-sky-700',
            'label': 'Medium',
        },
        'high': {
            'badge': 'bg-amber-50 text-amber-700',
            'label': 'High',
        },
        'critical': {
            'badge': 'bg-red-50 text-red-700',
            'label': 'Critical',
        },
    }

    config = priority_config.get(
        priority,
        priority_config['medium'],
    )

    with ui.card().classes(
        'app-card w-full '
        'p-4 '
        'rounded-xl '
        'border border-gray-200 '
        'shadow-sm '
        'bg-white'
    ):
        with ui.row().classes(
            'w-full items-start gap-3'
        ):
            with ui.element('div').classes(
                'app-icon w-10 h-10 shrink-0'
            ):
                ui.icon(icon).classes(
                    'text-xl'
                )

            with ui.column().classes(
                'flex-1 min-w-0 gap-1'
            ):
                with ui.row().classes(
                    'items-center gap-2 flex-wrap'
                ):
                    ui.label(title).classes(
                        'text-sm font-semibold '
                        'text-primary-app'
                    )

                    ui.label(
                        config['label']
                    ).classes(
                        f'px-2 py-0.5 rounded-full '
                        f'text-[11px] font-medium '
                        f'{config["badge"]}'
                    )

                ui.label(message).classes(
                    'text-sm text-secondary-app'
                )

                if action_label:
                    ui.button(
                        action_label,
                        on_click=on_action,
                    ).props(
                        'flat no-caps'
                    ).classes(
                        'self-start mt-2 '
                        'px-0 text-sm font-semibold'
                    )


def alert_list(
    alerts,
    *,
    empty_title='No alerts',
    empty_message='There are no alerts to display.',
):
    with ui.column().classes(
        'w-full gap-3'
    ):
        if not alerts:
            with ui.element('div').classes(
                'empty-state'
            ):
                ui.icon(
                    'notifications_none'
                ).classes(
                    'empty-state-icon'
                )

                ui.label(
                    empty_title
                ).classes(
                    'text-sm font-semibold '
                    'text-primary-app'
                )

                ui.label(
                    empty_message
                ).classes(
                    'text-xs text-secondary-app'
                )

            return

        for alert in alerts:
            alert_card(
                title=alert.get('title', 'Alert'),
                message=alert.get('message', ''),
                severity=alert.get(
                    'severity',
                    'info',
                ),
                timestamp=alert.get(
                    'timestamp'
                ),
                action_label=alert.get(
                    'action_label'
                ),
            )


def recommendation_list(
    recommendations,
    *,
    empty_title='No recommendations',
    empty_message=(
        'Recommendations will appear when '
        'the system has enough data.'
    ),
):
    with ui.column().classes(
        'w-full gap-3'
    ):
        if not recommendations:
            with ui.element('div').classes(
                'empty-state'
            ):
                ui.icon(
                    'lightbulb_outline'
                ).classes(
                    'empty-state-icon'
                )

                ui.label(
                    empty_title
                ).classes(
                    'text-sm font-semibold '
                    'text-primary-app'
                )

                ui.label(
                    empty_message
                ).classes(
                    'text-xs text-secondary-app'
                )

            return

        for recommendation in recommendations:
            recommendation_card(
                title=recommendation.get(
                    'title',
                    'Recommendation',
                ),
                message=recommendation.get(
                    'message',
                    '',
                ),
                priority=recommendation.get(
                    'priority',
                    'medium',
                ),
                icon=recommendation.get(
                    'icon',
                    'lightbulb_outline',
                ),
                action_label=recommendation.get(
                    'action_label'
                ),
            )