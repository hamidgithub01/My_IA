from nicegui import ui


def prediction_card(
    *,
    title,
    date=None,
    value='—',
    subtitle=None,
    description=None,
    confidence=None,
    status=None,
    icon='auto_awesome',
):
    with ui.card().classes(
        'app-card w-full '
        'p-4 '
        'rounded-xl '
        'border border-gray-200 '
        'shadow-sm '
        'bg-white'
    ):
        with ui.row().classes(
            'w-full items-start justify-between gap-3'
        ):
            with ui.row().classes(
                'items-center gap-3 min-w-0'
            ):
                with ui.element('div').classes(
                    'app-icon w-9 h-9 shrink-0'
                ):
                    ui.icon(icon).classes(
                        'text-lg'
                    )

                with ui.column().classes(
                    'gap-0 min-w-0'
                ):
                    ui.label(title).classes(
                        'text-sm font-semibold '
                        'text-primary-app truncate'
                    )

                    if date:
                        ui.label(date).classes(
                            'text-xs text-muted-app'
                        )

            if status:
                _status_badge(status)

        ui.separator().classes(
            'my-3'
        )

        with ui.column().classes(
            'gap-1'
        ):
            ui.label(value).classes(
                'text-xl font-bold text-primary-app'
            )

            if description is not None:
                subtitle = description

            if subtitle:
                ui.label(subtitle).classes(
                    'text-xs text-secondary-app'
                )

        if confidence is not None:
            with ui.column().classes(
                'gap-1 mt-4'
            ):
                with ui.row().classes(
                    'w-full items-center justify-between'
                ):
                    ui.label(
                        'Confidence'
                    ).classes(
                        'text-xs text-muted-app'
                    )

                    ui.label(
                        f'{confidence}%'
                    ).classes(
                        'text-xs font-semibold text-secondary-app'
                    )

                ui.linear_progress(
                    value=max(
                        0,
                        min(
                            1,
                            confidence / 100,
                        ),
                    ),
                ).props(
                    'rounded'
                ).classes(
                    'w-full'
                )


def compact_prediction_card(
    *,
    label,
    value='—',
    date=None,
    icon='auto_awesome',
):
    with ui.card().classes(
        'w-full '
        'p-3 '
        'rounded-xl '
        'border border-gray-200 '
        'shadow-none '
        'bg-white'
    ):
        with ui.row().classes(
            'w-full items-center gap-3'
        ):
            with ui.element('div').classes(
                'app-icon w-8 h-8 shrink-0'
            ):
                ui.icon(icon).classes(
                    'text-base'
                )

            with ui.column().classes(
                'gap-0 min-w-0 flex-1'
            ):
                ui.label(label).classes(
                    'text-xs font-medium '
                    'text-secondary-app '
                    'truncate'
                )

                if date:
                    ui.label(date).classes(
                        'text-[11px] text-muted-app'
                    )

            ui.label(value).classes(
                'text-sm font-bold '
                'text-primary-app'
            )


def prediction_summary(
    *,
    title='Prediction Summary',
    description=None,
    predicted_value='—',
    value=None,
    confidence=None,
    horizon=None,
):
    if value is not None:
        predicted_value = value

    with ui.card().classes(
        'app-card w-full '
        'p-5 '
        'rounded-2xl '
        'border border-gray-200 '
        'shadow-sm '
        'bg-white'
    ):
        with ui.row().classes(
            'items-center gap-3'
        ):
            with ui.element('div').classes(
                'app-icon w-10 h-10'
            ):
                ui.icon(
                    'auto_awesome'
                ).classes(
                    'text-xl'
                )

            with ui.column().classes(
                'gap-0'
            ):
                ui.label(title).classes(
                    'text-base font-semibold '
                    'text-primary-app'
                )

                if description:
                    ui.label(description).classes(
                        'text-sm text-secondary-app'
                    )

        with ui.row().classes(
            'w-full flex-wrap gap-6 mt-5'
        ):
            _summary_metric(
                'Predicted',
                predicted_value,
            )

            if confidence is not None:
                _summary_metric(
                    'Confidence',
                    f'{confidence}%',
                )

            if horizon:
                _summary_metric(
                    'Horizon',
                    horizon,
                )


def _summary_metric(
    label,
    value,
):
    with ui.column().classes(
        'gap-0'
    ):
        ui.label(label).classes(
            'text-xs text-muted-app'
        )

        ui.label(value).classes(
            'text-lg font-bold '
            'text-primary-app'
        )


def _status_badge(status):
    normalized = str(status).lower()

    variants = {
        'available': (
            'bg-green-50 text-green-700',
            'check_circle',
        ),
        'active': (
            'bg-green-50 text-green-700',
            'check_circle',
        ),
        'reliable': (
            'bg-green-50 text-green-700',
            'verified',
        ),
        'pending': (
            'bg-amber-50 text-amber-700',
            'schedule',
        ),
        'warning': (
            'bg-amber-50 text-amber-700',
            'warning',
        ),
        'unavailable': (
            'bg-gray-100 text-gray-600',
            'remove_circle_outline',
        ),
        'error': (
            'bg-red-50 text-red-700',
            'error_outline',
        ),
    }

    classes, icon = variants.get(
        normalized,
        (
            'bg-gray-100 text-gray-600',
            'info_outline',
        ),
    )

    with ui.row().classes(
        f'items-center gap-1.5 '
        f'px-2 py-1 rounded-full '
        f'text-[11px] font-medium {classes}'
    ):
        ui.icon(icon).classes(
            'text-xs'
        )

        ui.label(status)