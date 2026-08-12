from nicegui import ui

from components.header import create_header
from services.data.income import (
    get_income_record,
    update_income,
)

@ui.page('/income/{income_id}/edit')
def edit_income_page(income_id):

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
                    'Edit Income'
                ).classes('income-title')

                ui.label(
                    'Update this income record.'
                ).classes('income-subtitle')

        # --------------------------------------------------
        # Form
        # --------------------------------------------------

        with ui.card().classes('income-form-card'):

            ui.label(
                'Income Information'
            ).classes('income-section-title')

            date_input = ui.input(
                'Date',
                value=str(income['Date'])
            ).props(
                'type=date'
            ).classes('income-form-input')

            time_input = ui.input(
                'Time',
                value=str(income['Time'])
            ).props(
                'type=time'
            ).classes('income-form-input')

            source_input = ui.input(
                'Source',
                value=income['Source'] or ''
            ).classes('income-form-input')

            description_input = ui.input(
                'Description',
                value=income['Description'] or ''
            ).classes('income-form-input')

            amount_input = ui.number(
                'Amount',
                value=float(income['Amount']),
                min=0,
                format='%.2f'
            ).classes('income-form-input')

            type_input = ui.select(
                ['Salary', 'Business', 'Gift', 'Other'],
                label='Type',
                value=income['Type']
            ).classes('income-form-input')

            # --------------------------------------------------
            # Actions
            # --------------------------------------------------

            with ui.row().classes('income-form-actions'):

                ui.button(
                    'Cancel',
                    on_click=lambda: ui.navigate.to(
                        '/income'
                    )
                ).props('flat')

                def save_changes():

                    source = source_input.value
                    description = description_input.value
                    amount = amount_input.value
                    income_type = type_input.value

                    if not source:
                        ui.notify(
                            'Source is required.',
                            type='negative'
                        )
                        return

                    if amount is None or amount <= 0:
                        ui.notify(
                            'Amount must be greater than zero.',
                            type='negative'
                        )
                        return

                    if not income_type:
                        ui.notify(
                            'Type is required.',
                            type='negative'
                        )
                        return

                    update_income(
                        income_id,
                        date_input.value,
                        time_input.value,
                        source,
                        description,
                        amount,
                        income_type
                    )

                    ui.notify(
                        'Income updated successfully.',
                        type='positive'
                    )

                    ui.navigate.to(
                        '/income'
                    )

                ui.button(
                    'Save Changes',
                    icon='save',
                    on_click=save_changes
                ).props(
                    'color=primary'
                )