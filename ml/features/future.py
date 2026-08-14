from datetime import date, datetime


# ==========================================================
# HELPERS
# ==========================================================

def normalize_text(value):
    """
    Safely normalize a value into lowercase text.
    """

    return str(
        value or ''
    ).strip().lower()


def to_date(value):
    """
    Safely convert a value to a date.

    Supported values:
        - date
        - datetime
        - ISO date string
        - None
    """

    if value is None:
        return None

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    if isinstance(value, str):

        value = value.strip()

        if not value:
            return None

        try:
            return datetime.fromisoformat(
                value
            ).date()

        except ValueError:
            try:
                return datetime.strptime(
                    value,
                    '%Y-%m-%d',
                ).date()

            except ValueError:
                return None

    return None


def safe_float(value):
    """
    Safely convert a value to float.
    """

    try:
        return float(
            value or 0
        )

    except (
        TypeError,
        ValueError,
    ):
        return 0.0


def safe_int(value):
    """
    Safely convert a value to integer.
    """

    try:
        return int(
            float(
                value or 0
            )
        )

    except (
        TypeError,
        ValueError,
    ):
        return 0


# ==========================================================
# PLAN FEATURES
# ==========================================================

def create_plan_features(
    target_date,
    plans=None,
):
    """
    Create features from plans known for the target date.

    IMPORTANT:

        Only information that could be known before the
        target day is used.

        Actual_Date and Actual_Cost are NEVER used.

    Expected information includes:

        - number of plans
        - expected total cost
        - duration
        - importance
        - plan type
        - active/planned status
    """

    target_date = to_date(
        target_date
    )

    result = {
        'Plan_Count': 0,
        'Plan_Expected_Cost_Total': 0.0,
        'Plan_Duration_Total': 0,
        'Plan_High_Importance_Count': 0,
        'Plan_Medium_Importance_Count': 0,
        'Plan_Low_Importance_Count': 0,

        'Plan_Travel_Count': 0,
        'Plan_Medical_Count': 0,
        'Plan_Family_Count': 0,
        'Plan_Purchase_Count': 0,
        'Plan_Social_Count': 0,
        'Plan_Other_Count': 0,

        'Plan_Has_Travel': 0,
        'Plan_Has_Medical': 0,
        'Plan_Has_Family': 0,
        'Plan_Has_Purchase': 0,
        'Plan_Has_Social': 0,
    }

    if not target_date or not plans:
        return result

    for plan in plans:

        plan_date = to_date(
            plan.get(
                'Plan_Date'
            )
        )

        if plan_date != target_date:
            continue

        status = normalize_text(
            plan.get(
                'Status'
            )
        )

        # Completed/cancelled plans should not describe
        # an upcoming target day.
        if status in {
            'cancelled',
            'canceled',
        }:
            continue

        result[
            'Plan_Count'
        ] += 1

        result[
            'Plan_Expected_Cost_Total'
        ] += safe_float(
            plan.get(
                'Expected_Cost'
            )
        )

        result[
            'Plan_Duration_Total'
        ] += safe_int(
            plan.get(
                'Duration_Days'
            )
        )

        importance = normalize_text(
            plan.get(
                'Importance'
            )
        )

        if importance == 'high':
            result[
                'Plan_High_Importance_Count'
            ] += 1

        elif importance == 'medium':
            result[
                'Plan_Medium_Importance_Count'
            ] += 1

        elif importance == 'low':
            result[
                'Plan_Low_Importance_Count'
            ] += 1

        plan_type = normalize_text(
            plan.get(
                'Plan_Type'
            )
        )

        if plan_type == 'travel':
            result[
                'Plan_Travel_Count'
            ] += 1

        elif plan_type == 'medical':
            result[
                'Plan_Medical_Count'
            ] += 1

        elif plan_type == 'family':
            result[
                'Plan_Family_Count'
            ] += 1

        elif plan_type == 'purchase':
            result[
                'Plan_Purchase_Count'
            ] += 1

        elif plan_type == 'social':
            result[
                'Plan_Social_Count'
            ] += 1

        else:
            result[
                'Plan_Other_Count'
            ] += 1

    result[
        'Plan_Has_Travel'
    ] = int(
        result[
            'Plan_Travel_Count'
        ] > 0
    )

    result[
        'Plan_Has_Medical'
    ] = int(
        result[
            'Plan_Medical_Count'
        ] > 0
    )

    result[
        'Plan_Has_Family'
    ] = int(
        result[
            'Plan_Family_Count'
        ] > 0
    )

    result[
        'Plan_Has_Purchase'
    ] = int(
        result[
            'Plan_Purchase_Count'
        ] > 0
    )

    result[
        'Plan_Has_Social'
    ] = int(
        result[
            'Plan_Social_Count'
        ] > 0
    )

    return result


# ==========================================================
# RECURRING FEATURES
# ==========================================================

def recurring_applies_to_date(
    recurring,
    target_date,
):
    """
    Determine whether a recurring record applies
    to the target date.
    """

    target_date = to_date(
        target_date
    )

    if not target_date:
        return False

    if not recurring.get(
        'Is_Active'
    ):
        return False

    start_date = to_date(
        recurring.get(
            'Start_Date'
        )
    )

    end_date = to_date(
        recurring.get(
            'End_Date'
        )
    )

    if start_date and target_date < start_date:
        return False

    if end_date and target_date > end_date:
        return False

    frequency = normalize_text(
        recurring.get(
            'Frequency'
        )
    )

    if frequency in {
        'daily',
        'day',
    }:
        return True

    if frequency in {
        'weekly',
        'week',
    }:
        day_of_week = safe_int(
            recurring.get(
                'Day_Of_Week'
            )
        )

        return (
            day_of_week == target_date.weekday()
        )

    if frequency in {
        'monthly',
        'month',
    }:
        day_of_month = safe_int(
            recurring.get(
                'Day_Of_Month'
            )
        )

        return (
            day_of_month == target_date.day
        )

    return False


def create_recurring_features(
    target_date,
    recurring=None,
):
    """
    Create features from recurring financial patterns
    that are expected to occur on the target date.

    These represent information known in advance.
    """

    result = {
        'Recurring_Count': 0,
        'Recurring_Income_Total': 0.0,
        'Recurring_Expense_Total': 0.0,
        'Recurring_Fixed_Income_Total': 0.0,
        'Recurring_Fixed_Expense_Total': 0.0,

        'Recurring_Income_Count': 0,
        'Recurring_Expense_Count': 0,

        'Recurring_Daily_Count': 0,
        'Recurring_Weekly_Count': 0,
        'Recurring_Monthly_Count': 0,

        'Recurring_Has_Income': 0,
        'Recurring_Has_Expense': 0,
    }

    if not recurring:
        return result

    for item in recurring:

        if not recurring_applies_to_date(
            item,
            target_date,
        ):
            continue

        result[
            'Recurring_Count'
        ] += 1

        amount = safe_float(
            item.get(
                'Amount'
            )
        )

        recurring_type = normalize_text(
            item.get(
                'Type'
            )
        )

        frequency = normalize_text(
            item.get(
                'Frequency'
            )
        )

        is_fixed = bool(
            item.get(
                'Is_Fixed_Amount'
            )
        )

        if recurring_type in {
            'income',
            'in',
        }:

            result[
                'Recurring_Income_Count'
            ] += 1

            result[
                'Recurring_Income_Total'
            ] += amount

            if is_fixed:
                result[
                    'Recurring_Fixed_Income_Total'
                ] += amount

        elif recurring_type in {
            'expense',
            'out',
        }:

            result[
                'Recurring_Expense_Count'
            ] += 1

            result[
                'Recurring_Expense_Total'
            ] += amount

            if is_fixed:
                result[
                    'Recurring_Fixed_Expense_Total'
                ] += amount

        if frequency in {
            'daily',
            'day',
        }:
            result[
                'Recurring_Daily_Count'
            ] += 1

        elif frequency in {
            'weekly',
            'week',
        }:
            result[
                'Recurring_Weekly_Count'
            ] += 1

        elif frequency in {
            'monthly',
            'month',
        }:
            result[
                'Recurring_Monthly_Count'
            ] += 1

    result[
        'Recurring_Has_Income'
    ] = int(
        result[
            'Recurring_Income_Count'
        ] > 0
    )

    result[
        'Recurring_Has_Expense'
    ] = int(
        result[
            'Recurring_Expense_Count'
        ] > 0
    )

    return result


# ==========================================================
# COMBINED FUTURE FEATURES
# ==========================================================

def create_future_features(
    target_date,
    plans=None,
    recurring=None,
):
    """
    Create all features representing information known
    in advance about the target date.
    """

    features = {}

    features.update(
        create_plan_features(
            target_date,
            plans,
        )
    )

    features.update(
        create_recurring_features(
            target_date,
            recurring,
        )
    )

    return features