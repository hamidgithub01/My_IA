# =========================================================
# TARGET DATASET BUILDER
# =========================================================

from ml.preparation.preparation import (
    get_prepared_dataset,
)

from ml.targets.activity import (
    create_activity_targets,
)

from ml.targets.behavioral import (
    create_behavioral_targets,
)

from ml.targets.events import (
    create_event_targets,
)

from ml.targets.financial import (
    create_financial_targets,
)

from ml.targets.health import (
    create_health_targets,
)

from ml.targets.location import (
    create_location_targets,
)

from ml.targets.patterns import (
    create_pattern_targets,
)

from ml.targets.travel import (
    create_travel_targets,
)


# =========================================================
# HORIZONS
# =========================================================

HORIZONS = {
    '1D': 1,
    '7D': 7,
    '30D': 30,
}


# =========================================================
# FUTURE WINDOW BUILDER
# =========================================================

def get_future_rows(
    prepared_data,
    current_index,
    horizon_days,
):
    """
    Return the future rows belonging to a target horizon.

    For a row at T:

        1D  -> T + 1
        7D  -> T + 1 ... T + 7
        30D -> T + 1 ... T + 30

    The current row T is NEVER included.

    Only rows that actually exist in the historical
    dataset are returned.

    Parameters
    ----------
    prepared_data : list[dict]

    current_index : int

    horizon_days : int

    Returns
    -------
    list[dict]
    """

    start_index = (
        current_index + 1
    )

    end_index = (
        current_index
        + horizon_days
        + 1
    )

    return prepared_data[
        start_index:end_index
    ]


# =========================================================
# TARGET AVAILABILITY
# =========================================================

def has_complete_future_window(
    prepared_data,
    current_index,
    horizon_days,
):
    """
    Determine whether the complete future horizon exists.

    Example:

        For a 7D target, the current row must have
        seven future rows available.

    This is important because a partially available
    future window should not be treated as a complete
    7D or 30D target.
    """

    future_rows = get_future_rows(
        prepared_data,
        current_index,
        horizon_days,
    )

    return len(future_rows) == horizon_days


# =========================================================
# TARGET DATASET BUILDER
# =========================================================

def build_target_dataset(
    prepared_data=None,
):
    """
    Build the final future-oriented Target Dataset.

    Data flow:

        Prepared Dataset
                ↓
        Chronological ordering
                ↓
        For each day T:
                ↓
        Future 1D / 7D / 30D windows
                ↓
        Target Engineering
                ↓
        Final Target Dataset

    Important
    ---------

    The target for date T is based exclusively on dates
    AFTER T.

    Therefore:

        Target_*_1D
            = outcome on T + 1

        Target_*_7D
            = outcome during T + 1 ... T + 7

        Target_*_30D
            = outcome during T + 1 ... T + 30

    The current day is never included.

    Incomplete future horizons return NaN targets.
    """

    # -----------------------------------------------------
    # Load prepared data
    # -----------------------------------------------------

    if prepared_data is None:

        prepared_data = get_prepared_dataset()

    if prepared_data is None:
        return []

    if not prepared_data:
        return []

    # -----------------------------------------------------
    # Chronological ordering
    # -----------------------------------------------------

    prepared_data = sorted(
        prepared_data,
        key=lambda row: row['Date'],
    )

    target_dataset = []

    # =====================================================
    # PROCESS EACH DAY
    # =====================================================

    for current_index, current_row in enumerate(
        prepared_data
    ):

        targets = {
            'Date': current_row['Date'],
        }

        # -------------------------------------------------
        # Future 1D
        # -------------------------------------------------

        future_1d = get_future_rows(
            prepared_data,
            current_index,
            HORIZONS['1D'],
        )

        # -------------------------------------------------
        # Future 7D
        # -------------------------------------------------

        future_7d = get_future_rows(
            prepared_data,
            current_index,
            HORIZONS['7D'],
        )

        # -------------------------------------------------
        # Future 30D
        # -------------------------------------------------

        future_30d = get_future_rows(
            prepared_data,
            current_index,
            HORIZONS['30D'],
        )

        # =================================================
        # ACTIVITY
        # =================================================

        targets.update(
            create_activity_targets(
                future_1d,
                '1D',
            )
        )

        targets.update(
            create_activity_targets(
                future_7d,
                '7D',
            )
        )

        targets.update(
            create_activity_targets(
                future_30d,
                '30D',
            )
        )

        # =================================================
        # BEHAVIORAL
        # =================================================

        targets.update(
            create_behavioral_targets(
                future_1d,
                '1D',
            )
        )

        targets.update(
            create_behavioral_targets(
                future_7d,
                '7D',
            )
        )

        targets.update(
            create_behavioral_targets(
                future_30d,
                '30D',
            )
        )

        # =================================================
        # EVENTS
        # =================================================

        targets.update(
            create_event_targets(
                future_1d,
                '1D',
            )
        )

        targets.update(
            create_event_targets(
                future_7d,
                '7D',
            )
        )

        targets.update(
            create_event_targets(
                future_30d,
                '30D',
            )
        )

        # =================================================
        # FINANCIAL
        # =================================================
        #
        # Financial is currently still based on the existing
        # financial target implementation.
        #
        # It will be redesigned next so that financial
        # targets contain useful numerical future values.
        # =================================================

        targets.update(
            create_financial_targets(
                current_row,
                prepared_data[
                    :current_index
                ],
            )
        )

        # =================================================
        # HEALTH
        # =================================================

        targets.update(
            create_health_targets(
                future_1d,
                '1D',
            )
        )

        targets.update(
            create_health_targets(
                future_7d,
                '7D',
            )
        )

        targets.update(
            create_health_targets(
                future_30d,
                '30D',
            )
        )

        # =================================================
        # LOCATION
        # =================================================

        targets.update(
            create_location_targets(
                future_1d,
                '1D',
            )
        )

        targets.update(
            create_location_targets(
                future_7d,
                '7D',
            )
        )

        targets.update(
            create_location_targets(
                future_30d,
                '30D',
            )
        )

        # =================================================
        # PATTERNS
        # =================================================

        targets.update(
            create_pattern_targets(
                future_1d,
                '1D',
            )
        )

        targets.update(
            create_pattern_targets(
                future_7d,
                '7D',
            )
        )

        targets.update(
            create_pattern_targets(
                future_30d,
                '30D',
            )
        )

        # =================================================
        # TRAVEL
        # =================================================

        targets.update(
            create_travel_targets(
                future_1d,
                '1D',
            )
        )

        targets.update(
            create_travel_targets(
                future_7d,
                '7D',
            )
        )

        targets.update(
            create_travel_targets(
                future_30d,
                '30D',
            )
        )

        # -------------------------------------------------
        # Store targets
        # -------------------------------------------------

        target_dataset.append(
            targets
        )

    return target_dataset


# =========================================================
# PUBLIC ENTRY POINT
# =========================================================

def get_target_dataset(
    prepared_data=None,
):
    """
    Public entry point for Target Engineering.
    """

    return build_target_dataset(
        prepared_data
    )


# =========================================================
# TARGET METADATA
# =========================================================

def get_target_names():
    """
    Return the raw target names generated by this builder.

    Financial targets are currently excluded from the
    horizon-specific list because they are still using
    the old implementation and will be redesigned next.
    """

    return [

        # -------------------------------------------------
        # Activity
        # -------------------------------------------------

        'Target_Has_Activity_1D',
        'Target_High_Activity_1D',
        'Target_Long_Activity_1D',

        'Target_Has_Activity_7D',
        'Target_High_Activity_7D',
        'Target_Long_Activity_7D',

        'Target_Has_Activity_30D',
        'Target_High_Activity_30D',
        'Target_Long_Activity_30D',

        # -------------------------------------------------
        # Behavioral
        # -------------------------------------------------

        'Target_High_Stress_1D',
        'Target_Moderate_or_High_Stress_1D',
        'Target_Low_Sleep_1D',
        'Target_Very_Low_Sleep_1D',
        'Target_High_Social_Activity_1D',
        'Target_Moderate_or_High_Social_Activity_1D',
        'Target_Working_Day_1D',
        'Target_Difficult_Behavioral_Day_1D',

        'Target_High_Stress_7D',
        'Target_Moderate_or_High_Stress_7D',
        'Target_Low_Sleep_7D',
        'Target_Very_Low_Sleep_7D',
        'Target_High_Social_Activity_7D',
        'Target_Moderate_or_High_Social_Activity_7D',
        'Target_Working_Day_7D',
        'Target_Difficult_Behavioral_Day_7D',

        'Target_High_Stress_30D',
        'Target_Moderate_or_High_Stress_30D',
        'Target_Low_Sleep_30D',
        'Target_Very_Low_Sleep_30D',
        'Target_High_Social_Activity_30D',
        'Target_Moderate_or_High_Social_Activity_30D',
        'Target_Working_Day_30D',
        'Target_Difficult_Behavioral_Day_30D',

        # -------------------------------------------------
        # Events
        # -------------------------------------------------

        'Target_Has_Event_1D',
        'Target_Multiple_Events_1D',
        'Target_Has_Special_Event_1D',

        'Target_Has_Event_7D',
        'Target_Multiple_Events_7D',
        'Target_Has_Special_Event_7D',

        'Target_Has_Event_30D',
        'Target_Multiple_Events_30D',
        'Target_Has_Special_Event_30D',

        # -------------------------------------------------
        # Financial - current raw targets
        # -------------------------------------------------

        'Target_Has_Expense',
        'Target_Has_Income',
        'Target_Positive_Balance',
        'Target_High_Expense',

        # -------------------------------------------------
        # Health
        # -------------------------------------------------

        'Target_Health_Problem_1D',
        'Target_High_Health_Severity_1D',
        'Target_Low_Energy_1D',
        'Target_Significant_Health_Day_1D',

        'Target_Health_Problem_7D',
        'Target_High_Health_Severity_7D',
        'Target_Low_Energy_7D',
        'Target_Significant_Health_Day_7D',

        'Target_Health_Problem_30D',
        'Target_High_Health_Severity_30D',
        'Target_Low_Energy_30D',
        'Target_Significant_Health_Day_30D',

        # -------------------------------------------------
        # Location
        # -------------------------------------------------

        'Target_Has_Location_1D',
        'Target_Location_Changed_1D',
        'Target_Same_Location_1D',
        'Target_Location_1D',

        'Target_Has_Location_7D',
        'Target_Location_Changed_7D',
        'Target_Same_Location_7D',
        'Target_Location_7D',

        'Target_Has_Location_30D',
        'Target_Location_Changed_30D',
        'Target_Same_Location_30D',
        'Target_Location_30D',

        # -------------------------------------------------
        # Patterns
        # -------------------------------------------------

        'Target_Busy_Day_1D',
        'Target_Financial_Activity_1D',
        'Target_Difficult_Day_1D',
        'Target_Active_Day_1D',
        'Target_Travel_Day_1D',
        'Target_Special_Day_1D',

        'Target_Busy_Day_7D',
        'Target_Financial_Activity_7D',
        'Target_Difficult_Day_7D',
        'Target_Active_Day_7D',
        'Target_Travel_Day_7D',
        'Target_Special_Day_7D',

        'Target_Busy_Day_30D',
        'Target_Financial_Activity_30D',
        'Target_Difficult_Day_30D',
        'Target_Active_Day_30D',
        'Target_Travel_Day_30D',
        'Target_Special_Day_30D',

        # -------------------------------------------------
        # Travel
        # -------------------------------------------------

        'Target_Travel_Day_1D',
        'Target_Travel_Day_7D',
        'Target_Travel_Day_30D',
    ]


# =========================================================
# VALIDATION
# =========================================================

def validate_target_dataset(
    target_dataset,
):
    """
    Validate the generated Target Dataset.
    """

    if target_dataset is None:
        raise ValueError(
            'Target dataset is None.'
        )

    if not target_dataset:
        return target_dataset

    dates = [
        row.get('Date')
        for row in target_dataset
    ]

    if any(
        date is None
        for date in dates
    ):
        raise ValueError(
            'Target dataset contains a row '
            'without Date.'
        )

    # -----------------------------------------------------
    # Ensure chronological ordering
    # -----------------------------------------------------

    if dates != sorted(dates):

        raise ValueError(
            'Target dataset is not chronologically ordered.'
        )

    # -----------------------------------------------------
    # Ensure all rows have the same structure
    # -----------------------------------------------------

    expected_columns = set(
        target_dataset[0].keys()
    )

    for index, row in enumerate(
        target_dataset
    ):

        actual_columns = set(
            row.keys()
        )

        if actual_columns != expected_columns:

            raise ValueError(
                f'Target row {index} has an '
                'inconsistent column structure.'
            )

    return target_dataset


# =========================================================
# DEBUG SUMMARY
# =========================================================

def print_target_summary(
    target_dataset,
):
    """
    Print a compact summary of the generated Targets.
    """

    if not target_dataset:

        print(
            'Target dataset is empty.'
        )

        return

    columns = [
        column
        for column in target_dataset[0].keys()
        if column != 'Date'
    ]

    print()
    print(
        '========== TARGET SUMMARY =========='
    )

    print(
        f'Total rows: {len(target_dataset)}'
    )

    print(
        f'Total target columns: {len(columns)}'
    )

    print()

    for horizon in (
        '1D',
        '7D',
        '30D',
    ):

        horizon_columns = [
            column
            for column in columns
            if column.endswith(
                f'_{horizon}'
            )
        ]

        if not horizon_columns:
            continue

        print(
            f'========== {horizon} =========='
        )

        for column in horizon_columns:

            values = [
                row.get(column)
                for row in target_dataset
            ]

            available = sum(
                value is not None
                and value == value
                for value in values
            )

            missing = (
                len(values)
                - available
            )

            print(
                f'{column}: '
                f'available={available}, '
                f'missing={missing}'
            )

        print()


# =========================================================
# SIMPLE TEST / DEBUG
# =========================================================

if __name__ == '__main__':

    print()
    print(
        '========== TARGET BUILD TEST =========='
    )

    dataset = build_target_dataset()

    if not dataset:

        print(
            'Target dataset is empty.'
        )

    else:

        validate_target_dataset(
            dataset
        )

        print(
            f'Total rows: {len(dataset)}'
        )

        print(
            f'Total columns: '
            f'{len(dataset[0])}'
        )

        print()

        print(
            'Date range:'
        )

        print(
            f"From: {dataset[0]['Date']}"
        )

        print(
            f"To:   {dataset[-1]['Date']}"
        )

        print_target_summary(
            dataset
        )

        print()

        print(
            '========== FIRST ROW =========='
        )

        for key, value in dataset[0].items():

            print(
                f'{key}: {value}'
            )

        print()

        print(
            '========== LAST ROW =========='
        )

        for key, value in dataset[-1].items():

            print(
                f'{key}: {value}'
            )

        print()

        print(
            '========== TARGET BUILD PASSED =========='
        )