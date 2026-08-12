from nicegui import ui

from components.header import create_header
from services.data.income import get_income_record

@ui.page('/income/{income_id}')
def income_details_page(income_id):

    create_header('Income')

    # --------------------------------------------------
    # Data
    # --------------------------------------------------

    income = get_income_record(income_id)

    if not income:

        with ui.column().classes('income-page'):

            ui.label(
                'Income record not found.'
            ).classes('income-empty-title')

            ui.button(
                'Back to Income',
                icon='arrow_back',
                on_click=lambda: ui.navigate.to(
                    '/income'
                )
            )

        return

    # --------------------------------------------------
    # Page
    # --------------------------------------------------

    with ui.column().classes('income-page'):

        # --------------------------------------------------
        # Page Header
        # --------------------------------------------------

        with ui.row().classes('income-header'):

            with ui.column().classes('income-heading'):

                ui.label(
                    'Income Details'
                ).classes('income-title')

                ui.label(
                    'View the details of this income record.'
                ).classes('income-subtitle')

        # --------------------------------------------------
        # Details
        # --------------------------------------------------

        with ui.card().classes('income-details-card'):

            ui.label(
                'Income Information'
            ).classes('income-section-title')

            with ui.column().classes('income-details'):

                with ui.row().classes('income-detail-row'):

                    ui.label(
                        'ID'
                    ).classes('income-detail-label')

                    ui.label(
                        str(income['ID'])
                    ).classes('income-detail-value')

                with ui.row().classes('income-detail-row'):

                    ui.label(
                        'Date'
                    ).classes('income-detail-label')

                    ui.label(
                        str(income['Date'])
                    ).classes('income-detail-value')

                with ui.row().classes('income-detail-row'):

                    ui.label(
                        'Time'
                    ).classes('income-detail-label')

                    ui.label(
                        str(income['Time'])
                    ).classes('income-detail-value')

                with ui.row().classes('income-detail-row'):

                    ui.label(
                        'Source'
                    ).classes('income-detail-label')

                    ui.label(
                        income['Source'] or ''
                    ).classes('income-detail-value')

                with ui.row().classes('income-detail-row'):

                    ui.label(
                        'Description'
                    ).classes('income-detail-label')

                    ui.label(
                        income['Description'] or ''
                    ).classes('income-detail-value')

                with ui.row().classes('income-detail-row'):

                    ui.label(
                        'Amount'
                    ).classes('income-detail-label')

                    ui.label(
                        f"{float(income['Amount']):,.2f}"
                    ).classes('income-detail-value')

                with ui.row().classes('income-detail-row'):

                    ui.label(
                        'Type'
                    ).classes('income-detail-label')

                    ui.label(
                        income['Type'] or ''
                    ).classes('income-detail-value')

            # --------------------------------------------------
            # Actions
            # --------------------------------------------------

            with ui.row().classes('income-details-actions'):

                ui.button(
                    'Back',
                    icon='arrow_back',
                    on_click=lambda: ui.navigate.to(
                        '/income'
                    )
                ).props('flat')

                ui.button(
                    'Edit Income',
                    icon='edit',
                    on_click=lambda: ui.navigate.to(
                        f"/income/{income_id}/edit"
                    )
                ).props(
                    'color=primary'
                )
