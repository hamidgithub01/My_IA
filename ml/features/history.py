
from datetime import date, datetime

from ml.features.behavioral import (
    create_historical_behavioral_features,
)

from ml.features.contextual import (
    create_historical_contextual_features,
)


# ==========================================================
# DATE
# ==========================================================

def _to_date(value):
    """
    Convert a supported value into date.
    """

    if isinstance(
        value,
        datetime,
    ):
        return value.date()

    if isinstance(
        value,
        date,
    ):
        return value

    if isinstance(
        value,
        str,
    ):

        try:
            return date.fromisoformat(
                value[:10]
            )

        except ValueError:
            return None

    return None


# ==========================================================
# BASIC HELPERS
# ==========================================================

def _float(
    row,
    field,
):
    """
    Safely return a numeric field.
    """

    return float(
        row.get(field)
        or 0.0
    )


def _int(
    row,
    field,
):
    """
    Safely return an integer field.
    """

    return int(
        row.get(field)
        or 0
    )


def _average(
    rows,
    field,
):
    """
    Calculate the average of a numeric field.
    """

    if not rows:
        return 0.0

    return sum(
        _float(
            row,
            field,
        )
        for row in rows
    ) / len(rows)


def _average_balance(rows):
    """
    Calculate average daily balance.
    """

    if not rows:
        return 0.0

    values = [
        _float(
            row,
            'Income_Total',
        )
        -
        _float(
            row,
            'Expense_Total',
        )
        for row in rows
    ]

    return sum(values) / len(values)


# ==========================================================
# HISTORICAL ENCODED FEATURES
# ==========================================================

def _average_encoded_feature(
    rows,
    builder,
    feature_name,
):
    """
    Calculate the average of an encoded historical feature.
    """

    if not rows:
        return 0.0

    values = []

    for row in rows:

        encoded = builder(
            row
        )

        values.append(
            float(
                encoded.get(
                    feature_name,
                    0.0,
                )
            )
        )

    return sum(values) / len(values)


# ==========================================================
# HISTORY FEATURES
# ==========================================================

def create_history_features(
    row,
    previous_rows=None,
):
    """
    Create historical features using ONLY rows before
    the target date.

    IMPORTANT:

        The target row is NEVER used as historical data.

    Days information is recorded after the day ends.
    Therefore:

        Target-day Days information
            -> NEVER used here

        Previous-day Days information
            -> allowed

        Older Days information
            -> allowed

    This function converts historical observations into
    features that can be used to predict a future day.
    """

    previous_rows = (
        previous_rows
        or []
    )

    target_date = _to_date(
        row.get('Date')
    )

    # ======================================================
    # DEFAULT FEATURES
    # ======================================================

    features = {

        # --------------------------------------------------
        # Financial history
        # --------------------------------------------------

        'Previous_Day_Expense': 0.0,
        'Previous_Day_Income': 0.0,
        'Previous_Day_Balance': 0.0,
        'Previous_Day_Events': 0,

        # --------------------------------------------------
        # Health history
        # --------------------------------------------------

        'Previous_Day_Health_Records': 0,
        'Previous_Day_Health_Severity': 0.0,
        'Previous_Day_Energy': 0.0,

        # --------------------------------------------------
        # Activity history
        # --------------------------------------------------

        'Previous_Day_Activity_Count': 0,
        'Previous_Day_Activity_Duration': 0.0,
        'Previous_Day_Activity_Cost': 0.0,

        # --------------------------------------------------
        # Sleep history
        # --------------------------------------------------

        'Previous_Day_Sleep_Duration': 0.0,
        'Previous_Day_Sleep_Quality': 0.0,
        'Previous_Day_Awakenings': 0.0,

        # --------------------------------------------------
        # Behavioral history
        # --------------------------------------------------

        'Previous_Day_Day_Type_Code': 0,
        'Previous_Day_Work_Status_Code': 0,
        'Previous_Day_Health_Impact_Code': 0,
        'Previous_Day_Travel_Flag': 0,

        'Previous_Day_Stress_Level': 0.0,
        'Previous_Day_Sleep_Hours': 0.0,

        'Previous_Day_Social_Activity_Code': 0,
        'Previous_Day_Special_Event_Flag': 0,
        'Previous_Day_Location_Flag': 0,

        # --------------------------------------------------
        # Historical contextual features
        # --------------------------------------------------

        'Previous_Day_Is_Workday': 0,
        'Previous_Day_Is_Holiday': 0,
        'Previous_Day_Is_Weekend_Day': 0,

        'Previous_Day_Is_Working': 0,
        'Previous_Day_Is_Off': 0,
        'Previous_Day_Is_Leave': 0,

        'Previous_Day_Has_Health_Impact': 0,
        'Previous_Day_Has_Travel': 0,
        'Previous_Day_Has_Special_Event': 0,
        'Previous_Day_Has_Location': 0,

        # ==================================================
        # SAME WEEKDAY
        # ==================================================

        'Same_Weekday_Avg_Expense': 0.0,
        'Same_Weekday_Avg_Income': 0.0,
        'Same_Weekday_Avg_Balance': 0.0,
        'Same_Weekday_Avg_Events': 0.0,

        'Same_Weekday_Avg_Health_Severity': 0.0,
        'Same_Weekday_Avg_Energy': 0.0,

        'Same_Weekday_Avg_Activity_Duration': 0.0,
        'Same_Weekday_Avg_Activity_Cost': 0.0,

        'Same_Weekday_Avg_Sleep_Duration': 0.0,
        'Same_Weekday_Avg_Sleep_Quality': 0.0,
        'Same_Weekday_Avg_Awakenings': 0.0,

        # --------------------------------------------------
        # Behavioral patterns
        # --------------------------------------------------

        'Same_Weekday_Avg_Stress_Level': 0.0,
        'Same_Weekday_Avg_Sleep_Hours': 0.0,
        'Same_Weekday_Avg_Social_Activity': 0.0,

        # --------------------------------------------------
        # Contextual rates
        # --------------------------------------------------

        'Same_Weekday_Workday_Rate': 0.0,
        'Same_Weekday_Holiday_Rate': 0.0,
        'Same_Weekday_Weekend_Rate': 0.0,

        'Same_Weekday_Working_Rate': 0.0,
        'Same_Weekday_Off_Rate': 0.0,
        'Same_Weekday_Leave_Rate': 0.0,

        'Same_Weekday_Travel_Rate': 0.0,
        'Same_Weekday_Special_Event_Rate': 0.0,
        'Same_Weekday_Health_Impact_Rate': 0.0,
        'Same_Weekday_Location_Rate': 0.0,

        'Same_Weekday_Count': 0,
    }

    if target_date is None:
        return features

    # ======================================================
    # PREVIOUS RECORDED DAY
    # ======================================================

    previous_day = None

    for historical_row in reversed(
        previous_rows
    ):

        historical_date = _to_date(
            historical_row.get('Date')
        )

        if historical_date is None:
            continue

        if historical_date < target_date:

            previous_day = historical_row

            break

    if previous_day is not None:

        # ==================================================
        # FINANCIAL
        # ==================================================

        previous_expense = _float(
            previous_day,
            'Expense_Total',
        )

        previous_income = _float(
            previous_day,
            'Income_Total',
        )

        features.update({

            'Previous_Day_Expense':
                previous_expense,

            'Previous_Day_Income':
                previous_income,

            'Previous_Day_Balance':
                previous_income
                - previous_expense,

            'Previous_Day_Events':
                _int(
                    previous_day,
                    'Event_Count',
                ),

            # ==============================================
            # HEALTH
            # ==============================================

            'Previous_Day_Health_Records':
                _int(
                    previous_day,
                    'Health_Record_Count',
                ),

            'Previous_Day_Health_Severity':
                _float(
                    previous_day,
                    'Max_Health_Severity',
                ),

            'Previous_Day_Energy':
                _float(
                    previous_day,
                    'Avg_Energy_Level',
                ),

            # ==============================================
            # ACTIVITY
            # ==============================================

            'Previous_Day_Activity_Count':
                _int(
                    previous_day,
                    'Activity_Count',
                ),

            'Previous_Day_Activity_Duration':
                _float(
                    previous_day,
                    'Activity_Duration_Minutes',
                ),

            'Previous_Day_Activity_Cost':
                _float(
                    previous_day,
                    'Activity_Cost',
                ),

            # ==============================================
            # SLEEP
            # ==============================================

            'Previous_Day_Sleep_Duration':
                _float(
                    previous_day,
                    'Sleep_Duration_Minutes',
                ),

            'Previous_Day_Sleep_Quality':
                _float(
                    previous_day,
                    'Avg_Sleep_Quality',
                ),

            'Previous_Day_Awakenings':
                _float(
                    previous_day,
                    'Total_Awakenings',
                ),
        })

        # ==================================================
        # HISTORICAL BEHAVIORAL DATA
        # ==================================================

        behavioral = (
            create_historical_behavioral_features(
                previous_day
            )
        )

        features.update({

            'Previous_Day_Day_Type_Code':
                behavioral[
                    'Historical_Day_Type_Code'
                ],

            'Previous_Day_Work_Status_Code':
                behavioral[
                    'Historical_Work_Status_Code'
                ],

            'Previous_Day_Health_Impact_Code':
                behavioral[
                    'Historical_Health_Impact_Code'
                ],

            'Previous_Day_Travel_Flag':
                behavioral[
                    'Historical_Travel_Flag'
                ],

            'Previous_Day_Stress_Level':
                behavioral[
                    'Historical_Stress_Level'
                ],

            'Previous_Day_Sleep_Hours':
                behavioral[
                    'Historical_Sleep_Hours'
                ],

            'Previous_Day_Social_Activity_Code':
                behavioral[
                    'Historical_Social_Activity_Code'
                ],

            'Previous_Day_Special_Event_Flag':
                behavioral[
                    'Historical_Special_Event_Flag'
                ],

            'Previous_Day_Location_Flag':
                behavioral[
                    'Historical_Location_Flag'
                ],
        })

        # ==================================================
        # HISTORICAL CONTEXTUAL DATA
        # ==================================================

        contextual = (
            create_historical_contextual_features(
                previous_day
            )
        )

        features.update({

            'Previous_Day_Is_Workday':
                contextual[
                    'Historical_Is_Workday'
                ],

            'Previous_Day_Is_Holiday':
                contextual[
                    'Historical_Is_Holiday'
                ],

            'Previous_Day_Is_Weekend_Day':
                contextual[
                    'Historical_Is_Weekend_Day'
                ],

            'Previous_Day_Is_Working':
                contextual[
                    'Historical_Is_Working'
                ],

            'Previous_Day_Is_Off':
                contextual[
                    'Historical_Is_Off'
                ],

            'Previous_Day_Is_Leave':
                contextual[
                    'Historical_Is_Leave'
                ],

            'Previous_Day_Has_Health_Impact':
                contextual[
                    'Historical_Has_Health_Impact'
                ],

            'Previous_Day_Has_Travel':
                contextual[
                    'Historical_Has_Travel'
                ],

            'Previous_Day_Has_Special_Event':
                contextual[
                    'Historical_Has_Special_Event'
                ],

            'Previous_Day_Has_Location':
                contextual[
                    'Historical_Has_Location'
                ],
        })

    # ======================================================
    # SAME WEEKDAY HISTORY
    # ======================================================

    same_weekday = []

    for historical_row in previous_rows:

        historical_date = _to_date(
            historical_row.get('Date')
        )

        if historical_date is None:
            continue

        if historical_date >= target_date:
            continue

        if (
            historical_date.weekday()
            == target_date.weekday()
        ):

            same_weekday.append(
                historical_row
            )

    if same_weekday:

        # ==================================================
        # FINANCIAL
        # ==================================================

        features.update({

            'Same_Weekday_Avg_Expense':
                _average(
                    same_weekday,
                    'Expense_Total',
                ),

            'Same_Weekday_Avg_Income':
                _average(
                    same_weekday,
                    'Income_Total',
                ),

            'Same_Weekday_Avg_Balance':
                _average_balance(
                    same_weekday
                ),

            'Same_Weekday_Avg_Events':
                _average(
                    same_weekday,
                    'Event_Count',
                ),

            # ==================================================
            # HEALTH
            # ==================================================

            'Same_Weekday_Avg_Health_Severity':
                _average(
                    same_weekday,
                    'Max_Health_Severity',
                ),

            'Same_Weekday_Avg_Energy':
                _average(
                    same_weekday,
                    'Avg_Energy_Level',
                ),

            # ==================================================
            # ACTIVITY
            # ==================================================

            'Same_Weekday_Avg_Activity_Duration':
                _average(
                    same_weekday,
                    'Activity_Duration_Minutes',
                ),

            'Same_Weekday_Avg_Activity_Cost':
                _average(
                    same_weekday,
                    'Activity_Cost',
                ),

            # ==================================================
            # SLEEP
            # ==================================================

            'Same_Weekday_Avg_Sleep_Duration':
                _average(
                    same_weekday,
                    'Sleep_Duration_Minutes',
                ),

            'Same_Weekday_Avg_Sleep_Quality':
                _average(
                    same_weekday,
                    'Avg_Sleep_Quality',
                ),

            'Same_Weekday_Avg_Awakenings':
                _average(
                    same_weekday,
                    'Total_Awakenings',
                ),

            # ==================================================
            # BEHAVIOR
            # ==================================================

            'Same_Weekday_Avg_Stress_Level':
                _average(
                    same_weekday,
                    'Stress_Level',
                ),

            'Same_Weekday_Avg_Sleep_Hours':
                _average(
                    same_weekday,
                    'Sleep_Hours',
                ),

            'Same_Weekday_Avg_Social_Activity':
                _average_encoded_feature(
                    same_weekday,
                    create_historical_behavioral_features,
                    'Historical_Social_Activity_Code',
                ),

            # ==================================================
            # CONTEXTUAL PATTERNS
            # ==================================================

            'Same_Weekday_Workday_Rate':
                _average_encoded_feature(
                    same_weekday,
                    create_historical_contextual_features,
                    'Historical_Is_Workday',
                ),

            'Same_Weekday_Holiday_Rate':
                _average_encoded_feature(
                    same_weekday,
                    create_historical_contextual_features,
                    'Historical_Is_Holiday',
                ),

            'Same_Weekday_Weekend_Rate':
                _average_encoded_feature(
                    same_weekday,
                    create_historical_contextual_features,
                    'Historical_Is_Weekend_Day',
                ),

            'Same_Weekday_Working_Rate':
                _average_encoded_feature(
                    same_weekday,
                    create_historical_contextual_features,
                    'Historical_Is_Working',
                ),

            'Same_Weekday_Off_Rate':
                _average_encoded_feature(
                    same_weekday,
                    create_historical_contextual_features,
                    'Historical_Is_Off',
                ),

            'Same_Weekday_Leave_Rate':
                _average_encoded_feature(
                    same_weekday,
                    create_historical_contextual_features,
                    'Historical_Is_Leave',
                ),

            'Same_Weekday_Travel_Rate':
                _average_encoded_feature(
                    same_weekday,
                    create_historical_contextual_features,
                    'Historical_Has_Travel',
                ),

            'Same_Weekday_Special_Event_Rate':
                _average_encoded_feature(
                    same_weekday,
                    create_historical_contextual_features,
                    'Historical_Has_Special_Event',
                ),

            'Same_Weekday_Health_Impact_Rate':
                _average_encoded_feature(
                    same_weekday,
                    create_historical_contextual_features,
                    'Historical_Has_Health_Impact',
                ),

            'Same_Weekday_Location_Rate':
                _average_encoded_feature(
                    same_weekday,
                    create_historical_contextual_features,
                    'Historical_Has_Location',
                ),

            'Same_Weekday_Count':
                len(same_weekday),
        })

    return features
