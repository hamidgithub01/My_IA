from pathlib import Path
from datetime import date, datetime

from nicegui import ui

from components.header import create_header
from services.data.settings import (
    get_setting_value,
    update_setting,
)


@ui.page('/settings')
def settings_page():

    create_header('Settings')

    # --------------------------------------------------
    # CSS
    # --------------------------------------------------

    css_file = Path('styles/settings.css')

    if css_file.exists():

        css_version = css_file.stat().st_mtime_ns

        ui.add_head_html(
            f'<link rel="stylesheet" '
            f'href="/styles/settings.css?v={css_version}">'
        )

    # --------------------------------------------------
    # Load settings
    # --------------------------------------------------

    currency = get_setting_value('Currency') or 'MAD'

    language = (
        get_setting_value('Default_Language')
        or 'English'
    )

    tracking_date = get_setting_value(
        'Start_Tracking_Date'
    )

    if tracking_date:

        if isinstance(tracking_date, datetime):
            tracking_date_value = (
                tracking_date.date().isoformat()
            )

        elif isinstance(tracking_date, date):
            tracking_date_value = tracking_date.isoformat()

        else:
            tracking_date_value = str(
                tracking_date
            )[:10]

    else:

        tracking_date_value = date.today().isoformat()

    # --------------------------------------------------
    # Page
    # --------------------------------------------------

    with ui.column().classes('settings-page'):

        # --------------------------------------------------
        # Hero
        # --------------------------------------------------

        with ui.column().classes('settings-hero'):

            with ui.row().classes('settings-hero-icon'):

                ui.icon(
                    'settings',
                    size='32px'
                )

            with ui.column().classes('settings-heading'):

                ui.label(
                    'Settings'
                ).classes('settings-title')

                ui.label(
                    'Customize how Personal Finance AI '
                    'works for you.'
                ).classes('settings-subtitle')

        # --------------------------------------------------
        # General Settings
        # --------------------------------------------------

        with ui.column().classes(
            'settings-section'
        ):

            with ui.column().classes(
                'settings-section-heading'
            ):

                ui.label(
                    'General'
                ).classes(
                    'settings-section-title'
                )

                ui.label(
                    'Basic preferences for your application.'
                ).classes(
                    'settings-section-subtitle'
                )

            with ui.column().classes(
                'settings-grid'
            ):

                # ------------------------------------------
                # Currency
                # ------------------------------------------

                with ui.card().classes(
                    'setting-card'
                ):

                    with ui.row().classes(
                        'setting-card-top'
                    ):

                        with ui.row().classes(
                            'setting-card-icon'
                        ):

                            ui.icon(
                                'payments'
                            )

                        with ui.column().classes(
                            'setting-card-content'
                        ):

                            ui.label(
                                'Currency'
                            ).classes(
                                'setting-label'
                            )

                            ui.label(
                                'The currency used throughout '
                                'your financial records.'
                            ).classes(
                                'setting-description'
                            )

                    currency_input = ui.select(
                        options=[
                            'MAD',
                            'USD',
                            'EUR',
                            'GBP',
                            'CAD',
                            'AUD',
                            'CHF',
                            'JPY',
                        ],
                        value=currency,
                        label='Currency',
                    ).classes(
                        'setting-control'
                    )

                # ------------------------------------------
                # Language
                # ------------------------------------------

                with ui.card().classes(
                    'setting-card'
                ):

                    with ui.row().classes(
                        'setting-card-top'
                    ):

                        with ui.row().classes(
                            'setting-card-icon'
                        ):

                            ui.icon(
                                'language'
                            )

                        with ui.column().classes(
                            'setting-card-content'
                        ):

                            ui.label(
                                'Default Language'
                            ).classes(
                                'setting-label'
                            )

                            ui.label(
                                'The default language used '
                                'by the application.'
                            ).classes(
                                'setting-description'
                            )

                    language_input = ui.select(
                        options=[
                            'English',
                            'French',
                            'Arabic',
                        ],
                        value=language,
                        label='Language',
                    ).classes(
                        'setting-control'
                    )

        # --------------------------------------------------
        # Tracking Settings
        # --------------------------------------------------

        with ui.column().classes(
            'settings-section'
        ):

            with ui.column().classes(
                'settings-section-heading'
            ):

                ui.label(
                    'Tracking'
                ).classes(
                    'settings-section-title'
                )

                ui.label(
                    'Control when your financial tracking '
                    'history begins.'
                ).classes(
                    'settings-section-subtitle'
                )

            with ui.column().classes(
                'settings-grid settings-grid-single'
            ):

                with ui.card().classes(
                    'setting-card'
                ):

                    with ui.row().classes(
                        'setting-card-top'
                    ):

                        with ui.row().classes(
                            'setting-card-icon'
                        ):

                            ui.icon(
                                'event_available'
                            )

                        with ui.column().classes(
                            'setting-card-content'
                        ):

                            ui.label(
                                'Start Tracking Date'
                            ).classes(
                                'setting-label'
                            )

                            ui.label(
                                'The date from which the application '
                                'considers your financial history.'
                            ).classes(
                                'setting-description'
                            )

                    tracking_date_input = ui.input(
                        'Start Tracking Date',
                        value=tracking_date_value,
                    ).props(
                        'type=date'
                    ).classes(
                        'setting-control'
                    )

        # --------------------------------------------------
        # Actions
        # --------------------------------------------------

        with ui.row().classes(
            'settings-actions'
        ):

            def save_settings():

                # ------------------------------------------
                # Validation
                # ------------------------------------------

                if not currency_input.value:

                    ui.notify(
                        'Please select a currency.',
                        type='negative',
                    )

                    return

                if not language_input.value:

                    ui.notify(
                        'Please select a language.',
                        type='negative',
                    )

                    return

                if not tracking_date_input.value:

                    ui.notify(
                        'Please select a tracking date.',
                        type='negative',
                    )

                    return

                try:

                    tracking_date_value = date.fromisoformat(
                        tracking_date_input.value
                    )

                except (TypeError, ValueError):

                    ui.notify(
                        'Please enter a valid date.',
                        type='negative',
                    )

                    return

                # ------------------------------------------
                # Save
                # ------------------------------------------

                update_setting(
                    'Currency',
                    currency_input.value,
                )

                update_setting(
                    'Default_Language',
                    language_input.value,
                )

                update_setting(
                    'Start_Tracking_Date',
                    tracking_date_value,
                )

                ui.notify(
                    'Settings saved successfully.',
                    type='positive',
                )

            ui.button(
                'Save Changes',
                icon='save',
                on_click=save_settings,
            ).classes(
                'settings-save-button'
            )