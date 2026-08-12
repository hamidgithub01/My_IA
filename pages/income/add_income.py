from datetime import date, datetime

from nicegui import ui

from components.header import create_header
from services.data.income import add_income

@ui.page('/income/add')
def add_income_page():

    create_header('Income')

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
                    'Add Income'
                ).classes('income-title')

                ui.label(
                    'Add a new income record.'
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
                value=str(date.today())
            ).props(
                'type=date'
            ).classes('income-form-input')

            time_input = ui.input(
                'Time',
                value=datetime.now().strftime('%H:%M:%S')
            ).props(
                'type=time'
            ).classes('income-form-input')

            source_input = ui.input(
                'Source'
            ).classes('income-form-input')

            description_input = ui.input(
                'Description'
            ).classes('income-form-input')

            amount_input = ui.number(
                'Amount',
                min=0,
                format='%.2f'
            ).classes('income-form-input')

            type_input = ui.select(
                ['Salary', 'Business', 'Gift', 'Other'],
                label='Type'
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

                def save_income():

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

                    add_income(
                        date_input.value,
                        time_input.value,
                        source,
                        description,
                        amount,
                        income_type
                    )

                    ui.notify(
                        'Income added successfully.',
                        type='positive'
                    )

                    ui.navigate.to(
                        '/income'
                    )

                ui.button(
                    'Save Income',
                    icon='save',
                    on_click=save_income
                ).props(
                    'color=primary'
                )
