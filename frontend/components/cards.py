from contextlib import contextmanager

from nicegui import ui


# ==========================================================
# BASE CARD
# ==========================================================

@contextmanager
def app_card(
    title=None,
    subtitle=None,
    icon=None,
    action_label=None,
    action=None,
    classes='',
):
    """
    Reusable application card.

    Usage:

        with app_card(
            title='Recent Expenses',
            subtitle='Latest activity',
        ):
            ...
    """

    card_classes = (
        'app-card '
        'w-full '
        'min-w-0 '
        + classes
    )

    with ui.card().classes(card_classes):

        if title or subtitle or icon or action_label:

            with ui.row().classes(
                'w-full '
                'items-start '
                'justify-between '
                'gap-4 '
                'mb-4'
            ):

                with ui.row().classes(
                    'items-start '
                    'gap-3 '
                    'min-w-0'
                ):

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

                    if title or subtitle:

                        with ui.column().classes(
                            'gap-0 '
                            'min-w-0'
                        ):

                            if title:

                                ui.label(
                                    title
                                ).classes(
                                    'text-base '
                                    'font-semibold '
                                    'text-primary-app'
                                )

                            if subtitle:

                                ui.label(
                                    subtitle
                                ).classes(
                                    'text-xs '
                                    'text-secondary-app '
                                    'mt-0.5'
                                )

                if action_label:

                    ui.button(
                        action_label,
                        on_click=action,
                    ).props(
                        'flat no-caps'
                    ).classes(
                        'text-sm '
                        'text-primary '
                        'shrink-0'
                    )

        yield


# ==========================================================
# SIMPLE CARD
# ==========================================================

def simple_card(
    title=None,
    value=None,
    subtitle=None,
    icon=None,
    classes='',
):

    with ui.card().classes(
        'app-card '
        'w-full '
        'min-w-0 '
        + classes
    ):

        with ui.row().classes(
            'w-full '
            'items-center '
            'gap-4'
        ):

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

            with ui.column().classes(
                'gap-0 '
                'min-w-0'
            ):

                if title:

                    ui.label(
                        title
                    ).classes(
                        'text-sm '
                        'font-medium '
                        'text-secondary-app'
                    )

                if value is not None:

                    ui.label(
                        value
                    ).classes(
                        'text-xl '
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


# ==========================================================
# SECTION CARD
# ==========================================================

@contextmanager
def section_card(
    title,
    subtitle=None,
    icon=None,
    action_label=None,
    action=None,
    classes='',
):

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
            'gap-4 '
            'mb-5'
        ):

            with ui.row().classes(
                'items-start '
                'gap-3 '
                'min-w-0'
            ):

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

                with ui.column().classes(
                    'gap-0 '
                    'min-w-0'
                ):

                    ui.label(
                        title
                    ).classes(
                        'text-lg '
                        'font-semibold '
                        'text-primary-app'
                    )

                    if subtitle:

                        ui.label(
                            subtitle
                        ).classes(
                            'text-sm '
                            'text-secondary-app '
                            'mt-0.5'
                        )

            if action_label:

                ui.button(
                    action_label,
                    on_click=action,
                ).props(
                    'flat no-caps'
                ).classes(
                    'text-sm '
                    'text-primary '
                    'shrink-0'
                )

        yield


# ==========================================================
# EMPTY CARD
# ==========================================================

def empty_card(
    title='No data available',
    message=None,
    icon='inbox',
    action_label=None,
    action=None,
    classes='',
):

    with ui.card().classes(
        'app-card '
        'w-full '
        'min-w-0 '
        + classes
    ):

        with ui.column().classes(
            'w-full '
            'min-h-48 '
            'items-center '
            'justify-center '
            'text-center '
            'p-6 '
            'gap-2'
        ):

            with ui.element('div').classes(
                'app-icon'
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

            if message:

                ui.label(
                    message
                ).classes(
                    'text-xs '
                    'text-secondary-app '
                    'max-w-md'
                )

            if action_label:

                ui.button(
                    action_label,
                    on_click=action,
                ).props(
                    'unelevated no-caps'
                ).classes(
                    'app-button '
                    'mt-3'
                )

# ==========================================================
# CARD HEADER
# ==========================================================

def card_header(
    title,
    subtitle=None,
    icon=None,
    action_label=None,
    action=None,
):

    with ui.row().classes(
        'w-full '
        'items-start '
        'justify-between '
        'gap-4 '
        'mb-4'
    ):

        with ui.row().classes(
            'items-start '
            'gap-3 '
            'min-w-0'
        ):

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

            with ui.column().classes(
                'gap-0 '
                'min-w-0'
            ):

                ui.label(
                    title
                ).classes(
                    'text-base '
                    'font-semibold '
                    'text-primary-app'
                )

                if subtitle:

                    ui.label(
                        subtitle
                    ).classes(
                        'text-xs '
                        'text-secondary-app '
                        'mt-0.5'
                    )

        if action_label:

            ui.button(
                action_label,
                on_click=action,
            ).props(
                'flat no-caps'
            ).classes(
                'text-sm '
                'text-primary '
                'shrink-0'
            )