import pandas as pd


# =========================================================
# CONFIGURATION
# =========================================================

HORIZONS = {
    '1D': 1,
    '7D': 7,
    '30D': 30,
}


# =========================================================
# TARGET DEFINITIONS
# =========================================================
#
# كل Target هنا يحدد:
#
# source      : العمود الأصلي
# aggregation : كيف نحول المستقبل إلى Target
#
# أنواع التجميع:
#
# next_value
# sum
# mean
# max
# count
# ratio
# categorical
#
# =========================================================

TARGET_DEFINITIONS = {

    # -----------------------------------------------------
    # Behavioral
    # -----------------------------------------------------

    'Stress_Level': {
        'source': 'Stress_Level',
        'aggregation': 'next_value',
        'type': 'numeric',
    },

    'Sleep_Hours': {
        'source': 'Sleep_Hours',
        'aggregation': 'next_value',
        'type': 'numeric',
    },

    'Social_Activity': {
        'source': 'Social_Activity',
        'aggregation': 'next_value',
        'type': 'categorical',
    },

    'Work_Status': {
        'source': 'Work_Status',
        'aggregation': 'next_value',
        'type': 'categorical',
    },

    # -----------------------------------------------------
    # Activity
    # -----------------------------------------------------

    'Activity_Count': {
        'source': 'Activity_Count',
        'aggregation': 'next_value',
        'type': 'numeric',
    },

    'Activity_Duration_Minutes': {
        'source': 'Activity_Duration_Minutes',
        'aggregation': 'next_value',
        'type': 'numeric',
    },

    # -----------------------------------------------------
    # Events
    # -----------------------------------------------------

    'Event_Count': {
        'source': 'Event_Count',
        'aggregation': 'next_value',
        'type': 'numeric',
    },

    # -----------------------------------------------------
    # Financial
    # -----------------------------------------------------

    'Expense_Total': {
        'source': 'Expense_Total',
        'aggregation': 'next_value',
        'type': 'numeric',
    },

    'Income_Total': {
        'source': 'Income_Total',
        'aggregation': 'next_value',
        'type': 'numeric',
    },

    # -----------------------------------------------------
    # Health
    # -----------------------------------------------------

    'Max_Health_Severity': {
        'source': 'Max_Health_Severity',
        'aggregation': 'next_value',
        'type': 'numeric',
    },

    'Avg_Energy_Level': {
        'source': 'Avg_Energy_Level',
        'aggregation': 'next_value',
        'type': 'numeric',
    },

    'Health_Record_Count': {
        'source': 'Health_Record_Count',
        'aggregation': 'next_value',
        'type': 'numeric',
    },

    # -----------------------------------------------------
    # Location
    # -----------------------------------------------------

    'Location': {
        'source': 'Location',
        'aggregation': 'next_value',
        'type': 'categorical',
    },

    # -----------------------------------------------------
    # Travel
    # -----------------------------------------------------

    'Travel': {
        'source': 'Travel',
        'aggregation': 'next_value',
        'type': 'categorical',
    },
}


# =========================================================
# REQUIRED SOURCE COLUMNS
# =========================================================

REQUIRED_SOURCE_COLUMNS = {
    definition['source']
    for definition in TARGET_DEFINITIONS.values()
}


# =========================================================
# LOAD FEATURE DATASET
# =========================================================

def load_feature_dataset():
    """
    Load the Feature Dataset from Feature Engineering.
    """

    from ml.features.engineering import (
        get_feature_dataset,
    )

    dataframe = get_feature_dataset()

    if dataframe is None:
        raise ValueError(
            'Feature dataset is None.'
        )

    return dataframe.copy()


# =========================================================
# INPUT VALIDATION
# =========================================================

def validate_input_dataset(
    dataframe,
):
    """
    Validate and chronologically sort the Feature Dataset.
    """

    if dataframe is None:
        raise ValueError(
            'Input Feature Dataset is None.'
        )

    if dataframe.empty:
        return dataframe

    if 'Date' not in dataframe.columns:
        raise ValueError(
            "Feature Dataset must contain 'Date'."
        )

    dataframe['Date'] = pd.to_datetime(
        dataframe['Date'],
        errors='coerce',
    )

    if dataframe['Date'].isna().any():
        raise ValueError(
            'Feature Dataset contains invalid dates.'
        )

    dataframe = (
        dataframe
        .sort_values('Date')
        .reset_index(drop=True)
    )

    if dataframe['Date'].duplicated().any():
        raise ValueError(
            'Feature Dataset contains duplicate dates.'
        )

    missing_columns = (
        REQUIRED_SOURCE_COLUMNS
        - set(dataframe.columns)
    )

    if missing_columns:

        missing_text = ', '.join(
            sorted(missing_columns)
        )

        raise ValueError(
            'Feature Dataset is missing required '
            f'columns: {missing_text}'
        )

    return dataframe


# =========================================================
# NORMALIZATION
# =========================================================

def normalize_numeric(value):
    """
    Safely convert a value to float.
    """

    if value is None:
        return None

    numeric = pd.to_numeric(
        value,
        errors='coerce',
    )

    if pd.isna(numeric):
        return None

    return float(numeric)


def normalize_categorical(value):
    """
    Safely normalize categorical values.
    """

    if value is None:
        return None

    if pd.isna(value):
        return None

    value = str(value).strip()

    if not value:
        return None

    return value


# =========================================================
# DATE MAP
# =========================================================

def create_date_map(
    dataframe,
):
    """
    Create a mapping:

        Date -> row

    This allows targets to be calculated using actual
    calendar dates rather than row positions.
    """

    return {
        row['Date']: row
        for _, row in dataframe.iterrows()
    }


# =========================================================
# FUTURE ROWS
# =========================================================

def get_future_rows(
    dataframe,
    current_date,
    horizon_days,
):
    """
    Return observed rows from:

        T+1 -> T+horizon

    The current day T is always excluded.
    """

    future_start = (
        current_date
        + pd.Timedelta(days=1)
    )

    future_end = (
        current_date
        + pd.Timedelta(days=horizon_days)
    )

    mask = (
        (dataframe['Date'] >= future_start)
        &
        (dataframe['Date'] <= future_end)
    )

    return dataframe.loc[mask]


# =========================================================
# NEXT VALUE
# =========================================================

def calculate_next_value(
    dataframe,
    current_date,
    source_column,
):
    """
    Return the value of T+1.
    """

    future_date = (
        current_date
        + pd.Timedelta(days=1)
    )

    rows = dataframe.loc[
        dataframe['Date'] == future_date
    ]

    if rows.empty:
        return None

    value = rows.iloc[0][
        source_column
    ]

    return value


# =========================================================
# FUTURE SUM
# =========================================================

def calculate_future_sum(
    future_rows,
    source_column,
):
    """
    Sum a numeric value over the future window.
    """

    if future_rows.empty:
        return None

    values = pd.to_numeric(
        future_rows[source_column],
        errors='coerce',
    ).dropna()

    if values.empty:
        return None

    return float(
        values.sum()
    )


# =========================================================
# FUTURE MEAN
# =========================================================

def calculate_future_mean(
    future_rows,
    source_column,
):
    """
    Calculate the mean value over the future window.
    """

    if future_rows.empty:
        return None

    values = pd.to_numeric(
        future_rows[source_column],
        errors='coerce',
    ).dropna()

    if values.empty:
        return None

    return float(
        values.mean()
    )


# =========================================================
# FUTURE MAX
# =========================================================

def calculate_future_max(
    future_rows,
    source_column,
):
    """
    Calculate maximum future value.
    """

    if future_rows.empty:
        return None

    values = pd.to_numeric(
        future_rows[source_column],
        errors='coerce',
    ).dropna()

    if values.empty:
        return None

    return float(
        values.max()
    )


# =========================================================
# FUTURE COUNT
# =========================================================

def calculate_future_count(
    future_rows,
    source_column,
):
    """
    Count future observed occurrences where the value
    is greater than zero.
    """

    if future_rows.empty:
        return None

    values = pd.to_numeric(
        future_rows[source_column],
        errors='coerce',
    )

    valid_values = values.dropna()

    if valid_values.empty:
        return None

    return int(
        valid_values.gt(0).sum()
    )


# =========================================================
# TARGET VALUE
# =========================================================

def calculate_target_value(
    dataframe,
    current_date,
    definition,
    horizon_days,
):
    """
    Calculate one Target according to its definition.
    """

    source_column = definition[
        'source'
    ]

    aggregation = definition[
        'aggregation'
    ]

    target_type = definition[
        'type'
    ]

    # -----------------------------------------------------
    # 1D next value
    # -----------------------------------------------------

    if aggregation == 'next_value':

        value = calculate_next_value(
            dataframe,
            current_date,
            source_column,
        )

        if target_type == 'numeric':
            return normalize_numeric(
                value
            )

        if target_type == 'categorical':
            return normalize_categorical(
                value
            )

        return value

    # -----------------------------------------------------
    # Future window
    # -----------------------------------------------------

    future_rows = get_future_rows(
        dataframe,
        current_date,
        horizon_days,
    )

    if aggregation == 'sum':

        return calculate_future_sum(
            future_rows,
            source_column,
        )

    if aggregation == 'mean':

        return calculate_future_mean(
            future_rows,
            source_column,
        )

    if aggregation == 'max':

        return calculate_future_max(
            future_rows,
            source_column,
        )

    if aggregation == 'count':

        return calculate_future_count(
            future_rows,
            source_column,
        )

    raise ValueError(
        f'Unknown target aggregation: '
        f'{aggregation}'
    )


# =========================================================
# TARGET NAME
# =========================================================

def make_target_name(
    target_name,
    horizon_name,
):
    """
    Build a standardized Target column name.
    """

    return (
        f'Target_{target_name}_{horizon_name}'
    )


# =========================================================
# BUILD TARGETS
# =========================================================

def create_targets_for_horizon(
    dataframe,
    horizon_name,
    horizon_days,
):
    """
    Create all Targets for one horizon.
    """

    dataframe = dataframe.copy()

    for target_name, definition in (
        TARGET_DEFINITIONS.items()
    ):

        values = []

        for current_date in dataframe[
            'Date'
        ]:

            value = calculate_target_value(
                dataframe,
                current_date,
                definition,
                horizon_days,
            )

            values.append(
                value
            )

        column_name = make_target_name(
            target_name,
            horizon_name,
        )

        dataframe[
            column_name
        ] = values

    return dataframe


# =========================================================
# TARGET COLUMN METADATA
# =========================================================

def get_target_columns():
    """
    Return all generated Target columns.
    """

    columns = []

    for horizon_name in HORIZONS:

        for target_name in (
            TARGET_DEFINITIONS
        ):

            columns.append(
                make_target_name(
                    target_name,
                    horizon_name,
                )
            )

    return columns


# =========================================================
# TARGET VALIDATION
# =========================================================

def validate_target_columns(
    dataframe,
):
    """
    Verify that all expected Target columns exist.
    """

    expected = set(
        get_target_columns()
    )

    actual = set(
        dataframe.columns
    )

    missing = expected - actual

    if missing:

        raise ValueError(
            'Missing Target columns: '
            + ', '.join(
                sorted(missing)
            )
        )

    return dataframe


# =========================================================
# TARGET FINALIZATION
# =========================================================

def finalize_targets(
    dataframe,
):
    """
    Finalize the Target Dataset.

    Important:

        Missing future information remains None/NaN.

    It is NEVER converted to zero.
    """

    dataframe = dataframe.copy()

    return dataframe


# =========================================================
# COMPLETE TARGET ENGINEERING
# =========================================================

def build_target_dataset():
    """
    Build the complete Target Dataset.

    Pipeline:

        Feature Dataset
             ↓
        Validation
             ↓
        Chronological ordering
             ↓
        1D Targets
             ↓
        7D Targets
             ↓
        30D Targets
             ↓
        Validation
             ↓
        Final Target Dataset
    """

    dataframe = load_feature_dataset()

    if dataframe.empty:
        return dataframe

    dataframe = validate_input_dataset(
        dataframe
    )

    # -----------------------------------------------------
    # 1D
    # -----------------------------------------------------

    dataframe = create_targets_for_horizon(
        dataframe,
        horizon_name='1D',
        horizon_days=1,
    )

    # -----------------------------------------------------
    # 7D
    # -----------------------------------------------------

    dataframe = create_targets_for_horizon(
        dataframe,
        horizon_name='7D',
        horizon_days=7,
    )

    # -----------------------------------------------------
    # 30D
    # -----------------------------------------------------

    dataframe = create_targets_for_horizon(
        dataframe,
        horizon_name='30D',
        horizon_days=30,
    )

    # -----------------------------------------------------
    # Finalization
    # -----------------------------------------------------

    dataframe = finalize_targets(
        dataframe
    )

    # -----------------------------------------------------
    # Validation
    # -----------------------------------------------------

    dataframe = validate_target_columns(
        dataframe
    )

    return dataframe


# =========================================================
# PUBLIC ENTRY POINT
# =========================================================

def get_target_dataset():
    """
    Public Target Engineering entry point.
    """

    return build_target_dataset()


# =========================================================
# SUMMARY
# =========================================================

def print_target_summary(
    dataframe,
):
    """
    Print Target availability summary.
    """

    print()
    print(
        '========== TARGET SUMMARY =========='
    )

    for horizon_name in HORIZONS:

        print()
        print(
            f'========== {horizon_name} =========='
        )

        for target_name in (
            TARGET_DEFINITIONS
        ):

            column = make_target_name(
                target_name,
                horizon_name,
            )

            available = (
                dataframe[column]
                .notna()
                .sum()
            )

            missing = (
                dataframe[column]
                .isna()
                .sum()
            )

            print(
                f'{column}: '
                f'available={available}, '
                f'missing={missing}'
            )


# =========================================================
# TEST
# =========================================================

if __name__ == '__main__':

    print()
    print(
        '========== TARGET ENGINEERING TEST =========='
    )

    dataframe = get_target_dataset()

    if dataframe.empty:

        print(
            'Target dataset is empty.'
        )

    else:

        print(
            f'Total rows: {len(dataframe)}'
        )

        print(
            f'Total columns: {len(dataframe.columns)}'
        )

        print(
            f'Total targets: '
            f'{len(get_target_columns())}'
        )

        print()

        print_target_summary(
            dataframe
        )

        print()

        print(
            '========== TARGET ENGINEERING PASSED =========='
        )