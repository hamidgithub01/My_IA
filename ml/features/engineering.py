from datetime import date

import pandas as pd

from ml.preparation.preparation import (
    get_prepared_dataset,
)


# =========================================================
# CONFIGURATION
# =========================================================

# Number of previous days used for historical features.
DEFAULT_ROLLING_WINDOWS = (3, 7, 30)


# =========================================================
# SAFE HELPERS
# =========================================================

def safe_divide(
    numerator,
    denominator,
):
    """
    Safely divide two numeric values.

    Returns 0.0 when the denominator is zero
    or the result is not finite.
    """

    numerator = pd.to_numeric(
        numerator,
        errors='coerce',
    )

    denominator = pd.to_numeric(
        denominator,
        errors='coerce',
    )

    result = numerator.div(
        denominator.replace(
            0,
            pd.NA,
        )
    )

    return (
        result
        .replace(
            [float('inf'), float('-inf')],
            pd.NA,
        )
        .fillna(0.0)
    )


def normalize_text_series(series):
    """
    Normalize text values for feature engineering.
    """

    return (
        series
        .fillna('')
        .astype(str)
        .str.strip()
        .str.lower()
    )


def add_binary_feature(
    dataframe,
    source_column,
    target_column,
    positive_values,
):
    """
    Create a binary feature from a text column.

    Example:

        Work_Status == 'work'
        -> Is_Work_Day
    """

    if source_column not in dataframe.columns:
        dataframe[target_column] = 0
        return

    normalized = normalize_text_series(
        dataframe[source_column]
    )

    dataframe[target_column] = (
        normalized
        .isin(
            {
                str(value).strip().lower()
                for value in positive_values
            }
        )
        .astype(int)
    )


# =========================================================
# DATAFRAME CREATION
# =========================================================

def create_dataframe():
    """
    Load the prepared daily dataset.

    The Data Preparation layer remains the only source
    of raw data for this stage.
    """

    records = get_prepared_dataset()

    if records is None:
        return pd.DataFrame()

    if not records:
        return pd.DataFrame()

    dataframe = pd.DataFrame(
        records
    )

    return dataframe


# =========================================================
# BASIC NORMALIZATION
# =========================================================

def normalize_dataframe(
    dataframe,
):
    """
    Normalize basic data types before feature engineering.
    """

    dataframe = dataframe.copy()

    if 'Date' not in dataframe.columns:
        raise ValueError(
            "Feature Engineering requires a 'Date' column."
        )

    dataframe['Date'] = pd.to_datetime(
        dataframe['Date'],
        errors='coerce',
    )

    dataframe = dataframe.dropna(
        subset=['Date']
    )

    dataframe = dataframe.sort_values(
        'Date'
    ).reset_index(
        drop=True
    )

    # -----------------------------------------------------
    # Numeric columns
    # -----------------------------------------------------

    numeric_columns = [
        'Stress_Level',
        'Sleep_Hours',

        'Expense_Total',
        'Expense_Count',

        'Income_Total',
        'Income_Count',

        'Event_Count',

        'Health_Record_Count',
        'Max_Health_Severity',
        'Avg_Energy_Level',

        'Activity_Count',
        'Activity_Duration_Minutes',
        'Activity_Cost',

        'Sleep_Record_Count',
        'Sleep_Duration_Minutes',
        'Avg_Sleep_Quality',
        'Total_Awakenings',

        'Plan_Count',
        'Plan_Expected_Cost',
        'Plan_Duration_Days',
        'High_Importance_Plan_Count',

        'Recurring_Count',
        'Recurring_Amount',
        'Recurring_Expense_Amount',
        'Recurring_Income_Amount',
        'Fixed_Recurring_Amount',
        'Active_Recurring_Count',
    ]

    for column in numeric_columns:

        if column in dataframe.columns:

            dataframe[column] = pd.to_numeric(
                dataframe[column],
                errors='coerce',
            ).fillna(0.0)

    return dataframe


# =========================================================
# CALENDAR FEATURES
# =========================================================

def add_calendar_features(
    dataframe,
):
    """
    Add calendar-based features.
    """

    dataframe = dataframe.copy()

    dataframe['Year'] = (
        dataframe['Date'].dt.year
    )

    dataframe['Month'] = (
        dataframe['Date'].dt.month
    )

    dataframe['Day_Of_Month'] = (
        dataframe['Date'].dt.day
    )

    dataframe['Day_Of_Week'] = (
        dataframe['Date'].dt.weekday
    )

    dataframe['Week_Of_Year'] = (
        dataframe['Date'].dt.isocalendar().week
        .astype(int)
    )

    dataframe['Quarter'] = (
        dataframe['Date'].dt.quarter
    )

    dataframe['Is_Weekend'] = (
        dataframe['Day_Of_Week']
        .isin([5, 6])
        .astype(int)
    )

    dataframe['Is_Month_Start'] = (
        dataframe['Date']
        .dt.is_month_start
        .astype(int)
    )

    dataframe['Is_Month_End'] = (
        dataframe['Date']
        .dt.is_month_end
        .astype(int)
    )

    dataframe['Is_Quarter_Start'] = (
        dataframe['Date']
        .dt.is_quarter_start
        .astype(int)
    )

    dataframe['Is_Quarter_End'] = (
        dataframe['Date']
        .dt.is_quarter_end
        .astype(int)
    )

    # -----------------------------------------------------
    # Cyclical calendar features
    # -----------------------------------------------------

    import numpy as np

    dataframe['Sin_Day_Of_Week'] = (
        np.sin(
            2
            * np.pi
            * dataframe['Day_Of_Week']
            / 7
        )
    )

    dataframe['Cos_Day_Of_Week'] = (
        np.cos(
            2
            * np.pi
            * dataframe['Day_Of_Week']
            / 7
        )
    )

    dataframe['Sin_Month'] = (
        np.sin(
            2
            * np.pi
            * dataframe['Month']
            / 12
        )
    )

    dataframe['Cos_Month'] = (
        np.cos(
            2
            * np.pi
            * dataframe['Month']
            / 12
        )
    )

    return dataframe


# =========================================================
# FINANCIAL FEATURES
# =========================================================

def add_financial_features(
    dataframe,
):
    """
    Create financial behavioral features.
    """

    dataframe = dataframe.copy()

    # -----------------------------------------------------
    # Basic financial balance
    # -----------------------------------------------------

    dataframe['Daily_Balance'] = (
        dataframe['Income_Total']
        - dataframe['Expense_Total']
    )

    dataframe['Net_Cashflow'] = (
        dataframe['Daily_Balance']
    )

    # -----------------------------------------------------
    # Average transaction values
    # -----------------------------------------------------

    dataframe['Average_Expense'] = safe_divide(
        dataframe['Expense_Total'],
        dataframe['Expense_Count'],
    )

    dataframe['Average_Income'] = safe_divide(
        dataframe['Income_Total'],
        dataframe['Income_Count'],
    )

    # -----------------------------------------------------
    # Expense / income ratios
    # -----------------------------------------------------

    dataframe['Expense_Income_Ratio'] = safe_divide(
        dataframe['Expense_Total'],
        dataframe['Income_Total'],
    )

    dataframe['Expense_To_Cashflow_Ratio'] = safe_divide(
        dataframe['Expense_Total'],
        dataframe['Daily_Balance'].abs(),
    )

    # -----------------------------------------------------
    # Recurring financial pressure
    # -----------------------------------------------------

    dataframe['Recurring_Expense_Ratio'] = safe_divide(
        dataframe['Recurring_Expense_Amount'],
        dataframe['Expense_Total'],
    )

    dataframe['Recurring_Income_Ratio'] = safe_divide(
        dataframe['Recurring_Income_Amount'],
        dataframe['Income_Total'],
    )

    dataframe['Fixed_Recurring_Ratio'] = safe_divide(
        dataframe['Fixed_Recurring_Amount'],
        dataframe['Recurring_Amount'],
    )

    # -----------------------------------------------------
    # Non-recurring financial activity
    # -----------------------------------------------------

    dataframe['Non_Recurring_Expense'] = (
        dataframe['Expense_Total']
        - dataframe['Recurring_Expense_Amount']
    ).clip(
        lower=0
    )

    dataframe['Non_Recurring_Income'] = (
        dataframe['Income_Total']
        - dataframe['Recurring_Income_Amount']
    ).clip(
        lower=0
    )

    return dataframe


# =========================================================
# HEALTH FEATURES
# =========================================================

def add_health_features(
    dataframe,
):
    """
    Create health-related features.
    """

    dataframe = dataframe.copy()

    dataframe['Has_Health_Record'] = (
        dataframe['Health_Record_Count']
        > 0
    ).astype(int)

    dataframe['Has_Health_Problem'] = (
        dataframe['Max_Health_Severity']
        > 0
    ).astype(int)

    dataframe['High_Health_Severity'] = (
        dataframe['Max_Health_Severity']
        >= 7
    ).astype(int)

    dataframe['Low_Energy'] = (
        (
            dataframe['Avg_Energy_Level']
            > 0
        )
        & (
            dataframe['Avg_Energy_Level']
            <= 3
        )
    ).astype(int)

    return dataframe


# =========================================================
# ACTIVITY FEATURES
# =========================================================

def add_activity_features(
    dataframe,
):
    """
    Create activity-related features.
    """

    dataframe = dataframe.copy()

    dataframe['Has_Activity'] = (
        dataframe['Activity_Count']
        > 0
    ).astype(int)

    dataframe['Average_Activity_Duration'] = safe_divide(
        dataframe['Activity_Duration_Minutes'],
        dataframe['Activity_Count'],
    )

    dataframe['Activity_Cost_Per_Minute'] = safe_divide(
        dataframe['Activity_Cost'],
        dataframe['Activity_Duration_Minutes'],
    )

    dataframe['Activity_Cost_Per_Activity'] = safe_divide(
        dataframe['Activity_Cost'],
        dataframe['Activity_Count'],
    )

    return dataframe


# =========================================================
# SLEEP FEATURES
# =========================================================

def add_sleep_features(
    dataframe,
):
    """
    Create sleep-related features.

    Sleep_Duration_Minutes is converted to hours,
    while the original field is preserved.
    """

    dataframe = dataframe.copy()

    dataframe['Sleep_Duration_Hours'] = (
        dataframe['Sleep_Duration_Minutes']
        / 60.0
    )

    dataframe['Average_Sleep_Duration_Minutes'] = (
        safe_divide(
            dataframe['Sleep_Duration_Minutes'],
            dataframe['Sleep_Record_Count'],
        )
    )

    dataframe['Awakenings_Per_Record'] = safe_divide(
        dataframe['Total_Awakenings'],
        dataframe['Sleep_Record_Count'],
    )

    dataframe['Has_Sleep_Record'] = (
        dataframe['Sleep_Record_Count']
        > 0
    ).astype(int)

    dataframe['Poor_Sleep_Quality'] = (
        (
            dataframe['Avg_Sleep_Quality']
            > 0
        )
        & (
            dataframe['Avg_Sleep_Quality']
            <= 3
        )
    ).astype(int)

    dataframe['Short_Sleep'] = (
        (
            dataframe['Sleep_Duration_Hours']
            > 0
        )
        & (
            dataframe['Sleep_Duration_Hours']
            < 6
        )
    ).astype(int)

    return dataframe


# =========================================================
# EVENT FEATURES
# =========================================================

def add_event_features(
    dataframe,
):
    """
    Create event-related features.
    """

    dataframe = dataframe.copy()

    dataframe['Has_Event'] = (
        dataframe['Event_Count']
        > 0
    ).astype(int)

    return dataframe


# =========================================================
# PLAN FEATURES
# =========================================================

def add_plan_features(
    dataframe,
):
    """
    Create plan-related features.

    Only planning information is used here.
    Actual outcomes are deliberately excluded.
    """

    dataframe = dataframe.copy()

    dataframe['Has_Plan'] = (
        dataframe['Plan_Count']
        > 0
    ).astype(int)

    dataframe['Average_Plan_Cost'] = safe_divide(
        dataframe['Plan_Expected_Cost'],
        dataframe['Plan_Count'],
    )

    dataframe['Average_Plan_Duration'] = safe_divide(
        dataframe['Plan_Duration_Days'],
        dataframe['Plan_Count'],
    )

    dataframe['High_Importance_Plan_Ratio'] = safe_divide(
        dataframe['High_Importance_Plan_Count'],
        dataframe['Plan_Count'],
    )

    return dataframe


# =========================================================
# RECURRING FEATURES
# =========================================================

def add_recurring_features(
    dataframe,
):
    """
    Create recurring-activity features.
    """

    dataframe = dataframe.copy()

    dataframe['Has_Recurring'] = (
        dataframe['Recurring_Count']
        > 0
    ).astype(int)

    dataframe['Recurring_Expense_Count_Ratio'] = safe_divide(
        dataframe['Recurring_Expense_Amount'],
        dataframe['Recurring_Amount'],
    )

    dataframe['Recurring_Income_Count_Ratio'] = safe_divide(
        dataframe['Recurring_Income_Amount'],
        dataframe['Recurring_Amount'],
    )

    dataframe['Recurring_Burden'] = (
        dataframe['Recurring_Expense_Amount']
    )

    dataframe['Recurring_Net_Impact'] = (
        dataframe['Recurring_Income_Amount']
        - dataframe['Recurring_Expense_Amount']
    )

    return dataframe


# =========================================================
# BEHAVIORAL FEATURES
# =========================================================

def add_behavioral_features(
    dataframe,
):
    """
    Create binary behavioral indicators from existing
    categorical daily information.

    Unknown categories are left untouched.
    """

    dataframe = dataframe.copy()

    # -----------------------------------------------------
    # Work
    # -----------------------------------------------------

    add_binary_feature(
        dataframe,
        'Work_Status',
        'Is_Work_Day',
        {
            'work',
            'working',
            'worked',
            'yes',
        },
    )

    # -----------------------------------------------------
    # Travel
    # -----------------------------------------------------

    add_binary_feature(
        dataframe,
        'Travel',
        'Is_Travel_Day',
        {
            'travel',
            'travelling',
            'traveling',
            'yes',
        },
    )

    # -----------------------------------------------------
    # Social activity
    # -----------------------------------------------------

    add_binary_feature(
        dataframe,
        'Social_Activity',
        'Has_Social_Activity',
        {
            'yes',
            'social',
            'active',
            'high',
        },
    )

    # -----------------------------------------------------
    # Special event
    # -----------------------------------------------------

    if 'Special_Event' in dataframe.columns:

        normalized = normalize_text_series(
            dataframe['Special_Event']
        )

        dataframe['Has_Special_Event'] = (
            normalized
            .ne('')
            .astype(int)
        )

    else:

        dataframe['Has_Special_Event'] = 0

    return dataframe


# =========================================================
# DAILY INTERACTION FEATURES
# =========================================================

def add_interaction_features(
    dataframe,
):
    """
    Create interpretable interactions between daily
    behavioral and financial variables.
    """

    dataframe = dataframe.copy()

    # -----------------------------------------------------
    # Stress and spending
    # -----------------------------------------------------

    dataframe['Stress_Expense_Interaction'] = (
        dataframe['Stress_Level']
        * dataframe['Expense_Total']
    )

    # -----------------------------------------------------
    # Health and spending
    # -----------------------------------------------------

    dataframe['Health_Expense_Interaction'] = (
        dataframe['Max_Health_Severity']
        * dataframe['Expense_Total']
    )

    # -----------------------------------------------------
    # Energy and activity
    # -----------------------------------------------------

    dataframe['Energy_Activity_Interaction'] = (
        dataframe['Avg_Energy_Level']
        * dataframe['Activity_Duration_Minutes']
    )

    # -----------------------------------------------------
    # Sleep and stress
    # -----------------------------------------------------

    dataframe['Sleep_Stress_Interaction'] = (
        dataframe['Sleep_Duration_Hours']
        * dataframe['Stress_Level']
    )

    # -----------------------------------------------------
    # Work and expenses
    # -----------------------------------------------------

    dataframe['Work_Expense_Interaction'] = (
        dataframe['Is_Work_Day']
        * dataframe['Expense_Total']
    )

    # -----------------------------------------------------
    # Weekend and expenses
    # -----------------------------------------------------

    dataframe['Weekend_Expense_Interaction'] = (
        dataframe['Is_Weekend']
        * dataframe['Expense_Total']
    )

    return dataframe


# =========================================================
# HISTORICAL FEATURES
# =========================================================

def add_lag_features(
    dataframe,
):
    """
    Create previous-day and previous-period features.

    IMPORTANT:

    All lag values come strictly from previous rows.
    Therefore they do not contain the current day's value.
    """

    dataframe = dataframe.copy()

    lag_columns = [
        'Expense_Total',
        'Income_Total',
        'Daily_Balance',
        'Expense_Count',
        'Income_Count',

        'Stress_Level',

        'Sleep_Duration_Minutes',
        'Avg_Sleep_Quality',

        'Activity_Duration_Minutes',
        'Activity_Count',

        'Max_Health_Severity',
        'Avg_Energy_Level',

        'Event_Count',
    ]

    lag_periods = [
        1,
        2,
        3,
        7,
    ]

    for column in lag_columns:

        if column not in dataframe.columns:
            continue

        for lag in lag_periods:

            dataframe[
                f'{column}_Lag_{lag}'
            ] = dataframe[
                column
            ].shift(
                lag
            )

    return dataframe


# =========================================================
# ROLLING FEATURES
# =========================================================

def add_rolling_features(
    dataframe,
    windows=None,
):
    """
    Create historical rolling features.

    The current day's value is excluded by using shift(1)
    before rolling calculations.

    This is essential for avoiding future leakage.
    """

    dataframe = dataframe.copy()

    if windows is None:
        windows = DEFAULT_ROLLING_WINDOWS

    rolling_columns = [
        'Expense_Total',
        'Income_Total',
        'Daily_Balance',

        'Stress_Level',

        'Sleep_Duration_Hours',
        'Avg_Sleep_Quality',

        'Activity_Duration_Minutes',

        'Max_Health_Severity',
        'Avg_Energy_Level',

        'Event_Count',
    ]

    for column in rolling_columns:

        if column not in dataframe.columns:
            continue

        historical = (
            dataframe[column]
            .shift(1)
        )

        for window in windows:

            dataframe[
                f'{column}_{window}D_Mean'
            ] = (
                historical
                .rolling(
                    window=window,
                    min_periods=1,
                )
                .mean()
            )

            dataframe[
                f'{column}_{window}D_Sum'
            ] = (
                historical
                .rolling(
                    window=window,
                    min_periods=1,
                )
                .sum()
            )

    return dataframe


# =========================================================
# TREND FEATURES
# =========================================================

def add_trend_features(
    dataframe,
):
    """
    Create simple historical trend features.

    These compare recent historical behavior against
    longer historical behavior.
    """

    dataframe = dataframe.copy()

    if (
        'Expense_Total_7D_Mean'
        in dataframe.columns
        and
        'Expense_Total_30D_Mean'
        in dataframe.columns
    ):

        dataframe['Expense_Trend'] = (
            dataframe['Expense_Total_7D_Mean']
            - dataframe['Expense_Total_30D_Mean']
        )

    else:

        dataframe['Expense_Trend'] = 0.0

    if (
        'Income_Total_7D_Mean'
        in dataframe.columns
        and
        'Income_Total_30D_Mean'
        in dataframe.columns
    ):

        dataframe['Income_Trend'] = (
            dataframe['Income_Total_7D_Mean']
            - dataframe['Income_Total_30D_Mean']
        )

    else:

        dataframe['Income_Trend'] = 0.0

    if (
        'Stress_Level_7D_Mean'
        in dataframe.columns
        and
        'Stress_Level_30D_Mean'
        in dataframe.columns
    ):

        dataframe['Stress_Trend'] = (
            dataframe['Stress_Level_7D_Mean']
            - dataframe['Stress_Level_30D_Mean']
        )

    else:

        dataframe['Stress_Trend'] = 0.0

    if (
        'Sleep_Duration_Hours_7D_Mean'
        in dataframe.columns
        and
        'Sleep_Duration_Hours_30D_Mean'
        in dataframe.columns
    ):

        dataframe['Sleep_Trend'] = (
            dataframe['Sleep_Duration_Hours_7D_Mean']
            - dataframe['Sleep_Duration_Hours_30D_Mean']
        )

    else:

        dataframe['Sleep_Trend'] = 0.0

    return dataframe


# =========================================================
# MISSING VALUE HANDLING
# =========================================================

def finalize_missing_values(
    dataframe,
):
    """
    Finalize missing values after feature engineering.

    Numeric columns are filled with 0.

    Categorical/text columns retain an explicit
    'Unknown' value.

    Date remains a datetime column.
    """

    dataframe = dataframe.copy()

    for column in dataframe.columns:

        if column == 'Date':
            continue

        if pd.api.types.is_numeric_dtype(
            dataframe[column]
        ):

            dataframe[column] = (
                dataframe[column]
                .replace(
                    [float('inf'), float('-inf')],
                    pd.NA,
                )
                .fillna(0.0)
            )

        else:

            dataframe[column] = (
                dataframe[column]
                .fillna('Unknown')
            )

    return dataframe


# =========================================================
# FEATURE COLUMN VALIDATION
# =========================================================

def validate_feature_dataset(
    dataframe,
):
    """
    Validate the final Feature Dataset.
    """

    if dataframe is None:
        raise ValueError(
            "Feature dataset is None."
        )

    if dataframe.empty:
        return dataframe

    if 'Date' not in dataframe.columns:
        raise ValueError(
            "Feature dataset must contain 'Date'."
        )

    if not dataframe[
        'Date'
    ].is_monotonic_increasing:

        raise ValueError(
            "Feature dataset dates are not sorted."
        )

    if dataframe[
        'Date'
    ].duplicated().any():

        raise ValueError(
            "Feature dataset contains duplicate dates."
        )

    numeric_columns = dataframe.select_dtypes(
        include='number'
    ).columns

    if len(numeric_columns) > 0:

        numeric_values = dataframe[
            numeric_columns
        ]

        if numeric_values.isna().any().any():

            raise ValueError(
                "Feature dataset contains NaN values "
                "in numeric columns."
            )

        if numeric_values.isin(
            [float('inf'), float('-inf')]
        ).any().any():

            raise ValueError(
                "Feature dataset contains infinite "
                "numeric values."
            )

    return dataframe


# =========================================================
# MAIN FEATURE ENGINEERING PIPELINE
# =========================================================

def build_feature_dataset(
    rolling_windows=None,
):
    """
    Build the complete Feature Dataset.

    Pipeline:

        Prepared Dataset
            ↓
        Normalization
            ↓
        Calendar Features
            ↓
        Financial Features
            ↓
        Health Features
            ↓
        Activity Features
            ↓
        Sleep Features
            ↓
        Event Features
            ↓
        Plan Features
            ↓
        Recurring Features
            ↓
        Behavioral Features
            ↓
        Interaction Features
            ↓
        Lag Features
            ↓
        Rolling Features
            ↓
        Trend Features
            ↓
        Missing Value Handling
            ↓
        Validation

    Returns:
        pandas.DataFrame
    """

    dataframe = create_dataframe()

    if dataframe.empty:
        return dataframe

    # -----------------------------------------------------
    # Basic normalization
    # -----------------------------------------------------

    dataframe = normalize_dataframe(
        dataframe
    )

    if dataframe.empty:
        return dataframe

    # -----------------------------------------------------
    # Calendar
    # -----------------------------------------------------

    dataframe = add_calendar_features(
        dataframe
    )

    # -----------------------------------------------------
    # Financial
    # -----------------------------------------------------

    dataframe = add_financial_features(
        dataframe
    )

    # -----------------------------------------------------
    # Health
    # -----------------------------------------------------

    dataframe = add_health_features(
        dataframe
    )

    # -----------------------------------------------------
    # Activities
    # -----------------------------------------------------

    dataframe = add_activity_features(
        dataframe
    )

    # -----------------------------------------------------
    # Sleep
    # -----------------------------------------------------

    dataframe = add_sleep_features(
        dataframe
    )

    # -----------------------------------------------------
    # Events
    # -----------------------------------------------------

    dataframe = add_event_features(
        dataframe
    )

    # -----------------------------------------------------
    # Plans
    # -----------------------------------------------------

    dataframe = add_plan_features(
        dataframe
    )

    # -----------------------------------------------------
    # Recurring
    # -----------------------------------------------------

    dataframe = add_recurring_features(
        dataframe
    )

    # -----------------------------------------------------
    # Behavioral
    # -----------------------------------------------------

    dataframe = add_behavioral_features(
        dataframe
    )

    # -----------------------------------------------------
    # Interactions
    # -----------------------------------------------------

    dataframe = add_interaction_features(
        dataframe
    )

    # -----------------------------------------------------
    # Historical features
    # -----------------------------------------------------

    dataframe = add_lag_features(
        dataframe
    )

    dataframe = add_rolling_features(
        dataframe,
        windows=rolling_windows,
    )

    # -----------------------------------------------------
    # Trends
    # -----------------------------------------------------

    dataframe = add_trend_features(
        dataframe
    )

    # -----------------------------------------------------
    # Final cleanup
    # -----------------------------------------------------

    dataframe = finalize_missing_values(
        dataframe
    )

    # -----------------------------------------------------
    # Validation
    # -----------------------------------------------------

    dataframe = validate_feature_dataset(
        dataframe
    )

    return dataframe


# =========================================================
# PUBLIC ENTRY POINT
# =========================================================

def get_feature_dataset(
    rolling_windows=None,
):
    """
    Public entry point for Feature Engineering.

    Returns a pandas DataFrame containing the prepared
    daily data plus engineered features.

    Parameters
    ----------
    rolling_windows : iterable of int, optional
        Historical windows used for rolling features.

        Default:
            3, 7, 30 days

    Returns
    -------
    pandas.DataFrame
    """

    return build_feature_dataset(
        rolling_windows=rolling_windows
    )


# =========================================================
# SIMPLE TEST / DEBUG OUTPUT
# =========================================================

if __name__ == '__main__':

    print()
    print(
        '========== FEATURE ENGINEERING TEST =========='
    )

    dataframe = get_feature_dataset()

    if dataframe.empty:

        print(
            'Feature dataset is empty.'
        )

    else:

        print(
            f'Total rows: {len(dataframe)}'
        )

        print(
            f'Total columns: {len(dataframe.columns)}'
        )

        print()

        print(
            'Date range:'
        )

        print(
            f"From: {dataframe['Date'].min().date()}"
        )

        print(
            f"To:   {dataframe['Date'].max().date()}"
        )

        print()

        print(
            '========== FEATURE COLUMNS =========='
        )

        for column in dataframe.columns:

            print(
                column
            )

        print()

        print(
            '========== FIRST ROW =========='
        )

        print(
            dataframe.iloc[0].to_dict()
        )

        print()

        print(
            '========== FEATURE ENGINEERING PASSED =========='
        )