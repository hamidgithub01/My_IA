
from ml.preparation.preparation import get_prepared_dataset


# =========================================================
# TIME FEATURES
# =========================================================

def build_time_features(record):
    """
    Build calendar-based features from the record date.
    """

    current_date = record['Date']

    return {
        'Year': current_date.year,

        'Month': current_date.month,

        'Day_Of_Month': current_date.day,

        'Day_Of_Week': current_date.weekday(),

        'Is_Weekend':
            int(current_date.weekday() >= 5),
    }


# =========================================================
# FINANCIAL FEATURES
# =========================================================

def build_financial_features(record):
    """
    Build financial features.

    These features describe the financial activity
    observed on the current calendar day.
    """

    expense_total = float(
        record.get('Expense_Total', 0.0)
    )

    income_total = float(
        record.get('Income_Total', 0.0)
    )

    expense_count = int(
        record.get('Expense_Count', 0)
    )

    income_count = int(
        record.get('Income_Count', 0)
    )

    recurring_expense = float(
        record.get(
            'Recurring_Expense_Amount',
            0.0,
        )
    )

    recurring_income = float(
        record.get(
            'Recurring_Income_Amount',
            0.0,
        )
    )

    return {
        'Expense_Total':
            expense_total,

        'Expense_Count':
            expense_count,

        'Income_Total':
            income_total,

        'Income_Count':
            income_count,

        'Net_Cash_Flow':
            income_total - expense_total,

        'Has_Expenses':
            int(expense_count > 0),

        'Has_Income':
            int(income_count > 0),

        'Expense_Income_Ratio':
            (
                expense_total / income_total
                if income_total > 0
                else 0.0
            ),

        'Recurring_Expense_Amount':
            recurring_expense,

        'Recurring_Income_Amount':
            recurring_income,

        'Recurring_Net_Flow':
            recurring_income - recurring_expense,
    }


# =========================================================
# PLAN FEATURES
# =========================================================

def build_plan_features(record):
    """
    Build features related to planned activities.
    """

    plan_count = int(
        record.get('Plan_Count', 0)
    )

    expected_cost = float(
        record.get(
            'Plan_Expected_Cost',
            0.0,
        )
    )

    duration_days = float(
        record.get(
            'Plan_Duration_Days',
            0.0,
        )
    )

    high_importance_count = int(
        record.get(
            'High_Importance_Plan_Count',
            0,
        )
    )

    return {
        'Plan_Count':
            plan_count,

        'Plan_Expected_Cost':
            expected_cost,

        'Plan_Duration_Days':
            duration_days,

        'High_Importance_Plan_Count':
            high_importance_count,

        'Has_Plans':
            int(plan_count > 0),

        'Has_High_Importance_Plan':
            int(high_importance_count > 0),
    }


# =========================================================
# RECURRING FEATURES
# =========================================================

def build_recurring_features(record):
    """
    Build features related to recurring financial records.
    """

    recurring_count = int(
        record.get(
            'Recurring_Count',
            0,
        )
    )

    recurring_amount = float(
        record.get(
            'Recurring_Amount',
            0.0,
        )
    )

    recurring_expense = float(
        record.get(
            'Recurring_Expense_Amount',
            0.0,
        )
    )

    recurring_income = float(
        record.get(
            'Recurring_Income_Amount',
            0.0,
        )
    )

    fixed_amount = float(
        record.get(
            'Fixed_Recurring_Amount',
            0.0,
        )
    )

    active_count = int(
        record.get(
            'Active_Recurring_Count',
            0,
        )
    )

    return {
        'Recurring_Count':
            recurring_count,

        'Recurring_Amount':
            recurring_amount,

        'Recurring_Expense_Amount':
            recurring_expense,

        'Recurring_Income_Amount':
            recurring_income,

        'Fixed_Recurring_Amount':
            fixed_amount,

        'Active_Recurring_Count':
            active_count,

        'Has_Recurring':
            int(recurring_count > 0),

        'Has_Active_Recurring':
            int(active_count > 0),

        'Has_Fixed_Recurring':
            int(fixed_amount > 0),
    }


# =========================================================
# HEALTH FEATURES
# =========================================================

def build_health_features(record):
    """
    Build numerical health-related features.
    """

    health_records = int(
        record.get(
            'Health_Record_Count',
            0,
        )
    )

    severity = float(
        record.get(
            'Max_Health_Severity',
            0.0,
        )
    )

    energy = float(
        record.get(
            'Avg_Energy_Level',
            0.0,
        )
    )

    stress = float(
        record.get(
            'Stress_Level',
            0.0,
        )
    )

    return {
        'Health_Record_Count':
            health_records,

        'Max_Health_Severity':
            severity,

        'Avg_Energy_Level':
            energy,

        'Stress_Level':
            stress,

        'Has_Health_Record':
            int(health_records > 0),

        'Has_Health_Severity':
            int(severity > 0),

        'High_Stress':
            int(stress >= 7),
    }


# =========================================================
# ACTIVITY FEATURES
# =========================================================

def build_activity_features(record):
    """
    Build activity-related features.
    """

    activity_count = int(
        record.get(
            'Activity_Count',
            0,
        )
    )

    duration = float(
        record.get(
            'Activity_Duration_Minutes',
            0.0,
        )
    )

    cost = float(
        record.get(
            'Activity_Cost',
            0.0,
        )
    )

    return {
        'Activity_Count':
            activity_count,

        'Activity_Duration_Minutes':
            duration,

        'Activity_Cost':
            cost,

        'Has_Activity':
            int(activity_count > 0),

        'Activity_Duration_Hours':
            duration / 60.0,
    }


# =========================================================
# SLEEP FEATURES
# =========================================================

def build_sleep_features(record):
    """
    Build sleep-related numerical features.
    """

    sleep_records = int(
        record.get(
            'Sleep_Record_Count',
            0,
        )
    )

    duration = float(
        record.get(
            'Sleep_Duration_Minutes',
            0.0,
        )
    )

    quality = float(
        record.get(
            'Avg_Sleep_Quality',
            0.0,
        )
    )

    awakenings = float(
        record.get(
            'Total_Awakenings',
            0.0,
        )
    )

    return {
        'Sleep_Record_Count':
            sleep_records,

        'Sleep_Duration_Minutes':
            duration,

        'Sleep_Duration_Hours':
            duration / 60.0,

        'Avg_Sleep_Quality':
            quality,

        'Total_Awakenings':
            awakenings,

        'Has_Sleep_Data':
            int(sleep_records > 0),

        'Low_Sleep':
            int(
                0 < duration < 360
            ),
    }


# =========================================================
# EVENT FEATURES
# =========================================================

def build_event_features(record):
    """
    Build event-related features.
    """

    event_count = int(
        record.get(
            'Event_Count',
            0,
        )
    )

    return {
        'Event_Count':
            event_count,

        'Has_Event':
            int(event_count > 0),
    }


# =========================================================
# CATEGORICAL FEATURES
# =========================================================

def build_categorical_features(record):
    """
    Convert categorical values into numerical features.

    None / missing values are treated as absence of
    the corresponding categorical condition.

    The actual categories are based on the values
    currently present in the prepared dataset.
    """

    day_type = record.get(
        'Day_Type'
    )

    work_status = record.get(
        'Work_Status'
    )

    health_impact = record.get(
        'Health_Impact'
    )

    travel = record.get(
        'Travel'
    )

    special_event = record.get(
        'Special_Event'
    )

    social_activity = record.get(
        'Social_Activity'
    )

    location = record.get(
        'Location'
    )

    return {

        # -------------------------------------------------
        # DAY TYPE
        # -------------------------------------------------

        'Day_Type_Holiday':
            int(
                day_type == 'Holiday'
            ),

        # -------------------------------------------------
        # WORK STATUS
        # -------------------------------------------------

        'Work_Status_Off':
            int(
                work_status == 'Off'
            ),

        # -------------------------------------------------
        # HEALTH IMPACT
        # -------------------------------------------------

        'Health_Impact_Low':
            int(
                health_impact == 'Low'
            ),

        # -------------------------------------------------
        # TRAVEL
        # -------------------------------------------------

        'Travel_No':
            int(
                travel == 'No'
            ),

        # -------------------------------------------------
        # SPECIAL EVENTS
        # -------------------------------------------------

        'Special_Event_Family_Visit':
            int(
                special_event == 'Family visit'
            ),

        'Special_Event_Tagdisht_Issaguen_Festival':
            int(
                special_event ==
                'Tagdisht Issaguen Festiva'
            ),

        # -------------------------------------------------
        # SOCIAL ACTIVITY
        # -------------------------------------------------

        'Social_Activity_High':
            int(
                social_activity == 'High'
            ),

        'Social_Activity_Low':
            int(
                social_activity == 'Low'
            ),

        'Social_Activity_Moderate':
            int(
                social_activity == 'Moderate'
            ),

        # -------------------------------------------------
        # LOCATION
        # -------------------------------------------------

        'Location_Tagdicht_Issaguen':
            int(
                location == 'Tagdicht issaguen'
            ),
    }


# =========================================================
# DAILY FEATURES
# =========================================================

def build_daily_features(record):
    """
    Build numerical and categorical features
    for one prepared daily record.
    """

    features = {}

    features.update(
        build_time_features(record)
    )

    features.update(
        build_financial_features(record)
    )

    features.update(
        build_plan_features(record)
    )

    features.update(
        build_recurring_features(record)
    )

    features.update(
        build_health_features(record)
    )

    features.update(
        build_activity_features(record)
    )

    features.update(
        build_sleep_features(record)
    )

    features.update(
        build_event_features(record)
    )

    features.update(
        build_categorical_features(record)
    )

    return features


# =========================================================
# FEATURE DATASET
# =========================================================

def build_feature_dataset(prepared_dataset):
    feature_rows = []

    for record in prepared_dataset:

        features = build_daily_features(
            record
        )

        # Keep Date for chronological alignment.
        # Date is metadata, not an ML feature.
        features['Date'] = record['Date']

        feature_rows.append(
            features
        )

    return feature_rows


# =========================================================
# PUBLIC ENTRY POINT
# =========================================================

def get_feature_dataset():
    """
    Public entry point for Feature Engineering.

    Returns:
        list[dict]
    """

    prepared_dataset = get_prepared_dataset()

    return build_feature_dataset(
        prepared_dataset
    )
