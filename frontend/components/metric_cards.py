from nicegui import ui


# ==========================================================
# METRIC CARD
# ==========================================================

def metric_card(
    title,
    value,
    subtitle=None,
    icon=None,
    status=None,
    trend=None,
    trend_direction='neutral',
    action_label=None,
    action=None,
    classes='',
):
    """
    Reusable metric card.

    Supports:
        title
        value
        subtitle
        icon
        status
        trend
        trend_direction
        action_label
        action
    """

    with ui.card().classes(
        'app-card '
        'w-full '
        'min-w-0 '
        + classes
    ):

        with ui.row().classes(
            'w-full '
            'items-start '
            'justify-between '
            'gap-4'
        ):

            with ui.column().classes(
                'gap-1 '
                'min-w-0'
            ):

                ui.label(
                    title
                ).classes(
                    'text-sm '
                    'font-medium '
                    'text-secondary-app'
                )

                ui.label(
                    value
                ).classes(
                    'text-2xl '
                    'font-bold '
                    'text-primary-app'
                )

                if subtitle:

                    ui.label(
                        subtitle
                    ).classes(
                        'text-xs '
                        'text-muted-app'
                    )

            if icon:

                with ui.element('div').classes(
                    'app-icon '
                    'shrink-0'
                ):

                    ui.icon(
                        icon
                    ).classes(
                        'text-xl'
                    )

        # ==================================================
        # STATUS / TREND
        # ==================================================

        if status or trend:

            with ui.row().classes(
                'w-full '
                'items-center '
                'justify-between '
                'gap-2 '
                'mt-4'
            ):

                if status:

                    _render_status(
                        status
                    )

                if trend:

                    _render_trend(
                        trend,
                        trend_direction,
                    )

        # ==================================================
        # ACTION
        # ==================================================

        if action_label:

            ui.button(
                action_label,
                on_click=action,
            ).props(
                'flat no-caps'
            ).classes(
                'text-sm '
                'text-primary '
                'mt-3'
            )


# ==========================================================
# STATUS
# ==========================================================

def _render_status(
    status,
):

    status_config = {
        'available': (
            'Available',
            'success',
        ),
        'reliable': (
            'Reliable',
            'success',
        ),
        'pending': (
            'Pending',
            'warning',
        ),
        'processing': (
            'Processing',
            'info',
        ),
        'monitoring': (
            'Monitoring',
            'info',
        ),
        'unavailable': (
            'Unavailable',
            'danger',
        ),
    }

    label, status_type = status_config.get(
        str(status).lower(),
        (
            str(status),
            'neutral',
        ),
    )

    background = {
        'success': 'bg-green-50 text-green-700',
        'warning': 'bg-amber-50 text-amber-700',
        'danger': 'bg-red-50 text-red-700',
        'info': 'bg-sky-50 text-sky-700',
        'neutral': 'bg-gray-100 text-gray-600',
    }.get(
        status_type,
        'bg-gray-100 text-gray-600',
    )

    with ui.row().classes(
        'inline-flex '
        'items-center '
        'gap-1.5 '
        'px-2.5 '
        'py-1 '
        'rounded-full '
        'text-xs '
        'font-medium '
        + background
    ):

        ui.label(
            label
        ).classes(
            'text-xs '
            'font-medium'
        )


# ==========================================================
# TREND
# ==========================================================

def _render_trend(
    value,
    direction='neutral',
):

    config = {
        'up': {
            'icon': 'trending_up',
            'classes': 'bg-green-50 text-green-700',
        },
        'down': {
            'icon': 'trending_down',
            'classes': 'bg-red-50 text-red-700',
        },
        'neutral': {
            'icon': 'trending_flat',
            'classes': 'bg-gray-100 text-gray-600',
        },
    }

    selected = config.get(
        str(direction).lower(),
        config['neutral'],
    )

    with ui.row().classes(
        'inline-flex '
        'items-center '
        'gap-1.5 '
        'px-2.5 '
        'py-1 '
        'rounded-full '
        'text-xs '
        'font-medium '
        + selected['classes']
    ):

        ui.icon(
            selected['icon']
        ).classes(
            'text-sm'
        )

        ui.label(
            value
        ).classes(
            'text-xs '
            'font-medium'
        )