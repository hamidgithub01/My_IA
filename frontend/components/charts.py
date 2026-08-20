from nicegui import ui


def chart_container(
    *,
    title,
    subtitle=None,
    icon=None,
    action=None,
    height='320px',
):
    with ui.card().classes(
        'app-card w-full '
        'p-5 '
        'rounded-2xl '
        'border border-gray-200 '
        'shadow-sm '
        'bg-white'
    ):
        with ui.row().classes(
            'w-full items-start justify-between gap-4'
        ):
            with ui.row().classes(
                'items-start gap-3 min-w-0'
            ):
                if icon:
                    with ui.element('div').classes(
                        'app-icon w-10 h-10 shrink-0'
                    ):
                        ui.icon(icon).classes('text-xl')

                with ui.column().classes(
                    'gap-0 min-w-0'
                ):
                    ui.label(title).classes(
                        'text-base font-semibold '
                        'text-primary-app'
                    )

                    if subtitle:
                        ui.label(subtitle).classes(
                            'text-sm text-secondary-app mt-0.5'
                        )

            if action:
                action()

        with ui.element('div').classes(
            'w-full mt-5'
        ).style(
            f'height: {height};'
        ) as container:
            yield container


def empty_chart(
    *,
    title='No chart data available',
    subtitle='Data will appear here when available.',
    message=None,
    icon='show_chart',
    height='320px',
):
    if message is not None:
        subtitle = message

    with ui.element('div').classes(
        'w-full '
        'flex flex-col '
        'items-center '
        'justify-center '
        'rounded-xl '
        'bg-[var(--surface-soft)] '
        'border border-dashed border-gray-200 '
        'text-center '
        'gap-2'
    ).style(
        f'height: {height};'
    ):
        ui.icon(icon).classes(
            'text-4xl text-gray-300'
        )

        ui.label(title).classes(
            'text-sm font-medium text-secondary-app'
        )

        ui.label(subtitle).classes(
            'text-xs text-muted-app'
        )


def section_title(
    title,
    subtitle=None,
    *,
    icon=None,
):
    with ui.row().classes(
        'items-center gap-3'
    ):
        if icon:
            ui.icon(icon).classes(
                'text-xl text-primary'
            )

        with ui.column().classes(
            'gap-0'
        ):
            ui.label(title).classes(
                'text-lg font-semibold text-primary-app'
            )

            if subtitle:
                ui.label(subtitle).classes(
                    'text-sm text-secondary-app'
                )