
# ============================================================
# TARGET DATASET BUILDER
# ============================================================

from ml.preparation.preparation import get_prepared_dataset

from ml.targets.activity import create_activity_targets
from ml.targets.behavioral import create_behavioral_targets
from ml.targets.events import create_event_targets
from ml.targets.financial import create_financial_targets
from ml.targets.health import create_health_targets
from ml.targets.location import create_location_targets
from ml.targets.patterns import create_pattern_targets
from ml.targets.travel import create_travel_targets


# ============================================================
# HORIZONS
# ============================================================

# Detailed targets:
# T+1 ... T+7

DAILY_HORIZONS = {
    '1D': 1,
    '2D': 2,
    '3D': 3,
    '4D': 4,
    '5D': 5,
    '6D': 6,
    '7D': 7,
}


# Aggregate future periods:
#
# 8_15D  -> T+8  ... T+15
# 16_30D -> T+16 ... T+30
# 30D    -> T+1  ... T+30

PERIOD_HORIZONS = {
    '8_15D': (8, 15),
    '16_30D': (16, 30),
    '30D': (1, 30),
}


ALL_HORIZONS = {
    **DAILY_HORIZONS,
    **{
        horizon: end_day
        for horizon, (_, end_day) in PERIOD_HORIZONS.items()
    },
}


# ============================================================
# FUTURE DATA HELPERS
# ============================================================

def get_future_day(
    prepared_data,
    current_index,
    future_day,
):
    """
    Return exactly one future row.

    Examples:
        future_day=1 -> T+1
        future_day=7 -> T+7
        future_day=30 -> T+30

    Returns None when the requested future day does not exist.
    """

    target_index = current_index + future_day

    if target_index < 0 or target_index >= len(prepared_data):
        return None

    return prepared_data[target_index]


def get_future_period(
    prepared_data,
    current_index,
    start_day,
    end_day,
):
    """
    Return rows belonging to a future period.

    Examples:
        8, 15  -> T+8 ... T+15
        16, 30 -> T+16 ... T+30
        1, 30  -> T+1 ... T+30

    The current row T is never included.
    """

    if start_day < 1:
        raise ValueError('start_day must be >= 1.')

    if end_day < start_day:
        raise ValueError('end_day must be >= start_day.')

    start_index = current_index + start_day
    end_index = current_index + end_day + 1

    return prepared_data[start_index:end_index]


def has_future_day(
    prepared_data,
    current_index,
    future_day,
):
    """Return True when the requested future day exists."""

    return (
        get_future_day(
            prepared_data,
            current_index,
            future_day,
        )
        is not None
    )


def has_complete_future_period(
    prepared_data,
    current_index,
    start_day,
    end_day,
):
    """
    Return True when every day in the requested future period exists.
    """

    future_rows = get_future_period(
        prepared_data,
        current_index,
        start_day,
        end_day,
    )

    expected_days = end_day - start_day + 1

    return len(future_rows) == expected_days


# ============================================================
# TARGET COLUMN HELPERS
# ============================================================

def _nan_targets(horizon_name):
    """
    Return the standard empty target structure for one horizon.
    """

    nan = float('nan')

    return {
        # Activity
        f'Target_Has_Activity_{horizon_name}': nan,
        f'Target_High_Activity_{horizon_name}': nan,
        f'Target_Long_Activity_{horizon_name}': nan,

        # Behavioral
        f'Target_High_Stress_{horizon_name}': nan,
        f'Target_Moderate_or_High_Stress_{horizon_name}': nan,
        f'Target_Low_Sleep_{horizon_name}': nan,
        f'Target_Very_Low_Sleep_{horizon_name}': nan,
        f'Target_High_Social_Activity_{horizon_name}': nan,
        f'Target_Moderate_or_High_Social_Activity_{horizon_name}': nan,
        f'Target_Working_Day_{horizon_name}': nan,
        f'Target_Difficult_Behavioral_Day_{horizon_name}': nan,

        # Events
        f'Target_Has_Event_{horizon_name}': nan,
        f'Target_Multiple_Events_{horizon_name}': nan,
        f'Target_Has_Special_Event_{horizon_name}': nan,

        # Financial
        f'Target_Expense_Total_{horizon_name}': nan,
        f'Target_Income_Total_{horizon_name}': nan,
        f'Target_Balance_{horizon_name}': nan,
        f'Target_Expense_Days_{horizon_name}': nan,
        f'Target_Income_Days_{horizon_name}': nan,
        f'Target_High_Expense_{horizon_name}': nan,

        # Health
        f'Target_Health_Problem_{horizon_name}': nan,
        f'Target_High_Health_Severity_{horizon_name}': nan,
        f'Target_Low_Energy_{horizon_name}': nan,
        f'Target_Significant_Health_Day_{horizon_name}': nan,

        # Location
        f'Target_Has_Location_{horizon_name}': nan,
        f'Target_Location_Changed_{horizon_name}': nan,
        f'Target_Same_Location_{horizon_name}': nan,
        f'Target_Location_{horizon_name}': None,

        # Patterns
        f'Target_Busy_Day_{horizon_name}': nan,
        f'Target_Financial_Activity_{horizon_name}': nan,
        f'Target_Difficult_Day_{horizon_name}': nan,
        f'Target_Active_Day_{horizon_name}': nan,
        f'Target_Travel_Day_{horizon_name}': nan,
        f'Target_Special_Day_{horizon_name}': nan,

        # Travel
        f'Target_Travel_Day_{horizon_name}': nan,
    }


# ============================================================
# TARGET CREATION
# ============================================================

def _create_targets(
    future_rows,
    horizon_name,
    previous_rows,
):
    """
    Create all target categories for the supplied future rows.

    This helper is shared by daily and period targets.
    """

    targets = {}

    targets.update(
        create_activity_targets(
            future_rows,
            horizon_name,
        )
    )

    targets.update(
        create_behavioral_targets(
            future_rows,
            horizon_name,
        )
    )

    targets.update(
        create_event_targets(
            future_rows,
            horizon_name,
        )
    )

    targets.update(
        create_financial_targets(
            future_rows,
            horizon_name,
            previous_rows,
        )
    )

    targets.update(
        create_health_targets(
            future_rows,
            horizon_name,
        )
    )

    targets.update(
        create_location_targets(
            future_rows,
            horizon_name,
            previous_rows,
        )
    )

    targets.update(
        create_pattern_targets(
            future_rows,
            horizon_name,
        )
    )

    targets.update(
        create_travel_targets(
            future_rows,
            horizon_name,
        )
    )

    return targets


def create_daily_targets(
    future_row,
    horizon_name,
    previous_rows,
):
    """
    Create targets for exactly one future day.

    Supported horizons:
        1D -> T+1
        ...
        7D -> T+7

    This function never aggregates multiple future days.
    """

    if horizon_name not in DAILY_HORIZONS:
        raise ValueError(
            f'Unsupported daily horizon: {horizon_name}'
        )

    if future_row is None:
        return _nan_targets(horizon_name)

    return _create_targets(
        [future_row],
        horizon_name,
        previous_rows,
    )


def create_period_targets(
    future_rows,
    horizon_name,
    previous_rows,
):
    """
    Create aggregate targets for one future period.

    Supported periods:
        8_15D
        16_30D
        30D

    These targets describe the period as a whole.
    """

    if horizon_name not in PERIOD_HORIZONS:
        raise ValueError(
            f'Unsupported period horizon: {horizon_name}'
        )

    if not future_rows:
        return _nan_targets(horizon_name)

    return _create_targets(
        future_rows,
        horizon_name,
        previous_rows,
    )


# ============================================================
# TARGET DATASET BUILDER
# ============================================================

def build_target_dataset(prepared_data=None):
    """
    Build the future-oriented Target Dataset.

    Detailed daily targets:
        T+1 ... T+7

    Period targets:
        T+8 ... T+15
        T+16 ... T+30
        T+1 ... T+30

    Incomplete future periods receive NaN targets.
    """

    if prepared_data is None:
        prepared_data = get_prepared_dataset()

    if not prepared_data:
        return []

    prepared_data = sorted(
        prepared_data,
        key=lambda row: row['Date'],
    )

    target_dataset = []

    for current_index, current_row in enumerate(prepared_data):

        targets = {
            'Date': current_row['Date'],
        }

        # Only historical rows before the current day.
        previous_rows = prepared_data[:current_index]

        # ----------------------------------------------------
        # DAILY TARGETS: T+1 ... T+7
        # ----------------------------------------------------

        for horizon_name, future_day in DAILY_HORIZONS.items():

            future_row = get_future_day(
                prepared_data,
                current_index,
                future_day,
            )

            targets.update(
                create_daily_targets(
                    future_row,
                    horizon_name,
                    previous_rows,
                )
            )

        # ----------------------------------------------------
        # PERIOD TARGETS
        # ----------------------------------------------------

        for horizon_name, (start_day, end_day) in (
            PERIOD_HORIZONS.items()
        ):

            future_rows = get_future_period(
                prepared_data,
                current_index,
                start_day,
                end_day,
            )

            expected_days = end_day - start_day + 1

            if len(future_rows) == expected_days:
                targets.update(
                    create_period_targets(
                        future_rows,
                        horizon_name,
                        previous_rows,
                    )
                )
            else:
                targets.update(
                    create_period_targets(
                        [],
                        horizon_name,
                        previous_rows,
                    )
                )

        target_dataset.append(targets)

    return target_dataset


# ============================================================
# PUBLIC ENTRY POINT
# ============================================================

def get_target_dataset(prepared_data=None):
    """
    Public entry point for Target Engineering.
    """

    return build_target_dataset(prepared_data)


# ============================================================
# TARGET NAMES
# ============================================================

def get_target_names():
    """
    Return all target names generated by this builder.
    """

    target_names = []

    for horizon in DAILY_HORIZONS:
        target_names.extend(
            _nan_targets(horizon).keys()
        )

    for horizon in PERIOD_HORIZONS:
        target_names.extend(
            _nan_targets(horizon).keys()
        )

    return target_names


# ============================================================
# TARGET DATASET VALIDATION
# ============================================================

def validate_target_dataset(target_dataset):
    """
    Validate the generated Target Dataset.

    Checks:
        - Dataset is not None.
        - Every row contains Date.
        - Dates are chronological.
        - Every row has the same columns.
        - Date is a required column.
    """

    if target_dataset is None:
        raise ValueError('Target dataset is None.')

    if not target_dataset:
        return target_dataset

    # --------------------------------------------------------
    # Validate Date values
    # --------------------------------------------------------

    dates = [
        row.get('Date')
        for row in target_dataset
    ]

    if any(date is None for date in dates):
        raise ValueError(
            'Target dataset contains a row without Date.'
        )

    # --------------------------------------------------------
    # Chronological ordering
    # --------------------------------------------------------

    if dates != sorted(dates):
        raise ValueError(
            'Target dataset is not chronologically ordered.'
        )

    # --------------------------------------------------------
    # Expected structure
    # --------------------------------------------------------

    expected_columns = set(
        target_dataset[0].keys()
    )

    # --------------------------------------------------------
    # Validate every row
    # --------------------------------------------------------

    for index, row in enumerate(target_dataset):

        actual_columns = set(row.keys())

        if actual_columns != expected_columns:

            missing_columns = (
                expected_columns - actual_columns
            )

            extra_columns = (
                actual_columns - expected_columns
            )

            raise ValueError(
                f'Target row {index} has an '
                'inconsistent column structure.\n'
                f'Missing columns: {sorted(missing_columns)}\n'
                f'Extra columns: {sorted(extra_columns)}'
            )

    # --------------------------------------------------------
    # Required Date column
    # --------------------------------------------------------

    if 'Date' not in expected_columns:
        raise ValueError(
            'Target dataset does not contain Date.'
        )

    return target_dataset


# ============================================================
# DEBUG SUMMARY
# ============================================================

def print_target_summary(target_dataset):
    """
    Print a compact summary of generated targets.
    """

    if not target_dataset:
        print('Target dataset is empty.')
        return

    columns = [
        column
        for column in target_dataset[0].keys()
        if column != 'Date'
    ]

    print()
    print('========== TARGET SUMMARY ==========')
    print(f'Total rows: {len(target_dataset)}')
    print(f'Total target columns: {len(columns)}')

    # --------------------------------------------------------
    # Daily targets
    # --------------------------------------------------------

    print()
    print('========== DAILY TARGETS ==========')

    for horizon in DAILY_HORIZONS:

        horizon_columns = [
            column
            for column in columns
            if column.endswith(f'_{horizon}')
        ]

        if not horizon_columns:
            continue

        available_values = 0
        missing_values = 0

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

            available_values += available
            missing_values += len(values) - available

        print(
            f'{horizon}: '
            f'columns={len(horizon_columns)}, '
            f'available={available_values}, '
            f'missing={missing_values}'
        )

    # --------------------------------------------------------
    # Period targets
    # --------------------------------------------------------

    print()
    print('========== PERIOD TARGETS ==========')

    for horizon in PERIOD_HORIZONS:

        horizon_columns = [
            column
            for column in columns
            if column.endswith(f'_{horizon}')
        ]

        if not horizon_columns:
            continue

        available_values = 0
        missing_values = 0

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

            available_values += available
            missing_values += len(values) - available

        print(
            f'{horizon}: '
            f'columns={len(horizon_columns)}, '
            f'available={available_values}, '
            f'missing={missing_values}'
        )

    print()


# ============================================================
# SIMPLE BUILD TEST
# ============================================================

if __name__ == '__main__':

    print()
    print('========== TARGET BUILD TEST ==========')

    dataset = build_target_dataset()

    if not dataset:

        print('Target dataset is empty.')

    else:

        validate_target_dataset(dataset)

        print(f'Total rows: {len(dataset)}')
        print(f'Total columns: {len(dataset[0])}')

        print()
        print('Date range:')
        print(f"From: {dataset[0]['Date']}")
        print(f"To:   {dataset[-1]['Date']}")

        print_target_summary(dataset)

        print()
        print('========== FIRST ROW ==========')

        for key, value in dataset[0].items():
            print(f'{key}: {value}')

        print()
        print('========== LAST ROW ==========')

        for key, value in dataset[-1].items():
            print(f'{key}: {value}')

        print()
        print('========== TARGET BUILD PASSED ==========')
