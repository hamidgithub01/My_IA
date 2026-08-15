from collections import defaultdict
from calendar import monthrange
from datetime import timedelta

from database.queries import (
    get_all_days,
    get_all_expenses,
    get_all_income,
    get_all_events,
    get_all_health_records,
    get_all_activities,
    get_all_sleep_records,
    get_all_travel,
    get_all_plans,
    get_all_recurring,
)

from ml.preparation.cleaning import (
    clean_date,
    clean_numeric,
    clean_text,
)


# =========================================================
# DAYS
# =========================================================

def prepare_days():
    """
    Prepare daily records from the days table.

    One record represents one calendar day.
    """

    records = get_all_days()

    prepared = []

    for record in records:

        day_date = clean_date(
            record.get('Date')
        )

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


# =========================================================
# EXPENSES
# =========================================================

def prepare_expenses():
    """
    Prepare actual expense records.
    """

    records = get_all_expenses()

    prepared = []

    for record in records:

        expense_date = clean_date(
            record.get('Date')
        )

        if expense_date is None:
            continue

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

            'Amount': clean_numeric(
                record.get('Amount')
            ),
        })

    return prepared


# =========================================================
# INCOME
# =========================================================

def prepare_income():
    """
    Prepare actual income records.
    """

    records = get_all_income()

    prepared = []

    for record in records:

        income_date = clean_date(
            record.get('Date')
        )

        if income_date is None:
            continue

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

            'Amount': clean_numeric(
                record.get('Amount')
            ),

            'Type': clean_text(
                record.get('Type')
            ),
        })

    return prepared


# =========================================================
# EVENTS
# =========================================================

def prepare_events():
    """
    Prepare actual event records.

    Events remain individual records at this stage.
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


# =========================================================
# HEALTH
# =========================================================

def prepare_health_records():
    """
    Prepare health records.

    Health information is preserved as observations.
    """

    records = get_all_health_records()

    prepared = []

    for record in records:

        health_date = clean_date(
            record.get('Date')
        )

        if health_date is None:
            continue

        prepared.append({
            'Health_ID':
                record.get('Health_ID'),

            'Date':
                health_date,

            'Health_Status':
                clean_text(
                    record.get('Health_Status')
                ),

            'Energy_Level':
                clean_numeric(
                    record.get('Energy_Level')
                ),

            'Symptoms':
                clean_text(
                    record.get('Symptoms')
                ),

            'Severity':
                clean_numeric(
                    record.get('Severity')
                ),

            'Treatment':
                clean_text(
                    record.get('Treatment')
                ),

            'Health_Notes':
                clean_text(
                    record.get('Notes')
                ),
        })

    return prepared


# =========================================================
# ACTIVITIES
# =========================================================

def prepare_activities():
    """
    Prepare activity records.
    """

    records = get_all_activities()

    prepared = []

    for record in records:

        activity_date = clean_date(
            record.get('Date')
        )

        if activity_date is None:
            continue

        prepared.append({
            'Activity_ID':
                record.get('Activity_ID'),

            'Date':
                activity_date,

            'Activity_Type':
                clean_text(
                    record.get('Activity_Type')
                ),

            'Duration_Minutes':
                clean_numeric(
                    record.get('Duration_Minutes')
                ),

            'Activity_Planned':
                clean_numeric(
                    record.get('Planned')
                ),

            'Activity_Actual':
                clean_numeric(
                    record.get('Actual')
                ),

            'Activity_Location':
                clean_text(
                    record.get('Location')
                ),

            'Activity_Cost':
                clean_numeric(
                    record.get('Cost')
                ),

            'People_Count':
                clean_numeric(
                    record.get('People_Count')
                ),

            'Activity_Notes':
                clean_text(
                    record.get('Notes')
                ),
        })

    return prepared


# =========================================================
# SLEEP
# =========================================================

def prepare_sleep():
    """
    Prepare sleep records.

    Multiple sleep records per day are preserved
    and aggregated later.
    """

    records = get_all_sleep_records()

    prepared = []

    for record in records:

        sleep_date = clean_date(
            record.get('Date')
        )

        if sleep_date is None:
            continue

        prepared.append({
            'Sleep_ID':
                record.get('Sleep_ID'),

            'Date':
                sleep_date,

            'Duration_Minutes':
                clean_numeric(
                    record.get('Duration_Minutes')
                ),

            'Sleep_Type':
                clean_text(
                    record.get('Sleep_Type')
                ),

            'Continuity':
                clean_text(
                    record.get('Continuity')
                ),

            'Sleep_Quality':
                clean_numeric(
                    record.get('Sleep_Quality')
                ),

            'Awakenings':
                clean_numeric(
                    record.get('Awakenings')
                ),

            'Noise_Level':
                clean_numeric(
                    record.get('Noise_Level')
                ),

            'Light_Level':
                clean_numeric(
                    record.get('Light_Level')
                ),

            'Temperature_Level':
                clean_numeric(
                    record.get('Temperature_Level')
                ),

            'Comfort_Level':
                clean_numeric(
                    record.get('Comfort_Level')
                ),

            'Stress_Before_Sleep':
                clean_numeric(
                    record.get('Stress_Before_Sleep')
                ),

            'Caffeine_Before_Sleep':
                clean_numeric(
                    record.get('Caffeine_Before_Sleep')
                ),

            'Screen_Before_Sleep':
                clean_numeric(
                    record.get('Screen_Before_Sleep')
                ),

            'Before_Sleep_Activity':
                clean_text(
                    record.get('Before_Sleep_Activity')
                ),

            'Dreams':
                clean_text(
                    record.get('Dreams')
                ),

            'Sleep_Notes':
                clean_text(
                    record.get('Notes')
                ),
        })

    return prepared


# =========================================================
# TRAVEL
# =========================================================

def prepare_travel():
    """
    Prepare travel records.

    Travel may cover multiple calendar days.
    """

    records = get_all_travel()

    prepared = []

    for record in records:

        start_date = clean_date(
            record.get('Start_Date')
        )

        end_date = clean_date(
            record.get('End_Date')
        )

        if start_date is None:
            continue

        if end_date is None:
            end_date = start_date

        if end_date < start_date:
            end_date = start_date

        prepared.append({
            'Travel_ID':
                record.get('Travel_ID'),

            'Start_Date':
                start_date,

            'End_Date':
                end_date,

            'Destination':
                clean_text(
                    record.get('Destination')
                ),

            'Purpose':
                clean_text(
                    record.get('Purpose')
                ),

            'Transport':
                clean_text(
                    record.get('Transport')
                ),

            'Planned':
                clean_numeric(
                    record.get('Planned')
                ),

            'Actual':
                clean_numeric(
                    record.get('Actual')
                ),

            'Expected_Cost':
                clean_numeric(
                    record.get('Expected_Cost')
                ),

            'Actual_Cost':
                clean_numeric(
                    record.get('Actual_Cost')
                ),

            'Travel_Notes':
                clean_text(
                    record.get('Notes')
                ),
        })

    return prepared


# =========================================================
# PLANS
# =========================================================

def prepare_plans():
    """
    Prepare planned future or scheduled records.

    Plans represent known intentions or expected events.
    They are NOT actual transactions merely because they exist.

    Actual_Date and Actual_Cost are preserved for historical
    comparison, but Feature Engineering must distinguish them
    from future planned information.
    """

    records = get_all_plans()

    prepared = []

    for record in records:

        plan_date = clean_date(
            record.get('Plan_Date')
        )

        if plan_date is None:
            continue

        actual_date = clean_date(
            record.get('Actual_Date')
        )

        duration_days = clean_numeric(
            record.get('Duration_Days'),
            default=1.0,
        )

        if duration_days is None or duration_days < 1:
            duration_days = 1.0

        prepared.append({
            'Plan_ID':
                record.get('Plan_ID'),

            'Plan_Date':
                plan_date,

            'Plan_Type':
                clean_text(
                    record.get('Plan_Type'),
                    default='Unknown',
                ),

            'Title':
                clean_text(
                    record.get('Title'),
                    default='Unknown',
                ),

            'Expected_Cost':
                clean_numeric(
                    record.get('Expected_Cost')
                ),

            'Duration_Days':
                duration_days,

            'Importance':
                clean_text(
                    record.get('Importance'),
                    default='Medium',
                ),

            'Status':
                clean_text(
                    record.get('Status'),
                    default='Planned',
                ),

            'Actual_Date':
                actual_date,

            'Actual_Cost':
                clean_numeric(
                    record.get('Actual_Cost')
                ),

            'Notes':
                clean_text(
                    record.get('Notes')
                ),
        })

    return prepared


# =========================================================
# RECURRING
# =========================================================

def prepare_recurring():
    """
    Prepare recurring rules.

    A recurring record is a RULE describing something expected
    to happen repeatedly.

    It is NOT an actual expense or income record.

    Examples:
        - monthly rent
        - monthly subscription
        - weekly payment
        - regular income
        - yearly recurring obligation

    The actual occurrence must remain separate from the rule.
    """

    records = get_all_recurring()

    prepared = []

    for record in records:

        start_date = clean_date(
            record.get('Start_Date')
        )

        if start_date is None:
            continue

        end_date = clean_date(
            record.get('End_Date')
        )

        if end_date is not None and end_date < start_date:
            continue

        prepared.append({
            'Recurring_ID':
                record.get('Recurring_ID'),

            'Name':
                clean_text(
                    record.get('Name'),
                    default='Unknown',
                ),

            'Type':
                clean_text(
                    record.get('Type'),
                    default='Unknown',
                ),

            'Category':
                clean_text(
                    record.get('Category')
                ),

            'Amount':
                clean_numeric(
                    record.get('Amount')
                ),

            'Frequency':
                clean_text(
                    record.get('Frequency'),
                    default='Unknown',
                ),

            'Day_Of_Month':
                clean_numeric(
                    record.get('Day_Of_Month'),
                    default=0.0,
                ),

            'Day_Of_Week':
                clean_numeric(
                    record.get('Day_Of_Week'),
                    default=-1.0,
                ),

            'Start_Date':
                start_date,

            'End_Date':
                end_date,

            'Is_Active':
                clean_numeric(
                    record.get('Is_Active'),
                    default=1.0,
                ),

            'Is_Fixed_Amount':
                clean_numeric(
                    record.get('Is_Fixed_Amount'),
                    default=1.0,
                ),

            'Notes':
                clean_text(
                    record.get('Notes')
                ),
        })

    return prepared


# =========================================================
# FINANCIAL AGGREGATION
# =========================================================

def aggregate_expenses_by_date(expenses):

    result = defaultdict(
        lambda: {
            'expense_total': 0.0,
            'expense_count': 0,
        }
    )

    for expense in expenses:

        expense_date = expense['Date']

        amount = expense['Amount'] or 0.0

        result[expense_date][
            'expense_total'
        ] += amount

        result[expense_date][
            'expense_count'
        ] += 1

    return dict(result)


def aggregate_income_by_date(income):

    result = defaultdict(
        lambda: {
            'income_total': 0.0,
            'income_count': 0,
        }
    )

    for record in income:

        income_date = record['Date']

        amount = record['Amount'] or 0.0

        result[income_date][
            'income_total'
        ] += amount

        result[income_date][
            'income_count'
        ] += 1

    return dict(result)


def aggregate_events_by_date(events):

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


# =========================================================
# HEALTH AGGREGATION
# =========================================================

def aggregate_health_by_date(records):

    result = defaultdict(
        lambda: {
            'health_record_count': 0,
            'max_health_severity': 0.0,
            'avg_energy_level': 0.0,
        }
    )

    energy_values = defaultdict(list)

    for record in records:

        record_date = record['Date']

        result[record_date][
            'health_record_count'
        ] += 1

        severity = record['Severity']

        if severity is not None:

            result[record_date][
                'max_health_severity'
            ] = max(
                result[record_date][
                    'max_health_severity'
                ],
                severity,
            )

        energy = record['Energy_Level']

        if energy is not None:
            energy_values[
                record_date
            ].append(energy)

    for record_date, values in energy_values.items():

        if values:

            result[record_date][
                'avg_energy_level'
            ] = sum(values) / len(values)

    return dict(result)


# =========================================================
# ACTIVITY AGGREGATION
# =========================================================

def aggregate_activities_by_date(activities):

    result = defaultdict(
        lambda: {
            'activity_count': 0,
            'activity_duration_minutes': 0.0,
            'activity_cost': 0.0,
        }
    )

    for activity in activities:

        activity_date = activity['Date']

        result[activity_date][
            'activity_count'
        ] += 1

        duration = (
            activity['Duration_Minutes']
            or 0.0
        )

        cost = (
            activity['Activity_Cost']
            or 0.0
        )

        result[activity_date][
            'activity_duration_minutes'
        ] += duration

        result[activity_date][
            'activity_cost'
        ] += cost

    return dict(result)


# =========================================================
# SLEEP AGGREGATION
# =========================================================

def aggregate_sleep_by_date(sleep_records):

    result = defaultdict(
        lambda: {
            'sleep_record_count': 0,
            'sleep_duration_minutes': 0.0,
            'avg_sleep_quality': 0.0,
            'total_awakenings': 0.0,
        }
    )

    quality_values = defaultdict(list)

    for record in sleep_records:

        sleep_date = record['Date']

        result[sleep_date][
            'sleep_record_count'
        ] += 1

        duration = (
            record['Duration_Minutes']
            or 0.0
        )

        awakenings = (
            record['Awakenings']
            or 0.0
        )

        result[sleep_date][
            'sleep_duration_minutes'
        ] += duration

        result[sleep_date][
            'total_awakenings'
        ] += awakenings

        quality = record['Sleep_Quality']

        if quality is not None:

            quality_values[
                sleep_date
            ].append(quality)

    for sleep_date, values in quality_values.items():

        if values:

            result[sleep_date][
                'avg_sleep_quality'
            ] = sum(values) / len(values)

    return dict(result)


# =========================================================
# PLANS AGGREGATION
# =========================================================

def aggregate_plans_by_date(plans):

    result = defaultdict(
        lambda: {
            'plan_count': 0,
            'plan_expected_cost': 0.0,
            'plan_duration_days': 0.0,
            'high_importance_plan_count': 0,
        }
    )

    for plan in plans:

        plan_date = plan['Plan_Date']

        result[plan_date][
            'plan_count'
        ] += 1

        expected_cost = (
            plan['Expected_Cost']
            or 0.0
        )

        duration_days = (
            plan['Duration_Days']
            or 1.0
        )

        result[plan_date][
            'plan_expected_cost'
        ] += expected_cost

        result[plan_date][
            'plan_duration_days'
        ] += duration_days

        importance = (
            plan['Importance'] or ''
        ).strip().lower()

        if importance in {
            'high',
            'urgent',
            'critical',
        }:

            result[plan_date][
                'high_importance_plan_count'
            ] += 1

    return dict(result)


def expand_plans_by_date(plans):
    """
    Expand plans across their planned duration.

    This does NOT create actual transactions.

    It only indicates that a planned event remains relevant
    on each day of its planned duration.
    """

    result = defaultdict(
        lambda: {
            'active_plan_count': 0,
            'active_plan_expected_cost': 0.0,
            'active_high_importance_plan_count': 0,
        }
    )

    for plan in plans:

        start_date = plan['Plan_Date']

        duration_days = int(
            max(
                1,
                plan['Duration_Days'] or 1,
            )
        )

        expected_cost = (
            plan['Expected_Cost']
            or 0.0
        )

        importance = (
            plan['Importance'] or ''
        ).strip().lower()

        for offset in range(duration_days):

            current_date = (
                start_date
                + timedelta(days=offset)
            )

            result[current_date][
                'active_plan_count'
            ] += 1

            # The expected cost belongs to the plan itself.
            # It is not multiplied into every day.
            if offset == 0:

                result[current_date][
                    'active_plan_expected_cost'
                ] += expected_cost

            if importance in {
                'high',
                'urgent',
                'critical',
            }:

                result[current_date][
                    'active_high_importance_plan_count'
                ] += 1

    return dict(result)


# =========================================================
# RECURRING HELPERS
# =========================================================

def normalize_frequency(value):
    """
    Normalize common recurring frequency names.

    Returns:

        daily
        weekly
        biweekly
        monthly
        yearly
        unknown
    """

    if value is None:
        return 'unknown'

    value = str(
        value
    ).strip().lower()

    normalized = (
        value
        .replace('_', ' ')
        .replace('-', ' ')
    )

    normalized = ' '.join(
        normalized.split()
    )

    if normalized in {
        'daily',
        'day',
        'every day',
    }:
        return 'daily'

    if normalized in {
        'weekly',
        'week',
        'every week',
    }:
        return 'weekly'

    if normalized in {
        'biweekly',
        'bi weekly',
        'every two weeks',
        'every 2 weeks',
        'fortnightly',
    }:
        return 'biweekly'

    if normalized in {
        'monthly',
        'month',
        'every month',
    }:
        return 'monthly'

    if normalized in {
        'yearly',
        'annual',
        'annually',
        'year',
        'every year',
    }:
        return 'yearly'

    return 'unknown'


def normalize_day_of_week(value):
    """
    Normalize day-of-week values.

    Accepted conventions:

        1 = Monday ... 7 = Sunday

    and Python:

        0 = Monday ... 6 = Sunday

    Returns:
        Python weekday 0-6
        or None when invalid.
    """

    if value is None:
        return None

    try:
        value = int(value)
    except (
        TypeError,
        ValueError,
    ):
        return None

    if 1 <= value <= 7:

        return value - 1

    if 0 <= value <= 6:

        return value

    return None


def recurring_is_active_on_date(
    recurring,
    current_date,
):
    """
    Determine whether a recurring rule has an expected
    occurrence on a specific calendar date.

    This function represents EXPECTED recurrence only.

    It does not create an actual expense or income.
    """

    start_date = recurring[
        'Start_Date'
    ]

    end_date = recurring[
        'End_Date'
    ]

    if current_date < start_date:
        return False

    if (
        end_date is not None
        and current_date > end_date
    ):
        return False

    if not recurring['Is_Active']:
        return False

    frequency = normalize_frequency(
        recurring['Frequency']
    )

    if frequency == 'daily':

        return True

    if frequency == 'weekly':

        expected_weekday = (
            normalize_day_of_week(
                recurring['Day_Of_Week']
            )
        )

        if expected_weekday is None:
            return False

        return (
            current_date.weekday()
            == expected_weekday
        )

    if frequency == 'biweekly':

        expected_weekday = (
            normalize_day_of_week(
                recurring['Day_Of_Week']
            )
        )

        if expected_weekday is None:
            return False

        if (
            current_date.weekday()
            != expected_weekday
        ):
            return False

        days_since_start = (
            current_date - start_date
        ).days

        return (
            days_since_start >= 0
            and days_since_start % 14 == 0
        )

    if frequency == 'monthly':

        day_of_month = int(
            recurring['Day_Of_Month']
        )

        if day_of_month <= 0:
            return False

        # A recurring rule scheduled for day 31 should not
        # accidentally occur on day 28/30 in shorter months.
        if day_of_month > monthrange(
            current_date.year,
            current_date.month,
        )[1]:
            return False

        return (
            current_date.day
            == day_of_month
        )

    if frequency == 'yearly':

        day_of_month = int(
            recurring['Day_Of_Month']
        )

        if day_of_month <= 0:
            return False

        if (
            current_date.month
            != start_date.month
        ):
            return False

        if day_of_month > monthrange(
            current_date.year,
            current_date.month,
        )[1]:
            return False

        return (
            current_date.day
            == day_of_month
        )

    return False


def aggregate_recurring_by_date(
    recurring,
    dates,
):
    """
    Expand recurring rules onto the supplied dates.

    Important:

    Recurring values represent EXPECTED recurring activity.

    They must NOT be added to:
        Expense_Total
        Income_Total

    because those fields represent ACTUAL recorded transactions.

    Recurring dates are evaluated only against the supplied
    dataset dates. This prevents recurring rules from creating
    an arbitrary future training horizon.
    """

    result = defaultdict(
        lambda: {
            'recurring_count': 0,
            'recurring_amount': 0.0,
            'recurring_expense_amount': 0.0,
            'recurring_income_amount': 0.0,
            'fixed_recurring_amount': 0.0,
        }
    )

    sorted_dates = sorted(
        set(dates)
    )

    if not sorted_dates:
        return dict(result)

    for recurring_record in recurring:

        if not recurring_record[
            'Is_Active'
        ]:
            continue

        for current_date in sorted_dates:

            if not recurring_is_active_on_date(
                recurring_record,
                current_date,
            ):
                continue

            amount = (
                recurring_record['Amount']
                or 0.0
            )

            result[current_date][
                'recurring_count'
            ] += 1

            result[current_date][
                'recurring_amount'
            ] += amount

            recurring_type = (
                recurring_record['Type']
                or ''
            ).strip().lower()

            if recurring_type in {
                'expense',
                'expenses',
                'cost',
                'payment',
            }:

                result[current_date][
                    'recurring_expense_amount'
                ] += amount

            elif recurring_type in {
                'income',
                'revenues',
                'revenue',
                'earning',
                'earnings',
            }:

                result[current_date][
                    'recurring_income_amount'
                ] += amount

            if recurring_record[
                'Is_Fixed_Amount'
            ]:

                result[current_date][
                    'fixed_recurring_amount'
                ] += amount

    return dict(result)


# =========================================================
# DATE RANGE HELPERS
# =========================================================

def build_historical_date_range(
    dates,
):
    """
    Build a continuous historical calendar range.

    This is useful because recurring activity can occur on a
    historical day where no other source has a record.

    Only historical dates are expanded this way.
    """

    valid_dates = sorted(
        set(dates)
    )

    if not valid_dates:
        return set()

    start_date = valid_dates[0]
    end_date = valid_dates[-1]

    result = set()

    current_date = start_date

    while current_date <= end_date:

        result.add(
            current_date
        )

        current_date += timedelta(
            days=1
        )

    return result


# =========================================================
# DAILY DATASET
# =========================================================

def build_daily_dataset():
    """
    Build the unified daily dataset.

    Data sources:

        days
        expenses
        income
        events
        health_records
        activities
        sleep
        travel
        plans
        recurring

    Design principles:

        1. Actual records remain actual.
        2. Plans remain planned/expected.
        3. Recurring remains expected recurring activity.
        4. Recurring is never added to actual income/expense.
        5. Historical dates are continuous.
        6. Future dates are created only by known plans.
        7. Recurring rules may enrich existing dates, but do not
           create an unlimited future horizon.
        8. Plans and recurring can coexist on the same date.
    """

    # -----------------------------------------------------
    # Prepare source data
    # -----------------------------------------------------

    days = prepare_days()

    expenses = prepare_expenses()
    income = prepare_income()
    events = prepare_events()

    health_records = prepare_health_records()
    activities = prepare_activities()
    sleep_records = prepare_sleep()

    travel_records = prepare_travel()

    plans = prepare_plans()
    recurring = prepare_recurring()

    # -----------------------------------------------------
    # Aggregate actual data
    # -----------------------------------------------------

    expenses_by_date = (
        aggregate_expenses_by_date(
            expenses
        )
    )

    income_by_date = (
        aggregate_income_by_date(
            income
        )
    )

    events_by_date = (
        aggregate_events_by_date(
            events
        )
    )

    health_by_date = (
        aggregate_health_by_date(
            health_records
        )
    )

    activities_by_date = (
        aggregate_activities_by_date(
            activities
        )
    )

    sleep_by_date = (
        aggregate_sleep_by_date(
            sleep_records
        )
    )

    # -----------------------------------------------------
    # Aggregate planned data
    # -----------------------------------------------------

    plans_by_date = (
        aggregate_plans_by_date(
            plans
        )
    )

    active_plans_by_date = (
        expand_plans_by_date(
            plans
        )
    )

    # -----------------------------------------------------
    # Build initial historical dates
    # -----------------------------------------------------

    historical_dates = set()

    historical_dates.update(
        row['Date']
        for row in days
    )

    historical_dates.update(
        expense['Date']
        for expense in expenses
    )

    historical_dates.update(
        record['Date']
        for record in income
    )

    historical_dates.update(
        event['Date']
        for event in events
    )

    historical_dates.update(
        record['Date']
        for record in health_records
    )

    historical_dates.update(
        activity['Date']
        for activity in activities
    )

    historical_dates.update(
        record['Date']
        for record in sleep_records
    )

    # -----------------------------------------------------
    # Travel historical dates
    # -----------------------------------------------------

    for travel in travel_records:

        current_date = (
            travel['Start_Date']
        )

        while current_date <= (
            travel['End_Date']
        ):

            historical_dates.add(
                current_date
            )

            current_date += timedelta(
                days=1
            )

    # -----------------------------------------------------
    # Continuous historical calendar
    # -----------------------------------------------------

    dates = build_historical_date_range(
        historical_dates
    )

    # -----------------------------------------------------
    # Planned dates
    #
    # Plans may legitimately introduce future dates.
    # We add only the dates explicitly represented by plans.
    # -----------------------------------------------------

    plan_dates = set()

    for plan in plans:

        plan_dates.add(
            plan['Plan_Date']
        )

        duration_days = int(
            max(
                1,
                plan['Duration_Days'] or 1,
            )
        )

        for offset in range(
            duration_days
        ):

            plan_dates.add(
                plan['Plan_Date']
                + timedelta(days=offset)
            )

        # Actual_Date is historical information when available.
        if plan['Actual_Date'] is not None:

            dates.add(
                plan['Actual_Date']
            )

    dates.update(
        plan_dates
    )

    # -----------------------------------------------------
    # Recurring activity
    #
    # Recurring does NOT create an arbitrary future horizon.
    #
    # It is evaluated against:
    #
    #   - historical calendar dates
    #   - known plan dates
    #
    # This allows recurring and plans to interact naturally.
    # -----------------------------------------------------

    recurring_evaluation_dates = set(
        dates
    )

    recurring_by_date = (
        aggregate_recurring_by_date(
            recurring,
            recurring_evaluation_dates,
        )
    )

    # -----------------------------------------------------
    # Build lookup for actual daily records
    # -----------------------------------------------------

    days_by_date = {
        row['Date']: row
        for row in days
    }

    # -----------------------------------------------------
    # Build final dataset
    # -----------------------------------------------------

    dataset = []

    for current_date in sorted(
        dates
    ):

        day = days_by_date.get(
            current_date
        )

        if day is None:

            day = {
                'Date':
                    current_date,

                'Day_Type':
                    None,

                'Work_Status':
                    None,

                'Health_Impact':
                    None,

                'Travel':
                    None,

                'Special_Event':
                    None,

                'Stress_Level':
                    0.0,

                'Notes':
                    None,

                'Sleep_Hours':
                    0.0,

                'Social_Activity':
                    None,

                'Location':
                    None,
            }

        row = dict(day)

        # -------------------------------------------------
        # Actual data
        # -------------------------------------------------

        expense_data = (
            expenses_by_date.get(
                current_date,
                {
                    'expense_total': 0.0,
                    'expense_count': 0,
                },
            )
        )

        income_data = (
            income_by_date.get(
                current_date,
                {
                    'income_total': 0.0,
                    'income_count': 0,
                },
            )
        )

        event_data = (
            events_by_date.get(
                current_date,
                {
                    'event_count': 0,
                },
            )
        )

        health_data = (
            health_by_date.get(
                current_date,
                {
                    'health_record_count': 0,
                    'max_health_severity': 0.0,
                    'avg_energy_level': 0.0,
                },
            )
        )

        activity_data = (
            activities_by_date.get(
                current_date,
                {
                    'activity_count': 0,
                    'activity_duration_minutes': 0.0,
                    'activity_cost': 0.0,
                },
            )
        )

        sleep_data = (
            sleep_by_date.get(
                current_date,
                {
                    'sleep_record_count': 0,
                    'sleep_duration_minutes': 0.0,
                    'avg_sleep_quality': 0.0,
                    'total_awakenings': 0.0,
                },
            )
        )

        # -------------------------------------------------
        # Plans
        # -------------------------------------------------

        plan_data = (
            plans_by_date.get(
                current_date,
                {
                    'plan_count': 0,
                    'plan_expected_cost': 0.0,
                    'plan_duration_days': 0.0,
                    'high_importance_plan_count': 0,
                },
            )
        )

        active_plan_data = (
            active_plans_by_date.get(
                current_date,
                {
                    'active_plan_count': 0,
                    'active_plan_expected_cost': 0.0,
                    'active_high_importance_plan_count': 0,
                },
            )
        )

        # -------------------------------------------------
        # Recurring
        # -------------------------------------------------

        recurring_data = (
            recurring_by_date.get(
                current_date,
                {
                    'recurring_count': 0,
                    'recurring_amount': 0.0,
                    'recurring_expense_amount': 0.0,
                    'recurring_income_amount': 0.0,
                    'fixed_recurring_amount': 0.0,
                },
            )
        )

        # -------------------------------------------------
        # Actual Financial Data
        # -------------------------------------------------

        row.update({

            'Expense_Total':
                expense_data[
                    'expense_total'
                ],

            'Expense_Count':
                expense_data[
                    'expense_count'
                ],

            'Income_Total':
                income_data[
                    'income_total'
                ],

            'Income_Count':
                income_data[
                    'income_count'
                ],

            # -------------------------------------------------
            # Events
            # -------------------------------------------------

            'Event_Count':
                event_data[
                    'event_count'
                ],

            # -------------------------------------------------
            # Health
            # -------------------------------------------------

            'Health_Record_Count':
                health_data[
                    'health_record_count'
                ],

            'Max_Health_Severity':
                health_data[
                    'max_health_severity'
                ],

            'Avg_Energy_Level':
                health_data[
                    'avg_energy_level'
                ],

            # -------------------------------------------------
            # Activities
            # -------------------------------------------------

            'Activity_Count':
                activity_data[
                    'activity_count'
                ],

            'Activity_Duration_Minutes':
                activity_data[
                    'activity_duration_minutes'
                ],

            'Activity_Cost':
                activity_data[
                    'activity_cost'
                ],

            # -------------------------------------------------
            # Sleep
            # -------------------------------------------------

            'Sleep_Record_Count':
                sleep_data[
                    'sleep_record_count'
                ],

            'Sleep_Duration_Minutes':
                sleep_data[
                    'sleep_duration_minutes'
                ],

            'Avg_Sleep_Quality':
                sleep_data[
                    'avg_sleep_quality'
                ],

            'Total_Awakenings':
                sleep_data[
                    'total_awakenings'
                ],

            # -------------------------------------------------
            # Plans - explicit date
            # -------------------------------------------------

            'Plan_Count':
                plan_data[
                    'plan_count'
                ],

            'Plan_Expected_Cost':
                plan_data[
                    'plan_expected_cost'
                ],

            'Plan_Duration_Days':
                plan_data[
                    'plan_duration_days'
                ],

            'High_Importance_Plan_Count':
                plan_data[
                    'high_importance_plan_count'
                ],

            # -------------------------------------------------
            # Plans - active duration
            # -------------------------------------------------

            'Active_Plan_Count':
                active_plan_data[
                    'active_plan_count'
                ],

            'Active_Plan_Expected_Cost':
                active_plan_data[
                    'active_plan_expected_cost'
                ],

            'Active_High_Importance_Plan_Count':
                active_plan_data[
                    'active_high_importance_plan_count'
                ],

            # -------------------------------------------------
            # Recurring - expected activity
            # -------------------------------------------------

            'Recurring_Count':
                recurring_data[
                    'recurring_count'
                ],

            'Recurring_Amount':
                recurring_data[
                    'recurring_amount'
                ],

            'Recurring_Expense_Amount':
                recurring_data[
                    'recurring_expense_amount'
                ],

            'Recurring_Income_Amount':
                recurring_data[
                    'recurring_income_amount'
                ],

            'Fixed_Recurring_Amount':
                recurring_data[
                    'fixed_recurring_amount'
                ],
        })

        dataset.append(
            row
        )

    dataset.sort(
        key=lambda row: row['Date']
    )

    return dataset


# =========================================================
# PUBLIC ENTRY POINT
# =========================================================

def get_prepared_dataset():
    """
    Public entry point for Data Preparation.

    Returns a unified daily dataset ready for
    Feature Engineering.

    The dataset keeps a clear separation between:

        Actual:
            Expense_Total
            Income_Total
            Event_Count
            etc.

        Planned:
            Plan_Count
            Plan_Expected_Cost
            Active_Plan_Count
            etc.

        Expected recurring:
            Recurring_Count
            Recurring_Amount
            Recurring_Expense_Amount
            Recurring_Income_Amount
            Fixed_Recurring_Amount
    """

    return build_daily_dataset()