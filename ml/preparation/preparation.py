from collections import defaultdict

from database.queries import (
    get_all_days,
    get_all_expenses,
    get_all_income,
    get_all_events,
)

from ml.preparation.cleaning import (
    clean_date,
    clean_numeric,
    clean_text,
)


def prepare_days():
    """
    Prepare daily records from the days table.

    One record represents one calendar day.
    """

    records = get_all_days()

    prepared = []

    for record in records:

        day_date = clean_date(record.get('Date'))

        if day_date is None:
            continue

        prepared.append({
            'Date': day_date,
            'Day_Type': clean_text(
                record.get('Day_Type')
            ),
            'Work_Status': clean_text(
                record.get('Work_Status')
            ),
            'Health_Impact': clean_text(
                record.get('Health_Impact')
            ),
            'Travel': clean_text(
                record.get('Travel')
            ),
            'Special_Event': clean_text(
                record.get('Special_Event')
            ),
            'Stress_Level': clean_numeric(
                record.get('Stress_Level')
            ),
            'Notes': clean_text(
                record.get('Notes')
            ),
            'Sleep_Hours': clean_numeric(
                record.get('Sleep_Hours')
            ),
            'Social_Activity': clean_text(
                record.get('Social_Activity')
            ),
            'Location': clean_text(
                record.get('Location')
            ),
        })

    return prepared


def prepare_expenses():
    """
    Prepare expense records.

    The original database is not modified.
    """

    records = get_all_expenses()

    prepared = []

    for record in records:

        expense_date = clean_date(
            record.get('Date')
        )

        if expense_date is None:
            continue

        amount = clean_numeric(
            record.get('Amount')
        )

        prepared.append({
            'ID': record.get('ID'),
            'Date': expense_date,
            'Category': clean_text(
                record.get('Category'),
                default='Unknown',
            ),
            'Description': clean_text(
                record.get('Description')
            ),
            'Amount': amount,
        })

    return prepared


def prepare_income():
    """
    Prepare income records.

    The original database is not modified.
    """

    records = get_all_income()

    prepared = []

    for record in records:

        income_date = clean_date(
            record.get('Date')
        )

        if income_date is None:
            continue

        amount = clean_numeric(
            record.get('Amount')
        )

        prepared.append({
            'ID': record.get('ID'),
            'Date': income_date,
            'Source': clean_text(
                record.get('Source'),
                default='Unknown',
            ),
            'Description': clean_text(
                record.get('Description')
            ),
            'Amount': amount,
            'Type': clean_text(
                record.get('Type')
            ),
        })

    return prepared


def prepare_events():
    """
    Prepare event records.

    Events are preserved individually at this stage.
    """

    records = get_all_events()

    prepared = []

    for record in records:

        event_date = clean_date(
            record.get('Date')
        )

        if event_date is None:
            continue

        prepared.append({
            'ID': record.get('ID'),
            'Date': event_date,
            'Event_Type': clean_text(
                record.get('Event_Type'),
                default='Unknown',
            ),
            'Description': clean_text(
                record.get('Description')
            ),
        })

    return prepared


def aggregate_expenses_by_date(expenses):
    """
    Aggregate expenses by date.

    Returns:
        {
            date: {
                'expense_total': float,
                'expense_count': int,
            }
        }
    """

    result = defaultdict(
        lambda: {
            'expense_total': 0.0,
            'expense_count': 0,
        }
    )

    for expense in expenses:

        expense_date = expense['Date']

        result[expense_date][
            'expense_total'
        ] += expense['Amount']

        result[expense_date][
            'expense_count'
        ] += 1

    return dict(result)


def aggregate_income_by_date(income):
    """
    Aggregate income by date.

    Returns:
        {
            date: {
                'income_total': float,
                'income_count': int,
            }
        }
    """

    result = defaultdict(
        lambda: {
            'income_total': 0.0,
            'income_count': 0,
        }
    )

    for record in income:

        income_date = record['Date']

        result[income_date][
            'income_total'
        ] += record['Amount']

        result[income_date][
            'income_count'
        ] += 1

    return dict(result)


def aggregate_events_by_date(events):
    """
    Aggregate events by date.

    Events are counted rather than merged into
    a single text field.
    """

    result = defaultdict(
        lambda: {
            'event_count': 0,
        }
    )

    for event in events:

        event_date = event['Date']

        result[event_date][
            'event_count'
        ] += 1

    return dict(result)


def build_daily_dataset():
    """
    Build the main daily dataset.

    Each row represents one calendar day.

    Data sources:
        - days
        - expenses
        - income
        - events

    Financial activity is aggregated by date.
    """

    days = prepare_days()
    expenses = prepare_expenses()
    income = prepare_income()
    events = prepare_events()

    expenses_by_date = aggregate_expenses_by_date(
        expenses
    )

    income_by_date = aggregate_income_by_date(
        income
    )

    events_by_date = aggregate_events_by_date(
        events
    )

    dataset = []

    for day in days:

        day_date = day['Date']

        expense_data = expenses_by_date.get(
            day_date,
            {
                'expense_total': 0.0,
                'expense_count': 0,
            },
        )

        income_data = income_by_date.get(
            day_date,
            {
                'income_total': 0.0,
                'income_count': 0,
            },
        )

        event_data = events_by_date.get(
            day_date,
            {
                'event_count': 0,
            },
        )

        row = dict(day)

        row.update({
            'Expense_Total':
                expense_data['expense_total'],

            'Expense_Count':
                expense_data['expense_count'],

            'Income_Total':
                income_data['income_total'],

            'Income_Count':
                income_data['income_count'],

            'Event_Count':
                event_data['event_count'],
        })

        dataset.append(row)

    dataset.sort(
        key=lambda row: row['Date']
    )

    return dataset


def get_prepared_dataset():
    """
    Public entry point for Data Preparation.

    Returns a clean daily dataset ready for
    Feature Engineering.
    """

    return build_daily_dataset()